"""Example Chess agent: any legal move at random."""
import random


def act(observation):
    return {"move": random.choice(observation["legal_moves"])}
