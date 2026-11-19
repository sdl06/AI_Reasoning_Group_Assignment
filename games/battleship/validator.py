"""Check an agent's placement and turn actions before the engine applies them.

Anything wrong costs the game. Answers are not corrected in the agent's favour.
"""
from __future__ import annotations

from tournament.agents import ILLEGAL, MALFORMED, AgentFailure

DIRECTIONS = {"N": (-1, 0), "S": (1, 0), "E": (0, 1), "W": (0, -1)}
ORIENTATIONS = ("H", "V")


def _is_int(value) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def ship_cells(row: int, col: int, orientation: str, length: int) -> list:
    if orientation == "H":
        return [(row, col + i) for i in range(length)]
    return [(row + i, col) for i in range(length)]


def check_cell(value, board_size: int, what: str) -> tuple:
    if not isinstance(value, (list, tuple)) or len(value) != 2 or not all(_is_int(v) for v in value):
        raise AgentFailure(MALFORMED, f"{what} must be [row, col], got {value!r}"[:300])
    row, col = value
    if not (0 <= row < board_size and 0 <= col < board_size):
        raise AgentFailure(ILLEGAL, f"{what} {value} is outside the board")
    return row, col


def check_placement(response, fleet: list, board_size: int) -> list:
    """fleet is [(ship_id, length), ...]. Returns the placements as a clean list."""
    if not isinstance(response, dict) or "placements" not in response:
        raise AgentFailure(MALFORMED, f'expected {{"placements": [...]}}, got {response!r}'[:300])
    placements = response["placements"]
    if placements is None:
        return None
    if not isinstance(placements, list):
        raise AgentFailure(MALFORMED, "placements must be a list or null")
    lengths = dict(fleet)
    clean, seen, occupied = [], set(), set()
    for item in placements:
        if not isinstance(item, dict):
            raise AgentFailure(MALFORMED, f"placement must be an object, got {item!r}"[:300])
        ship, row, col, orientation = item.get("ship"), item.get("row"), item.get("col"), item.get("orientation")
        if not isinstance(ship, str) or ship not in lengths:
            raise AgentFailure(ILLEGAL, f"unknown ship: {ship!r}"[:300])
        if ship in seen:
            raise AgentFailure(ILLEGAL, f"ship placed twice: {ship}")
        if not _is_int(row) or not _is_int(col) or orientation not in ORIENTATIONS:
            raise AgentFailure(MALFORMED, f"bad placement: {item!r}"[:300])
        seen.add(ship)
        cells = ship_cells(row, col, orientation, lengths[ship])
        if not all(0 <= r < board_size and 0 <= c < board_size for r, c in cells):
            raise AgentFailure(ILLEGAL, f"{ship} leaves the board at row {row}, col {col}, {orientation}")
        if occupied.intersection(cells):
            raise AgentFailure(ILLEGAL, f"{ship} overlaps another ship")
        occupied.update(cells)
        clean.append({"ship": ship, "row": row, "col": col, "orientation": orientation})
    if seen != set(lengths):
        raise AgentFailure(ILLEGAL, "missing ships: " + ", ".join(sorted(set(lengths) - seen)))
    return clean


def check_turn(response, board_size: int, legal_moves: list, sonar_left: int) -> dict:
    """Returns {"move": {...}|None, "shot": (r, c)} or {"move": ..., "sonar": (r, c)}."""
    if not isinstance(response, dict):
        raise AgentFailure(MALFORMED, f"action must be an object, got {response!r}"[:300])
    unknown = set(response) - {"move", "shot", "sonar"}
    if unknown:
        raise AgentFailure(ILLEGAL, "unknown action keys: " + ", ".join(sorted(map(str, unknown)))[:200])
    has_shot, has_sonar = response.get("shot") is not None, response.get("sonar") is not None
    if has_shot == has_sonar:
        raise AgentFailure(ILLEGAL, 'each turn needs exactly one of "shot" or "sonar"')

    move = response.get("move")
    if move is not None:
        if not isinstance(move, dict):
            raise AgentFailure(ILLEGAL, f'move must be one entry of legal_moves or None, got {move!r}'[:300])
        clean_move = {"ship": move.get("ship"), "direction": move.get("direction")}
        if clean_move not in legal_moves:
            raise AgentFailure(ILLEGAL, f"move not legal now: {move!r}"[:300])
        move = clean_move

    if has_sonar:
        if sonar_left <= 0:
            raise AgentFailure(ILLEGAL, "no sonar uses left")
        return {"move": move, "sonar": check_cell(response["sonar"], board_size, "sonar")}
    return {"move": move, "shot": check_cell(response["shot"], board_size, "shot")}
