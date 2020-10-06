from collections import deque
import sys

check_checked = False

# TODO CASTLING, EN PASSANT AND PROMOTIONS
class Board:
    def __init__(self, w_pieces, b_pieces):
        # set up stack data structure (last in, first out) for storing all moves that have been made
        # functions that use move_stack: is_stalemate, undo, push
        self.move_stack = deque()

        # taken pieces
        self.taken_whites = deque()
        self.taken_blacks = deque()

        self.board = [[None, None, None, None, None, None, None, None],
                      [None, None, None, None, None, None, None, None],
                      [None, None, None, None, None, None, None, None],
                      [None, None, None, None, None, None, None, None],
                      [None, None, None, None, None, None, None, None],
                      [None, None, None, None, None, None, None, None],
                      [None, None, None, None, None, None, None, None],
                      [None, None, None, None, None, None, None, None]
                      ]

        # dictionaries of white and black pieces with id mapping to piece objects
        self.whites = w_pieces
        self.blacks = b_pieces

        # Places white pieces on the board
        for piece in self.whites.values():
            i, j = piece.position
            self.board[i][j] = piece

        # Places black pieces on the board
        for piece in self.blacks.values():
            i, j = piece.position
            self.board[i][j] = piece

        # dictionary of all states board has been in mapping to number of times (for stalemate)
        self.board_states = dict()

    def print(self):
        """
        method to print a text based version of board
        :return: none
        """
        # iterate through pieces row by row
        for row in self.board:
            for piece in row:
                if piece is None:
                    print(0, end="  |  ")
                else:
                    # print id of piece
                    print(piece.id, end=" | ")
            print("\n----------------------------------------------")

    def can_be_eaten_w(self, position):
        """
        tests if a white piece can be taken
        :return: True or False and id of checking pieces
        """

        attacked = False
        attacking_pieces = []

        # test if any black pieces can move into white piece's current position
        for name, piece in self.blacks.items():
            if name != "bK":
                if position in piece.get_moves(self):
                    attacked = True
                    attacking_pieces.append(name)

        return attacked, attacking_pieces

    def can_be_eaten_b(self, position):
        """
        tests if black a black piece can be taken
        :return: True or False and a list of the checking pieces or an empty list
        """

        attacked = False
        attacking_pieces = []

        # test if any white pieces can move in black's current position
        for name, piece in self.whites.items():
            if name != "wK":
                if position in piece.get_moves(self):
                    attacked = True
                    attacking_pieces.append(name)

        return attacked, attacking_pieces

    def check(self, position):
        """
        Turns out we need an additional check function to avoid problems with recursion
        Could be a better solution but this will do
        :param positiion:
        :return: bool
        """
        check = False
        i, j = position

        # If white get all black moves and check king isnt in them
        if self.board[i][j].colour == 'white':
            if position in [move[1] for move in self.get_all_moves_b()]:
                check = True

        # Do the same for black
        else:
            if position in [move[1] for move in self.get_all_moves_w()]:
                check = True

        return check

    def is_checkmate(self):
        """
        tests for checkmate by checking if king is in check, cannot move,
        cannot take the checking pieces or cannot move a piece to block
        :return: 'white', 'black' or None (might run into issue there) - loser
        """
        # is white in check
        check, checking_pieces = self.can_be_eaten_w(self.whites['wK'].position)

        if check:

            # Tests to see if king can move
            moves = self.whites['wK'].get_moves(self)

            # If it can't, pass
            if moves:
                pass
            else:

                # Tests to see if checking pieces can be taken
                taking_pieces = []
                can_take = False
                for checking_piece in checking_pieces:

                    # Loops through checking pieces and checks that taking doesnt leave king in check
                    can_take, taking_pieces = self.can_be_eaten_b(self.blacks[checking_piece].position)
                    if can_take:
                        for taking_piece in taking_pieces:
                            self.push(taking_piece, self.blacks[checking_piece].position)
                            check1, checking_pieces1 = self.can_be_eaten_w(self.whites['wK'].position)
                            self.undo()

                            if check1:
                                can_take = False
                                break

                # If checking pieces can be taken, pass
                if can_take:
                    pass
                else:
                    # Test to see if a piece can block
                    blocking_moves = self.get_all_moves_w()
                    can_block = False
                    for move in blocking_moves:
                        self.push(move[0], move[1])
                        check2, checking_pieces2 = self.can_be_eaten_w(self.whites['wK'].position)
                        self.undo()

                        if not check2:
                            can_block = True
                            break
                    if not can_block:
                        return 'white'

        # is black in check
        check, checking_pieces = self.can_be_eaten_b(self.blacks['bK'].position)

        if check:

            # Tests to see if king can move
            moves = self.blacks['bK'].get_moves(self)
            can_move = False

            # If it can't, pass
            if moves:
                pass

            else:
                # Tests to see if checking pieces can be taken
                taking_pieces = []
                can_take = False
                for checking_piece in checking_pieces:

                    # Loops through checking pieces and checks that taking doesnt leave king in check
                    can_take, taking_pieces = self.can_be_eaten_w(self.whites[checking_piece].position)
                    for taking_piece in taking_pieces:
                        self.push(taking_piece, self.whites[checking_piece].position)
                        check1, checking_pieces1 = self.can_be_eaten_b(self.blacks['bK'].position)
                        self.undo()

                        if not check1:
                            can_take = True
                            break

                # If the checking pieces can be taken, pass
                if can_take:
                    pass
                else:
                    # Test to see if a piece can block
                    blocking_moves = self.get_all_moves_b()
                    can_block = False
                    for move in blocking_moves:
                        self.push(move[0], move[1])
                        check2, checking_pieces2 = self.can_be_eaten_b(self.blacks['bK'].position)
                        self.undo()

                        if not check2:
                            can_block = True
                            break
                    if not can_block:
                        return 'black'

        return None

    def is_stalemate(self):
        """
        checks if game is a draw
        rules:
            3 fold repetition
            no legal moves 1 side
            50 move rule
            insufficient material:  king versus king
                                    king and bishop versus king
                                    king and knight versus king
                                    king and bishop versus king and bishop with the bishops on the same colour
        :return: True or False
        """
        # TODO FIX STALEMATE
        # convert deque to list
        move_list = list(self.move_stack)

        # 3 fold repetition
        if 3 in self.board_states.values():
            return True

        # get last 3 moves
        # last_2_moves = move_list[-2:]
        # fourth_and_third = move_list[-4:-2]
        # fifth_and_fourth = move_list[-6:-4]
        # # check for 3 fold
        # if last_2_moves == fourth_and_third and last_2_moves == fifth_and_fourth:
        #     return True


        # no legal moves
        if not self.get_all_moves_w() or not self.get_all_moves_b():
            return True

        # 50 move rule
        fifty_move_rule = False
        if len(move_list) >= 50:
            fifty_move_rule = True
            # get last 50 moves
            last_50_moves = move_list[-50:]
            for move in last_50_moves:
                # if pawn has moved or piece has been captured
                if len(move) == 5 or move[3] is not None:
                    # 50 move rule does not hold
                    fifty_move_rule = False

        if fifty_move_rule:
            return True

        # insufficient material
        remaining_b = self.blacks.keys()
        remaining_w = self.whites.keys()

        if len(remaining_w) == 1:
            # king vs king
            if len(remaining_b) == 1:
                return True
            # king vs bishop or king vs knight
            if len(self.blacks) == 2:
                if "bB1" in remaining_b or "bB2" in remaining_b or "bK1" in remaining_b or "bK2" in remaining_b:
                    return True

        if len(remaining_b) == 1:
            # king vs king
            if len(remaining_w) == 1:
                return True
            # king vs bishop or king vs knight
            if len(remaining_b) == 2:
                if ("wB1" in remaining_w) or ("wB2" in remaining_w) or ("wK1" in remaining_w) or ("wK2" in remaining_w):
                    return True

        # king and bishop versus king and bishop with the bishops on the same colour
        if len(remaining_w) == 2 and len(remaining_b) == 2:
            if ("wB1" in remaining_w and "bB2" in remaining_b) or ("wB2" in remaining_w and "bB1" in remaining_b):
                return True

        return False

    def undo(self):
        """
        undoes the most recent move by deleting it from move_stack
        :return: Nothing
        """

        # get last move
        try:
            prev_move = self.move_stack.pop()
        except IndexError:
            print("tried to pop from empty stack - can't undo this move")
            sys.exit()

        piece = prev_move[0]
        prev_pos = prev_move[1]
        current_pos = prev_move[2]
        captured = prev_move[3]

        i, j = prev_pos
        p, q = current_pos

        # remove piece from current position
        self.board[p][q] = None

        # if white
        if piece[0] == "w":
            # if pawn's first move set first back to True
            if piece[1] == "P":
                self.whites[piece].first = prev_move[4]
            # return to previous position and update piece class
            self.whites[piece].position = prev_pos
            self.board[i][j] = self.whites[piece]

            # if a piece was captured in last move
            if captured is not None:
                captured_piece = self.taken_blacks.pop()
                # put back in dictionary
                self.blacks[captured_piece.id] = captured_piece
                # set state to true
                captured_piece.state = True
                # put piece back on board
                self.board[p][q] = captured_piece

        # if black
        else:
            # if pawn's first move set first back to True
            if piece[1] == "P":
                self.blacks[piece].first = prev_move[4]
            # return to previous position and update piece class
            self.blacks[piece].position = prev_pos
            self.board[i][j] = self.blacks[piece]

            # if a piece was captured in last move
            if captured is not None:
                captured_piece = self.taken_whites.pop()
                # put back in dictionary
                self.whites[captured_piece.id] = captured_piece
                # set state to true
                captured_piece.state = True
                # put piece back on board
                self.board[p][q] = captured_piece

    def push(self, piece, move):
        """
        updates board by putting piece in new position and adding move to stack
        :param piece: piece id (string)
        :param move: (i, j)
        :return: nothing
        """
        captured = None

        # variable for storing whether its a pawns first move
        pawn_first = False

        # if white
        if piece[0] == "w":

            # if its a pawn and first move
            if piece[1] == "P":
                if self.whites[piece].first:
                    pawn_first = True
                    # set first move to false
                    self.whites[piece].first = False

            # remove piece from current position
            i, j = self.whites[piece].position
            self.board[i][j] = None

            p, q = move

            # if piece captured set its state to false
            if self.board[p][q] is not None:
                self.board[p][q].state = False
                captured = self.board[p][q]
                self.taken_blacks.append(captured)
                if captured.id == 'bK':
                    raise Exception("Tried to remove black king from board")
                del self.blacks[captured.id]

            # update board and piece class with new position
            self.whites[piece].position = move
            self.board[p][q] = self.whites[piece]

        # if black
        else:

            # check if its a pawn and first move
            if piece[1] == "P":
                if self.blacks[piece].first:
                    pawn_first = True
                    # set first move to false
                    self.blacks[piece].first = False

            # remove piece from current position
            i, j = self.blacks[piece].position
            self.board[i][j] = None

            p, q = move

            # if piece captured set its state to false
            if self.board[p][q] is not None:
                self.board[p][q].state = False
                captured = self.board[p][q]
                self.taken_whites.append(captured)
                if captured.id == 'wK':
                    raise Exception("Tried to remove white king from board")
                del self.whites[captured.id]

            # update board and piece class with new position
            self.blacks[piece].position = move
            self.board[p][q] = self.blacks[piece]

        # update move stack

        # if it a pawn include whether its first move or not
        if piece[1] == "P":
            self.move_stack.append((piece, (i, j), (p, q), captured, pawn_first))
            return

        self.move_stack.append((piece, (i, j), (p, q), captured))

    def get_all_moves_w(self):
        """
        gets all the possible moves that can be made by white pieces on the board
        returns a list of these moves in the form (id, (i, j))
        :return: list of all moves
        """
        all_moves = list()

        # loop through all pieces
        for piece in self.whites.values():

            # loop through moves for each piece and add to list
            for move in piece.get_moves(self):
                formatted_move = (piece.id, move)
                all_moves.append(formatted_move)

        return all_moves

    def get_all_moves_b(self):
        """
        gets all the possible moves that can be made by black pieces on the board
        returns a list of these moves in the form (id, (i, j))
        :return: list of all moves
        """
        all_moves = list()

        # loop through all pieces
        for piece in self.blacks.values():

            # loop through moves for each piece and add to list
            for move in piece.get_moves(self):
                formatted_move = (piece.id, move)
                all_moves.append(formatted_move)

        return all_moves

    def evaluate(self):
        """
        finds value of the board based on pieces taken
        assumes white is maximiser
        board value = (total value of taken blacks - total value of taken whites) + piece square values
        :return: value of current board (int)
        """
        piece_square_table = {
            "pawn": [
                [0, 0, 0, 0, 0, 0, 0, 0],
                [5, 10, 10, -20, -20, 10, 10, 5],
                [5, -5, -10, 0, 0, -10, -5, 5],
                [0, 0, 0, 20, 20, 0, 0, 0],
                [5, 5, 10, 25, 25, 10, 5, 5],
                [10, 10, 20, 30, 30, 20, 10, 10],
                [50, 50, 50, 50, 50, 50, 50, 50],
                [0, 0, 0, 0, 0, 0, 0, 0]],
            "knight": [
                [-50, -40, -30, -30, -30, -30, -40, -50],
                [-40, -20, 0, 5, 5, 0, -20, -40],
                [-30, 5, 10, 15, 15, 10, 5, -30],
                [-30, 0, 15, 20, 20, 15, 0, -30],
                [-30, 5, 15, 20, 20, 15, 5, -30],
                [-30, 0, 10, 15, 15, 10, 0, -30],
                [-40, -20, 0, 0, 0, 0, -20, -40],
                [-50, -40, -30, -30, -30, -30, -40, -50]],
            "bishop": [
                [-20, -10, -10, -10, -10, -10, -10, -20],
                [-10, 5, 0, 0, 0, 0, 5, -10],
                [-10, 10, 10, 10, 10, 10, 10, -10],
                [-10, 0, 10, 10, 10, 10, 0, -10],
                [-10, 5, 5, 10, 10, 5, 5, -10],
                [-10, 0, 5, 10, 10, 5, 0, -10],
                [-10, 0, 0, 0, 0, 0, 0, -10],
                [-20, -10, -10, -10, -10, -10, -10, -20]],
            "rook": [
                [0, 0, 0, 5, 5, 0, 0, 0],
                [-5, 0, 0, 0, 0, 0, 0, -5],
                [-5, 0, 0, 0, 0, 0, 0, -5],
                [-5, 0, 0, 0, 0, 0, 0, -5],
                [-5, 0, 0, 0, 0, 0, 0, -5],
                [-5, 0, 0, 0, 0, 0, 0, -5],
                [5, 10, 10, 10, 10, 10, 10, 5],
                [0, 0, 0, 0, 0, 0, 0, 0]],
            "queen": [
                [-20, -10, -10, -5, -5, -10, -10, -20],
                [-10, 0, 0, 0, 0, 0, 0, -10],
                [-10, 5, 5, 5, 5, 5, 0, -10],
                [0, 0, 5, 5, 5, 5, 0, -5],
                [-5, 0, 5, 5, 5, 5, 0, -5],
                [-10, 0, 5, 5, 5, 5, 0, -10],
                [-10, 0, 0, 0, 0, 0, 0, -10],
                [-20, -10, -10, -5, -5, -10, -10, -20]],
            "king": [
                [20, 30, 10, 0, 0, 10, 30, 20],
                [20, 20, 0, 0, 0, 0, 20, 20],
                [-10, -20, -20, -20, -20, -20, -20, -10],
                [-20, -30, -30, -40, -40, -30, -30, -20],
                [-30, -40, -40, -50, -50, -40, -40, -30],
                [-30, -40, -40, -50, -50, -40, -40, -30],
                [-30, -40, -40, -50, -50, -40, -40, -30],
                [-30, -40, -40, -50, -50, -40, -40, -30]]
        }

        piece_values = {
            "queen": 900,
            "bishop": 330,
            "rook": 500,
            "knight": 320,
            "pawn": 100
        }
        checkmate = self.is_checkmate()
        if checkmate == "white":
            return -100000000000
        elif checkmate == "black":
            return 100000000000
        elif self.is_stalemate():
            return 0

        # calculate total value of black pieces taken
        total_black_taken = 0
        for piece in self.taken_blacks:
            total_black_taken += piece_values[piece.type]

        # calculate total value of white pieces taken
        total_white_taken = 0
        for piece in self.taken_whites:
            total_white_taken += piece_values[piece.type]

        # calculate material value (black-white when white is maximiser)
        material = total_black_taken - total_white_taken

        piece_square_value = 0

        for piece in self.whites.values():
            table = piece_square_table[piece.type]
            i, j = piece.position
            piece_square_value += table[7 - i][j]

        for piece in self.blacks.values():
            table = piece_square_table[piece.type]
            i, j = piece.position
            piece_square_value += -1 * table[i][j]

        board_val = piece_square_value + material
        return board_val

    def is_terminal(self):

        if self.is_checkmate() is not None or self.is_stalemate():
            return True

        return False


