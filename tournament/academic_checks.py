"""Automatic evidence that a team really implemented the required algorithms.

This is separate from competing. Each agent file exposes a few small functions
with fixed signatures (see student_templates/). They run in the agent's own
process, with a time limit, against answers the judge computes independently.
"""
from __future__ import annotations

import heapq
import math
import random
from pathlib import Path

import chess

from games.battleship.engine import sonar_distribution
from games.battleship.validator import ship_cells
from games.catan.engine import SIDE_OF, legal_actions, new_game, observation_for
from games.european_road_trip.engine import RoadGraph

from .agents import AgentFailure, AgentProcess
from .config import load_config
from .teams import AGENT_FILES, GAME_OF_FILE, load_team

CALL_TIMEOUT_S = 30.0
PASS, FAIL, MISSING = "PASS", "FAIL", "NOT IMPLEMENTED"
TOLERANCE = 1e-6


class _NotImplemented(Exception):
    pass


class _Hooks:
    """Calls a student's function in its process and surfaces missing ones."""

    def __init__(self, process: AgentProcess):
        self.process = process

    def __call__(self, name: str, *args):
        response, _ = self.process.request({"fn": name, "args": list(args)}, CALL_TIMEOUT_S)
        if not isinstance(response, dict) or response.get("__missing__") or response.get("__not_implemented__"):
            raise _NotImplemented(name)
        return response["value"]


def _dijkstra(graph: RoadGraph, start: str, goal: str) -> float:
    best = {start: 0}
    queue = [(0, start)]
    while queue:
        cost, city = heapq.heappop(queue)
        if city == goal:
            return cost
        if cost > best[city]:
            continue
        for neighbour, km in graph.adjacency[city].items():
            if cost + km < best.get(neighbour, math.inf):
                best[neighbour] = cost + km
                heapq.heappush(queue, (cost + km, neighbour))
    return math.inf


def _path_km(graph: RoadGraph, path: list):
    total = 0
    for a, b in zip(path, path[1:]):
        km = graph.km(a, b)
        if km is None:
            return None
        total += km
    return total


def _check_road_trip(call) -> list:
    graph = RoadGraph.load()
    rng = random.Random(2026)
    cities = sorted(graph.cities)
    pairs = [tuple(rng.sample(cities, 2)) for _ in range(8)]
    payload = graph.to_dict()

    expanded = {}

    def search_check(name):
        total = 0
        for start, goal in pairs:
            answer = call(name, payload, start, goal)
            km = _path_km(graph, answer["path"])
            if answer["path"][0] != start or answer["path"][-1] != goal or km is None:
                return FAIL, f"invalid path from {start} to {goal}"
            optimal = _dijkstra(graph, start, goal)
            if abs(km - optimal) > TOLERANCE:
                return FAIL, f"{start} to {goal}: {km} km, shortest is {optimal} km"
            total += int(answer["expanded"])
        expanded[name] = total
        return PASS, f"optimal on {len(pairs)} city pairs, {total} nodes expanded"

    outcomes = [
        ("Road Trip", "Uniform-cost search / Dijkstra", *_run(lambda: search_check("ucs"))),
        ("Road Trip", "A* with a geographic heuristic", *_run(lambda: search_check("astar"))),
    ]
    if len(expanded) == 2:
        status = PASS if expanded["astar"] <= expanded["ucs"] else FAIL
        outcomes.append(("Road Trip", "A* expands no more nodes than UCS", status, f"A* {expanded['astar']} vs UCS {expanded['ucs']}"))

    def local_search_check():
        tour_rng = random.Random(7)
        tour = ["madrid"] + tour_rng.sample([c for c in cities if c != "madrid"], 11)
        distance = {
            a: {b: graph.straight_line_km(a, b) for b in tour if b != a}
            for a in tour
        }

        def length(order):
            return sum(distance[x][y] for x, y in zip(order, order[1:] + order[:1]))

        improved = call("local_search", tour, distance, 3.0)
        if sorted(improved) != sorted(tour) or improved[0] != tour[0]:
            return FAIL, "the result must be a reordering of the tour that keeps the first city, without repeating it at the end"
        if length(improved) > length(tour) + TOLERANCE:
            return FAIL, "the tour got longer"
        if length(improved) >= length(tour) - TOLERANCE:
            return FAIL, "no improvement on a random tour"
        return PASS, f"tour improved from {length(tour):.0f} to {length(improved):.0f}"

    outcomes.append(("Road Trip", "Local search / optimization", *_run(local_search_check)))
    return outcomes


