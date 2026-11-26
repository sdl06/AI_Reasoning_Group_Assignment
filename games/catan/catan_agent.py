"""Catan Tournament 1v1 agent. Team: AI_Reasoning_Group

Playbook: docs/students/CATAN_PLAYBOOK.md
Full rules: games/catan/README.md
Samples: docs/students/sample_observations/catan_*.json
Training: docs/students/TRAINING.md

Step 1 — interface notes (from samples + rules):
- phase: initial_placement | play_turn | move_robber | free_roads
- actions: list of {id, type, ...}; answer with {"action": <id>}
- me: victory_points, resources, settlements, cities, roads, development_cards_in_hand, ...
- opponent: visible_victory_points only (no hand); resource_cards / development_cards are counts
- board.tiles: tile [x,y,z], resource, number, nodes, edges
- board.ports: resource (null => 3:1), nodes
- log: public history; opponent BUY_DEVELOPMENT_CARD does not reveal the card
- time_remaining_s: may be None during offline training — never assume it is a float
- Forced single-action turns are played by the judge; we are only asked when there is a choice

You may not import catanatron.players. Values learned offline must live in this file.
"""
import random


def act(observation):
    """Called at each decision. Module-level variables survive between calls.

    Return {"action": <id of one action in observation["actions"]>}.
    """
    # Step 1 scaffold: legal random play. Replaced in later steps.
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
