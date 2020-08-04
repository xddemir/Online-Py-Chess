import pygame as p
import object
import socket
import pickle

from threading import Thread
from client import ReadThread
from client import WriteThread
from client import client

p.init()
# GAME ENVIRONMENTS
WIDTH, HEIGHT = 512, 512
WIN = p.display.set_mode((WIDTH, HEIGHT))
p.display.set_caption("PyChess")
clock = p.time.Clock()
SIZE = 8
#for squeezing coordinates 5120 to 8 X 8
SQ_SIZE = 512 // SIZE

# LOAD IMAGES
images = {}
img_lst = ["wr", "wkn","wb","wq","wk","wp","br", "bkn", "bb", "bq", "bk","bp"]
# load pieces
for img in img_lst:
    images[img] = p.transform.scale(p.image.load(f"Assets/{img}.png"), (SQ_SIZE, SQ_SIZE))
# load board
board = p.transform.scale(p.image.load(f"Assets/board.jpg"), (512, 512))
# CONNECT TO THE SERVER
host = '127.0.0.1' # LOCAL IP
port = 6666
BUFFER_SIZE = 2048
# connect client to the server
tcpClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcpClient.connect((host, port))

# main block that everything procress 
# redraw function draws everything 
# animate function animate valid moves

def main(client):
    #creating read_thread and write_thread
    read_thread = ReadThread(tcpClient)
    write_thread = WriteThread(tcpClient)
    # start threads
    read_thread.start()
    write_thread.start()
    
    def animateMove(move, WIN):
        global Colors
        dR = move.endRow - move.startRow
        dC = move.endColumn - move.startColumn
        framePerSquare = 10 # frames to move one square
        frameCount = (abs(dR) + abs(dC)) * framePerSquare
        for frame in range(frameCount+1):
            r, c = move.startRow + dR*frame/frameCount, move.startColumn + dC*frame/frameCount
            Redraw()
            #erase the piece moved from its ending square
            color = Colors[(move.endRow + move.endColumn) % 2]
            endSquare = p.Rect(move.endColumn * SQ_SIZE, move.endRow*SQ_SIZE, SQ_SIZE, SQ_SIZE)
            p.draw.rect(WIN, color, endSquare)
            # draw captured piece onto rectangle
            if move.captureMove != '--':
                WIN.blit(images[move.captureMove], endSquare)
            # draw moving piece
            WIN.blit(images[move.piecesMove], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
            p.display.flip()
            clock.tick(60)

    #"draw pieces, board, texts"
    def Redraw():
        # board's color
        global Colors
        Colors = [p.Color("white"), p.Color("darkgrey")]
        # DRAW BOARD 8X8
        for r in range(SIZE):
            for c in range(SIZE):
                color = Colors[(r + c) % 2] 
                p.draw.rect(WIN, color,(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
        WIN.blit(board, (0, 0))

        # HIGHLIGHT MOVEMENTS
        if client.selectPosition != ():
            row, col = client.selectPosition
            if client.gameState.board[row][col][0] == ('w' if client.gameState.whiteToMoveOn else 'b'):
                surface = p.Surface((SQ_SIZE, SQ_SIZE))
                surface.set_alpha(100) # transparency value 
                surface.fill(p.Color('blue'))
                WIN.blit(surface, (col*SQ_SIZE, row*SQ_SIZE))
                # highlight moves from that square
                surface.fill(p.Color('yellow'))
                for move in client.validMoves:
                    if move.startRow == row and move.startColumn == col:
                        WIN.blit(surface, (move.endColumn * SQ_SIZE, move.endRow * SQ_SIZE))

        # DRAW PIECES
        for r in range(SIZE):
            for c in range(SIZE):
                if client.gameState.board[r][c] != "--" :
                    WIN.blit(images[client.gameState.board[r][c]], (c * SQ_SIZE, r * SQ_SIZE))
                    
        # CHECK CHECKMATE
        if client.gameState.checkMate:
            client.checkGameOver = True
            if client.gameState.whiteToMoveOn:
                textObj = client.font.render("BLACK WINS BY CHECKMATE", 1,  (0, 0, 0))
                WIN.blit(textObj, (WIDTH/2 - textObj.get_width()/2, HEIGHT/2 - textObj.get_height()/2))
            else:
                textObj = client.font.render("WHITE WINS BY CHECKMATE", 1,  (0, 0, 0))
                WIN.blit(textObj, (WIDTH/2 - textObj.get_width()/2, HEIGHT/2 - textObj.get_height()/2))
        elif client.gameState.staleMate:
            client.checkGameOver = True
            textObj = client.font.render("STALEMATE", 1, (0, 0, 0))
            WIN.blit(textObj, (WIDTH/2 - textObj.get_width()/2, HEIGHT/2 - textObj.get_height()/2))
        p.display.update()

    # start the game in infinitive loop
    while client.startGame:
        # after player moved, it makes move the other clients 
        if read_thread.data != None:
            # if data is ready to read it gets data
            client.gameState, moves = read_thread.data
            # moving pieces
            if moves in client.validMoves:
                client.gameState.makeMove(moves)
                client.isMovingValid = True
                client.isAnimatemove = True
                client.selectPosition = () # restart
                client.clicks_of_player = []
                read_thread.data = None

        # quit movement
        for event in p.event.get():
            if event.type == p.QUIT:
                client.startGame = False

            # mouse movements
            elif event.type == p.MOUSEBUTTONDOWN:
                if not client.checkGameOver:
                    # mouse gets clicks of player
                    position = p.mouse.get_pos()
                    # it squeeze location of position in order to make coordinates 8X8
                    row = (position[1])//SQ_SIZE
                    col = (position[0])//SQ_SIZE
                    
                    # mouse checks that player clicks twice 
                    if client.selectPosition == (row, col):
                        client.selectPosition = ()
                        client.clicks_of_player = []

                    # if player clicks twice it's into 
                    else:
                        client.selectPosition = (row, col)
                        # it contains clicks_of_player in touple [(first), (last)]
                        client.clicks_of_player.append(client.selectPosition)

                    # when player clicked twice 
                    if len(client.clicks_of_player) == 2:

                        # make player move in move class 
                        moves = object.Move(client.clicks_of_player[0], client.clicks_of_player[1], client.gameState.board)
                        
                        # data packs are packed in order to send server
                        data_package = (client.gameState, moves)

                        # data is sends to the server
                        write_thread.send_data(data_package)
                        
                        # it checks that making a move is valid 
                        if moves in client.validMoves:
                            # it makes move
                            client.gameState.makeMove(moves)
                            client.isMovingValid = True
                            client.isAnimatemove = True
                            # clicks of player's list reset to get new clicks
                            client.selectPosition = () 
                            client.clicks_of_player = []
                          
                        # getting data    
                        if not client.isMovingValid:
                            client.clicks_of_player = [client.selectPosition]
                            
            # key's movements
            elif event.type == p.KEYDOWN:

                if event.key == p.K_z:
                    # it undo player's move by clicking "z"
                    client.gameState.undoMove()
                    client.isMovingValid = True
                    client.isAnimatemove = False

                if event.key == p.K_r:
                    # it reset the gameBoard and player's object for new game
                    client.gameState = object.GameState()
                    client.validMoves = client.gameState.getValidMoves()
                    client.selectPosition = ()
                    client.clicks_of_player = []
                    client.isMovingValid =False
                    client.isAnimatemove = False

        # if player makes a move then the player animation works  
        if  client.isMovingValid:
            animateMove(client.gameState.moveLog[-1], WIN)
            # valid moves is reset to change possibility of move
            client.validMoves = client.gameState.getValidMoves()
            client.isMovingValid = False
        # it frame of game
        clock.tick(60)
        # in every 60 ms it redraw the object
        Redraw()
        # for background
        p.display.flip()
    
if __name__ == "__main__":
    # create player client to get values from it
    player = client()
    # start the game
    main(player)
# quit the game when checkmate or event.exit
p.quit()