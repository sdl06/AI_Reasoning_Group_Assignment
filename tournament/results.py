"""The summary students report to the professor, and the JSON record behind it."""
from __future__ import annotations

import html
import json
from pathlib import Path

JUDGE_ERROR = "judge_error"
GAME_TITLES = {"road_trip": "EUROPEAN ROAD TRIP", "chess": "CHESS", "battleship": "BATTLESHIP", "catan": "CATAN"}
WIDE = "=" * 44
THIN = "-" * 44
ENDINGS = {
    "crash": "Agent crashed",
    "exact_tie": "Exactly the same distance",
    "exception": "Agent raised an exception",
    "fifty_moves": "Fifty-move rule",
    "fleet_destroyed": "All enemy ships sunk",
    "load_error": "Agent file failed to load",
    "malformed_response": "Answer in the wrong format",
    "opponent_has_no_valid_route": "Rival has no valid route",
    "reached_victory_points": "Reached the winning points",
    "timeout": "Out of time",
    "timeout_vs_insufficient_material": "Out of time, but the rival could not mate",
}


def ending_words(reason: str) -> str:
    """Plain words for how a game ended. The result itself keeps the code in "reason"."""
    return ", ".join(ENDINGS.get(part, part.replace("_", " ").capitalize()) for part in reason.split(" / "))


def _winner_name(game: dict, names: dict) -> str:
    return names[game["winner"]] if game["winner"] else "DRAW"


def _incident_lines(game: dict, names: dict, where: str = "") -> list:
    lines = []
    for item in game.get("incidents", []):
        who = names.get(item.get("side"), "judge")
        first_line = (item.get("detail") or "").strip().splitlines()
        lines.append(f"  ! {where}{who}: {ending_words(item['kind'])}" + (f" ({first_line[-1][:100]})" if first_line else ""))
    return lines


def _game_block(game: dict, names: dict, title: str = None) -> list:
    lines = [THIN, title or GAME_TITLES[game["game"]], THIN]
    lines += [f"{names[side]}: {game['score'][side]}" for side in ("A", "B")]
    lines.append(f"Winner: {_winner_name(game, names)}")
    lines.append(f"How it ended: {ending_words(game['reason'])}")
    return lines + _incident_lines(game, names)


def _table(rows: list) -> list:
    widths = [max(len(str(row[column])) for row in rows) for column in range(len(rows[0]))]
    return ["  ".join(str(cell).ljust(width) for cell, width in zip(row, widths)).rstrip() for row in rows]


def format_game_summary(game: dict) -> str:
    names = game["names"]
    lines = [""] + _game_block(game, names)
    lines.append(f"Seed: {game.get('match_seed')}   Took: {game['duration_s']} s")
    for item in game.get("incidents", []):
        if "\n" in (item.get("detail") or "").strip():
            lines += ["", f"Full error, {names.get(item.get('side'), 'judge')}:", item["detail"].strip()]
    return "\n".join(lines)


def format_match_summary(match: dict) -> str:
    names = match["teams"]
    lines = ["", WIDE, "IE UNIVERSITY AI AGENT TOURNAMENT", WIDE, ""]
    if match.get("round"):
        lines += [f"ROUND: {match['round']}", ""]
    played = [(GAME_TITLES[game["game"]], game) for game in match["games"]]
    played += [(f"TIEBREAK {number}: ROAD TRIP", game) for number, game in enumerate(match["tiebreaks"], 1)]
    rows = [("GAME", names["A"], names["B"], "WINNER", "HOW IT ENDED")]
    rows += [(title, game["score"]["A"], game["score"]["B"], _winner_name(game, names), ending_words(game["reason"])) for title, game in played]
    lines += _table(rows) + [""]
    incidents = [line for title, game in played for line in _incident_lines(game, names, f"{title}, ")]
    if incidents:
        lines += ["Incidents:", *incidents, ""]
    points = match["points"]
    totals = ", ".join(f"{names[side]} {points[side]:g} point{'' if points[side] == 1 else 's'}" for side in ("A", "B"))
    lines += [f"FINAL RESULT: {totals}", ""]
    if any(game["reason"] == JUDGE_ERROR for game in match["games"]):
        lines.append(">>> THE JUDGE FAILED, SO THERE IS NO RESULT: TELL THE PROFESSOR <<<")
    elif match["winner"]:
        lines.append(f">>> {names[match['winner']]} ADVANCES <<<")
    else:
        lines.append(">>> STILL TIED AFTER EVERY TIEBREAK: TELL THE PROFESSOR <<<")
    lines += ["", f"Seed: {match['seed']}   Took: {match['duration_s']} s"]
    if match.get("results_file"):
        lines.append(f"Saved to: {match['results_file']}")
    return "\n".join(lines)


def save_match(match: dict, results_dir="results") -> Path:
    """Local JSON record. Written only here, never in a team's folder."""
    folder = Path(results_dir)
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"match_{match['match_id']}.json"
    path.write_text(json.dumps(match, indent=1), encoding="utf-8")
    return path


def _visualizers() -> dict:
    from games.battleship.visualization import show as battleship
    from games.catan.visualization import show as catan
    from games.chess.visualization import show as chess
    from games.european_road_trip.visualization import show as road_trip

    return {"road_trip": road_trip, "chess": chess, "battleship": battleship, "catan": catan}


def show_game(game: dict, names: dict = None, title: str = None) -> None:
    """Maps, boards and replays for one challenge, in a notebook."""
    from IPython.display import HTML, display

    names = names or game["names"]
    outcome = f"Winner: {names[game['winner']]}." if game["winner"] else "Draw."
    display(HTML(f"<h3>{title or GAME_TITLES[game['game']]}</h3><p>{html.escape(outcome)} {html.escape(ending_words(game['reason']))}.</p>"))
    if game["reason"] != JUDGE_ERROR:
        _visualizers()[game["game"]](game, names)


def show_match(match: dict) -> None:
    """Everything visual, once the match is over, so it never slows the agents.

    run_match has already printed the summary, so it is not repeated here.
    """
    for game in match["games"]:
        show_game(game, match["teams"])
    for number, game in enumerate(match["tiebreaks"], 1):
        show_game(game, match["teams"], f"TIEBREAK {number}")


def download_result(match: dict) -> None:
    """In Colab, offer the JSON record as a download."""
    try:
        from google.colab import files
    except ImportError:
        print(f"Result file: {match['results_file']}")
        return
    files.download(match["results_file"])
