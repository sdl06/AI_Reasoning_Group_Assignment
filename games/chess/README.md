# Challenge: Chess

## Objective

Play regular chess against another team's agent. The judge enforces all the rules through `python-chess`, so you do not have to implement them.

## Rules

Standard chess: legal movement of all pieces, castling, en passant, promotion, check, checkmate, stalemate. Draws by repetition and the other standard conditions apply.

These endings are automatic, with nothing to claim:

| Ending | Result |
|---|---|
| Checkmate | The mating side wins |
| Stalemate | Draw |
| Insufficient material | Draw |
| Threefold repetition | Draw |
| Fifty moves without a capture or pawn move | Draw |
| 400 plies played (safety limit) | Draw |

Nobody ever wins on material when the rules say it is a draw.

## Format and time

Two games with colours swapped, to cancel out White's advantage. The seed decides who is White first.

- Each player has **5 seconds of decision time per game**, not per move.
- The whole challenge is limited to **60 seconds**.
- Each game counts 1 for a win and 0.5 for a draw. The team with more points wins the challenge. A 1-1 result is a draw.

The professor can switch to a single game with a 10-second clock in `tournament_config.json`. The limit will be announced if that happens.

If the 60-second limit itself runs out, which should not happen in normal play, the game in progress is a draw.

## What your agent receives

A complete real example is in `docs/students/sample_observations/chess.json`.

```python
def act(observation):
    return {"move": "e2e4"}
```

| Field | Meaning |
|---|---|
| `fen` | Current position in FEN |
| `color` | `"white"` or `"black"` |
| `legal_moves` | Every legal move, in UCI format |
| `history` | Every move played so far, in UCI |
| `ply` | Half-moves played so far |
| `is_check` | Whether you are in check |
| `game_number`, `games_total` | Which game this is |
| `time_remaining_s` | Your clock |
| `opponent_time_remaining_s` | The rival's clock |

## What your agent returns

`{"move": "<uci>"}`, for example `"e2e4"`, or `"e7e8q"` for a promotion, which must name the piece. `{"move": "resign"}` resigns.

## Losing

| Situation | Result |
|---|---|
| Illegal move | You lose the game |
| Wrong format or not valid UCI | You lose the game |
| Exception or crash | You lose the game |
| Your clock reaches zero | You lose the game, **unless the rival cannot possibly checkmate** (for example a bare king), which is a draw |

## Required algorithms

Minimax, alpha-beta pruning, a heuristic evaluation function, and depth-limited search. You must be able to explain which features your evaluation uses, how you choose the depth, how you apply alpha-beta, and what you do when time runs short.

Optional extensions: Monte Carlo Tree Search, move ordering, iterative deepening, transposition tables, richer evaluation.

**You may not delegate the decision to Stockfish or any other chess engine.** You may use `python-chess` to represent the board, generate moves and check rules. `chess.engine` is rejected automatically.

## Testing your agent

```python
practice = run_game("chess", "chess_agent.py", opponent="demo")
show_game(practice)
check_requirements("chess_agent.py")
```

Template: `student_templates/chess_agent.py`. A working example with no search at all: `examples/team_demo_A/chess_agent.py`.
