"""Example Catan agent: a fixed priority list. No planning, no values, no learning."""
import random

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
PIPS = {2: 1, 3: 2, 4: 3, 5: 4, 6: 5, 8: 5, 9: 4, 10: 3, 11: 2, 12: 1}


def node_production(board):
    production = {}
    for tile in board["tiles"]:
        for node in tile["nodes"]:
            production[node] = production.get(node, 0) + PIPS.get(tile["number"], 0)
    return production


def act(observation):
    actions = observation["actions"]
    if observation["phase"] == "initial_placement" and actions[0]["type"] == "BUILD_SETTLEMENT":
        production = node_production(observation["board"])
        return {"action": max(actions, key=lambda a: production.get(a["node"], 0))["id"]}
    if observation["phase"] == "move_robber":
        stealing = [a for a in actions if a.get("steal_from") == "opponent"]
        return {"action": random.choice(stealing or actions)["id"]}
    for kind in PRIORITY:
        options = [a for a in actions if a["type"] == kind]
        if options:
            return {"action": random.choice(options)["id"]}
    return {"action": actions[0]["id"]}
