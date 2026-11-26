"""European Road Trip agent.

Strategy: road distances between the required cities with A*, a visiting order
with nearest neighbour + 2-opt, a route builder that never reuses a city
(look-ahead check, both directions, insertion fallback), and iterated local
search until 85% of the time limit.
"""
import heapq
import random
import time
from math import asin, cos, radians, sin, sqrt


# -------------------------------------------------------
# STEP 1: Build the graph
# -------------------------------------------------------

def build_graph(roads):
    """Turns the list of roads into an adjacency dictionary.
    Result: {city: {neighbour: km, ...}, ...}
    All roads go both ways, so we add it in both directions.
    """
    graph = {}
    for road in roads:
        a, b, km = road["from"], road["to"], road["km"]
        graph.setdefault(a, {})[b] = km
        graph.setdefault(b, {})[a] = km
    return graph


# -------------------------------------------------------
# STEP 2: search function between ucs or A star
# -------------------------------------------------------

def straight_line_d(a, b):
    """Haversine distance in km between two cities.
    a and b are entries of problem["cities"], with "lat" and "lon".
    """
    dlat = radians(b["lat"] - a["lat"])
    dlon = radians(b["lon"] - a["lon"])
    h = sin(dlat / 2) ** 2 + cos(radians(a["lat"])) * cos(radians(b["lat"])) * sin(dlon / 2) ** 2
    return 2 * 6371 * asin(sqrt(h))


def search(adj, cities, start, goal, blocked=(), use_heuristic=True):
    """Shortest road path from start to goal that ignores the cities that are `blocked`.
    The frontier is a priority queue ordered by f = g + h:
        g = km travelled so far
        h = straight-line km to the goal (A*), or 0 (UCS).
    """
    def h(city):
        if use_heuristic:
            return straight_line_d(cities[city], cities[goal])
        return 0

    frontier = [(h(start), 0, start, [start])]    # (f, g, city, path)
    explored = set()
    expanded = 0

    while frontier:
        f, km, city, path = heapq.heappop(frontier)   # f with lowest value
        if city in explored:
            continue                                  # reached with lower distance 
        explored.add(city)
        expanded += 1                                 # removed from the frontier 

        if city == goal:
            return km, path, expanded

        for neighbour, road_km in adj[city].items():
            if neighbour not in explored and neighbour not in blocked:
                g = km + road_km
                heapq.heappush(frontier, (g + h(neighbour), g, neighbour, path + [neighbour]))

    return None, None, expanded


def ucs(graph, start, goal):
    """uniform cost search: search without heuristic."""
    km, path, expanded = search(build_graph(graph["roads"]), graph["cities"], start, goal, use_heuristic=False)
    return {"path": path, "km": km, "expanded": expanded}


def astar(graph, start, goal):
    """A star: search with the straight-line heuristic."""
    km, path, expanded = search(build_graph(graph["roads"]), graph["cities"], start, goal, use_heuristic=True)
    return {"path": path, "km": km, "expanded": expanded}


# ---------------------------------------------------------------
# STEP 3: Local search with 2-opt
# ---------------------------------------------------------------

def tour_length(tour, dist):
    """The length in distance of the tour from last to first city."""
    total = 0
    for i in range(len(tour)):
        total += dist(tour[i], tour[(i + 1) % len(tour)])
    return total


def local_search(tour, distance, time_limit_s):
    """Improves a tour with 2-opt hill climbing.
    Reverse one segment tour[i..j].
    Accept only if it makes the tour shorter.
    Stops when no shorter paths or time runs out.
    """
    def dist(a, b):
        if a in distance:
            row = distance[a]
        else:
            row = distance[str(a)]
        if b in row:
            return row[b]
        else:
            return row[str(b)]

    tour = list(tour)
    n = len(tour)
    deadline = time.monotonic() + time_limit_s * 0.8   # safety margin

    improved = True
    while improved and time.monotonic() < deadline:
        improved = False
        for i in range(1, n - 1):
            for j in range(i + 1, n):
                a = tour[i - 1]
                b = tour[i]          # first edge  a-b
                c = tour[j] 
                d = tour[(j + 1) % n]    # second edge c-d
                delta = dist(a, c) + dist(b, d) - dist(a, b) - dist(c, d)
                if delta < -1e-9:
                    tour[i:j + 1] = reversed(tour[i:j + 1])
                    improved = True
    return tour


# ---------------------------------------------------------------
# STEP 4: The agent
# ---------------------------------------------------------------

def nearest_neighbour_order(start, required, D):
    """Always go to the closest city not yet visited."""
    order = [start]
    left = set(required) - {start}
    while left:
        current = order[-1]
        closest = min(left, key=lambda city: D[current][city])
        order.append(closest)
        left.remove(closest)
    return order


