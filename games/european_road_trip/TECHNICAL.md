# European Road Trip: technical write-up

## Problem formulation
The map is an undirected weighted graph: 105 cities are the nodes, and the 262 roads are the edges, weighted by their driving km. `build_graph` stores it as an adjacency dictionary `{city: {neighbour: km}}`.

The task is a constrained travelling-salesman problem. A state is a partial route from Madrid, together with the set of cities it has already used. An action is driving to a neighbouring city that is not used yet. The goal is a closed route that starts and ends in Madrid, visits all 25 required cities, and passes through no city twice. We minimise the total road km. The agent observes the whole map and the required cities, and it has `time_limit_s` seconds.

## Algorithms
| Algorithm | Function | Why |
|---|---|---|
| UCS and A* | `search` (wrappers `ucs`, `astar`) | Shortest road path between two cities, optionally avoiding blocked cities |
| Nearest neighbour | `nearest_neighbour_order` | A quick first visiting order |
| 2-opt hill climbing | `local_search` | Shortens the visiting order |
| Route builder with look-ahead | `build_route`, `still_possible` | Turns an order into a road route that never reuses a city |
| Cheapest insertion (fallback) | `insertion_route` | Used when `build_route` gets stuck |
| Iterated local search | `solve` | Keeps improving until 85% of the time limit |

**UCS and A\*.** Both use one function, `search`. Its frontier is a priority queue ordered by f = g + h, where g is the km driven so far. h is 0 for UCS, and the Haversine straight-line distance to the goal for A\*. A city is expanded when it leaves the frontier. Road km are never negative, so the first time the goal leaves the frontier, its path is the shortest. Every road is at least as long as the straight line between its ends, so h never overestimates (it is admissible), and A\* is still optimal. It also holds with blocked cities, because blocking cities can only make real paths longer. A\* expands fewer cities: 184 vs 392 for UCS over the judge's 8 test pairs. `solve` uses A\* for every path.

**Local search (2-opt).**
- *Neighbourhood:* reverse one segment `tour[i..j]`. This replaces edges a–b and c–d with a–c and b–d. The first city never moves.
- *Acceptance rule:* only if the tour gets shorter (hill climbing). We compute only the change in those four distances, not the whole tour.
- *Local optima:* 2-opt stops when no reversal helps. To escape, `solve` "kicks" the best order (swaps 3 random cities), runs 2-opt again, and keeps the result only if the real route is shorter. This is iterated local search.

**Valid routes without repeating a city.** Joining the cities by plain shortest paths often reuses a city, so:
1. Each leg is found by A\* with every city already in the route blocked.
2. Before accepting a leg, `still_possible` runs a search over the free cities to check that every remaining required city and Madrid can still be reached. If not, that city is postponed and the next one is tried.
3. A tour has the same length in both directions, but one direction can get trapped where the other does not, so `make_route` tries both.
4. If both get stuck, `insertion_route` starts from the loop [Madrid, Madrid] and inserts each city at the cheapest detour that avoids used cities. This idea was inspired by the course's example agent, but our version uses A\* paths and the cheapest insertion point.

## Baseline against improved version
We ran the official judge locally (`test_roadtrip.py`): `run_game` over seeds 1–50, under the real 5-second limit. `check_requirements` shows 4/4 passing.

| Comparison | Wins / losses / draws | Average route | Draws with no valid route |
|---|---|---|---|
| Final vs first version (`roadtrip_v1.py`) | 1 / 0 / 49 | 12,977 km vs 13,000 km | 0 vs 0 |
| Final vs example agent `demo_a` | 50 / 0 / 0 | 12,977 km vs 15,879 km (18% shorter) | 0 vs 0 |

**What the comparison with the first version shows.** The first version is nearest neighbour + 2-opt, with every leg joined by a shortest path that avoids used cities. Both versions are deterministic and share the same first steps, so on 49 of the 50 draws they produced exactly the same route. The improvements in the final version (look-ahead check, both directions, insertion fallback) only act when the simple builder gets trapped: a leg uses up the only roads out of a region, and the next city can no longer be reached without repeating a city. On these 50 draws the first version always found a valid route, so the two versions are almost equal here. The improvements are a safeguard: the handbook warns that a method that gets stuck can end with no valid route, which loses the challenge. With more time, we would test both versions on many more draws to measure how often the first version gets stuck.

## Time and memory
`solve` submits its first valid route as soon as it has built one, then keeps improving until 85% of `time_limit_s` (4.25 s of 5), keeping a margin for Colab's slower machines. Each 2-opt run is capped at 80% of the time it is given. It reads `time_limit_s` instead of assuming 5. Memory use is tiny: a 105-city graph and a 25 × 25 distance table.

## Limits
- The order is optimised with shortest-path distances, but the real route can be longer, because legs must avoid used cities.
- The kicks are random swaps; simulated annealing or Or-opt moves could find shorter routes.
- With more time we would try dynamic programming or branch and bound for an exact order.