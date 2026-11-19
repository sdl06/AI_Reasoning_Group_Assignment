"""Play the chess challenge: normally two games with colours swapped."""
from __future__ import annotations

import time
from typing import Optional

import chess

from tournament.agents import TIMEOUT, AgentFailure
from tournament.scoring import SIDES, GameResult, derive_seed, incident, other, start_players
from tournament.timing import ChallengeTimeUp, TurnClocks

from .validator import RESIGN, parse_move


def draw_reason(board: chess.Board) -> Optional[str]:
    """Every automatic ending. Repetition and fifty-move draws are claimed for both."""
    outcome = board.outcome()
    if outcome is not None:
        names = {
            chess.Termination.CHECKMATE: "checkmate",
            chess.Termination.STALEMATE: "stalemate",
            chess.Termination.INSUFFICIENT_MATERIAL: "insufficient_material",
            chess.Termination.SEVENTYFIVE_MOVES: "seventyfive_moves",
            chess.Termination.FIVEFOLD_REPETITION: "fivefold_repetition",
        }
        return names.get(outcome.termination, outcome.termination.name.lower())
    if board.is_repetition(3):
        return "threefold_repetition"
    if board.halfmove_clock >= 100:
        return "fifty_moves"
    return None


def observation(board: chess.Board, color: chess.Color, clocks: TurnClocks, side: str, game_number: int, games_total: int) -> dict:
    return {
        "game": "chess",
        "game_number": game_number,
        "games_total": games_total,
        "color": "white" if color == chess.WHITE else "black",
        "fen": board.fen(),
        "legal_moves": sorted(move.uci() for move in board.legal_moves),
        "history": [move.uci() for move in board.move_stack],
        "ply": board.ply(),
        "is_check": board.is_check(),
        "time_remaining_s": round(clocks.remaining[side], 3),
        "opponent_time_remaining_s": round(clocks.remaining[other(side)], 3),
    }


def _result_of_flag(board: chess.Board, flagged_color: chess.Color) -> Optional[chess.Color]:
    """Losing on time is a draw if the rival cannot possibly mate. Returns winner or None."""
    rival = not flagged_color
    return None if board.has_insufficient_material(rival) else rival


def _other_side_also_fails(board, side, clocks, game_number, games_total, color_of) -> Optional[dict]:
    """After one failure, ask the rival once: if it fails too, it is a technical draw."""
    probe = board.copy()
    moves = sorted(probe.legal_moves, key=lambda m: m.uci())
    if not moves:
        return None
    probe.push(moves[0])
    if probe.is_game_over():
        return None
    rival = other(side)
    try:
        response = clocks.ask(rival, observation(probe, color_of[rival], clocks, rival, game_number, games_total))
        parse_move(response, probe)
    except AgentFailure as failure:
        return incident(rival, failure)
    except ChallengeTimeUp:
        return None
    return None


def play_game(players: dict, white_side: str, clock_s: float, limit_s: float, max_plies: int, game_number: int = 1,
              games_total: int = 1, on_progress=None, start_fen: str = None) -> dict:
    """One game. players maps "A"/"B" to started players. Returns a plain record."""
    board = chess.Board(start_fen) if start_fen else chess.Board()
    color_of = {white_side: chess.WHITE, other(white_side): chess.BLACK}
    side_of = {chess.WHITE: white_side, chess.BLACK: other(white_side)}
    clocks = TurnClocks(players, clock_s, limit_s)
    incidents = []
    winner, reason = None, None

    while True:
        reason = draw_reason(board)
        if reason is not None:
            if reason == "checkmate":
                winner = side_of[not board.turn]
            break
        if board.ply() >= max_plies:
            reason = "move_limit"
            break
        side = side_of[board.turn]
        try:
            response = clocks.ask(side, observation(board, board.turn, clocks, side, game_number, games_total))
            move = parse_move(response, board)
        except ChallengeTimeUp:
            reason = "challenge_time_limit"
            break
        except AgentFailure as failure:
            incidents.append(incident(side, failure))
            reason = failure.kind
            if failure.kind == TIMEOUT:
                flag_winner = _result_of_flag(board, board.turn)
                winner = side_of[flag_winner] if flag_winner is not None else None
                if winner is None:
                    reason = "timeout_vs_insufficient_material"
                break
            second = _other_side_also_fails(board, side, clocks, game_number, games_total, color_of)
            if second is not None:
                incidents.append(second)
                reason = "both_agents_failed"
            else:
                winner = other(side)
            break
        if move == RESIGN:
            winner, reason = other(side), "resignation"
            break
        board.push(move)
        if on_progress is not None:
            on_progress(board, clocks)

    return {
        "white": white_side,
        "winner": winner,
        "reason": reason,
        "moves": [move.uci() for move in board.move_stack],
        "final_fen": board.fen(),
        "plies": board.ply(),
        "clock_left_s": {side: round(clocks.remaining[side], 2) for side in SIDES},
        "incidents": incidents,
    }


def play_challenge(make_player, config: dict, seed: int, names: dict, live=None) -> GameResult:
    """make_player(side, seed) returns a new, unstarted player for that side."""
    began = time.monotonic()
    two_games = config["format"] == "two_games"
    clock_s = config["clock_s"] if two_games else config["single_game_clock_s"]
    total_limit = config["challenge_limit_s"]
    first_white = "A" if derive_seed(seed, "chess-colours") % 2 else "B"
    whites = [first_white, other(first_white)] if two_games else [first_white]

    points = {"A": 0.0, "B": 0.0}
    records, incidents = [], []
    played_s = 0.0  # loading agents does not count against the limit
    for number, white in enumerate(whites, 1):
        players = {side: make_player(side, derive_seed(seed, f"chess-{number}-{side}")) for side in SIDES}
        failed = start_players(players, "chess", seed)
        if failed is not None:
            incidents.extend(failed.incidents)
            record = {"white": white, "winner": failed.winner, "reason": failed.reason, "moves": [],
                      "final_fen": chess.STARTING_FEN, "plies": 0, "clock_left_s": {}, "incidents": failed.incidents}
        else:
            def progress(board, clocks, number=number):
                if live is not None:
                    live.update(
                        f"CHESS game {number}/{len(whites)}\n\n{board}\n\n"
                        f"White: {names[white]}  {clocks.remaining[white]:.1f} s\n"
                        f"Black: {names[other(white)]}  {clocks.remaining[other(white)]:.1f} s\nPly {board.ply()}"
                    )

            game_began = time.monotonic()
            try:
                record = play_game(players, white, clock_s, total_limit - played_s, config["max_plies"], number, len(whites), progress)
            finally:
                played_s += time.monotonic() - game_began
                for player in players.values():
                    player.stop()
            incidents.extend(record["incidents"])
        records.append(record)
        if record["winner"] is None:
            points["A"] += 0.5
            points["B"] += 0.5
        else:
            points[record["winner"]] += 1.0

    if points["A"] == points["B"]:
        winner = None
    else:
        winner = "A" if points["A"] > points["B"] else "B"
    reason = " / ".join(record["reason"] for record in records)
    if live is not None:
        live.update(f"CHESS finished: {names['A']} {points['A']:g} - {points['B']:g} {names['B']}", force=True)
    return GameResult(
        game="chess",
        winner=winner,
        reason=reason,
        score={side: f"{points[side]:g}" for side in SIDES},
        incidents=incidents,
        seed=seed,
        duration_s=round(time.monotonic() - began, 2),
        details={"games": records, "points": points},
    )
