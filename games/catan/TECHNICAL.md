# Catan technical explanation

Team: AI_Reasoning_Group  
Agent file: `games/catan/catan_agent.py`  
Playbook: `docs/students/CATAN_PLAYBOOK.md`  
Eval numbers: `docs/students/CATAN_EVAL.md`

## Problem formulation

- **State (what we optimise over):** public board, our hand, visible opponent facts, phase, legal actions.
- **Actions:** the judge’s listed action ids (build, trade, play card, roll, end turn, move robber).
- **Observation:** JSON described in `games/catan/README.md`. Opponent hand is hidden; we only reconstruct what the public `log` entails.
- **Objective:** reach 7 VP before the opponent under a 5-second decision clock.

## Algorithms

| Piece | Where | Role |
|---|---|---|
| `state_features` | `catan_agent.py` | Coarse MDP abstraction (phase, VP buckets, build flags, resource shape, hand bucket) |
| `action_value` | `catan_agent.py` | Lookup in offline `Q` keyed by `features\|ACTION_TYPE` |
| `q_update` | `catan_agent.py` | Classic one-step Q-learning update |
| `heuristic_policy` | `catan_agent.py` | Hand-written planning policy (baseline **and** tournament player) |
| `estimate_opponent_resources` | `catan_agent.py` | Certain deductions from the public log |
| Offline trainer | `docs/students/train_catan.py` | 3000 games, both sides, ε-greedy vs heuristic/random |
| Eval | `docs/students/eval_catan.py` | Held-out seeds outside the training range |

**Planning.** Builds/trades are chosen by preconditions (legal + resources) and effects (+VP, production, unlock next build). Trades fire only when they unlock a build (or to shed cards at ≥8).

**Inference.** Dice payouts, visible builds, maritime trades, and known steals update an opponent-hand estimate. Discard composition and unknown steals are not invented.

## Baseline against improved version

| Matchup | Result |
|---|---|
| Heuristic v2 vs random (held-out, 1000 games) | **1000–0** |
| Heuristic v2 vs heuristic v1 (held-out, 1000 games) | **638–362** |
| H+Q (`act` with `USE_Q=True`) vs heuristic v2 (1000 games) | 373–627 |
| Demo team A vs heuristic v1 → v2 (1000 games) | 236 → 139 demo wins |

The learned table did **not** beat the hand-written policy on held-out seeds, so the tournament default is `USE_Q = False` (`act` == heuristic). The Q-table remains embedded so `action_value` is a real learned estimate for the academic checks and write-up. It was trained against heuristic v1, which is part of why it loses by more against v2.

Earlier versions of `eval_catan.py` called `act` with whatever `USE_Q` was set to, so once `USE_Q = False` the "H+Q vs H" row compared the heuristic with itself (exactly 50%). The script now forces Q on for the H+Q side.

### Heuristic v2 (what changed from v1, and why)

Each change was kept only if it won against the previous version over 1000 seeds × both sides (2000 games, standard error about 1.1%). Changes that tested neutral were dropped.

| Change | Result vs previous version |
|---|---|
| **Robber** scores a tile as `pips × (rival cards per payout − 1.5 × our cards per payout)`, plus a bonus for stealing when the rival holds cards. v1 only added pips, so it blocked our own tiles in 1017 of 2737 robber moves (37%). | 54.5% |
| **Roads** aim only at nodes we can legally settle (distance rule from the board's edge adjacency), and count a buildable node one more road away at 0.7. | 59.4% (cumulative vs v1) |
| **Trades** no longer fire just to afford a road (4:1 for a road spends cards a city or settlement needs), unless we are racing for longest road. | 55.6% |
| Tried and dropped: saving ore instead of buying dev cards, cities by raw pips, settlements before cities early, skipping roads that lead nowhere. | 49.6–50.0% |

**Speed.** The board never changes during a game, so per-node production, tile nodes, tiles by number and node adjacency are computed once and cached at module level (the process lives for the whole game). The opponent-hand reconstruction no longer rescans every tile for every roll in the log. Agent time per decision fell from about 0.066 ms to 0.024 ms, far below the judge's 2–6 ms transport cost per Catan decision.

Retrain / re-eval:

```bash
python docs/students/train_catan.py --games 3000
python docs/students/eval_catan.py --games 500 --start-seed 100000
```

## Time and memory

- Decisions are O(#legal actions) scoring, about 0.02 ms each; static board facts are cached once per game.
- If `time_remaining_s < 0.35`, `act` skips Q scoring and uses the heuristic immediately.
- Offline training: ~3000 games in under a minute on a typical machine.

## Limits

- Tabular Q over a coarse abstraction underfits; more games or richer features may help, but must be re-validated.
- Opponent-hand estimate is a lower bound; monopoly/robber still use heuristics when the log is uninformative.
- No MCTS / expectimax under the 5s clock (left as future work).

## How to use the agent

```python
from tournament.runner import run_game, show_game
from tournament.academic_checks import check_requirements

practice = run_game("catan", "games/catan/catan_agent.py", opponent="demo", quiet=True)
show_game(practice)
check_requirements("games/catan/catan_agent.py", games=["catan"])
```

For a full team zip, copy `games/catan/catan_agent.py` next to your other three agent files.