CHESS_POSITIONS = [
    chess.STARTING_FEN,
    "r1bqkbnr/pppp1ppp/2n5/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R b KQkq - 3 3",
    "r3k2r/ppp2ppp/2n1bn2/3qp3/3P4/2N1PN2/PPP2PPP/R1BQK2R w KQkq - 0 9",
    "8/5pk1/6p1/8/2Q5/6P1/5PK1/3q4 b - - 0 40",
]


def _check_chess(call) -> list:
    def evaluate_check():
        balanced = float(call("evaluate", chess.STARTING_FEN))
        white_up = float(call("evaluate", "rnb1kbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 3"))
        black_up = float(call("evaluate", "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNB1KBNR b KQkq - 0 3"))
        if not all(map(math.isfinite, (balanced, white_up, black_up))):
            return FAIL, "evaluate must return a finite number"
        if not white_up > balanced > black_up:
            return FAIL, f"should rank queen-up white > level > queen-up black, got {white_up}, {balanced}, {black_up}"
        return PASS, "ranks material correctly from White's point of view"

    def search_check():
        fewer = False
        for fen in CHESS_POSITIONS:
            plain = call("minimax", fen, 2)
            pruned = call("alphabeta", fen, 2)
            if abs(float(plain["value"]) - float(pruned["value"])) > TOLERANCE:
                return FAIL, f"alpha-beta and minimax disagree on {fen}"
            if int(pruned["nodes"]) > int(plain["nodes"]):
                return FAIL, f"alpha-beta visited more nodes than minimax on {fen}"
            fewer = fewer or int(pruned["nodes"]) < int(plain["nodes"])
        if not fewer:
            return FAIL, "alpha-beta never pruned anything"
        return PASS, f"same value as minimax with fewer nodes on {len(CHESS_POSITIONS)} positions"

    def depth_check():
        shallow = int(call("alphabeta", CHESS_POSITIONS[1], 1)["nodes"])
        deep = int(call("alphabeta", CHESS_POSITIONS[1], 2)["nodes"])
        if deep <= shallow:
            return FAIL, f"depth 2 ({deep} nodes) should visit more than depth 1 ({shallow} nodes)"
        return PASS, f"depth 1 visits {shallow} nodes, depth 2 visits {deep}"

    return [
        ("Chess", "Heuristic evaluation function", *_run(evaluate_check)),
        ("Chess", "Minimax with alpha-beta pruning", *_run(search_check)),
        ("Chess", "Depth-limited search", *_run(depth_check)),
    ]


def _exact_placements(length: int, size: int, blocked, required) -> set:
    found = set()
    blocked = {tuple(cell) for cell in blocked}
    required = {tuple(cell) for cell in required}
    for orientation in "HV":
        for row in range(size):
            for col in range(size):
                cells = ship_cells(row, col, orientation, length)
                if all(0 <= r < size and 0 <= c < size for r, c in cells) and not blocked.intersection(cells) and required.issubset(cells):
                    found.add((row, col, orientation))
    return found


def _exact_posterior(prior: dict, reading: int, region_cells: int, correct: float) -> dict:
    joint = {count: p * sonar_distribution(count, region_cells, correct).get(reading, 0.0) for count, p in prior.items()}
    total = sum(joint.values())
    return {count: value / total for count, value in joint.items()}


def _exact_prediction(belief, length: int, orientation: str, move_probability: float) -> list:
    size = len(belief)
    new = [[0.0] * size for _ in range(size)]

    def fits(row, col):
        return all(0 <= r < size and 0 <= c < size for r, c in ship_cells(row, col, orientation, length))

    for row in range(size):
        for col in range(size):
            mass = belief[row][col]
            if not mass:
                continue
            options = [(row + dr, col + dc) for dr, dc in ((-1, 0), (1, 0), (0, 1), (0, -1)) if fits(row + dr, col + dc)]
            if not options:
                new[row][col] += mass
                continue
            new[row][col] += mass * (1 - move_probability)
            for r, c in options:
                new[r][c] += mass * move_probability / len(options)
    return new


