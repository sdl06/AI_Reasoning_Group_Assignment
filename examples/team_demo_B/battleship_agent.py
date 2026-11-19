"""Example Battleship agent: random shots, ships never move."""
import random


def act(observation):
    if observation["phase"] == "placement":
        return {"placements": None}
    size = observation["board_size"]
    return {"shot": [random.randrange(size), random.randrange(size)]}
