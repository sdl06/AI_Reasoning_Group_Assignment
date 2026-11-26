"""Tests the Road Trip agent with the official judge. Run from the repo's top folder."""
from tournament.academic_checks import check_requirements
from tournament.runner import run_game

AGENT = "games/european_road_trip/roadtrip_agent.py"
FIRST_VERSION = "games/european_road_trip/roadtrip_v1.py"

# 1) The required functions (ucs, astar, local_search)
check_requirements(AGENT, games=["road_trip"])

# 2) 50 races against the first version and against the example agent
for opponent in [FIRST_VERSION, "demo_a"]:
    wins = {"A": 0, "B": 0, None: 0}
    ours, theirs, no_route = [], [], 0
    for seed in range(1, 51):
        r = run_game("road_trip", AGENT, opponent=opponent, seed=seed, quiet=True, live=False)
        wins[r["winner"]] += 1
        a = r["details"]["routes"]["A"]["km"]
        b = r["details"]["routes"]["B"]["km"]
        if a is None:
            no_route += 1
        else:
            ours.append(a)
        if b is not None:
            theirs.append(b)
    print(f"vs {opponent}: wins={wins['A']} losses={wins['B']} draws={wins[None]} | "
          f"our avg {sum(ours) / len(ours):.0f} km | "
          f"their avg {sum(theirs) / len(theirs):.0f} km on {len(theirs)}/50 draws | "
          f"our draws with no route: {no_route}")