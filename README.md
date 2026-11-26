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

Student guide for all four challenges: [`docs/students/README.md`](docs/students/README.md).
