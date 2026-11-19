# Challenge: European Road Trip

## Objective

Find the shortest route by road that starts in Madrid, visits every required city, and returns to Madrid, without passing through any city twice. Every match has 25 required cities: Madrid plus 24 others, drawn at random and all different.

## Rules

- The route must start and end in Madrid and pass through every required city.
- No city may appear twice in a route. The only exception is Madrid, at the start and at the end. A route that breaks this is invalid.
- You may pass through cities that are not required, each at most once.
- The required cities can be visited in any order.
- You may only travel along roads in the graph.
- The route length is the sum of the kilometres of the roads travelled. The judge computes it. Straight-line distances never count.

## The map

The map is public and the same in every match: 105 cities joined by 262 roads, in `data/cities.csv` and `data/roads.csv`. Road distances are driving kilometres derived from OpenStreetMap data, and ferry crossings are excluded (see `data/README.md`). Only the required cities change.

Neighbouring cities may have no direct road, so finding a path between two required cities is part of the problem. The shortest path may go through a city you have already used, and then you cannot take it.

Twelve cities are never drawn, because no route can visit them and return to Madrid without passing through a city twice: Aarhus, Bari, Copenhagen, Gothenburg, Malmo, Naples, Odense, Oslo, Reggio Calabria, Rome, Stockholm and Tallinn. Every draw has at least one valid route.

## Heuristic

You receive each city's latitude and longitude, so you can compute the straight-line (Haversine) distance:

$$h(n) = d_{\text{Haversine}}(n, \text{goal})$$

Every road in the map is at least as long as the straight line between its two ends, using an Earth radius of 6371 km. So this distance never overestimates the road distance, and it is an admissible heuristic for A\*.

## Practice instances

- `data/training_instance.json`: 25 required cities, always the same. Use `run_game("road_trip", team, training=True)`.
- `data/small_instances.json`: smaller problems for checking your algorithms by hand.

Tournament instances are drawn when the match starts and are never the training set.

## What your agent receives and does

A real example, with the map shortened, is in `docs/students/sample_observations/road_trip.json`.

```python
def solve(problem, submit):
    ...
```

| Field | Meaning |
|---|---|
| `problem["start"]` | `"madrid"` |
| `problem["required"]` | The 25 cities to visit, including the start |
| `problem["time_limit_s"]` | Seconds available |
| `problem["cities"]` | `{id: {"name", "country", "lat", "lon"}}` |
| `problem["roads"]` | `[{"from", "to", "km", "bidirectional"}]`. Every road goes both ways, so `bidirectional` is always `true` |

Call `submit(route)` every time you have a better route. `route` is the full list of cities you pass through, including intermediate cities and the return to Madrid:

```python
submit(["madrid", "zaragoza", "barcelona", ..., "valencia", "madrid"])
```

A list of destinations alone is not accepted, because the judge must be able to check every road. Each call sends one JSON Lines message to the judge at once, such as `{"type": "solution", "path": [...]}`, without interrupting your search.

## Submit early, then keep improving

You do not have to wait until the end. Submit a valid route early, then keep improving it. An agent that submits at 1, 2 and 4 seconds has its best valid route counted. Your 5 seconds start when you receive the problem, and loading your file does not count.

For each submission, the judge checks that it starts and ends in Madrid, repeats no city, visits all required cities and uses only existing roads. It then computes the real distance and keeps the best valid route so far.

- An invalid route is rejected, and your previous best stands. `submit` gives no feedback during the race, so afterwards look in `practice["details"]["routes"]["A"]`, which has `km`, `path`, `valid_solutions`, `invalid_solutions`, `improvements` and the `rejections` with their reasons.
- A route sent after the limit is ignored.
- Your process is stopped at the limit.
- If `solve` returns early, your best route stands.
- If your code crashes, raises an exception or exceeds the memory limit after a valid submission, that submission still counts.

## Time

Both agents start together on the same instance and have **5 seconds** of real time. On Colab, each agent gets its own CPU core. On your own computer they may share.

## Winning

| Situation | Result |
|---|---|
| Shorter valid route | Win |
| Exactly the same distance | Draw |
| Only one agent has a valid route | That agent wins. Test on many draws: a method that gets stuck can end up with no route at all |
| Neither has a valid route | Technical draw |

## Required algorithms

Uniform-cost search or Dijkstra, A\* with a geographic heuristic, at least one optimisation method, and a comparison between a first strategy and an improved one. See `docs/students/ASSIGNMENT.md`. You may add others: 2-opt, dynamic programming, branch and bound, hybrids.

## Testing your agent

```python
practice = run_game("road_trip", "roadtrip_agent.py", opponent="demo", training=True)
show_game(practice)
check_requirements("roadtrip_agent.py")
```

Template: `student_templates/roadtrip_agent.py`. A working example, deliberately weak: `examples/team_demo_A/roadtrip_agent.py`.