class Piece:

    def __init__(self, state, position, id, colour):
        self.state = state
        self.position = position
        self.id = id
        self.colour = colour

    def remove_moves(self, pos_moves, board):
        """
        Loops through the moves in pos moves and removes erroneous ones
        i.e off the board or occupied by a piece of the same colour
        :param board: board object
        :param pos_moves: possible moves
        :return: pos_moves array
        """

        global check_checked
        to_remove = []
        for move in pos_moves:
            p, q = move

            # off the board
            if (p > 7 or p < 0) or (q > 7 or q < 0):
                to_remove.append(move)
                continue

            # Occupied by a piece of the same colour
            if board.board[p][q]:
                if board.board[p][q].colour == self.colour:
                    to_remove.append(move)

        # Break from loop or push function may push to square with piece of the same colour
        [pos_moves.remove(move) for move in to_remove]
        to_remove = []

        for move in pos_moves:

            i, j = move
            # Checks that making move wont put king in check
            if self.colour == 'white' and not check_checked:
                if board.board[i][j] is not None:
                    if board.board[i][j].id == 'bK':
                        continue
                board.push(self.id, move)
                check_checked = True
                check = board.check(board.whites['wK'].position)
                check_checked = False
                board.undo()
                if check:
                    to_remove.append(move)

            elif self.colour == 'black' and not check_checked:
                if board.board[i][j] is not None:
                    if board.board[i][j].id == 'wK':
                        continue
                board.push(self.id, move)
                check_checked = True
                check = board.check(board.blacks['bK'].position)
                check_checked = False
                board.undo()
                if check:
                    to_remove.append(move)

        [pos_moves.remove(move) for move in to_remove]

        return pos_moves

    def get_diagonals(self, board_object):

        i, j = self.position
        pos_moves = list()
        board = board_object.board

        # up and right
        n = min(i, 7 - j)
        for k in range(1, n + 1):
            if board[i - k][j + k] is not None:
                # check for a piece of opposite colour
                if board[i - k][j + k].colour != self.colour:
                    pos_moves.append((i - k, j + k))
                break
            pos_moves.append((i - k, j + k))

        # up and left
        n = min(i, j)
        for k in range(1, n + 1):
            if board[i - k][j - k] is not None:
                # check for a piece of opposite colour
                if board[i - k][j - k].colour != self.colour:
                    pos_moves.append((i - k, j - k))
                break
            pos_moves.append((i - k, j - k))

        # down and right
        n = min(7 - i, 7 - j)
        for k in range(1, n + 1):
            if board[i + k][j + k] is not None:
                # check for a piece of opposite colour
                if board[i + k][j + k].colour != self.colour:
                    pos_moves.append((i + k, j + k))
                break
            pos_moves.append((i + k, j + k))

        # down and left
        n = min(7 - i, j)
        for k in range(1, n + 1):
            if board[i + k][j - k] is not None:
                # check for a piece of opposite colour
                if board[i + k][j - k].colour != self.colour:
                    pos_moves.append((i + k, j - k))
                break
            pos_moves.append((i + k, j - k))

        return pos_moves

    def get_v_and_h(self, board_object):
        i, j = self.position
        pos_moves = list()
        board = board_object.board

        # up
        for k in range(1, i + 1):
            if board[i - k][j] is not None:
                # check for a piece of opposite colour
                if board[i - k][j].colour != self.colour:
                    pos_moves.append((i - k, j))
                break
            pos_moves.append((i - k, j))

        # left
        for k in range(1, j + 1):
            if board[i][j - k] is not None:
                # check for a piece of opposite colour
                if board[i][j - k].colour != self.colour:
                    pos_moves.append((i, j - k))
                break
            pos_moves.append((i, j - k))

        # down
        for k in range(1, 8 - i):
            if board[i + k][j] is not None:
                # check for a piece of opposite colour
                if board[i + k][j].colour != self.colour:
                    pos_moves.append((i + k, j))
                break
            pos_moves.append((i + k, j))

        # right
        for k in range(1, 8 - j):
            if board[i][j + k] is not None:
                # check for a piece of opposite colour
                if board[i][j + k].colour != self.colour:
                    pos_moves.append((i, j + k))
                break
            pos_moves.append((i, j + k))

        return pos_moves


