"""Example Chess agent: looks one move ahead and counts material. No search at all."""
import random

import chess

VALUES = {chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3, chess.ROOK: 5, chess.QUEEN: 9, chess.KING: 0}


def material(board, color):
    return sum(VALUES[piece.piece_type] * (1 if piece.color == color else -1) for piece in board.piece_map().values())


def act(observation):
    board = chess.Board(observation["fen"])
    me = board.turn
    best_moves, best_score = [], None
    for uci in observation["legal_moves"]:
        board.push_uci(uci)
        score = 1000 if board.is_checkmate() else material(board, me)
        board.pop()
        if best_score is None or score > best_score:
            best_moves, best_score = [uci], score
        elif score == best_score:
            best_moves.append(uci)
    return {"move": random.choice(best_moves)}
