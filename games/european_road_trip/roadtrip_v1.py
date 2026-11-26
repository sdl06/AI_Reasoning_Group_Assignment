import heapq
import random
import time
from math import asin, cos, radians, sin, sqrt


# ---------------------------------------------------------------
# STEP 1: Build the graph
# ---------------------------------------------------------------

def build_graph(roads):
    """Turns the list of roads into an adjacency dictionary.
    Result: {city: {neighbour: km, ...}, ...}
    Every road goes both ways, so we add it in both directions.
    """
    graph = {}
    for road in roads:
        a, b, km = road["from"], road["to"], road["km"]
        graph.setdefault(a, {})[b] = km
        graph.setdefault(b, {})[a] = km
    return graph


# ---------------------------------------------------------------
# STEP 2: Uniform-Cost Search (UCS)
# ---------------------------------------------------------------
def ucs(graph, start, goal):
    """Finds the shortest road path from start to goal.
    The frontier is a priority queue ordered by the km travelled so far.
    """
    adj = build_graph(graph["roads"])

    frontier = [(0, start, [start])]   # (km so far, city, path to city)
    explored = set()
    expanded = 0

    while frontier:
        km, city, path = heapq.heappop(frontier)   # cheapest path first
        if city in explored:
            continue                               # already reached more cheaply
        explored.add(city)
        expanded += 1                              # taken out of the frontier = expanded

        if city == goal:
            return {"path": path, "km": km, "expanded": expanded}

        for neighbour, road_km in adj[city].items():
            if neighbour not in explored:
                heapq.heappush(frontier, (km + road_km, neighbour, path + [neighbour]))

    return {"path": [], "km": float("inf"), "expanded": expanded}   # no path exists


# ---------------------------------------------------------------
# STEP 3a: straight line distance (heuristic)
# ---------------------------------------------------------------
def straight_line_km(a, b):
    """Haversine distance in km between two cities (given by the handbook).

    a and b are entries of problem["cities"], with "lat" and "lon".
    """
    dlat = radians(b["lat"] - a["lat"])
    dlon = radians(b["lon"] - a["lon"])
    h = sin(dlat / 2) ** 2 + cos(radians(a["lat"])) * cos(radians(b["lat"])) * sin(dlon / 2) ** 2
    return 2 * 6371 * asin(sqrt(h))


# ---------------------------------------------------------------
# STEP 3b: A star
# ---------------------------------------------------------------
def astar(graph, start, goal):
    """Same as UCS, but the frontier is ordered by f = g + h:
        g = km travelled so far
        h = straight-line km from the city to the goal
    """
    adj = build_graph(graph["roads"])
    cities = graph["cities"]

    def h(city):
        return straight_line_km(cities[city], cities[goal])

    frontier = [(h(start), 0, start, [start])]   # (f, g, city, path)
    explored = set()
    expanded = 0

    while frontier:
        f, km, city, path = heapq.heappop(frontier)   # lowest f first
        if city in explored:
            continue
        explored.add(city)
        expanded += 1

        if city == goal:
            return {"path": path, "km": km, "expanded": expanded}

        for neighbour, road_km in adj[city].items():
            if neighbour not in explored:
                g = km + road_km
                heapq.heappush(frontier, (g + h(neighbour), g, neighbour, path + [neighbour]))

    return {"path": [], "km": float("inf"), "expanded": expanded}


# ---------------------------------------------------------------
# STEP 4: Local search with 2-opt
# ---------------------------------------------------------------
def tour_length(tour, dist):
    """Length of the closed tour"""
    total = 0
    for i in range(len(tour)):
        total += dist(tour[i], tour[(i + 1) % len(tour)])
    return total


def local_search(tour, distance, time_limit_s):
    """Improves a tour with 2-opt hill climbing.
    The first city never moves, because i starts at 1.
    """
    def dist(a, b):
        # JSON may turn keys into strings, so try both
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
    deadline = time.time() + time_limit_s * 0.8   # keep a safety margin

    improved = True
    while improved and time.time() < deadline:
        improved = False
        for i in range(1, n - 1):
            for j in range(i + 1, n):
                a, b = tour[i - 1], tour[i]          # first edge  a-b
                c, d = tour[j], tour[(j + 1) % n]    # second edge c-d
                # change in length if we reverse b..c  (a-c and b-d instead)
                delta = dist(a, c) + dist(b, d) - dist(a, b) - dist(c, d)
                if delta < -1e-9:
                    tour[i:j + 1] = reversed(tour[i:j + 1])
                    improved = True
    return tour


# ---------------------------------------------------------------
# STEP 5: The agent 
# ---------------------------------------------------------------
def shortest_path(adj, start, goal, blocked):
    """UCS that is not allowed to pass through the cities in `blocked`.
    """
    frontier = [(0, start, [start])]
    explored = set()
    while frontier:
        km, city, path = heapq.heappop(frontier)
        if city in explored:
            continue
        explored.add(city)
        if city == goal:
            return km, path
        for neighbour, road_km in adj[city].items():
            if neighbour not in explored and neighbour not in blocked:
                heapq.heappush(frontier, (km + road_km, neighbour, path + [neighbour]))
    return None, None


def nearest_neighbour_order(start, required, D):
    """Always go to the closest city not visited yet."""
    order = [start]
    left = set(required) - {start}
    while left:
        current = order[-1]
        closest = min(left, key=lambda city: D[current][city])
        order.append(closest)
        left.remove(closest)
    return order


def build_route(order, start, adj):
    """Turns a visiting order into the full road route, with no repeats.
    """
    route = [start]
    used = {start}
    for target in order[1:] + [start]:          # visit everyone, then back to Madrid
        if target in used and target != start:
            continue                             # already passed through it
        blocked = used - {target}
        km, path = shortest_path(adj, route[-1], target, blocked)
        if path is None:
            return None       
        route += path[1:]
        used.update(path[1:])
    return route


def route_km(route, adj):
    """Real length of a route: the sum of the road kilometres."""
    total = 0
    for i in range(len(route) - 1):
        total += adj[route[i]][route[i + 1]]
    return total


def solve(problem, submit):
    t0 = time.time()
    deadline = t0 + problem["time_limit_s"] * 0.85    # stop early, keep a margin
    start = problem["start"]
    required = problem["required"]
    adj = build_graph(problem["roads"])
    rng = random.Random(0)

    # 1) Road distance between every pair of required cities
    D = {a: {} for a in required}
    for i, a in enumerate(required):
        for b in required[i + 1:]:
            km, _ = shortest_path(adj, a, b, set())
            D[a][b] = km
            D[b][a] = km

    # 2) First order: nearest neighbour, improved with 2-opt
    order = nearest_neighbour_order(start, required, D)
    order = local_search(order, D, 0.5)

    best_route, best_km, best_order = None, float("inf"), order
    route = build_route(order, start, adj)
    if route is not None:
        best_route, best_km = route, route_km(route, adj)
        submit(best_route)                            # submit early

    # 3) Keep improving until time runs out (iterated local search)
    while time.time() < deadline:
        if best_route is None:
            rest = [c for c in required if c != start]
            rng.shuffle(rest)
            candidate = [start] + rest
        else:
            # swap a few random cities in the best order
            candidate = list(best_order)
            for _ in range(3):
                i, j = rng.sample(range(1, len(candidate)), 2)
                candidate[i], candidate[j] = candidate[j], candidate[i]

        candidate = local_search(candidate, D, 0.3)
        route = build_route(candidate, start, adj)
        if route is not None:
            km = route_km(route, adj)
            if km < best_km:
                best_route, best_km, best_order = route, km, candidate
                submit(best_route)