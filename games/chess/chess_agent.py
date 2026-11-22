"""Chess agent. Team: <your team name>

Start here: docs/students/README.md
Full rules: games/chess/README.md
Example of what you receive: docs/students/sample_observations/chess.json

You may use python-chess (`import chess`) to represent the board and generate moves.
You may not use chess.engine, Stockfish or any other existing chess engine.

Keep the function names and signatures below. Add any helpers you need.
"""
import chess

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
    board = chess.Board(observation["fen"])
    _, _, move = _alphabeta(board, 2, float("-inf"), float("inf"))
    return {"move": move.uci()} if move is not None else {"move": "resign"}



# ---------------------------------------------------------------------------------
# Required algorithms. check_requirements() tests these.
# ---------------------------------------------------------------------------------


PIECE_VALUES = {
    chess.PAWN: 1,
    chess.KNIGHT: 3,
    chess.BISHOP: 3,
    chess.ROOK: 5,
    chess.QUEEN: 9,
    chess.KING: 0,
}
CENTER_SQUARES = {chess.D4, chess.E4, chess.D5, chess.E5}
CENTER_BONUS = 0.1


def evaluate(fen):
    """Heuristic score of a position, from White's point of view (higher favours White).

    It must always return a finite number. For a finished game, use a large score for
    checkmate and 0 for a draw.
    """
    board = chess.Board(fen)
    terminal_score = _terminal_score(board)
    if terminal_score is not None:
        return terminal_score
    return _evaluate_material_and_center(board)


def _terminal_score(board):
    outcome = board.outcome()
    if outcome is not None:
        if outcome.winner is None:
            return 0
        return 100_000 if outcome.winner == chess.WHITE else -100_000
    if board.halfmove_clock >= 100 or board.is_repetition(3):
        return 0
    return None


def _evaluate_material_and_center(board):
    material = 0
    center_count = 0
    for square, piece in board.piece_map().items():
        sign = 1 if piece.color == chess.WHITE else -1
        material += sign * PIECE_VALUES[piece.piece_type]
        if square in CENTER_SQUARES and piece.piece_type in (chess.PAWN, chess.KNIGHT):
            center_count += sign
    return material + CENTER_BONUS * center_count


def minimax(fen, depth):
    """Plain minimax to a fixed depth, scoring leaf positions with evaluate().

    A leaf is a position at depth 0 or a finished game. Count every position you visit,
    including the root. Returns {"value": score, "nodes": positions_visited}.
    """
    value, nodes = _minimax(chess.Board(fen), depth)
    return {"value": value, "nodes": nodes}


def _minimax(board, depth):
    terminal_score = _terminal_score(board)
    if terminal_score is not None:
        return terminal_score, 1
    if depth == 0:
        return _evaluate_material_and_center(board), 1

    white_to_move = board.turn == chess.WHITE
    best = float("-inf") if white_to_move else float("inf")
    choose = max if white_to_move else min
    nodes = 1
    for move in list(board.legal_moves):
        board.push(move)
        score, child_nodes = _minimax(board, depth - 1)
        board.pop()
        nodes += child_nodes
        best = choose(best, score)
    return best, nodes


def alphabeta(fen, depth):
    """Return the minimax value and number of nodes visited with pruning."""
    value, nodes, _ = _alphabeta(chess.Board(fen), depth, float("-inf"), float("inf"))
    return {"value": value, "nodes": nodes}


def _alphabeta(board, depth, alpha, beta):
    """Return the score, visited node count, and best move at this node."""
    terminal_score = _terminal_score(board)
    if terminal_score is not None:
        return terminal_score, 1, None
    if depth == 0:
        return _evaluate_material_and_center(board), 1, None

    white_to_move = board.turn == chess.WHITE
    best = float("-inf") if white_to_move else float("inf")
    best_move = None
    nodes = 1

    for move in list(board.legal_moves):
        board.push(move)
        score, child_nodes, _ = _alphabeta(board, depth - 1, alpha, beta)
        board.pop()
        nodes += child_nodes

        if white_to_move:
            if score > best:
                best, best_move = score, move
            alpha = max(alpha, best)
        else:
            if score < best:
                best, best_move = score, move
            beta = min(beta, best)
        if alpha >= beta:
            break

    return best, nodes, best_move
