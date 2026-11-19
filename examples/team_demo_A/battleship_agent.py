"""Example Battleship agent: shoots at random, then around any hit. No probabilities."""
import random


def act(observation):
    if observation["phase"] == "placement":
        return {"placements": None}  # the judge places the fleet at random

    size = observation["board_size"]
    shots = observation["my_shots"]
    tried = {tuple(shot["target"]) for shot in shots}
    hits = [tuple(shot["target"]) for shot in shots if shot["result"] in ("HIT", "SUNK")]

    # A damaged ship can no longer move, so the cells around a hit stay interesting.
    near_hits = [
        (row + dr, col + dc)
        for row, col in hits
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1))
        if 0 <= row + dr < size and 0 <= col + dc < size and (row + dr, col + dc) not in tried
    ]
    if near_hits:
        target = random.choice(near_hits)
    else:
        untried = [(r, c) for r in range(size) for c in range(size) if (r, c) not in tried]
        # Earlier misses are not proof of anything, because ships move.
        target = random.choice(untried) if untried else (random.randrange(size), random.randrange(size))

    moves = observation["legal_moves"]
    move = random.choice(moves) if moves and random.random() < 0.25 else None
    return {"move": move, "shot": list(target)}