# pawn class
class Pawn(Piece):

    def __init__(self, state, position, id, colour):
        # this syntax calls the init on the super class (Piece) so you don't have to rewrite the whole of init
        super().__init__(state, position, id, colour)
        self.first = True
        self.type = "pawn"

    def get_moves(self, board_object):
        """
        Works out the possible moves for a pawn
        :return: list of possible moves
        """
        # check if captured
        if not self.state:
            return []

        i, j = self.position
        pos_moves = []

        # get board array from object
        board = board_object.board

        # Finds possible moves for white regardless of cell content
        if self.colour == 'white':
            # if it is the first move
            if self.first:
                if board[i - 1][j] is None and board[i - 2][j] is None:
                    pos_moves.append((i - 2, j))

            # if it is not the first move
            # make sure move is valid
            if i - 1 >= 0 and j - 1 >= 0:
                if board[i - 1][j - 1] is not None:
                    pos_moves.append((i - 1, j - 1))
            if i - 1 >= 0 and j + 1 <= 7:
                if board[i - 1][j + 1] is not None:
                    pos_moves.append((i - 1, j + 1))
            if i - 1 >= 0:
                if board[i - 1][j] is None:
                    pos_moves.append((i - 1, j))

        # Finds possible moves for black regardless of cell content
        if self.colour == 'black':
            # if it is the first move
            if self.first:
                if board[i + 1][j] is None and board[i + 2][j] is None:
                    pos_moves.append((i + 2, j))

            # if it is not the first move
            # make sure move is valid
            if i + 1 <= 7 and j - 1 >= 0:
                if board[i + 1][j - 1] is not None:
                    pos_moves.append((i + 1, j - 1))
            if i + 1 <= 7 and j + 1 <= 7:
                if board[i + 1][j + 1] is not None:
                    pos_moves.append((i + 1, j + 1))
            if i + 1 <= 7:
                if board[i + 1][j] is None:
                    pos_moves.append((i + 1, j))

        return self.remove_moves(pos_moves, board_object)


