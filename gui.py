import pygame as p
from classes import *
from runner import load_pieces
from minimax import *
import time

p.init()
black = (0, 0, 0)
white = (255, 255, 255)
WIDTH = HEIGHT = 512
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}
mediumFont = p.font.Font("../chess/OpenSans-Regular.ttf", 28)
largeFont = p.font.Font("../chess/OpenSans-Regular.ttf", 40)
moveFont = p.font.Font("../chess/OpenSans-Regular.ttf", 60)
depth = 2


def loadImages():
    pieces = ["wP", "wR", "wN", "wB", "wK", "wQ", "bP", "bR", "bN", "bB", "bK", "bQ"]
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("pieces/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))


def main():
    """main driver for code"""
    # set up screen
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))

    # load pieces and images
    whites, blacks = load_pieces()
    board = Board(whites, blacks)
    moveMade = False
    loadImages()
    running = True
    sqSelected = ()
    playerClicks = []
    gameOver = False
    numMoves = 0
    player = None

    # game loop
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False

            # Let user choose a player.
            if player is None:

                # Draw title
                screen.fill(black)
                title = largeFont.render("Chess", True, white)
                titleRect = title.get_rect()
                titleRect.center = ((WIDTH / 2), 50)
                screen.blit(title, titleRect)

                # Draw buttons
                playWButton = p.Rect((WIDTH / 9), (HEIGHT / 3), WIDTH / 3, 50)
                playW = mediumFont.render("Play as white", True, black)
                playWRect = playW.get_rect()
                playWRect.center = playWButton.center
                p.draw.rect(screen, white, playWButton)
                screen.blit(playW, playWRect)

                playBButton = p.Rect(5 * (WIDTH / 9), (HEIGHT / 3), WIDTH / 3, 50)
                playB = mediumFont.render("Play as black", True, black)
                playBRect = playB.get_rect()
                playBRect.center = playBButton.center
                p.draw.rect(screen, white, playBButton)
                screen.blit(playB, playBRect)

                # Check if button is clicked
                if e.type == p.MOUSEBUTTONDOWN:
                    mouse = p.mouse.get_pos()
                    if playWButton.collidepoint(mouse):
                        time.sleep(0.2)
                        player = 0
                    elif playBButton.collidepoint(mouse):
                        time.sleep(0.2)
                        player = 1

            # play game
            else:
                if player == 0:
                    validMoves = board.get_all_moves_w()
                else:
                    validMoves = board.get_all_moves_b()
                if not gameOver:
                    # if its users go and a square is clicked
                    if numMoves % 2 == player:
                        if e.type == p.MOUSEBUTTONDOWN:
                            # get click location
                            location = p.mouse.get_pos()
                            col = location[0] // SQ_SIZE
                            row = location[1] // SQ_SIZE

                            # if user clicks on same square twice - skip
                            if sqSelected == (row, col):
                                sqSelected = ()
                                playerClicks = []

                            # save user selection
                            else:
                                sqSelected = (row, col)
                                playerClicks.append(sqSelected)

                            # if empty square clicked as first click - skip
                            if len(playerClicks) == 1:
                                pieceSelected = board.board[sqSelected[0]][sqSelected[1]]
                                if pieceSelected is None:
                                    sqSelected = ()
                                    playerClicks = []

                            # if second click has been made
                            if len(playerClicks) == 2:
                                # get first click
                                start_i, start_j = playerClicks[0]
                                # get second click
                                end_i, end_j = playerClicks[1]
                                # get piece at this location and check its not None
                                pieceSelected = board.board[start_i][start_j]
                                move = (pieceSelected.id, (end_i, end_j))
                                # if its a valid move
                                if move in validMoves:
                                    # push the piece to new position
                                    board.push(move[0], move[1])
                                    moveMade = True
                                sqSelected = ()
                                playerClicks = []

                    else:
                        if player == 0:
                            move = get_move(board, False, depth)
                        else:
                            move = get_move(board, True, depth)
                        id, pos = move
                        board.push(id, pos)
                        moveMade = True

                    if moveMade:
                        # add board to board_states
                        flattened_board = [piece.id if piece is not None else None for row in board.board for piece in
                                           row]
                        flattened_board = tuple(flattened_board)
                        if flattened_board in board.board_states.keys():
                            board.board_states[flattened_board] += 1
                        else:
                            board.board_states[flattened_board] = 1

                        print(board.move_stack)

                        if board.is_checkmate() == "black":
                            gameOver = True
                            winner = "WHITE"
                        elif board.is_checkmate() == "white":
                            print("BLACK WINS")
                            gameOver = True
                            winner = "BLACK"
                        elif board.is_stalemate():
                            print("STALEMATE")
                            gameOver = True
                            winner = None

                        numMoves += 1
                        # if white
                        if player == 0:
                            validMoves = board.get_all_moves_w()
                        # if black
                        else:
                            validMoves = board.get_all_moves_b()
                        moveMade = False

                # draw board
                drawGameState(screen, board, sqSelected, player)

                # if game over
                if gameOver:
                    if winner is None:
                        title = f"Game Over: Tie."
                    else:
                        title = f"Game Over: {winner} wins."
                    p.draw.rect(screen, black, (0, (WIDTH / 2) - 30, WIDTH, 60))
                    title = largeFont.render(title, True, (255, 255, 255))
                    titleRect = title.get_rect()
                    titleRect.center = ((WIDTH / 2), HEIGHT / 2)
                    screen.blit(title, titleRect)

                clock.tick(MAX_FPS)
        p.display.flip()


def highlightSquares(screen, gs, sqSelected, player):
    if sqSelected != ():
        r, c = sqSelected
        if gs.board[r][c].colour == ("white" if player == 0 else "black"):
            pieceSelected = gs.board[r][c]
            validMoves = pieceSelected.get_moves(gs)
            # highlight selected square
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)
            s.fill(p.Color("blue"))
            screen.blit(s, (c * SQ_SIZE, r * SQ_SIZE))
            # highlight moves from that square
            s.fill(p.Color("yellow"))
            for move in validMoves:
                i, j = move
                screen.blit(s, (j * SQ_SIZE, i * SQ_SIZE))


def drawGameState(screen, gs, sqSelected, player):
    """responsible for graphics"""
    # draw grid
    drawBoard(screen)
    highlightSquares(screen, gs, sqSelected, player)
    # put pieces on screen
    drawPieces(screen, gs.board)


def drawBoard(screen):
    """draw squares on board"""
    colors = [p.Color("white"), p.Color("gray")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r + c) % 2)]
            p.draw.rect(screen, color, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def drawPieces(screen, board):
    """draw piece on board using current board"""
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece is not None:
                if piece.type == "knight":
                    index = piece.id[0] + "N"
                    screen.blit(IMAGES[index], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))
                else:
                    screen.blit(IMAGES[piece.id[:2]], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


if __name__ == "__main__":
    main()
