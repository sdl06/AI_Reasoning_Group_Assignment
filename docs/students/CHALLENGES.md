# The four challenges in one page

You write one Python file per challenge. The judge runs the game and calls one function in your file. It gives you everything you are allowed to know, and you answer with your decision. The judge takes care of the rules, turns, clocks and scoring. Your work is the decision-making.

| Challenge | Your file | The judge calls | You answer |
|---|---|---|---|
| European Road Trip | `roadtrip_agent.py` | `solve(problem, submit)` | `submit(route)`, as often as you like |
| Chess | `chess_agent.py` | `act(observation)` | `{"move": "e2e4"}` |
| Battleship | `battleship_agent.py` | `act(observation)` | `{"placements": None}` once, then `{"shot": [4, 7]}` each turn |
| Catan | `catan_agent.py` | `act(observation)` | `{"action": 12}` |

`problem` and `observation` are ordinary dictionaries.

## European Road Trip

**The game.** Drive from Madrid through 24 other cities and back to Madrid, in as few kilometres as possible, without passing through any city twice. The cities change every match, and the map of 105 cities stays the same. You have 5 seconds. The shorter route wins.

**You receive.** `problem["required"]` has the 25 cities, `problem["roads"]` has every road with its kilometres, and `problem["cities"]` has each city's latitude and longitude.

**You answer.** The whole trip, city by city, along real roads, with no city twice except Madrid at both ends. Send a route as soon as you have one, then send better ones. Your best route counts.

```python
def solve(problem, submit):
    route = ...  # ["madrid", "zaragoza", "barcelona", ..., "valencia", "madrid"]
    submit(route)
```

**You design.** How to find a short path between two cities that avoids the cities you have already used, which order to visit them in, and how to keep improving while time remains.

## Chess

**The game.** Two games against the other team, one with each colour. Each player has 5 seconds per game, not per move. The team with more points wins.

**You receive.** `fen` is the position, plus `color`, `legal_moves` and `time_remaining_s`.

**You answer.** One of the legal moves.

```python
def act(observation):
    return {"move": observation["legal_moves"][0]}
```

**You design.** How to score a position, how deep to search, and how to spend your 5 seconds.

## Battleship with moving ships

**The game.** Sink all 5 enemy ships on a 10 x 10 board. Unlike the board game, each turn a ship can move one cell, until it is hit for the first time. So a miss only tells you that a cell was empty at that moment. You have 5 seconds in total.

**You receive.** `my_ships`, `legal_moves`, `my_shots` with their results, `my_sonar` and `sonar_remaining`.

**You answer.** First where your fleet goes, then one action each turn.

```python
import random

def act(observation):
    if observation["phase"] == "placement":
        return {"placements": None}  # the judge places your fleet at random
    return {"shot": [random.randrange(10), random.randrange(10)]}
```

Instead of shooting, you can scan with `{"sonar": [4, 7]}`, twice per game. It gives a noisy count of the enemy segments in the 3 x 3 square around that cell. To move one of your ships as well, add a `move`: `{"move": {"ship": "destroyer", "direction": "N"}, "shot": [4, 7]}`.

**You design.** Where the enemy ships probably are now, given that they move and the sonar is noisy. When a scan is worth more than a shot. Where to place your fleet, and whether to move it.

## Catan 1v1

**The game.** The first to 7 victory points wins. There are two players and no trading between them, though you can trade with the bank. You have 5 seconds in total.

**You receive.** `actions` lists what you can legally do right now, each with an `id`. You also get `me`, the public facts about `opponent`, the `board` and a `log` of everything that has happened. The judge handles dice, payouts and costs, and it only asks you when you have a real choice.

**You answer.** The `id` of one action.

```python
def act(observation):
    return {"action": observation["actions"][0]["id"]}
```

**You design.** Where to settle, what to build next, and how much each action is worth. You need a hand-written strategy and a value you learned, for example by playing thousands of games before the tournament.

## What applies to all four

- **Any mistake costs that game.** An illegal action, a wrong format, an exception or running out of time loses it. In Road Trip, a bad route is only ignored. The judge never fixes an answer for you.
- **Required functions.** Each file also has a few small functions with fixed names, such as `ucs`, `minimax` or `sonar_posterior`. They are listed in the templates, and `check_requirements` tests them.
- **One file per agent.** You can use the Python standard library, `numpy`, `networkx`, `chess`, and `catanatron` to simulate the rules. Ready-made engines, bots and the network are not allowed.

## Try it

1. In Colab, upload `Tournament.ipynb` and `ai_agent_tournament.zip`, then choose **Runtime > Run all**. Two example teams play a full match.
2. Copy a template from `student_templates/`, upload that `.py` to Colab and play it against an example agent:

```python
practice = run_game("chess", "chess_agent.py")   # plays an example agent
show_game(practice)                              # shows the replay
check_requirements("chess_agent.py")             # tests your required functions
```

3. For a full match, zip your four files as `Team_07.zip`, upload it and write `TEAM_A = "Team_07.zip"` in the notebook.

The complete rules for each challenge are in its `README.md`, inside `games/`. Real examples of what your agent receives are in `docs/students/sample_observations/`.
