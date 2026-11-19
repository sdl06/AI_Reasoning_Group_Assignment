"""Battleship agent. Team: <your team name>

Start here: docs/students/README.md
Full rules: games/battleship/README.md
Examples of what you receive: docs/students/sample_observations/battleship_placement.json and battleship_turn.json

Ships can move one cell per turn until they take their first hit, so an old miss
proves nothing about where a ship is now. Cells are [row, col], with row 0 at the top.
North is row - 1 and east is col + 1.

Keep the function names and signatures below. Add any helpers you need.
"""
import random


def act(observation):
    """Called once for placement, then once per turn. Module-level variables survive.

    Placement phase, observation["phase"] == "placement":
        observation["board_size"], observation["fleet"] = [{"ship", "length"}, ...]
        Return {"placements": [{"ship": "carrier", "row": 0, "col": 0, "orientation": "H"}, ...]}
        with one entry per ship, or {"placements": None} to let the judge place at random.

    Turn phase, observation["phase"] == "turn":
        observation["my_ships"]         [{"ship", "length", "orientation", "cells",
                                          "damaged_cells", "immobile", "sunk"}, ...]
        observation["legal_moves"]      [{"ship", "direction"}, ...]
        observation["my_shots"]         [{"turn", "target", "result"}, ...]
        observation["my_sonar"]         [{"turn", "center", "reading"}, ...]
        observation["sonar_remaining"]  uses left
        observation["enemy_ships_sunk"] lengths of enemy ships you have sunk
        observation["damage_received"]  hits your own fleet has taken
        observation["turn"], ["max_rounds"], ["time_remaining_s"]

        Return {"shot": [row, col]} or {"sonar": [row, col]}.
        To move a ship as well, add "move": <one entry of legal_moves>.
    """
    if observation["phase"] == "placement":
        return {"placements": None}
    # TODO: replace with your inference. This placeholder shoots at random and never moves.
    size = observation["board_size"]
    return {"shot": [random.randrange(size), random.randrange(size)]}


# ---------------------------------------------------------------------------------
# Required algorithms. check_requirements() tests these.
# ---------------------------------------------------------------------------------


def consistent_placements(length, board_size, blocked, required):
    """Every position of one ship consistent with the evidence.

    blocked   cells the ship cannot occupy, as [[row, col], ...]
    required  cells the ship must cover, as [[row, col], ...]

    Returns [[row, col, "H" or "V"], ...], where [row, col] is the ship's top-left cell,
    in any order and without duplicates. Length is always at least 2.
    """
    raise NotImplementedError


def sonar_posterior(prior, reading, region_cells, correct_probability):
    """Bayes' rule: P(true count | sonar reading).

    prior  {"0": 0.5, "1": 0.3, ...}, a probability for each true count (keys are strings,
           and never above region_cells)
    reading  the number the sonar returned
    region_cells  how many cells the sonar covered, which is the largest possible reading

    Sensor model: the reading equals the true count with correct_probability, and is
    one lower or one higher with the remaining probability split equally. A reading
    outside 0..region_cells is impossible, so the other outcomes are renormalised.

    Returns {"0": p0, "1": p1, ...}, the posterior over the same keys.
    """
    raise NotImplementedError


def predict_ship_belief(belief, length, orientation, move_probability):
    """One prediction step of a belief filter for one unseen ship.

    belief[row][col] = P(the ship's top-left cell is [row, col]), on a square board.

    Transition model used here: with move_probability the ship moves one cell, chosen
    uniformly among the directions where it stays on the board. Otherwise it stays
    put. A ship with no legal direction always stays put.

    Returns the new belief, with the same shape.
    """
    raise NotImplementedError
