"""Results of one challenge and of a whole match."""
from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass, field
from typing import Optional

from .agents import AgentFailure

SIDES = ("A", "B")


def other(side: str) -> str:
    return "B" if side == "A" else "A"


def derive_seed(master: int, label: str) -> int:
    """Stable sub-seed, always positive, identical on every machine."""
    digest = hashlib.sha256(f"{master}:{label}".encode()).hexdigest()
    return int(digest[:12], 16) % (2**31 - 1) + 1


@dataclass
class GameResult:
    game: str
    winner: Optional[str]  # "A", "B", or None for a draw
    reason: str
    score: dict  # what to show per side, e.g. {"A": "5,842 km", "B": "6,103 km"}
    incidents: list = field(default_factory=list)  # [{"side", "kind", "detail"}]
    seed: Optional[int] = None
    duration_s: float = 0.0
    details: dict = field(default_factory=dict)  # game data used by visualizations

    @property
    def points(self) -> dict:
        if self.winner is None:
            return {"A": 0.5, "B": 0.5}
        return {self.winner: 1.0, other(self.winner): 0.0}

    def to_dict(self) -> dict:
        data = asdict(self)
        data["points"] = self.points
        return data


def incident(side: str, failure: AgentFailure) -> dict:
    return {"side": side, "kind": failure.kind, "detail": failure.detail[:2000]}


def start_players(players: dict, game: str, seed, score_when_failed: str = "-") -> Optional[GameResult]:
    """Start both agents. Returns a finished result if any failed to load."""
    failures = {}
    for side, player in players.items():
        try:
            player.start()
        except AgentFailure as failure:
            failures[side] = failure
    if not failures:
        return None
    for player in players.values():
        player.stop()
    incidents = [incident(side, failure) for side, failure in failures.items()]
    score = {side: score_when_failed for side in SIDES}
    if len(failures) == 2:
        return GameResult(game, None, "both_agents_failed", score, incidents, seed)
    loser = next(iter(failures))
    return GameResult(game, other(loser), failures[loser].kind, score, incidents, seed)


def match_points(results) -> dict:
    return {side: sum(result.points[side] for result in results) for side in SIDES}


def leader(points: dict) -> Optional[str]:
    if points["A"] == points["B"]:
        return None
    return "A" if points["A"] > points["B"] else "B"
