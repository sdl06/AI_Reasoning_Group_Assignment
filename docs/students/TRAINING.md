# Training your Catan agent before the tournament

You may learn values offline and store them inside `catan_agent.py`. To do that you need to play many games quickly. The code below plays Catan in your own process, with the same observations and the same action ids the judge uses, so a policy you train here works unchanged in `act`.

Run it from the folder where the zip was extracted. In Colab that is `/content/ai_agent_tournament`, which is already the current folder after cell 1 of the notebook.

```python
import random

from games.catan.engine import SIDE_OF, adjudicate, legal_actions, new_game, observation_for, victory_points


def play_one_game(policy_a, policy_b, seed, on_decision=None):
    """Plays a whole game. A policy takes an observation and returns an action id.

    on_decision(side, observation, action_id) is called at every decision, so you
    can record what happened. Returns the winner ("A", "B" or None for a draw) and
    the points, like {"A": 7, "B": 2}, with the same result the judge would give.
    Use a positive seed: with 0, the engine picks a random game.
    """
    game = new_game(seed, vps_to_win=7)
    policies = {"A": policy_a, "B": policy_b}
    while game.winning_color() is None and game.state.num_turns // 2 < 100:
        actions = legal_actions(game)
        if len(actions) == 1:
            game.execute(actions[0])  # the judge plays forced actions for you
            continue
        side = SIDE_OF[game.state.current_color()]
        observation = observation_for(game, side, actions, None, {"max_rounds": 100})
        action_id = policies[side](observation)
        if on_decision is not None:
            on_decision(side, observation, action_id)
        game.execute(actions[action_id])
    champion = game.winning_color()
    winner = SIDE_OF[champion] if champion is not None else adjudicate(game)[0]
    return winner, victory_points(game)


rng = random.Random(1)  # use your own generator: new_game() reseeds Python's global random


def random_policy(observation):
    return rng.choice(observation["actions"])["id"]


wins = {"A": 0, "B": 0, None: 0}
for seed in range(1, 21):
    winner, points = play_one_game(random_policy, random_policy, seed)
    wins[winner] += 1
print(wins)
```

## What to expect

- **Speed.** A game between simple policies takes between 0.03 and 0.25 seconds, depending on the machine, plus the time your own policy needs. So 1,000 games take from under a minute to a few minutes. Colab may be slower.
- **How many games.** A tabular method over a small state needs thousands of games before its table says anything reliable. Evaluate on seeds you did not train on, over at least 500 games, because Catan has a lot of luck and fewer games mostly measure noise.
- **Rewards.** Points gained between your decisions are a natural intermediate reward: compare `observation["me"]["victory_points"]` between decisions. Your last decision has no next observation, because `on_decision` does not fire when the game ends. Close that last step using what `play_one_game` returns.
- **Which player goes first.** The seed decides it, so play both sides or average over many seeds.

## Differences from a real match

- There are no clocks here, and `time_remaining_s` is `None` in these observations. Your agent must not assume it is a number when you train this way. A slow policy is fine here but can lose on time in a match.
- Your agent is in the same process as the game. Do not read anything except the observation, because the real judge only gives you the observation.
- Training against `catanatron.players` is fine, though its bots are simple and work on the game object, not on an observation. Importing it in the `catan_agent.py` you hand in is rejected.

## Your learned table against your baseline

Do not assume learning helps. A table can easily turn out worse than a good hand-written baseline, and the required checks only test that your functions work, not that they win. Measure it, and compete with whichever is better. The comparison is part of what you explain, whichever way it comes out.

## Moving your table into the agent

Your agent must be a single file, so the table goes inside it. Tables are too large to paste by hand, so have your training script write the line for you, then copy it into `catan_agent.py`:

```python
table = {"('play_turn', 3, 2)|BUILD_CITY": 0.81}  # what your training produced
with open("q_table_line.py", "w") as f:
    f.write(f"Q = {table!r}\n")
```

A table of a few hundred kilobytes is fine, as long as your file loads within the 15-second limit. Use the same `state_features` function in training and in the agent, so the keys match.
