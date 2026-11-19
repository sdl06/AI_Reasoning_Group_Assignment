# Challenge: Battleship with moving ships

## Objective

Sink the enemy fleet. Unlike the traditional game, **ships can move until they take their first hit**, so you reason about hidden positions that change over time.

## Board and fleet

The board is 10 × 10. Cells are `[row, col]`, with `[0, 0]` at the top left.

| Ship | Length |
|---|---|
| `carrier` | 5 |
| `battleship` | 4 |
| `cruiser` | 3 |
| `submarine` | 3 |
| `destroyer` | 2 |

That makes 17 segments in total. Ships are horizontal (`"H"`) or vertical (`"V"`). They cannot overlap, leave the board, bend or sit diagonally. They may touch each other.

## Placement

Your first observation has `"phase": "placement"`, plus `board_size`, `time_remaining_s` and `fleet`, a list of `{"ship", "length"}`. Return your fleet, with `row` and `col` being the ship's top-left cell:

```python
{"placements": [{"ship": "carrier", "row": 0, "col": 0, "orientation": "H"}, ...]}
```

Every ship must appear exactly once. Return `{"placements": None}` to let the judge place your fleet at random. An invalid placement loses the game.

## Your turn

The seed decides who moves first. Each turn, in this order:

1. **Optionally move one ship** that has not been hit.
2. **Either shoot or use sonar.**

```python
{"shot": [4, 7]}                                                   # shoot
{"sonar": [4, 7]}                                                  # scan instead of shooting
{"move": {"ship": "destroyer", "direction": "N"}, "shot": [4, 7]}  # move a ship, then shoot
```

`move` is optional. Leave it out, or set it to `None`, if no ship moves.

## Movement

- A ship moves at most one cell per turn, in direction `N` (row - 1), `S` (row + 1), `E` (col + 1) or `W` (col - 1).
- It keeps its orientation and cannot rotate.
- It must stay on the board and cannot overlap another ship.
- Only one ship may move per turn.
- **A ship that has been hit once is immobile for the rest of the game**, even with undamaged segments.

`legal_moves` in your observation lists every move available to you.

## Shots

| Result | Meaning |
|---|---|
| `MISS` | Nothing new was damaged |
| `HIT` | A segment was damaged for the first time |
| `SUNK` | That hit destroyed the ship's last segment. `sunk_length` gives its length. |

Damage is permanent and a segment is only damaged once. Shooting an already damaged segment returns `MISS` with `"already_damaged": true`.

**You may shoot the same cell again.** Because ships move, a cell that was empty earlier may be occupied now. A past miss proves nothing about the present. This is the main difference from the traditional game.

## Sonar

You have **2 sonar scans per game**. A scan replaces your shot for that turn. You may still move a ship.

A scan covers the 3 × 3 square around the chosen cell, clipped at the board's edges. It returns a noisy count of the enemy segments there, including damaged ones:

| True count `n` | Reading |
|---|---|
| Correct, 80% | `n` |
| One lower, 10% | `n - 1` |
| One higher, 10% | `n + 1` |

A reading can never be below 0 or above the number of cells scanned. In those cases the impossible outcome is removed and the remaining probabilities are renormalised. For example, with a true count of 0 the reading is 0 with probability 8/9 and 1 with probability 1/9.

## What your agent knows

Each observation has `"phase": "turn"`. A complete real example, with a miss, a hit, a sunk ship and a sonar scan, is in `docs/students/sample_observations/battleship_turn.json`.

| Field | Meaning |
|---|---|
| `my_ships` | Each ship's `ship`, `length`, `orientation`, `cells`, `damaged_cells`, `immobile`, `sunk` |
| `legal_moves` | `[{"ship", "direction"}, ...]` |
| `my_shots` | `[{"turn", "target", "result"}, ...]`, also with `sunk_length` or `already_damaged` when they apply |
| `my_sonar` | `[{"turn", "center", "reading"}, ...]` |
| `sonar_remaining`, `sonar_correct_probability` | Scans left, and the sensor's accuracy |
| `enemy_ships_sunk` | Lengths of the enemy ships you have sunk |
| `enemy_segments_destroyed` | Total enemy segments destroyed |
| `damage_received` | Hits on your own fleet: `[{"turn", "cell", "ship", "sunk"}, ...]` |
| `turn` | Actions played so far by both players, so it rises by 2 per round. The `turn` inside `my_shots` and `my_sonar` numbers each action from 1, so your next action will be `turn + 1`. |
| `max_rounds` | Rounds in the game: each player gets this many turns |
| `board_size`, `time_remaining_s` | Board side and your clock |

You never learn the current position of undiscovered enemy ships, the moves the rival made, whether it used sonar, or where its shots missed.

## Time and limits

- Each player has **5 seconds of decision time**. The whole challenge is limited to **60 seconds**.
- The game ends after **150 rounds**, so both players always get the same number of turns.

## Winning

Destroying all 17 enemy segments wins at once. If the round or challenge limit is reached first, the judge decides in this order:

1. More enemy segments destroyed.
2. More enemy ships sunk.
3. Fewer of your own segments destroyed.
4. Otherwise, a draw.

An illegal action, wrong format, exception, crash, or running out of your own clock loses the game.

## Required algorithms

Representing partial information. Constraints over possible positions, with backtracking or systematic reasoning, plus forward checking, AC-3 or equivalent propagation where it helps. Logical and probabilistic inference, Bayes' rule, and updating beliefs with new evidence.

You must also have an explicit transition model for at least one unseen ship and a belief-filtering procedure. Keep in mind that this is an estimate: the rival has its own strategy and may not move at random.

Optional extension: hidden Markov models and particle filtering.

## Testing your agent

To test your belief filter against both kinds of rival: `opponent="demo_a"` moves a random ship on about a quarter of its turns, and `opponent="demo_b"` never moves.

```python
practice = run_game("battleship", "battleship_agent.py", opponent="demo")
show_game(practice)
check_requirements("battleship_agent.py")
```

Template: `student_templates/battleship_agent.py`. A working example with no probabilities: `examples/team_demo_A/battleship_agent.py`.