def still_possible(adj, current, used, remaining, start):
    """Look-ahead check: from `current`, without passing through used cities,
    can we still reach every remaining required city and get back to Madrid?
    (Breadth-first search over the cities that are still free.)
    """
    seen = {current}
    stack = [current]
    while stack:
        city = stack.pop()
        for neighbour in adj[city]:
            if neighbour not in seen and neighbour not in used:
                seen.add(neighbour)
                stack.append(neighbour)
    can_return = any(n in seen for n in adj[start]) or current in adj[start]
    return can_return and all(city in seen for city in remaining)


def build_route(order, start, adj, cities):
    """Turns a visiting order into the full road route, with no repeats.
    """
    route = [start]
    used = {start}
    todo = [city for city in order if city != start]

    while todo:
        for target in todo:                       
            km, path, _ = search(adj, cities, route[-1], target, used)
            if path is None:
                continue
            new_used = used | set(path[1:])
            remaining = [c for c in todo if c not in new_used]
            if still_possible(adj, target, new_used, remaining, start):
                break                             # this leg is safe
        else:
            return None                           
        route += path[1:]
        used = new_used
        todo = remaining

    km, path, _ = search(adj, cities, route[-1], start, used - {start})   # back to Madrid
    if path is None:
        return None
    return route + path[1:]


def insertion_route(order, start, adj, cities):
    """Used when build_route gets stuck.
    Start with the closed route [Madrid, Madrid]. Insert the cities one by one.
    Slower than build_route, but much harder to trap.
    """
    route = [start, start]
    for city in order:
        if city in route:
            continue
        used = set(route)
        best = None
        for i in range(len(route) - 1):
            a, b = route[i], route[i + 1]
            km1, there, _ = search(adj, cities, a, city, used)
            if there is None:
                continue
            km2, back, _ = search(adj, cities, city, b, (used | set(there)) - {b})
            if back is None:
                continue
            old_km = adj[a].get(b, 0)                 # [Madrid, Madrid] has no road yet
            extra = km1 + km2 - old_km
            if best is None or extra < best[0]:
                best = (extra, route[:i] + there + back[1:] + route[i + 2:])
        if best is None:
            return None
        route = best[1]
    return route


def make_route(order, start, adj, cities):
    """Turns an order into a valid route.
    1) build_route in both directions;
    2) if both get stuck, fall back to insertion_route.
    Returns the shortest valid route found, or None.
    """
    best = None
    for candidate in (order, [order[0]] + order[1:][::-1]):
        route = build_route(candidate, start, adj, cities)
        if route is not None and (best is None or route_km(route, adj) < route_km(best, adj)):
            best = route
    if best is None:
        best = insertion_route(order, start, adj, cities)
    return best


def route_km(route, adj):
    """Real length of a route: the sum of the road kilometres."""
    total = 0
    for i in range(len(route) - 1):
        total += adj[route[i]][route[i + 1]]
    return total


def solve(problem, submit):
    t0 = time.monotonic()
    deadline = t0 + problem["time_limit_s"] * 0.85    # stop early, keep a margin
    start = problem["start"]
    required = problem["required"]
    cities = problem["cities"]
    adj = build_graph(problem["roads"])
    rng = random.Random(0)

    # 1) Road distance between every pair of required cities
    D = {a: {} for a in required}
    for i, a in enumerate(required):
        for b in required[i + 1:]:
            km, _, _ = search(adj, cities, a, b, set())
            D[a][b] = km
            D[b][a] = km

    # 2) First order: nearest neighbour, improved with 2-opt
    order = nearest_neighbour_order(start, required, D)
    order = local_search(order, D, 0.5)

    best_route, best_km, best_order = None, float("inf"), order
    route = make_route(order, start, adj, cities)
    if route is not None:
        best_route, best_km = route, route_km(route, adj)
        submit(best_route)

    # 3) Keep improving until time runs out 
    while time.monotonic() < deadline:
        if best_route is None:
            # no valid route yet
            rest = [c for c in required if c != start]
            rng.shuffle(rest)
            candidate = [start] + rest
        else:
            # swap a few random cities in the best order to escape local optimum
            candidate = list(best_order)
            for _ in range(3):
                i, j = rng.sample(range(1, len(candidate)), 2)
                candidate[i], candidate[j] = candidate[j], candidate[i]

        candidate = local_search(candidate, D, 0.3)
        route = make_route(candidate, start, adj, cities)
        if route is not None:
            km = route_km(route, adj)
            if km < best_km:
                best_route, best_km, best_order = route, km, candidate
                submit(best_route)