"""Example Road Trip agent: inserts the cities at random, one by one, and stops at its first valid route."""
import random
import time
from collections import deque


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


def solve(problem, submit):
    deadline = time.monotonic() + problem["time_limit_s"] * 0.8
    neighbours = {city: [] for city in problem["cities"]}
    for road in problem["roads"]:
        neighbours[road["from"]].append(road["to"])
        if road["bidirectional"]:
            neighbours[road["to"]].append(road["from"])
    while time.monotonic() < deadline:
        route = build_route(problem, neighbours)
        if route is not None:
            submit(route)
            return