def _check_battleship(call) -> list:
    def placements_check():
        cases = [
            (3, 10, [[0, 0], [5, 5]], []),
            (4, 10, [[2, c] for c in range(0, 10, 2)], [[7, 3]]),
            (5, 10, [[r, 4] for r in range(10)], [[3, 7], [3, 8]]),
            (2, 4, [], [[1, 1]]),
        ]
        for length, size, blocked, required in cases:
            answer = {(p[0], p[1], p[2]) for p in call("consistent_placements", length, size, blocked, required)}
            exact = _exact_placements(length, size, blocked, required)
            if answer != exact:
                return FAIL, f"length {length}, board {size}: found {len(answer)} placements, there are {len(exact)}"
        return PASS, f"all placements found on {len(cases)} constraint sets"

    def posterior_check():
        cases = [({"0": 0.5, "1": 0.3, "2": 0.2}, 1, 9), ({"0": 0.25, "3": 0.25, "4": 0.5}, 3, 9), ({"0": 0.6, "1": 0.4}, 0, 4)]
        for prior, reading, cells in cases:
            answer = call("sonar_posterior", prior, reading, cells, 0.8)
            exact = _exact_posterior({int(k): v for k, v in prior.items()}, reading, cells, 0.8)
            for count, probability in exact.items():
                if abs(float(answer.get(str(count), 0.0)) - probability) > 1e-4:
                    return FAIL, f"P(count={count} | reading={reading}) should be {probability:.4f}"
        return PASS, f"Bayes update exact on {len(cases)} cases"

    def prediction_check():
        size = 6
        rng = random.Random(11)
        raw = [[rng.random() for _ in range(size)] for _ in range(size)]
        for row in raw:
            row[-1] = 0.0  # no H ship of length 2 can start in the last column
        total = sum(map(sum, raw))
        belief = [[value / total for value in row] for row in raw]
        answer = call("predict_ship_belief", belief, 2, "H", 0.5)
        exact = _exact_prediction(belief, 2, "H", 0.5)
        worst = max(abs(float(answer[r][c]) - exact[r][c]) for r in range(size) for c in range(size))
        if worst > 1e-6:
            return FAIL, f"prediction differs from the transition model by up to {worst:.4f}"
        return PASS, "belief correctly propagated through the transition model"

    return [
        ("Battleship", "Constraints over hidden ship positions", *_run(placements_check)),
        ("Battleship", "Bayesian update from noisy sonar", *_run(posterior_check)),
        ("Battleship", "Transition model / belief prediction", *_run(prediction_check)),
    ]


def _sample_catan_observations(count: int = 6) -> list:
    game = new_game(424242, 7)
    rng = random.Random(424242)
    samples = []
    steps = 0
    while len(samples) < count and game.winning_color() is None and steps < 2000:
        steps += 1
        actions = legal_actions(game)
        if len(actions) > 1:
            side = SIDE_OF[game.state.current_color()]
            if steps % 11 == 0 or not samples:
                samples.append(observation_for(game, side, actions, None, load_config()["catan"]))
        game.execute(rng.choice(actions))
    return samples


