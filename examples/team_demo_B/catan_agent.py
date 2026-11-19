"""Example Catan agent: any legal action at random."""
import random


def act(observation):
    return {"action": random.choice(observation["actions"])["id"]}
