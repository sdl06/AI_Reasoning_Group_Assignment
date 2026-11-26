# Catan evaluation results

Held-out seeds `100000` … `100499` (each played both sides).
Training used seeds starting at 1 for 3000 games, so this range does not overlap.

## H vs random

| | Wins |
|---|---|
| Heuristic (H) | 998 |
| Random | 2 |
| Draw | 0 |

## H+Q (`act`) vs H (`heuristic_policy`)

| | Wins |
|---|---|
| H+Q | 423 |
| H | 577 |
| Draw | 0 |

H+Q win rate: **42.3%** over 1000 games in 28.9s.

## Tournament default

`USE_Q = False` — heuristic alone won the held-out matchup; Q values stay for `action_value` / the write-up.
