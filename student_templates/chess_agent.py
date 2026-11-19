"""Chess agent. Team: <your team name>

Start here: docs/students/README.md
Full rules: games/chess/README.md
Example of what you receive: docs/students/sample_observations/chess.json

You may use python-chess (`import chess`) to represent the board and generate moves.
You may not use chess.engine, Stockfish or any other existing chess engine.

Keep the function names and signatures below. Add any helpers you need.
"""
import random


def act(observation):
    """Called once per move. Module-level variables survive between calls within a game.

    observation["fen"]                        the position
    observation["color"]                      "white" or "black"
    observation["legal_moves"]                legal moves in UCI, for example "e2e4"
    observation["history"]                    every move so far in UCI
    observation["ply"], ["is_check"]          public game state
    observation["game_number"], ["games_total"]
    observation["time_remaining_s"]           your clock (losing on time loses the game)
    observation["opponent_time_remaining_s"]  the rival's clock

    Return {"move": "e2e4"}, or {"move": "resign"} to resign.
    """
    # TODO: replace with your search. This placeholder plays at random.
    return {"move": random.choice(observation["legal_moves"])}


# ---------------------------------------------------------------------------------
# Required algorithms. check_requirements() tests these.
# ---------------------------------------------------------------------------------


def evaluate(fen):
    """Heuristic score of a position, from White's point of view (higher favours White).

    It must always return a finite number. For a finished game, use a large score for
    checkmate and 0 for a draw.
    """
    raise NotImplementedError


def minimax(fen, depth):
    """Plain minimax to a fixed depth, scoring leaf positions with evaluate().

    A leaf is a position at depth 0 or a finished game. Count every position you visit,
    including the root. Returns {"value": score, "nodes": positions_visited}.
    """
    raise NotImplementedError


def alphabeta(fen, depth):
    """The same search with alpha-beta pruning.

    Returns {"value": score, "nodes": positions_visited}. The value must equal minimax's.
    """
    raise NotImplementedError
