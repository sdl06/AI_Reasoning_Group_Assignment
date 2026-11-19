"""One call plays a whole match: Road Trip, Chess, Battleship, Catan, tiebreak if needed."""
from __future__ import annotations

import os
import secrets
import time
import traceback
import uuid

from games.battleship import engine as battleship_engine
from games.catan import engine as catan_engine
from games.chess import engine as chess_engine
from games.european_road_trip import engine as road_engine

from .agents import AgentProcess, SubprocessPlayer
from .config import load_config
from .live import LiveView
from .results import JUDGE_ERROR, format_game_summary, format_match_summary, save_match
from .scoring import SIDES, GameResult, derive_seed, leader, match_points
from .teams import AGENT_FILES, Team, load_team

GAME_ORDER = ("road_trip", "chess", "battleship", "catan")
PRINTED_OUTPUT_CHARS = 20000


def _new_seed() -> int:
    return secrets.randbelow(2**31 - 1) + 1


def _display_names(team_a: Team, team_b: Team) -> dict:
    if team_a.name == team_b.name:
        return {"A": f"{team_a.name} (A)", "B": f"{team_b.name} (B)"}
    return {"A": team_a.name, "B": team_b.name}


class _Contest:
    """The two teams in one match and the settings that apply to both."""

    def __init__(self, teams: dict, config: dict, live_enabled: bool):
        self.teams = teams
        self.config = config
        self.names = _display_names(teams["A"], teams["B"])
        self.live_enabled = live_enabled
        self.processes = {"A": [], "B": []}

    def live(self) -> LiveView:
        return LiveView(self.live_enabled)

    def process(self, side: str, game: str, mode: str, seed: int, cpu=None) -> AgentProcess:
        process = AgentProcess(
            self.teams[side].agent(game),
            mode,
            label=f"{self.names[side]}:{game}",
            seed=seed,
            memory_limit_mb=self.config["memory_limit_mb"],
            forbidden_imports=self.config["forbidden_imports"],
            cpu=cpu,
        )
        self.processes[side].append(process)
        return process

    def player(self, side: str, game: str, seed: int) -> SubprocessPlayer:
        return SubprocessPlayer(self.process(side, game, "turn", seed), self.config["startup_timeout_s"])

    def road_trip(self, seed: int, time_limit_s: float, title: str, instance=None) -> GameResult:
        settings = self.config["road_trip"]
        graph = road_engine.RoadGraph.load()
        if instance is None:
            instance = road_engine.generate_instance(graph, seed, settings["required_cities"], settings["start_city"])
        cpus = _race_cpus()
        agents = {
            side: self.process(side, "road_trip", "stream", derive_seed(seed, f"agent-{side}"), cpu=cpus[side])
            for side in SIDES
        }
        return road_engine.play_race(
            agents, graph, instance, time_limit_s, self.config["startup_timeout_s"], self.names,
            self.live(), title, settings["max_route_length"],
        )

    def guarded(self, game: str, seed: int, play) -> GameResult:
        """If the judge fails in one game, the rest of the match and its results survive."""
        try:
            return play()
        except Exception:
            detail = traceback.format_exc()
            print(f"JUDGE ERROR in {game}. Tell the professor.\n{detail}")
            incident = {"side": None, "kind": JUDGE_ERROR, "detail": detail[-2000:]}
            return GameResult(game, None, JUDGE_ERROR, {"A": "-", "B": "-"}, [incident], seed)

    def play(self, game: str, seed: int, instance=None) -> GameResult:
        return self.guarded(game, seed, lambda: self._play(game, seed, instance))

    def _play(self, game: str, seed: int, instance=None) -> GameResult:
        if game == "road_trip":
            return self.road_trip(seed, self.config["road_trip"]["time_limit_s"], "EUROPEAN ROAD TRIP", instance)
        if game == "chess":
            return chess_engine.play_challenge(lambda side, s: self.player(side, "chess", s), self.config["chess"], seed, self.names, self.live())
        players = {side: self.player(side, game, derive_seed(seed, f"agent-{side}")) for side in SIDES}
        if game == "battleship":
            return battleship_engine.play_game(players, self.config["battleship"], seed, self.names, self.live())
        if game == "catan":
            return catan_engine.play_game(players, self.config["catan"], seed, self.names, self.live())
        raise ValueError(f"Unknown game: {game}")


