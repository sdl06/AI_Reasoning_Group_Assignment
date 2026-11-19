"""Turn an agent's answer into a legal chess move, or explain why it is not one."""
from __future__ import annotations

import chess

from tournament.agents import ILLEGAL, MALFORMED, AgentFailure

RESIGN = "resign"


def parse_move(response, board: chess.Board):
    """Returns a chess.Move, or RESIGN. Raises AgentFailure for anything else."""
    if not isinstance(response, dict) or not isinstance(response.get("move"), str):
        raise AgentFailure(MALFORMED, f'expected {{"move": "e2e4"}}, got {response!r}'[:300])
    text = response["move"]
    if text == RESIGN:
        return RESIGN
    try:
        move = chess.Move.from_uci(text)
    except ValueError as error:
        raise AgentFailure(MALFORMED, f"not a UCI move: {text!r}"[:300]) from error
    if move not in board.legal_moves:
        raise AgentFailure(ILLEGAL, f"{text} is not legal in {board.fen()}")
    return move
