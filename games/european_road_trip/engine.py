"""The road graph, instance generation, and the live two-agent race."""
from __future__ import annotations

import csv
import json
import math
import random
import time
from dataclasses import dataclass
from pathlib import Path

import networkx as nx

from tournament.agents import EXCEPTION, MALFORMED, AgentFailure
from tournament.scoring import SIDES, GameResult, incident

from .validator import check_route

DATA_DIR = Path(__file__).parent / "data"
EARTH_RADIUS_KM = 6371.0088
POLL_S = 0.02
MAX_RECORDED_REJECTIONS = 20


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    phi1, lam1, phi2, lam2 = map(math.radians, (lat1, lon1, lat2, lon2))
    h = math.sin((phi2 - phi1) / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin((lam2 - lam1) / 2) ** 2
    return 2 * EARTH_RADIUS_KM * math.asin(math.sqrt(h))


class RoadGraph:
    """Cities joined by roads. The km of these roads are the only ones that count."""

    def __init__(self, cities: dict, roads: list):
        self.cities = cities
        self.roads = roads
        self.adjacency = {city: {} for city in cities}
        for road in roads:
            self.adjacency[road["from"]][road["to"]] = road["km"]
            if road["bidirectional"]:
                self.adjacency[road["to"]][road["from"]] = road["km"]

    @classmethod
    def load(cls, data_dir=DATA_DIR) -> "RoadGraph":
        data_dir = Path(data_dir)
        with open(data_dir / "cities.csv", newline="", encoding="utf-8") as f:
            cities = {
                row["id"]: {"name": row["name"], "country": row["country"], "lat": float(row["lat"]), "lon": float(row["lon"])}
                for row in csv.DictReader(f)
            }
        with open(data_dir / "roads.csv", newline="", encoding="utf-8") as f:
            roads = [
                {"from": row["from"], "to": row["to"], "km": int(row["km"]), "bidirectional": row["bidirectional"] == "true"}
                for row in csv.DictReader(f)
            ]
        return cls(cities, roads)

    def km(self, origin: str, destination: str):
        return self.adjacency.get(origin, {}).get(destination)

    def straight_line_km(self, a: str, b: str) -> float:
        ca, cb = self.cities[a], self.cities[b]
        return haversine_km(ca["lat"], ca["lon"], cb["lat"], cb["lon"])

    def reachable_from(self, start: str) -> set:
        seen, stack = {start}, [start]
        while stack:
            for neighbour in self.adjacency[stack.pop()]:
                if neighbour not in seen:
                    seen.add(neighbour)
                    stack.append(neighbour)
        return seen

    def round_trip_cities(self, start: str) -> set:
        """Cities a route can visit and still return to start without repeating a city."""
        roads = nx.Graph((road["from"], road["to"]) for road in self.roads)
        return next(block for block in nx.biconnected_components(roads) if start in block)

    def problems(self) -> list:
        """Data errors that would make the challenge unfair. Empty means healthy."""
        issues = []
        for road in self.roads:
            for end in (road["from"], road["to"]):
                if end not in self.cities:
                    issues.append(f"road uses unknown city {end}")
        if issues:
            return issues
        for road in self.roads:
            straight = self.straight_line_km(road["from"], road["to"])
            if road["km"] < straight - 0.5:
                issues.append(f"{road['from']}-{road['to']}: {road['km']} km is shorter than the straight line ({straight:.0f} km)")
        for city in self.cities:
            if self.reachable_from(city) != set(self.cities):
                issues.append(f"{city} cannot reach every other city")
                break
        return issues

    def to_dict(self) -> dict:
        return {"cities": self.cities, "roads": self.roads}


@dataclass(frozen=True)
class Instance:
    start: str
    required: tuple  # includes the start city
    seed: int = 0

    def to_dict(self) -> dict:
        return {"start": self.start, "required": list(self.required), "seed": self.seed}


def generate_instance(graph: RoadGraph, seed: int, required_cities: int = 25, start: str = "madrid") -> Instance:
    """Madrid plus random, all different, other cities. Never the training set.

    Cities that no round trip can reach without repeating a city are never drawn.
    """
    training = set(training_instance().required)
    others = sorted(graph.round_trip_cities(start) - {start})
    rng = random.Random(seed)
    while True:
        chosen = rng.sample(others, required_cities - 1)
        if {start, *chosen} != training:
            return Instance(start, tuple([start] + chosen), seed)


def training_instance() -> Instance:
    data = json.loads((DATA_DIR / "training_instance.json").read_text(encoding="utf-8"))
    return Instance(data["start"], tuple(data["required"]), 0)


def small_instances() -> dict:
    data = json.loads((DATA_DIR / "small_instances.json").read_text(encoding="utf-8"))
    return {name: Instance(item["start"], tuple(item["required"]), 0) for name, item in data.items()}


class RouteTracker:
    """Keeps one team's best valid route. Pure logic, so it is easy to test."""

    def __init__(self, graph: RoadGraph, instance: Instance, deadline: float, started: float, max_length: int):
        self.graph = graph
        self.instance = instance
        self.deadline = deadline
        self.started = started
        self.max_length = max_length
        self.best_km = None
        self.best_path = None
        self.valid = 0
        self.invalid = 0
        self.late = 0
        self.improvements = []
        self.rejections = []

    def submit(self, path, received_at: float) -> str:
        """Returns "best", "valid", "invalid" or "late"."""
        if received_at > self.deadline:
            self.late += 1
            return "late"
        check = check_route(path, self.graph, self.instance.start, self.instance.required, self.max_length)
        if not check.valid:
            self.invalid += 1
            if len(self.rejections) < MAX_RECORDED_REJECTIONS:
                self.rejections.append(check.reason)
            return "invalid"
        self.valid += 1
        if self.best_km is None or check.km < self.best_km:
            self.best_km = check.km
            self.best_path = list(path)
            self.improvements.append({"t": round(received_at - self.started, 2), "km": check.km})
            return "best"
        return "valid"

    def to_dict(self) -> dict:
        return {
            "km": self.best_km,
            "path": self.best_path,
            "valid_solutions": self.valid,
            "invalid_solutions": self.invalid,
            "late_solutions": self.late,
            "improvements": self.improvements,
            "rejections": self.rejections,
        }


def problem_for(graph: RoadGraph, instance: Instance, time_limit_s: float) -> dict:
    return {
        "game": "road_trip",
        "start": instance.start,
        "required": list(instance.required),
        "time_limit_s": time_limit_s,
        **graph.to_dict(),
    }


def _board(title: str, names: dict, trackers: dict, seconds_left: float) -> str:
    left = max(0, math.ceil(seconds_left))
    lines = [title, f"Time remaining: {left // 60:02d}:{left % 60:02d}", ""]
    for side in SIDES:
        km = trackers[side].best_km
        lines.append(f"{names[side]}: {km:,} km" if km is not None else f"{names[side]}: no valid route yet")
    a, b = trackers["A"].best_km, trackers["B"].best_km
    if a is None and b is None:
        lead = "nobody yet"
    elif a == b:
        lead = "tied"
    elif b is None or (a is not None and a < b):
        lead = names["A"]
    else:
        lead = names["B"]
    lines += ["", f"Currently leading: {lead}", "", "Valid solutions:"]
    lines += [f"{names[side]}: {trackers[side].valid}" for side in SIDES]
    return "\n".join(lines)


def _consume(messages, side, tracker, agent, incidents, finished) -> None:
    for received_at, message in messages:
        kind = message.get("type")
        if kind == "solution":
            tracker.submit(message.get("path"), received_at)
        elif kind == "malformed":
            tracker.invalid += 1
            incidents.append({"side": side, "kind": MALFORMED, "detail": "unreadable message from the agent"})
        elif kind == "error":
            incidents.append({"side": side, "kind": EXCEPTION, "detail": str(message.get("error", ""))[:2000]})
            finished.add(side)
        elif kind == "done":
            finished.add(side)
        elif kind == "exit":
            if side not in finished:
                incidents.append({"side": side, "kind": agent.death_reason(), "detail": agent.stderr_tail()})
            finished.add(side)


def play_race(agents: dict, graph: RoadGraph, instance: Instance, time_limit_s: float, startup_timeout_s: float,
              names: dict, live=None, title: str = "EUROPEAN ROAD TRIP", max_route_length: int = 5000) -> GameResult:
    """Both agents start together on the same problem and race until the limit."""
    began = time.monotonic()
    failures = {}
    for side, agent in agents.items():
        try:
            agent.start(startup_timeout_s)
        except AgentFailure as failure:
            failures[side] = failure

    incidents = [incident(side, failure) for side, failure in failures.items()]
    finished = set(failures)
    problem = problem_for(graph, instance, time_limit_s)
    started = time.monotonic()
    deadline = started + time_limit_s
    trackers = {side: RouteTracker(graph, instance, deadline, started, max_route_length) for side in SIDES}

    try:
        for side, agent in agents.items():
            if side not in failures:
                agent.send_problem(problem)
        while time.monotonic() < deadline and len(finished) < 2:
            for side, agent in agents.items():
                if side not in failures:
                    _consume(agent.drain(), side, trackers[side], agent, incidents, finished)
            if live is not None:
                live.update(_board(title, names, trackers, deadline - time.monotonic()))
            time.sleep(POLL_S)
        for side, agent in agents.items():
            if side not in failures:
                _consume(agent.drain(10_000), side, trackers[side], agent, incidents, finished)
    finally:
        for agent in agents.values():
            agent.stop()

    km = {side: trackers[side].best_km for side in SIDES}
    for side in SIDES:
        if km[side] is None and side not in failures:
            detail = "no valid route before the limit"
            if trackers[side].rejections:
                detail += "; last rejection: " + trackers[side].rejections[-1]
            elif not trackers[side].invalid:
                detail += ": your agent never called submit(route)"
            incidents.append({"side": side, "kind": "no_valid_route", "detail": detail})

    if km["A"] is None and km["B"] is None:
        winner, reason = None, "both_agents_failed"
    elif km["A"] is None or km["B"] is None:
        winner = "A" if km["B"] is None else "B"
        reason = "opponent_has_no_valid_route"
    elif km["A"] == km["B"]:
        winner, reason = None, "exact_tie"
    else:
        winner = "A" if km["A"] < km["B"] else "B"
        reason = "shorter_route"

    score = {side: f"{km[side]:,} km" if km[side] is not None else "no valid route" for side in SIDES}
    if live is not None:
        live.update(f"{title} finished: {names['A']} {score['A']} | {names['B']} {score['B']}", force=True)
    return GameResult(
        game="road_trip",
        winner=winner,
        reason=reason,
        score=score,
        incidents=incidents,
        seed=instance.seed,
        duration_s=round(time.monotonic() - began, 2),
        details={"instance": instance.to_dict(), "routes": {side: trackers[side].to_dict() for side in SIDES}},
    )