def _check_catan(call) -> list:
    samples = _sample_catan_observations()

    def features_check():
        results = [call("state_features", observation) for observation in samples]
        again = call("state_features", samples[0])
        if results[0] != again:
            return FAIL, "the same observation produced different features"
        if len({str(result) for result in results}) < 2:
            return FAIL, "every state maps to the same features"
        return PASS, f"{len({str(r) for r in results})} distinct abstract states from {len(samples)} observations"

    def values_check():
        for observation in samples:
            for action in observation["actions"][:12]:
                value = float(call("action_value", observation, action["id"]))
                if not math.isfinite(value):
                    return FAIL, "action_value must return a finite number"
        return PASS, "a finite value for every legal action tested"

    def update_check():
        cases = [(1.0, 2.0, 3.0, 0.5, 0.9), (0.0, -1.0, 0.5, 0.1, 0.99), (10.0, 0.0, 0.0, 1.0, 0.5)]
        for q, reward, best_next, alpha, gamma in cases:
            exact = q + alpha * (reward + gamma * best_next - q)
            if abs(float(call("q_update", q, reward, best_next, alpha, gamma)) - exact) > TOLERANCE:
                return FAIL, f"q_update({q}, {reward}, {best_next}, {alpha}, {gamma}) should be {exact}"
        return PASS, "matches the Q-learning update rule"

    def policy_check():
        for observation in samples:
            choice = call("heuristic_policy", observation)
            if choice not in [action["id"] for action in observation["actions"]]:
                return FAIL, f"returned {choice}, which is not a legal action id"
        return PASS, "always returns a legal action"

    return [
        ("Catan", "State abstraction", *_run(features_check)),
        ("Catan", "Value estimate for actions", *_run(values_check)),
        ("Catan", "Q-learning update", *_run(update_check)),
        ("Catan", "Baseline heuristic policy", *_run(policy_check)),
    ]


def _run(check) -> tuple:
    """Every check returns (status, note), whatever the student's code does."""
    try:
        return check()
    except _NotImplemented as missing:
        return MISSING, f"{missing} is not implemented"
    except AgentFailure as failure:
        lines = failure.detail.strip().splitlines()
        return FAIL, f"{failure.kind}: {lines[-1] if lines else ''}"[:200]
    except (KeyError, IndexError, TypeError, ValueError, AttributeError) as error:
        return FAIL, f"unexpected answer format: {error!r}"[:200]


CHECKS = {"road_trip": _check_road_trip, "chess": _check_chess, "battleship": _check_battleship, "catan": _check_catan}


def run_checks(team, games=None, config: dict = None) -> list:
    """Returns [(challenge, requirement, status, note), ...]."""
    settings = load_config(config)
    file_name = Path(str(team)).name
    if not games and file_name in GAME_OF_FILE:
        games = [GAME_OF_FILE[file_name]]
    games = tuple(games) if games else tuple(AGENT_FILES)
    unknown = [game for game in games if game not in CHECKS]
    if unknown:
        raise ValueError(f"game must be one of {sorted(CHECKS)}, got {unknown[0]!r}")
    loaded = load_team(team, games)
    outcomes = []
    for game in games:
        process = AgentProcess(loaded.agent(game), "rpc", seed=1, memory_limit_mb=settings["memory_limit_mb"],
                               forbidden_imports=settings["forbidden_imports"])
        try:
            process.start(settings["startup_timeout_s"])
        except AgentFailure as failure:
            outcomes.append((game, "Agent file loads", FAIL, f"{failure.kind}: {failure.detail}"[:200]))
            process.stop()
            continue
        try:
            outcomes.extend(_with_restart(CHECKS[game], process, loaded.agent(game), settings))
        finally:
            process.stop()
    return outcomes


def _with_restart(checker, first_process, path, settings) -> list:
    """A failing hook may kill the process, so each call goes through a live one."""
    state = {"process": first_process}

    def call(name, *args):
        process = state["process"]
        if process.proc.poll() is not None:
            process.stop()
            process = AgentProcess(path, "rpc", seed=1, memory_limit_mb=settings["memory_limit_mb"],
                                   forbidden_imports=settings["forbidden_imports"])
            process.start(settings["startup_timeout_s"])
            state["process"] = process
        return _Hooks(process)(name, *args)

    try:
        return checker(call)
    finally:
        if state["process"] is not first_process:
            state["process"].stop()


def check_requirements(team, games=None, config: dict = None) -> list:
    """Print which required algorithms pass. Run it often while developing."""
    outcomes = run_checks(team, games, config)
    width = max(len(requirement) for _, requirement, _, _ in outcomes)
    for challenge, requirement, status, note in outcomes:
        print(f"{status:16} {challenge:11} {requirement:{width}}  {note}")
    passed = sum(status == PASS for _, _, status, _ in outcomes)
    print(f"\n{passed}/{len(outcomes)} requirements pass.")
    return outcomes
