# AI_Reasoning_Group_Assignment

Course AI agent tournament (Road Trip, Chess, Battleship, Catan).

## Catan agent (ready to use)

| Item | Path |
|---|---|
| Competing agent | [`games/catan/catan_agent.py`](games/catan/catan_agent.py) |
| Build playbook (steps 0–9) | [`docs/students/CATAN_PLAYBOOK.md`](docs/students/CATAN_PLAYBOOK.md) |
| Technical write-up | [`games/catan/TECHNICAL.md`](games/catan/TECHNICAL.md) |
| Held-out eval | [`docs/students/CATAN_EVAL.md`](docs/students/CATAN_EVAL.md) |
| Offline trainer | [`docs/students/train_catan.py`](docs/students/train_catan.py) |
| Eval harness | [`docs/students/eval_catan.py`](docs/students/eval_catan.py) |

```bash
pip install -r requirements.txt
python docs/students/eval_catan.py --games 100 --start-seed 100000
```

```python
from tournament.runner import run_game
from tournament.academic_checks import check_requirements

run_game("catan", "games/catan/catan_agent.py", opponent="demo", quiet=True)
check_requirements("games/catan/catan_agent.py", games=["catan"])
```

## Road Trip agent (ready to use)

| Item | Path |
|---|---|
| Competing agent | [`games/european_road_trip/roadtrip_agent.py`](games/european_road_trip/roadtrip_agent.py) |
| First version (baseline) | [`games/european_road_trip/roadtrip_v1.py`](games/european_road_trip/roadtrip_v1.py) |
| Technical write-up | [`games/european_road_trip/TECHNICAL.md`](games/european_road_trip/TECHNICAL.md) |

Results: 4/4 required checks pass. Over 50 races: 50 wins vs `demo_a` (12,977 km vs 15,879 km on average), and 1 win and 49 draws vs the first version.

```python
from tournament.runner import run_game
from tournament.academic_checks import check_requirements

run_game("road_trip", "games/european_road_trip/roadtrip_agent.py", opponent="demo", quiet=True)
check_requirements("games/european_road_trip/roadtrip_agent.py", games=["road_trip"])
```

Student guide for all four challenges: [`docs/students/README.md`](docs/students/README.md).
