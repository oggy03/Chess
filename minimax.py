from classes import *
import sys

INFINITY = 100000000000000000000000000000000000000000000


def minimax(board, depth, isMaximizingPlayer, alpha, beta):
    if depth == 0 or board.is_terminal():
        return board.evaluate()

    if isMaximizingPlayer:
        best_val = -1 * INFINITY
        moves = board.get_all_moves_w()
        for move in moves:
            id = move[0]
            pos = move[1]
            try:
                board.push(id, pos)
            except:
                print(f"there was an error trying to do move: {move} on board:")
                board.print()
            value = minimax(board, depth - 1, False, alpha, beta)
            board.undo()
            best_val = max(best_val, value)
            alpha = max(alpha, best_val)
            if beta <= alpha:
                break
        return best_val

    else:
        best_val = INFINITY
        moves = board.get_all_moves_b()
        for move in moves:
            id = move[0]
            pos = move[1]
            try:
                board.push(id, pos)
            except:
                print(f"there was an error trying to do move: {move} on board:")
                board.print()
                sys.exit()
            value = minimax(board, depth - 1, True, alpha, beta)
            board.undo()
            best_val = min(best_val, value)
            beta = min(beta, best_val)
            if beta <= alpha:
                break
        return best_val


def get_move(board, isMaximising, depth):
    """

    :param depth:
    :param board: board object
    :param isMaximising: True or False depending on black or white
    :return: best_move in form (id, (i, j))
    """
    # white
    if isMaximising:
        best_val = -1 * INFINITY
        pos_moves = board.get_all_moves_w()
        for move in pos_moves:
            id = move[0]
            pos = move[1]
            # print(id, move)
            board.push(id, pos)
            board_val = minimax(board=board, depth=depth - 1, isMaximizingPlayer=False, alpha=-1 * INFINITY,
                                beta=INFINITY)
            # print("value after move:", board_val)
            board.undo()
            if board_val > best_val:
                best_move = move
                best_val = board_val
    # black
    else:
        best_val = INFINITY
        pos_moves = board.get_all_moves_b()
        # pos_moves = [("bB2", (3, 2)), ("bQ", (4, 7))]
        for move in pos_moves:
            id = move[0]
            pos = move[1]

            # debugging
            # print(id, move)

            board.push(id, pos)
            board_val = minimax(board=board, depth=1, isMaximizingPlayer=True, alpha=-1 * INFINITY, beta=INFINITY)
            # print("value after move:", board_val)
            board.undo()
            if board_val < best_val:
                best_move = move
                best_val = board_val

    return best_move
