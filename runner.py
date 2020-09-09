from classes import *
from minimax import *

depth = 3


def load_pieces():
    # generates white pieces
    wP1 = Pawn(True, (6, 0), 'wP1', 'white')
    wP2 = Pawn(True, (6, 1), 'wP2', 'white')
    wP3 = Pawn(True, (6, 2), 'wP3', 'white')
    wP4 = Pawn(True, (6, 3), 'wP4', 'white')
    wP5 = Pawn(True, (6, 4), 'wP5', 'white')
    wP6 = Pawn(True, (6, 5), 'wP6', 'white')
    wP7 = Pawn(True, (6, 6), 'wP7', 'white')
    wP8 = Pawn(True, (6, 7), 'wP8', 'white')

    wR1 = Rook(True, (7, 0), 'wR1', 'white')
    wR2 = Rook(True, (7, 7), 'wR2', 'white')

    wK1 = Knight(True, (7, 1), 'wK1', 'white')
    wK2 = Knight(True, (7, 6), 'wK2', 'white')

    wB1 = Bishop(True, (7, 2), 'wB1', 'white')
    wB2 = Bishop(True, (7, 5), 'wB2', 'white')

    wK = King(True, (7, 4), 'wK', 'white')
    wQ = Queen(True, (7, 3), 'wQ', 'white')

    # Black
    bP1 = Pawn(True, (1, 0), 'bP1', 'black')
    bP2 = Pawn(True, (1, 1), 'bP2', 'black')
    bP3 = Pawn(True, (1, 2), 'bP3', 'black')
    bP4 = Pawn(True, (1, 3), 'bP4', 'black')
    bP5 = Pawn(True, (1, 4), 'bP5', 'black')
    bP6 = Pawn(True, (1, 5), 'bP6', 'black')
    bP7 = Pawn(True, (1, 6), 'bP7', 'black')
    bP8 = Pawn(True, (1, 7), 'bP8', 'black')

    bR1 = Rook(True, (0, 0), 'bR1', 'black')
    bR2 = Rook(True, (0, 7), 'bR2', 'black')

    bK1 = Knight(True, (0, 1), 'bK1', 'black')
    bK2 = Knight(True, (0, 6), 'bK2', 'black')

    bB1 = Bishop(True, (0, 2), 'bB1', 'black')
    bB2 = Bishop(True, (0, 5), 'bB2', 'black')

    bK = King(True, (0, 4), 'bK', 'black')
    bQ = Queen(True, (0, 3), 'bQ', 'black')

    w_pieces = [wP1, wP2, wP3, wP4, wP5, wP6, wP7, wP8, wR1, wR2, wK1, wK2, wB1, wB2, wK, wQ]
    b_pieces = [bP1, bP2, bP3, bP4, bP5, bP6, bP7, bP8, bR1, bR2, bK1, bK2, bB1, bB2, bK, bQ]

    # convert into dictionary of pieces with id mapping to object
    whites = dict()
    for piece in w_pieces:
        whites[piece.id] = piece

    # convert into dictionary of pieces with id mapping to object
    blacks = dict()
    for piece in b_pieces:
        blacks[piece.id] = piece

    return whites, blacks


def main():
    whites, blacks = load_pieces()
    board = Board(whites, blacks)
    game_over = False

    # n for keeping track of whose go it is
    n = 0

    board.print()
    print()

    while not game_over:
        # check whose go it is
        if n % 2 == 0:
            print("white")
            id = input("Enter piece id: ")
            position = input("Enter new position (i,j): ")
            pos = (int(position[0]), int(position[2]))
            # id, pos = get_move(board, True, depth)
            board.push(id, pos)

        else:
            print("black")
            move = get_move(board, False, depth)
            id, pos = move
            board.push(id, pos)
        board.print()
        print()
        print()

        if board.is_checkmate() == "black":
            print("WHITE WINS")
            game_over = True
        elif board.is_checkmate() == "white":
            print("BLACK WINS")
            game_over = True
        elif board.is_stalemate():
            print("STALEMATE")
            game_over = True

        n += 1


if __name__ == "__main__":
    main()
