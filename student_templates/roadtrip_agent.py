"""European Road Trip agent. Team: <your team name>

Start here: docs/students/README.md
Full rules: games/european_road_trip/README.md
Example of what you receive: docs/students/sample_observations/road_trip.json

Your goal: the shortest route by road that starts in Madrid, visits every required
city, and returns to Madrid, without passing through any city twice. Submit a complete
route as soon as you have one, then keep improving it. Your best valid route submitted
in time is the one that counts.

Keep the function names and signatures below. Add any helpers you need.
"""
import random
import time
from collections import deque


def solve(problem, submit):
    """Called once. Runs until it returns or the judge stops it at the time limit.

    problem["start"]         "madrid"
    problem["required"]      the 25 different cities to visit, including the start
    problem["time_limit_s"]  seconds available
    problem["cities"]        {city_id: {"name", "country", "lat", "lon"}}
    problem["roads"]         [{"from", "to", "km", "bidirectional"}]

    submit(route)            route is every city you pass through, in order, including
                             intermediate cities and the return to the start. No city may
                             appear twice, except the start at both ends. Example:
                             ["madrid", "zaragoza", "barcelona", ..., "valencia", "madrid"]
                             Call it every time you find a better route.
    """
    # TODO: replace with your own search. This placeholder starts from a closed route through
    # one city and inserts the others one by one, along any path that avoids the cities already
    # used. It stops at its first valid route, which is very long.
    neighbours = {city: [] for city in problem["cities"]}
    for road in problem["roads"]:
        neighbours[road["from"]].append(road["to"])
        if road["bidirectional"]:
            neighbours[road["to"]].append(road["from"])

    deadline = time.monotonic() + problem["time_limit_s"] * 0.8
    while time.monotonic() < deadline:
        route = build_route(problem, neighbours)
        if route is not None:
            submit(route)
            return


def path_avoiding(neighbours, start, goal, used):
    """The path with the fewest roads that avoids the cities in used, or None."""
    previous = {start: None}
    queue = deque([start])
    while queue:
        city = queue.popleft()
        if city == goal:
            path = [goal]
            while previous[path[-1]] is not None:
                path.append(previous[path[-1]])
            return path[::-1]
        for next_city in neighbours[city]:
            if next_city not in previous and (next_city not in used or next_city == goal):
                previous[next_city] = city
                queue.append(next_city)
    return None


def insert_city(route, city, neighbours):
    """Replace one road of the closed route with a detour through city, or return None."""
    used = set(route)
    for i in random.sample(range(len(route) - 1), len(route) - 1):
        there = path_avoiding(neighbours, route[i], city, used)
        if there is not None:
            back = path_avoiding(neighbours, city, route[i + 1], used | set(there))
            if back is not None:
                return route[:i] + there + back[1:] + route[i + 2:]
    return None


def build_route(problem, neighbours):
    """Start from a closed route through one city, then insert the others one by one."""
    start = problem["start"]
    others = random.sample([c for c in problem["required"] if c != start], len(problem["required"]) - 1)
    route = [start]
    for city in others:
        if city not in route:
            route = insert_city(route + [start] if len(route) == 1 else route, city, neighbours)
            if route is None:
                return None
    return route


# ---------------------------------------------------------------------------------
# Required algorithms. check_requirements() tests these. They must be real and must
# work, even if your final route is produced some other way.
# ---------------------------------------------------------------------------------


def ucs(graph, start, goal):
    """Uniform-cost search (or Dijkstra) on graph = {"cities": ..., "roads": ...}.

    start and goal are always different cities. A node is expanded when you remove it from
    the frontier to explore its neighbours.

    Returns {"path": [start, ..., goal], "km": total_km, "expanded": nodes_expanded}.
    """
    raise NotImplementedError


def astar(graph, start, goal):
    """A* using the straight-line (Haversine) distance to the goal as the heuristic.

    Returns the same dictionary as ucs(). It must find the same km, expanding no more nodes in total.
    """
    raise NotImplementedError


def local_search(tour, distance, time_limit_s):
    """Improve a visiting order with hill climbing, simulated annealing, a genetic
    algorithm or similar.

    tour      different city ids in visiting order, for example ["madrid", "paris", "rome"].
              The first city is not repeated at the end: the tour closes back to it by itself.
    distance  {a: {b: km}} between every pair of cities in the tour.

    Returns a reordering of tour, in the same shape, with the same first city and a
    shorter closed length.
    """
    raise NotImplementedError
