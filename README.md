# AI_Reasoning_Group_Assignment

## Technical explanation
 
### Battleship
 
#### Problem formulation
The enemy fleet is hidden. Each enemy ship is a variable whose value is its top left cell and orientation, so its domain is every placement that fits on the 10x10 board. The constraints are: a ship covers all of its damaged cells, no ship that can still move covers a cell that is already damaged, and a ship that has been hit never moves again. The state also changes over time, because ships that have not been hit can move one cell per turn, and only one ship per turn.
 
What we observe each turn: the result of every shot we fired (MISS, HIT, SUNK with its length, or MISS on an already damaged cell), our sonar readings, and what the rival did to our own fleet. We never see the rival's moves, its sonar or its misses.
 
What we optimise: sink all 17 segments in as few turns as possible, while making our own fleet hard to find.
 
#### Algorithms
All of this is in `battleship_agent.py`.
 
**Constraint reasoning for ships we have hit** (`consistent_placements`, `EnemyModel.target_scores`). When there are open hits (hits on ships not yet sunk), we stop guessing and reason about the ships we know are there. For every ship length still afloat, `consistent_placements` lists every placement that covers an open hit and avoids the cells of sunk ships. We then remove placements that cover a cell we missed after that ship was first hit, since a hit ship cannot move. This is forward checking on the hit ship's domain. Each remaining placement votes for the cells it covers, and placements that line up with two or more open hits get a much bigger vote (`LINE_BONUS`). We shoot the cell with the most votes.
 
What the agent knows for certain: damaged cells never change, a hit ship is frozen forever, and a SUNK result tells us the exact length of the ship that went down. When a ship sinks, `mark_sunk` finds the line of damaged cells through the last shot with that length and marks those cells as that ship.
 
**Belief filtering for ships that can move** (`Filter`, `EnemyModel.advance`, `EnemyModel.apply_shot`). When there are no open hits, we hunt using a belief for every enemy ship still afloat: the probability of each placement, stored as a numpy array of shape (2, 10, 10), one layer per orientation. Ships are treated as independent.
 
* Prior: uniform over every placement that fits and does not cover a damaged cell.
* Transition model (`spread`, the same code used by `predict_ship_belief`): with probability p the ship takes one step N, S, E or W, picked uniformly among the steps that keep it in a valid position, otherwise it stays. Since the rules let only one ship move per turn, p is the rival's move rate divided by the number of ships that can still move.
* Predict: between two of our actions the rival gets one turn, so every belief is pushed through the transition model once.
* Update after a miss: every placement covering that cell gets probability 0 (likelihood 0), then the belief is normalised.
* Update after a hit: placements of the moving ships that would overlap a damaged cell are removed.
To pick a hunting shot we combine the beliefs into the probability that each cell holds some ship, 1 minus the product over ships of (1 minus that ship's coverage), and shoot the highest.
 
**Not knowing how often the rival moves.** The transition model needs a move rate, and different rivals behave very differently: demo_b never moves, demo_a moves on about a quarter of its turns, and a careful team might move every turn. So we run three filters side by side with rates 0, 0.25 and 1 (`MOVE_RATES`). After every hunting shot each filter is weighted by how likely it said that result was (Bayes rule over the three models), and the shot is chosen from the weighted mix. Against a rival that never moves, the rate 0 filter wins the weight within a few dozen shots and old misses stay trusted. Against a rival that moves, the other filters take over and the agent comes back to cells it missed earlier. A floor on the weights (`MIN_WEIGHT`) keeps every model alive in case the rival changes behaviour.
 
**Sonar** (`sonar_posterior`, `Filter.apply_sonar`, `EnemyModel.sonar_gain`). The sensor model is in `reading_probability`: the reading equals the true count with probability 0.8, and is one lower or one higher with 0.1 each, with impossible readings removed and the rest normalised. `sonar_posterior` is the exact Bayes update on a prior over counts. Inside the agent the update goes down to placements: for each ship we compute how many of its cells each placement puts in the 3x3 window, combine the other ships' count distributions by convolution, and weight each placement by the probability of the reading given that placement. This is the exact marginal update under the independence assumption.
 
A scan is worth more than a shot when no cell is a good shot. So the agent only scans while hunting, when the best cell's hit probability is below 0.12, which happens once the fleet is spread out or only small ships are left. It picks the centre with the highest mutual information between the true count and the reading, and only scans if that gain is above 0.3 bits.
 
**Our own fleet.** `place_fleet` places ships at random but never touching, so finding one ship does not lead the rival straight onto the next. Every turn `choose_move` moves one ship if it can. It scores cells near our damaged ships as dangerous, because that is where any rival in target mode is shooting, and picks the move that most lowers the danger of the moved ship. If nothing is at risk it still makes a random move, because that makes the rival's old misses out of date.
 
#### Baseline against improved version
The baseline (a first version we kept locally, not handed in) is classic hunt and target: shoot next to recent hits, otherwise shoot checkerboard cells never tried before. It treats every miss as permanent, never moves, never scans and lets the judge place the fleet.
 
Win rates on the course judge (`run_game`, seeds 1 to 100):
* Against demo_b: baseline 100%, improved 100%.
* Against demo_a (shoots around hits, moves on a quarter of turns): baseline 16%, improved 97%.
* Improved against the baseline directly: 98 wins out of 100.
To see where this comes from we also measured, on our own copy of the rules, how many shots each version needs to sink the whole fleet against a rival that does not shoot back (200 games, capped at 150):
* Ships never move: baseline 57.0 shots, improved 44.9.
* Rival moves a ship on 25% of turns: baseline 127.2, improved 56.7.
* Rival moves a ship every turn: baseline 136.4, improved 62.5.
The baseline falls apart as soon as ships move, because once it has shot a cell it never comes back. Ablations on the same test (150 games each), averaged over the three movement rates: the full agent needs 55.0 shots, 57.7 without sonar, 58.2 with a single filter that assumes no movement and 74.3 with a single filter that assumes a rate of 0.5. In mirror matches of 200 games, moving our ships won 68% against the same agent with movement turned off, and spacing our ships out won 58% against judge placement.
 
#### Time and memory
A whole game uses about 0.15 seconds of the 5 second clock on a laptop. Each turn only pushes 3 filters times 5 ships times 2 small arrays through the transition model, and the valid placement masks are cached until a new cell is damaged. The most expensive step is choosing a sonar centre, and the agent skips sonar if less than 1 second is left. If anything unexpected raises an error, `act` catches it and returns a legal random shot instead of losing the game. Memory use is a few kilobytes.
 
#### Limits
Treating ships as independent means beliefs can put two ships on the same cells, which matters most early on. The move rate guesses are fixed, and a rival that moves only some ships, or moves them away from our shots on purpose, is not modelled. When several ships are hit next to each other, `mark_sunk` can pick the wrong cells for a sunk ship. With more time we would use a particle filter over whole fleets, which handles overlap and the one ship per turn rule exactly, and learn a better danger map for our own moves from the rival's shot pattern.

## Use of generative AI
We used AI to assist us with the development of battleship_agent.py and the structure of this README. It helped with the local test setup and the baseline comparison. We then ran the agent on the course judge, checked that all three required functions pass check_requirements, compared it against demo_a, demo_b and our baseline over 100 games each, and went through the code to make sure we can understand and explain it. All of the numbers in the README come from our own runs on the judge and are not forged.
