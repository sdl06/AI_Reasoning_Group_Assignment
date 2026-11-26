# Catan evaluation results

Held-out seeds `100000` … `100499` (each played both sides).
Training used seeds starting at 1 for 3000 games, so this range does not overlap.

## H vs random

| | Wins |
|---|---|
| Heuristic (H) | 1000 |
| Random | 0 |
| Draw | 0 |

## H+Q (`act`) vs H (`heuristic_policy`)

| | Wins |
|---|---|
| H+Q | 373 |
| H | 627 |
| Draw | 0 |

H+Q win rate: **37.3%** over 1000 games in 12.7s.

## Tournament default

`USE_Q = False` — heuristic alone won the held-out matchup; Q values stay for `action_value` / the write-up.