# knight class
class Knight(Piece):
    def __init__(self, state, position, id, colour):
        super().__init__(state, position, id, colour)
        self.type = "knight"

    def get_moves(self, board_object):
        """
        Works out the possible moves for a knight
        :param board_object: board object
        :return: list of possible moves
        """
        # check if captured
        if not self.state:
            return []

        i, j = self.position
        pos_moves = [(i + 2, j + 1), (i + 2, j - 1), (i - 2, j + 1), (i - 2, j - 1),
                     (i + 1, j + 2), (i + 1, j - 2), (i - 1, j + 2), (i - 1, j - 2)]

        return self.remove_moves(pos_moves, board_object)


# bishop class
class Bishop(Piece):

    def __init__(self, state, position, id, colour):
        super().__init__(state, position, id, colour)
        self.type = "bishop"

    def get_moves(self, board_object):
        """
        Works out the possible moves for a bishop
        :param board_object: board object
        :return: list of possible moves
        """
        # check if captured
        if not self.state:
            return []

        return self.remove_moves(self.get_diagonals(board_object), board_object)


# king class
class King(Piece):

    def __init__(self, state, position, id, colour):
        super().__init__(state, position, id, colour)
        self.type = "king"

    def get_moves(self, board_object):
        """
        get moves using kings rules
        :param board_object: board object
        :return: list of possible moves
        """
        # check if captured
        if not self.state:
            return []

        i, j = self.position
        pos_moves = [(i + 1, j), (i - 1, j), (i, j + 1), (i, j - 1), (i + 1, j + 1), (i - 1, j - 1), (i + 1, j - 1),
                     (i - 1, j + 1)]

        pos_moves = self.remove_moves(pos_moves, board_object)

        to_remove = list()

        if self.colour == "white":
            # get opposite colour's king object
            other_king = board_object.blacks["bK"]

        else:
            # get opposite colour's king object
            other_king = board_object.whites["wK"]

        # find position
        other_i, other_j = other_king.position
        # get surrounding squares
        other_pos_moves = [(other_i + 1, other_j), (other_i - 1, other_j), (other_i, other_j + 1),
                           (other_i, other_j - 1), (other_i + 1, other_j + 1), (other_i - 1, other_j - 1),
                           (other_i + 1, other_j - 1), (other_i - 1, other_j + 1)]
        # check if any of these moves
        for move in pos_moves:
            if move in other_pos_moves:
                to_remove.append(move)

        [pos_moves.remove(move) for move in to_remove]

        return pos_moves


# queen class
class Queen(Piece):

    def __init__(self, state, position, id, colour):
        super().__init__(state, position, id, colour)
        self.type = "queen"

    def get_moves(self, board_object):
        """
        get moves using queens rules
        :param board_object: board object
        :return: list of possible moves
        """
        # check if captured
        if not self.state:
            return []

        pos_moves = list()

        # get vertical and horizontal moves
        if self.get_v_and_h(board_object):
            [pos_moves.append(move) for move in self.get_v_and_h(board_object)]

        # get diagonal moves
        if self.get_diagonals(board_object):
            [pos_moves.append(move) for move in self.get_diagonals(board_object)]
        return self.remove_moves(pos_moves, board_object)


# rook class
class Rook(Piece):

    def __init__(self, state, position, id, colour):
        super().__init__(state, position, id, colour)
        self.type = "rook"

    def get_moves(self, board_object):
        """
        get moves using rooks rules
        :param board_object: board object
        :return: list of possible moves
        """
        # check if captured
        if not self.state:
            return []

        return self.remove_moves(self.get_v_and_h(board_object), board_object)