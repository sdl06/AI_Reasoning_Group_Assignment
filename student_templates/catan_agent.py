"""Catan Tournament 1v1 agent. Team: <your team name>

Start here: docs/students/README.md
Full rules: games/catan/README.md
Examples of what you receive: docs/students/sample_observations/catan_*.json
Training offline: docs/students/TRAINING.md

The judge lists the legal actions at each decision. You answer with one action's id.
When only one action is possible the judge plays it for you, without asking.

You may not import catanatron.players or any other ready-made Catan bot. Any values
you learned before the tournament must be inside this file. Do not train from scratch during a game.

Keep the function names and signatures below. Add any helpers you need.
"""
import random


def act(observation):
    """Called at each decision. Module-level variables survive between calls.

    observation["phase"]    "initial_placement", "play_turn", "move_robber" or "free_roads"
    observation["actions"]  [{"id": 0, "type": "BUILD_ROAD", "edge": [3, 4]}, ...]
    observation["me"]       your "victory_points", "resources", "development_cards_in_hand", ...
    observation["opponent"] the rival's public facts: "visible_victory_points", "settlements", ...
    observation["board"]    "tiles" and "ports"; a tile's position is a list like [0, -1, 1]
    observation["robber_tile"], ["development_cards_left"]
    observation["building_costs"], ["vps_to_win"], ["round"], ["max_rounds"]
    observation["log"]      every public action so far
    observation["time_remaining_s"]

    Return {"action": <id of one action in observation["actions"]>}.
    """
    # TODO: replace with your policy. This placeholder chooses at random.
    return {"action": random.choice(observation["actions"])["id"]}


# ---------------------------------------------------------------------------------
# Required algorithms. check_requirements() tests these.
# ---------------------------------------------------------------------------------


def state_features(observation):
    """Your abstraction of the game state: a short list of numbers or strings.

    It must be deterministic. The same observation must give the same features, and
    different situations should give different features.
    """
    raise NotImplementedError


def action_value(observation, action_id):
    """Your estimate of how good this action is here, as a finite number.

    It should use values you learned or estimated, for example a Q-table over
    state_features(), or the average outcome of simulations.
    """
    raise NotImplementedError


def q_update(q, reward, best_next_q, alpha, gamma):
    """One Q-learning update. Returns the new value for Q(s, a)."""
    raise NotImplementedError


def heuristic_policy(observation):
    """Your baseline strategy, to compare with your advanced one. Returns a legal action id."""
    raise NotImplementedError
