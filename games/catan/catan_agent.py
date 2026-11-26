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

# Learned Q-table is filled in Step 5 (offline training). Key: "features|ACTION_TYPE".
Q = {}

PIPS = {2: 1, 3: 2, 4: 3, 5: 4, 6: 5, 8: 5, 9: 4, 10: 3, 11: 2, 12: 1}

PRIORITY = [
    "BUILD_CITY",
    "BUILD_SETTLEMENT",
    "BUY_DEVELOPMENT_CARD",
    "PLAY_KNIGHT_CARD",
    "PLAY_YEAR_OF_PLENTY",
    "PLAY_MONOPOLY",
    "PLAY_ROAD_BUILDING",
    "BUILD_ROAD",
    "MARITIME_TRADE",
    "ROLL",
    "MOVE_ROBBER",
    "END_TURN",
]


def act(observation):
    """Called at each decision. Module-level variables survive between calls.

    Return {"action": <id of one action in observation["actions"]>}.
    """
    # Step 2: use the baseline heuristic (advanced act comes in later steps).
    return {"action": heuristic_policy(observation)}


# ---------------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------------


def _vp_bucket(vp):
    if vp <= 2:
        return 0
    if vp <= 4:
        return 1
    if vp <= 6:
        return 2
    return 3


def _hand_bucket(n):
    if n <= 3:
        return 0
    if n <= 7:
        return 1
    return 2


def _resource_shape(resources):
    road = resources.get("WOOD", 0) + resources.get("BRICK", 0)
    city = resources.get("WHEAT", 0) + resources.get("ORE", 0)
    if road >= city + 2:
        return "road"
    if city >= road + 2:
        return "city"
    return "mixed"


def _action_types(observation):
    return {a["type"] for a in observation["actions"]}


def _node_production(board):
    production = {}
    for tile in board["tiles"]:
        for node in tile["nodes"]:
            production[node] = production.get(node, 0) + PIPS.get(tile.get("number"), 0)
    return production


def _q_key(features, action_type):
    return f"{features}|{action_type}"


def _action_by_id(observation, action_id):
    for action in observation["actions"]:
        if action["id"] == action_id:
            return action
    return None


# ---------------------------------------------------------------------------------
# Required algorithms. check_requirements() tests these.
# ---------------------------------------------------------------------------------


def state_features(observation):
    """Coarse, deterministic abstraction for tabular Q-learning."""
    me = observation["me"]
    opp = observation["opponent"]
    types = _action_types(observation)
    resources = me.get("resources") or {}
    return [
        observation.get("phase", "?"),
        _vp_bucket(me.get("victory_points", me.get("visible_victory_points", 0))),
        _vp_bucket(opp.get("visible_victory_points", 0)),
        int("BUILD_CITY" in types),
        int("BUILD_SETTLEMENT" in types),
        int("BUILD_ROAD" in types),
        int("BUY_DEVELOPMENT_CARD" in types),
        _resource_shape(resources),
        _hand_bucket(me.get("resource_cards", sum(resources.values()) if resources else 0)),
    ]


def action_value(observation, action_id):
    """Q-table lookup by state features + action type; missing keys are 0.0."""
    action = _action_by_id(observation, action_id)
    if action is None:
        return 0.0
    key = _q_key(state_features(observation), action["type"])
    return float(Q.get(key, 0.0))


def q_update(q, reward, best_next_q, alpha, gamma):
    """One Q-learning update. Returns the new value for Q(s, a)."""
    return q + alpha * (reward + gamma * best_next_q - q)


def heuristic_policy(observation):
    """Baseline priority policy. Always returns a legal action id."""
    actions = observation["actions"]
    if not actions:
        raise ValueError("no legal actions")

    phase = observation.get("phase")
    if phase == "initial_placement" and actions[0]["type"] == "BUILD_SETTLEMENT":
        production = _node_production(observation["board"])
        return max(actions, key=lambda a: production.get(a["node"], 0))["id"]

    if phase == "move_robber":
        stealing = [a for a in actions if a.get("steal_from") == "opponent"]
        return random.choice(stealing or actions)["id"]

    for kind in PRIORITY:
        options = [a for a in actions if a["type"] == kind]
        if options:
            if kind in ("BUILD_SETTLEMENT", "BUILD_CITY"):
                production = _node_production(observation["board"])
                return max(options, key=lambda a: production.get(a.get("node"), 0))["id"]
            return random.choice(options)["id"]

    return actions[0]["id"]
