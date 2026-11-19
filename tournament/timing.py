"""Chess-style clocks for turn-based games, measured only by the judge."""
from __future__ import annotations

import time

from .agents import TIMEOUT, AgentFailure


class ChallengeTimeUp(Exception):
    """The challenge's global limit ran out. This is not any one player's fault."""


class TurnClocks:
    """One decision clock per player plus one global limit for the challenge.

    A player whose own clock runs out loses by time. If the global limit runs
    out first, nobody is blamed and the game adjudicates its result instead.
    """

    def __init__(self, players: dict, clock_s: float, challenge_limit_s: float):
        self.players = players
        self.remaining = {side: float(clock_s) for side in players}
        self.deadline = time.monotonic() + challenge_limit_s

    def time_left(self) -> float:
        return self.deadline - time.monotonic()

    def ask(self, side: str, observation: dict):
        global_left = self.time_left()
        if global_left <= 0:
            raise ChallengeTimeUp()
        budget = min(self.remaining[side], global_left)
        if budget <= 0:
            raise AgentFailure(TIMEOUT, "decision clock exhausted")
        try:
            response, elapsed = self.players[side].decide(observation, budget)
        except AgentFailure as failure:
            if failure.kind != TIMEOUT:
                raise
            if self.remaining[side] <= global_left:
                self.remaining[side] = 0.0
                raise
            self.remaining[side] -= budget
            raise ChallengeTimeUp() from failure
        self.remaining[side] -= elapsed
        if self.remaining[side] <= 0:
            self.remaining[side] = 0.0
            raise AgentFailure(TIMEOUT, "decision clock exhausted")
        return response
