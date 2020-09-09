from classes import Board
from runner import *
import sys
import time

depth = 3

whites, blacks = load_pieces()
board = Board(whites, blacks)


def addBoard():
    # add board to board_states
    flattened_board = [piece.id if piece is not None else None for row in board.board for piece in
                       row]
    flattened_board = tuple(flattened_board)
    if flattened_board in board.board_states.keys():
        board.board_states[flattened_board] += 1
    else:
        board.board_states[flattened_board] = 1

# board.push()

board.print()

print(board.evaluate())

sys.exit()

game_over = False

# n for keeping track of whose go it is
n = 0

# get them to play each other til checkmate
while not game_over:
    # check whose go it is
    if n % 2 == 0:
        print("white")
        # id = input("Enter piece id: ")
        # position = input("Enter new position (i,j): ")
        # pos = (int(position[0]), int(position[2]))
        id, pos = get_move(board, True, depth)
        print(id, pos)
        board.push(id, pos)

    else:
        print("black")
        id, pos = get_move(board, False, depth)
        print(id, pos)
        board.push(id, pos)
    board.print()

    if board.is_checkmate() == "black":
        print("WHITE WINS")
        game_over = True
    elif board.is_checkmate() == "white":
        game_over = True
    elif board.is_stalemate():
        print("STALEMATE")
        game_over = True

    n += 1
