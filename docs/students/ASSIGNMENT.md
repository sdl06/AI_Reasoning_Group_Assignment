# Assignment: what you must implement

The goal is not only to win. You must show that you can apply what the course teaches.

## Required algorithms

Each agent file has small functions with fixed names, which the judge tests automatically against answers it computes on its own. Your competing agent may produce its moves another way, but these implementations must be real and must work.

Run this as often as you like:

```python
check_requirements("Team_07.zip")
```

| Challenge | Function | What is checked |
|---|---|---|
| Road Trip | `ucs(graph, start, goal)` | Finds the shortest path on real city pairs |
| Road Trip | `astar(graph, start, goal)` | Finds the same distance as UCS, expanding no more nodes in total over the test pairs |
| Road Trip | `local_search(tour, distance, time_limit_s)` | Shortens a random tour and returns a valid reordering |
| Chess | `evaluate(fen)` | Finite score from White's point of view that ranks material correctly |
| Chess | `minimax(fen, depth)` and `alphabeta(fen, depth)` | Same value, alpha-beta visits fewer nodes |
| Chess | `alphabeta(fen, depth)` | Deeper searches visit more nodes |
| Battleship | `consistent_placements(length, board_size, blocked, required)` | Every placement consistent with the evidence, and no others |
| Battleship | `sonar_posterior(prior, reading, region_cells, correct_probability)` | Exact Bayes update using the published sensor model |
| Battleship | `predict_ship_belief(belief, length, orientation, move_probability)` | Correct prediction step through a transition model |
| Catan | `state_features(observation)` | Deterministic abstraction that distinguishes situations |
| Catan | `action_value(observation, action_id)` | Finite value for legal actions |
| Catan | `q_update(q, reward, best_next_q, alpha, gamma)` | The Q-learning update rule |
| Catan | `heuristic_policy(observation)` | A baseline that always returns a legal action |

### What the checks use

Each call has a 30-second limit.

| Function | Test |
|---|---|
| `ucs`, `astar` | 8 pairs of cities on the real map |
| `local_search` | A random tour of 12 cities with straight-line distances, and `time_limit_s` of 3 |
| `evaluate` | 3 positions: level, White a queen up, Black a queen up |
| `minimax`, `alphabeta` | Depth 2 on 4 positions, with values compared to within 0.000001 |
| `alphabeta` | Depth 1 against depth 2 on one position |
| `consistent_placements` | 4 sets of constraints, in any order |
| `sonar_posterior` | 3 cases, to within 0.0001 |
| `predict_ship_belief` | One 6 x 6 belief, for a horizontal ship of length 2 |
| `state_features` | 6 real observations: the same one must give the same features, and at least 2 of them must differ |
| `action_value`, `heuristic_policy` | The same observations |

### What the checks do not show

Passing means your functions work. It does not mean your agent uses them, or that your agent is any good. `action_value` passes with an empty table, so the checks cannot tell a table you really learned from an invented one, or a useful table from a harmful one. That is judged from your technical explanation and your comparison between versions.

## What each challenge asks you to explain

**Road Trip.** Your formal problem and graph representation. How UCS or Dijkstra and A\* work on it, and why straight-line distance is a valid heuristic. How your agent finds a valid route without passing through any city twice. Which optimisation method you use (hill climbing, simulated annealing, a genetic algorithm, 2-opt, dynamic programming, or a hybrid). A comparison between a first strategy and your improved one.

**Chess.** Which features your evaluation uses. How you choose the depth. How alpha-beta pruning is applied. What you do when time is running out. Optional extensions: Monte Carlo Tree Search, move ordering, iterative deepening, transposition tables.

**Battleship.** How you represent partial information and the constraints on hidden positions. How evidence updates your beliefs. Your transition model for at least one unseen ship, and your belief-filtering procedure. Remember that your transition model is an estimate: a rival has its own strategy and need not move at random. Optional extension: hidden Markov models and particle filtering.

**Catan.** Your baseline heuristic strategy and a more advanced one, compared. How you plan with actions, their preconditions and their effects, and what your agent can deduce with certainty from public events. Which variables define your state, which actions you consider, how you set rewards, and how you build your policy. You must have an explicit learned or estimated value for states or actions, for example Q-learning over a small abstraction. You do not need a complete MDP of the whole game. A simplified one is fine, as long as it is explicit and you can defend it. You may train before the tournament and store the values in your `.py`, but you may not train from scratch during a match. [TRAINING.md](TRAINING.md) has a working loop for playing thousands of games offline.

## Course topics by challenge

| Block | Challenge | Required or optional | Automatic check | You must explain |
|---|---|---|---|---|
| Agents and problem formulation | All | Required | Agents play legally | Your agent, its environment and its problem formulation |
| Uninformed search, UCS, A\*, heuristics | Road Trip | Required | `ucs`, `astar` | Optimality, and why the heuristic is admissible |
| Local search and optimization | Road Trip | Required | `local_search` | Neighbourhood, acceptance rule, how you escape local optima |
| CSPs, backtracking and propagation | Battleship | Required | `consistent_placements` | Variables, domains and constraints |
| Logic and inference | Battleship, Catan | Required | None | What your agent can deduce with certainty |
| Classical planning | Catan | Required | None | Preconditions and effects of the actions you plan with |
| Minimax and alpha-beta | Chess | Required | `minimax`, `alphabeta` | How and why pruning preserves the value |
| Evaluation functions | Chess | Required | `evaluate` | Your features and their weights |
| Stochastic games and expectiminimax | Catan | Optional | None | How you handle dice and hidden cards |
| Monte Carlo Tree Search | Chess, Catan | Optional | None | Selection, expansion, simulation and backpropagation |
| Hidden information | Battleship | Required | None | How your agent acts on what it cannot see |
| MDPs and value functions | Catan | Required | `action_value`, `state_features` | States, actions, rewards and your abstraction |
| Reinforcement learning | Catan | Required | `q_update` | How you trained, and what you learned |
| Probability and Bayesian inference | Battleship | Required | `sonar_posterior` | Your prior, likelihood and posterior |
| Decision theory and value of information | Catan, Battleship | Optional | None | When a sonar scan is worth more than a shot |
| HMMs and particle filtering | Battleship | Optional extension | `predict_ship_belief` covers the prediction step | Your transition and observation models |

## Technical explanation template

Add this to your team's `README.md`, about one page per challenge.

```markdown
# <Team> technical explanation

## <Challenge>
### Problem formulation
States, actions, what the agent observes, and what it optimises.

### Algorithms
What you implemented, and where in the file. Why you chose them.

### Baseline against improved version
What you compared, on which test, and the numbers you got.

### Time and memory
How your agent uses its clock, and what it does when time runs short.

### Limits
What your agent does badly, and what you would do with more time.
```

## Use of generative AI

Follow the course's AI policy. Acknowledge any use of generative AI in your `README.md`, and make sure you can explain every algorithm yourself.
