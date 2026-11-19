# AI Agent Tournament: student guide

Your team writes four Python agents, one for each challenge. They play another team's agents in a knockout tournament. The judge supplies the rules, refereeing, maps and clocks. You write how the agents decide.

**Teams** have 4 to 6 people, both included. One member emails the professor with all the other members in copy.

| Challenge | Your file | Rules |
|---|---|---|
| European Road Trip | `roadtrip_agent.py` | [games/european_road_trip/README.md](../../games/european_road_trip/README.md) |
| Chess | `chess_agent.py` | [games/chess/README.md](../../games/chess/README.md) |
| Battleship with moving ships | `battleship_agent.py` | [games/battleship/README.md](../../games/battleship/README.md) |
| Catan Tournament 1v1 | `catan_agent.py` | [games/catan/README.md](../../games/catan/README.md) |

**Read [CHALLENGES.md](CHALLENGES.md) first: it explains the four challenges in one page.** [ASSIGNMENT.md](ASSIGNMENT.md) lists the algorithms you must implement. [TRAINING.md](TRAINING.md) shows how to train your Catan agent offline. [sample_observations/](sample_observations/) has real examples of what your agents receive, so read them before writing code.

## Getting started

1. In [Google Colab](https://colab.research.google.com), choose **File > Upload notebook** and pick `Tournament.ipynb`. Then open the Files panel on the left and upload `ai_agent_tournament.zip`.
2. Choose **Runtime > Run all**. Two example teams play a full match, so you can see what happens.
3. Copy a file from `student_templates/`, for example `chess_agent.py`. It already plays legally, badly.
4. Upload that file in the Files panel and practise it against an example agent, in section 5 of the notebook or in any new cell. Colab deletes uploads when the session ends, so keep your own copies.

```python
practice = run_game("chess", "chess_agent.py", opponent="demo")
show_game(practice)                  # boards, maps and replays
print(practice["logs"]["A"])         # what your agent printed (the last 20,000 characters per game)
check_requirements("chess_agent.py")
```

5. When you have all four files, put them in a folder named after your team, zip it as `Team_07.zip` and upload the zip. Colab's Files panel takes files, not folders. Write `TEAM_A = "Team_07.zip"` in section 2 of the notebook to play a full match.

| To play | Give the judge |
|---|---|
| One game, in practice | One `.py`, with any name, or your team's zip |
| A full match | A `.zip` or a folder with your four files |

The name alone is enough for anything you uploaded, and a full path works too. When your agent fails, the result shows the reason and the full error.

## Comparing versions of your agent

The assignment asks you to compare a baseline with an improved version. Give the older file as the opponent, and use several seeds because a single game proves little. In the result, your team is `"A"`.

```python
wins = {"A": 0, "B": 0, None: 0}
for seed in range(1, 51):
    result = run_game("catan", "catan_v2.py", opponent="catan_v1.py", seed=seed, quiet=True)
    wins[result["winner"]] += 1
print(wins)
```

| Result key | Meaning |
|---|---|
| `winner` | `"A"`, `"B"`, or `None` for a draw |
| `reason` | How it ended |
| `score` | What the summary shows for each side |
| `incidents` | Failures, each with `side`, `kind` and `detail` |
| `logs` | What each side printed |
| `match_seed` | The seed to pass if you want to replay this game |
| `seed` | This game's own seed, derived from `match_seed`. `play_one_game`, in [TRAINING.md](TRAINING.md), takes this one |
| `details` | Game data such as routes or moves |

Fifty games are enough to spot a big difference in most challenges. Catan has much more luck: for it, use the faster loop in [TRAINING.md](TRAINING.md) and at least 500 games.

The practice rivals are examples, and they are weak on purpose. Beating them does not show your agent is good.

| Opponent | How it plays |
|---|---|
| `"demo"` or `"demo_a"` | No search or learning: routes rebuilt at random for 4 seconds, one-move material count, shooting around hits, a fixed priority list. In Battleship it moves a random ship on about a quarter of its turns. |
| `"demo_b"` | Random legal play. In Road Trip it stops at its first valid route. In Battleship its ships never move. |

## Debugging

Prints are the simplest tool, but `logs` keeps only the last 20,000 characters per game, and one Catan observation alone is about 15,000. In practice your agent may also write a debug file to a full path such as `/content/debug.json`. Its working folder is deleted when the game ends, so a relative path is lost. Remove debug files before the tournament.

To play against an earlier version of your own agent, or against another team, give its file or zip as the opponent:

```python
run_game("chess", "chess_agent.py", opponent="chess_old.py")
run_game("chess", "chess_agent.py", opponent="Team_12.zip")
```

The judge you practise with is the one used on tournament day. You can also run it on your own computer with Python 3.10 or newer, using `pip install -r requirements.txt`. Colab is the reference environment, so test there before the tournament.

## Settings for practice

Practice uses the real limits. While you debug, you can change them, for example to run Road Trip for 20 seconds:

```python
run_game("road_trip", "roadtrip_agent.py", config={"road_trip": {"time_limit_s": 20}})
```

| Setting | Real value | Meaning |
|---|---|---|
| `road_trip.time_limit_s` | 5 | Seconds for each agent |
| `chess.clock_s` | 5 | Decision seconds per player, per game |
| `chess.challenge_limit_s` | 60 | Limit for the whole challenge |
| `battleship.clock_s` | 5 | Decision seconds per player |
| `battleship.max_rounds` | 150 | Rounds before the game is adjudicated |
| `catan.clock_s` | 5 | Decision seconds per player |
| `catan.max_rounds` | 100 | Value of `round` at which the game is adjudicated |
| `catan.vps_to_win` | 7 | Victory points to win |

A misspelt setting raises an error. Tournament matches use the real values, so test with them before the tournament.

## Tournament day

Each pair of teams shares one Colab, usually on the laptop of one of the two teams. Bring your zip and send it to the other team, or to whoever is hosting. Set `TEAM_A` and `TEAM_B` to the two zips, run all the cells, and keep the tab open until the match ends.

## How a match works

Two teams play all four challenges in this order, without anyone touching the keyboard:

| Order | Challenge | Time |
|---|---|---|
| 1 | European Road Trip | At most 5 s, both agents at the same time |
| 2 | Chess | About 20 s at most, two games with colours swapped |
| 3 | Battleship | About 10 s at most |
| 4 | Catan | About 10 s at most |

A challenge ends as soon as it is decided, so a match is often much shorter. Road Trip ends when both agents have finished.

A win scores 1 point and a draw scores 0.5. The team with more points advances. If the match is tied, a new Road Trip with new random cities and the same 5-second limit decides it, repeated up to 3 times. If it is still tied, the professor decides. The notebook never picks a winner at random.

At the end, the notebook shows the winner of each game and the team that advances. Tell the professor, who keeps the bracket on the board.

## How your code is called

Each file defines one entry point. You never read from standard input or write protocol messages yourself.

```python
# chess_agent.py, battleship_agent.py, catan_agent.py
def act(observation: dict) -> dict:
    ...

# roadtrip_agent.py
def solve(problem: dict, submit) -> None:
    ...
```

Your file is loaded once per game, in its own process, and stays alive for the whole game. Module-level variables keep their values between calls. Each new game starts a new process with a clean state, so nothing carries over from one game to the next, not even between the two chess games.

Everything travels as JSON, which shapes what you receive: tuples arrive as lists and dictionary keys as strings. A list cannot be a dictionary key, so convert it first, for example `tuple(tile)`.

Observations contain only what your agent is entitled to know. Anything you `print()` is harmless: it never reaches the judge, and in practice you can read it in `practice["logs"]["A"]`.

## Clocks

The judge's clock is the only one that counts.

- Time starts when the judge sends you an observation and stops when your answer arrives.
- Every turn-based observation tells you `time_remaining_s`. Use it. An agent that searches too deep will lose on time.
- Between your turns your process is paused, so you cannot think during the rival's time.
- Loading your file has its own limit of 15 seconds, which does not count against your clock. Do not train or do heavy work at import time.
- Sending the observation and your answer counts against your clock: about 1 millisecond per decision in chess and 2 to 6 in Catan.
- Colab's free machines are often slower than a laptop, so keep about half a second of your clock in reserve and test there.

## Penalties

| What your agent does | Consequence |
|---|---|
| Runs out of its clock | Loses that game (in chess, a draw if the rival cannot possibly checkmate) |
| Illegal action or move | Loses that game |
| Answer in the wrong format | Loses that game |
| Raises an exception | Loses that game |
| Crashes or exits | Loses that game |
| Uses more than 2 GB of memory | Loses that game |
| File fails to load, or imports something forbidden | Loses that game |
| Road Trip: invalid route | That route is ignored and your best valid route stands |
| Road Trip: exception, crash or too much memory | Your agent stops, and your best valid route so far stands |
| Road Trip: no valid route by the deadline | Loses the challenge |

Nothing is ever corrected in your favour. If both agents fail in the same challenge, it is a technical draw. To find out, after one agent fails in Battleship or Catan, or fails in chess other than on time, the judge asks the rival for one more decision: if that also fails, the game is a technical draw instead of a win. The notebook lists every incident and its cause.

## Allowed and forbidden

Answers may contain regular Python values or `numpy` numbers and arrays.

**Allowed:** the Python standard library, `numpy`, `networkx`, `chess` (for the board and move generation), and `catanatron` only to simulate the rules. Parameters you learned before the tournament, stored inside your `.py`.

**Forbidden, and rejected automatically when your file loads:**

- Existing game engines and bots: `stockfish`, `chess.engine`, `catanatron.players`, `catanatron_experimental`.
- Network and external programs: `socket`, `requests`, `urllib.request`, `http.client`, `httpx`, `aiohttp`, `subprocess`.

**Also not allowed, even if no check catches it:** calling external services during a match, training a model from scratch during a match, downloading a model, reading the rival's files, or anything else designed to get around these rules. The aim is for your own algorithms to play.

Only your four agent files are ever run. Anything else in your folder is ignored, so a helper module would not be found: each agent must be a single file, with its helpers inside it.

## What to hand in

```
Team_07/
    chess_agent.py
    catan_agent.py
    battleship_agent.py
    roadtrip_agent.py
    README.md
```

`student_templates/README.md` is the template for the `README.md`, which also holds your technical explanation.

Upload two files to Blackboard: `Team_07.zip` and, as a separate file, your presentation as a PDF. You will present your work in class, in 5 minutes at most.

## Reproducing a game

Each result prints a seed, which for a practice game is also in `result["match_seed"]`. Pass it to `run_game` or `run_match` to replay the same cities and the same random events. The game replays exactly only if your agents are deterministic too. The judge seeds Python's `random` module for you, and the agents' seeds also derive from it.

```python
run_match(team_a=TEAM_A, team_b=TEAM_B, seed=123456)
```
