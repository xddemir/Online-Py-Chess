import pygame as p
import object
import socket
from threading import Thread
import pickle

p.init()
WIDTH, HEIGHT = 512, 512
WIN = p.display.set_mode((WIDTH, HEIGHT))
p.display.set_caption("PyChess")
clock = p.time.Clock()
SIZE = 8
SQ_SIZE = 512 // SIZE
images = {}

# images
img_lst = ["wr", "wkn","wb","wq","wk","wp","br", "bkn", "bb", "bq", "bk","bp"]

" loads pieces"
for img in img_lst:
    images[img] = p.transform.scale(p.image.load(f"Assets/{img}.png"), (SQ_SIZE, SQ_SIZE))

"""  it is not implemented for now but having finished program it will be added  """
#bg = p.transform.scale(p.image.load("Assets/board.png"),(512,512))

host = '127.0.0.1'
port = 6666
BUFFER_SIZE = 2048

tcpClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcpClient.connect((host, port))

class ReadThread(Thread):
    def __init__(self, client):
        self.client = client
        self.data = None
        super().__init__()
    
    def run(self):
        while True:
            data = pickle.loads(self.client.recv(BUFFER_SIZE * 10))
            if data:
                self.data = data   

class WriteThread(Thread):
    def __init__(self, client):
        self.client = client
        self.data = None
        super().__init__()
    
    def send_data(self, data):
        self.data = data
        print("data : ", self.data)
    
    def run(self):
        while True:
            if self.data:
                self.client.send(pickle.dumps(self.data))
                self.data = None

def main():
    """ Animating Move """
    def animateMove(move, WIN, board, clokc):
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

    "draw pieces, board, texts"
    def Redraw():
        global Colors
        Colors = [p.Color("white"), p.Color("darkgrey")]
        # board
        for r in range(SIZE):
            for c in range(SIZE):
                color = Colors[(r + c) % 2] 
                p.draw.rect(WIN, color,(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

        #WIN.blit(bg, (0, 0))
                
        """ highlight the moves"""
        if sqSelected != ():
            row, col = sqSelected
            if gameState.board[row][col][0] == ('w' if gameState.whiteToMoveOn else 'b'):
                surface = p.Surface((SQ_SIZE, SQ_SIZE))
                surface.set_alpha(100) # transparency value 
                surface.fill(p.Color('blue'))
                WIN.blit(surface, (col*SQ_SIZE, row*SQ_SIZE))
                # highlight moves from that square
                surface.fill(p.Color('yellow'))
                for move in validMoves:
                    if move.startRow == row and move.startColumn == col:
                        WIN.blit(surface, (move.endColumn * SQ_SIZE, move.endRow * SQ_SIZE))

        " draw pieces upon the board"
        for r in range(SIZE):
            for c in range(SIZE):
                if gameState.board[r][c] != "--" :
                    WIN.blit(images[gameState.board[r][c]], (c * SQ_SIZE, r * SQ_SIZE))
                    
        " check game ending"
        if gameState.checkMate:
            gameOver = True
            if gameState.whiteToMoveOn:
                textObj = font.render("BLACK WINS BY CHECKMATE", 1,  (0, 0, 0))
                WIN.blit(textObj, (WIDTH/2 - textObj.get_width()/2, HEIGHT/2 - textObj.get_height()/2))
            else:
                textObj = font.render("WHITE WINS BY CHECKMATE", 1,  (0, 0, 0))
                WIN.blit(textObj, (WIDTH/2 - textObj.get_width()/2, HEIGHT/2 - textObj.get_height()/2))
        elif gameState.staleMate:
            gameOver = True
            textObj = font.render("STALEMATE", 1, (0, 0, 0))
            WIN.blit(textObj, (WIDTH/2 - textObj.get_width()/2, HEIGHT/2 - textObj.get_height()/2))

        p.display.update()

    font = p.font.SysFont('Helvitca', 40, True, False)
    gameOver = False
    animate = False #flag veriable when animate moves
    startGame = True #run for while loop
    sqSelected = () #it contains x,y cordinates 
    playerClicks = []
    gameState = object.GameState() #gameEngine class
    validMoves = gameState.getValidMoves() #Move Class
    moveMade = False #validMoves's a very expensive method, in this reason we should put a flag thus it won't be looping in every frame.
    #creating read_thread and write_thread
    read_thread = ReadThread(tcpClient)
    write_thread = WriteThread(tcpClient)
    read_thread.start()
    write_thread.start()
    
    while startGame:
        # just in case an issue occurs
        if read_thread == None or write_thread == None:
            print("readThread and writeThread couldn't occur")

        # it moves the other client
        if read_thread.data != None:
            gameState, moves = read_thread.data
            print("Read Thread : ", read_thread.data)
            # moving pieces
            if moves in validMoves:
                print("pieces2 moved")
                gameState.makeMove(moves)
                moveMade = True
                animate = True
                sqSelected = () # restart
                playerClicks = []
                read_thread.data = None
                #read_thread.join()
                #write_thread.join()
        
        #event handler
        for event in p.event.get():
            if event.type == p.QUIT:
                startGame = False
        
            # mouse handler
            elif event.type == p.MOUSEBUTTONDOWN:
                if not gameOver:
                    position = p.mouse.get_pos()
                    row = (position[1])//SQ_SIZE
                    col = (position[0])//SQ_SIZE
                    
                    if sqSelected == (row, col):
                        sqSelected = ()
                        playerClicks = []
                    else:
                        sqSelected = (row, col)
                        playerClicks.append(sqSelected)
                    
                    if len(playerClicks) == 2:
                        moves = object.Move(playerClicks[0], playerClicks[1], gameState.board)
                        # here all procress, sending and pulling data
                        data_package = (gameState, moves)

                        # sending data
                        if data_package != None:
                            print("data sent")
                            write_thread.send_data(data_package)

                        # it moves player
                        if moves in validMoves:
                            print("pieces1 moved")
                            gameState.makeMove(moves)
                            moveMade = True
                            animate = True
                            sqSelected = () # restart
                            playerClicks = []
                            #read_thread.data = None
                            #read_thread.join()
                            #write_thread.join()

                        # getting data    
                        if not moveMade:
                            print("if not movemade")
                            playerClicks = [sqSelected]
                            
           # key handler
            elif event.type == p.KEYDOWN:
                if event.key == p.K_z:
                    print("pieces undo")
                    gameState.undoMove()
                    moveMade = True
                    animate = False
                if event.key == p.K_r: # reset the board
                    print("game restart")
                    gameState = object.GameState()
                    validMoves = gameState.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade =False
                    animate = False

        if moveMade:
            animateMove(gameState.moveLog[-1], WIN, gameState.board, clock)
            validMoves = gameState.getValidMoves()
            moveMade = False
        
        clock.tick(60)
        Redraw()
        p.display.flip()
        
if __name__ == "__main__":
    main()
p.quit()