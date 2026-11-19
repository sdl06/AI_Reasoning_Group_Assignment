# Challenge: Catan Tournament 1v1

## Objective

Beat the other agent to the target number of victory points by colonising the board, gathering resources and building.

This is a two-player tournament variant, run on the open-source [Catanatron](https://github.com/bcollazo/catanatron) engine for this course's competition. It is not affiliated with or endorsed by the owners of the Catan board game.

## Differences from the traditional game

| Topic | This variant |
|---|---|
| Players | 2, on the regular 19-tile board |
| Target | **7 victory points** instead of 10 |
| Trading with the other player | Not available |
| Trading with the bank and ports | Available |
| Discarding on a 7 | Above 7 cards, half your hand is discarded **at random** by the engine |
| Forced actions | When only one action is possible, the judge plays it for you, free of charge |
| Development cards | A card can be played the turn it is bought, one per turn |
| Road Building card | Only offered if you could also afford a road at that moment |
| Limits | 99 turns each and a clock, resolved by the tiebreak below |

Everything else follows the engine's usual rules: settlements and roads placed at the start, production by dice, the robber, cities, development cards, longest road and largest army.

## Costs

| Build | Cost |
|---|---|
| Road | 1 wood, 1 brick |
| Settlement | 1 wood, 1 brick, 1 sheep, 1 wheat |
| City | 2 wheat, 3 ore |
| Development card | 1 sheep, 1 wheat, 1 ore |

## What your agent receives

The judge handles dice, payouts, building, costs, robbing and turns. At each decision it sends the legal actions.

```python
def act(observation):
    return {"action": 12}
```

| Field | Meaning |
|---|---|
| `phase` | `initial_placement`, `play_turn`, `move_robber` or `free_roads` |
| `actions` | The legal actions, each with an `id` |
| `me` | Everything about you, see below |
| `opponent` | What the table can see about the rival, see below |
| `board` | `tiles` (`tile`, `resource`, `number`, `nodes`, `edges`) and `ports` (`resource`, `nodes`). `resource: null` on a port means 3:1 |
| `robber_tile` | Where the robber is |
| `development_cards_left` | How many development cards remain |
| `building_costs`, `vps_to_win`, `round`, `max_rounds` | Game settings and progress |
| `log` | Every public action so far, including forced ones. Each entry has `player` (`"me"` or `"opponent"`), `type`, and details such as `dice`, `node`, `edge` or `tile` |
| `time_remaining_s` | Your clock |

Real examples of each kind of decision are in `docs/students/sample_observations/`: `catan_initial_placement.json`, `catan_play_turn.json` and `catan_move_robber.json`. Read them before writing code, because a misspelt key fails silently.

Values arrive as JSON. Tiles such as `tile` and `robber_tile` are lists of three cube coordinates, like `[0, -1, 1]`, and edges are lists of two node ids in increasing order. To use one as a dictionary key, convert it first: `tuple(action["tile"])`. Resource names are in capitals: `WOOD`, `BRICK`, `SHEEP`, `WHEAT`, `ORE`.

Both `me` and `opponent` have these keys:

| Key | Meaning |
|---|---|
| `visible_victory_points` | Points everyone can see, without hidden Victory Point cards |
| `settlements`, `cities` | Node ids |
| `roads` | `[[node, node], ...]` |
| `resource_cards`, `development_cards` | How many cards they hold |
| `played_development_cards` | `{"KNIGHT": 2, ...}`, counts of played cards |
| `longest_road_length`, `has_longest_road`, `has_largest_army` | Bonus status |

`me` also has:

| Key | Meaning |
|---|---|
| `victory_points` | Your real total, including hidden cards |
| `resources` | `{"WOOD": 1, "BRICK": 0, "SHEEP": 2, "WHEAT": 0, "ORE": 1}` |
| `development_cards_in_hand` | `{"KNIGHT": 1, "YEAR_OF_PLENTY": 0, "MONOPOLY": 0, "ROAD_BUILDING": 0, "VICTORY_POINT": 0}` |

Each `log` entry has `player` and `type`, plus:

| `type` | Extra keys |
|---|---|
| `ROLL` | `dice`, as `[a, b]` |
| `BUILD_SETTLEMENT`, `BUILD_CITY` | `node` |
| `BUILD_ROAD` | `edge` |
| `MOVE_ROBBER` | `tile`, `stole_from` (`"me"`, `"opponent"` or `null`), and `stolen_resource` when a card was stolen |
| `BUY_DEVELOPMENT_CARD` | `card`, only if you bought it |
| `DISCARD` | `count`, and `cards` only if they were yours |
| `MARITIME_TRADE` | `give`, `give_count`, `receive` |
| `PLAY_YEAR_OF_PLENTY` | `resources` |
| `PLAY_MONOPOLY` | `resource` |
| `PLAY_KNIGHT_CARD`, `PLAY_ROAD_BUILDING`, `END_TURN` | None |

**You are never given the rival's hand or development cards.** The log shows that the rival bought a card, not which one, and you see how many cards it discarded, not which. You may work out the rest of its hand yourself from public events such as dice and buildings, as a player at the table could.

## Actions

Each action has an `id` and a `type`, plus:

| `type` | Extra fields |
|---|---|
| `BUILD_SETTLEMENT`, `BUILD_CITY` | `node` |
| `BUILD_ROAD` | `edge`, as `[node, node]` |
| `MOVE_ROBBER` | `tile`, `steal_from` (`"opponent"` or `null`) |
| `MARITIME_TRADE` | `give`, `give_count`, `receive` |
| `PLAY_YEAR_OF_PLENTY` | `resources` |
| `PLAY_MONOPOLY` | `resource` |
| `ROLL`, `END_TURN`, `BUY_DEVELOPMENT_CARD`, `PLAY_KNIGHT_CARD`, `PLAY_ROAD_BUILDING` | None |

Return `{"action": <id>}`. An id that is not in the list loses the game.

## Time and limits

- Each player has **5 seconds of decision time**. The whole challenge is limited to **60 seconds**.
- The game stops after **99 turns each** or 3,000 decisions in total. The placement phase takes up the rest of the first round, so `round` reaches `max_rounds` (100) after 99 turns each.
- The seed decides the board and who starts.

## Winning

The first player to reach 7 victory points wins. If a limit is reached first, the judge compares, in this order:

1. Victory points, including hidden ones.
2. Number of cities.
3. Number of settlements.
4. Number of resource cards in hand.
5. If still equal, a draw.

An illegal action, wrong format, exception, crash, or running out of your own clock loses the game.

## Required algorithms

This challenge focuses on planning, utility and learning: representing states, preconditions and effects, immediate against future rewards, expectations under uncertainty, Markov decision processes, policies and reinforcement learning.

You must implement a baseline heuristic strategy and compare it with a more advanced one, and you must have an explicit learned or estimated value for states and actions, for example Q-learning over a small state abstraction.

You do not need a complete MDP of the whole game. A simplified abstraction is allowed if it is explicit and you can defend it.

You may train **before** the tournament and store the values in your `.py`. `docs/students/TRAINING.md` has a working loop for playing thousands of games offline. You may not train from scratch during a match or download a model. You may add search, Monte Carlo simulation and other techniques. You may import `catanatron` to simulate the rules, but `catanatron.players` is rejected automatically.

## Testing your agent

```python
practice = run_game("catan", "catan_agent.py", opponent="demo")
show_game(practice)
check_requirements("catan_agent.py")
```

Template: `student_templates/catan_agent.py`. A working example, a fixed priority list: `examples/team_demo_A/catan_agent.py`.