def _race_cpus() -> dict:
    """Give each racing agent its own core where the machine allows it (Colab has two)."""
    available = sorted(os.sched_getaffinity(0)) if hasattr(os, "sched_getaffinity") else []
    if len(available) >= 2:
        return {"A": available[0], "B": available[1]}
    return {"A": None, "B": None}


def _attach_report(result: GameResult, names: dict) -> dict:
    data = result.to_dict()
    data["names"] = names
    return data


def run_game(game: str, team, opponent="demo", seed: int = None, live: bool = True, config: dict = None, training: bool = False, quiet: bool = False) -> dict:
    """Practice one challenge against a rival, by default the bundled example agent.

    Only that one .py file is needed, so a team can work on its agents one at a time.
    training=True uses the published Road Trip instance instead of random cities.
    quiet=True prints nothing, which is handy when comparing agents over many seeds.
    """
    live = live and not quiet
    if game not in AGENT_FILES:
        raise ValueError(f"game must be one of {sorted(AGENT_FILES)}, got {game!r}")
    settings = load_config(config)
    seed = _new_seed() if seed is None else seed
    contest = _Contest({"A": load_team(team, [game]), "B": load_team(opponent, [game])}, settings, live)
    instance = road_engine.training_instance() if game == "road_trip" and training else None
    data = _attach_report(contest.play(game, derive_seed(seed, game), instance), contest.names)
    data["match_seed"] = seed
    data["logs"] = {side: "".join(p.stderr_tail(PRINTED_OUTPUT_CHARS) for p in contest.processes[side]) for side in SIDES}
    if not quiet:
        print(format_game_summary(data))
    return data


def _tiebreak(contest: _Contest, seed: int) -> list:
    """New Road Trip instances until one team wins or the attempts run out."""
    settings = contest.config["road_trip"]
    attempts = []
    for attempt in range(1, settings["tiebreak_max_attempts"] + 1):
        instance_seed = derive_seed(seed, f"tiebreak-{attempt}")
        title = f"TIEBREAK {attempt}/{settings['tiebreak_max_attempts']}: EUROPEAN ROAD TRIP"
        result = contest.guarded(
            "road_trip", instance_seed,
            lambda: contest.road_trip(instance_seed, settings["tiebreak_time_limit_s"], title),
        )
        attempts.append(result)
        if result.winner is not None:
            break
    return attempts


def run_match(team_a, team_b, seed: int = None, round_name: str = None, live: bool = True, config: dict = None, results_dir="results", games=None) -> dict:
    """Play a full match between two team folders. No intervention is ever needed.

    Road Trip cities are drawn at random from `seed` (printed in the result). Pass
    the same seed again to replay the same instances and random events.
    """
    settings = load_config(config)
    seed = _new_seed() if seed is None else seed
    games = tuple(games) if games else GAME_ORDER
    teams = {"A": load_team(team_a, games), "B": load_team(team_b, games)}
    contest = _Contest(teams, settings, live)
    began = time.monotonic()

    results = []
    for game in games:
        results.append(contest.play(game, derive_seed(seed, game)))

    points = match_points(results)
    judge_failed = any(result.reason == JUDGE_ERROR for result in results)
    winner = None if judge_failed else leader(points)
    tiebreaks = []
    if winner is None and not judge_failed:
        tiebreaks = _tiebreak(contest, seed)
        winner = tiebreaks[-1].winner if tiebreaks else None

    match = {
        "match_id": uuid.uuid4().hex[:12],
        "seed": seed,
        "round": round_name,
        "teams": contest.names,
        "games": [result.to_dict() for result in results],
        "points": points,
        "tiebreaks": [result.to_dict() for result in tiebreaks],
        "winner": winner,
        "advances": contest.names[winner] if winner else None,
        "needs_professor": winner is None,
        "duration_s": round(time.monotonic() - began, 1),
    }
    match["results_file"] = str(save_match(match, results_dir))
    print(format_match_summary(match))
    return match
