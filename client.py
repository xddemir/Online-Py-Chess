from threading import Thread
import socket
import pickle
import pygame as p
import object



WIDTH, HEIGHT = 512, 512
p.init()
p.display.set_caption("PyChess")
SIZE = 8
SQ_SIZE = 512 // SIZE
WIN = p.display.set_mode((WIDTH, HEIGHT))
images = {}
# images
img_lst = ["wr", "wkn","wb","wq","wk","wp","br", "bkn", "bb", "bq", "bk","bp"]
" loads pieces"
for img in img_lst:
    images[img] = p.transform.scale(p.image.load(f"Assets/{img}.png"), (SQ_SIZE, SQ_SIZE))

"""
 data transfering between clients and server step by step (line 191)

1- when player clicks == 2, create a new datapackage and if it's not null it sends writeThread.sen_data(data)
2- then in run fuction of WriteThread it sends data to server
3- server checks is move valid and gamestate is equal server's gamestate
4- after server checked the data it sends data to clients back
5- and will create new data called self.data then it will be equal data
6- then data reached to client it will continue procressing
"""
class ReadThread(Thread):
    def __init__(self, client):
        self.client = client
        super().__init__()
    
    def run(self):
        while True:
            data = self.client.tcpClient.recv(2048 * 10)
            if data:
                self.data = data
                self.data = pickle.loads(self.data)
                self.client.display_data(self.data)
                
class WriteThread(Thread):
    def __init__(self, client):
        self.client = client
        self.data = None
        super().__init__()
    
    def send_data(self, data):
        self.data = data
    
    def run(self):
        while True:
            if self.data:
                self.client.tcpClient.send(pickle.dumps(self.data))
                self.data = None

class Client(Thread):
    def __init__(self):
        host = "127.0.0.1"
        port = 6666
        BUFFER_SIZE = 2048

        self.tcpClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcpClient.connect((host, port))
        
        self.gamestate = object.GameState() #gameEngine class
        self.validMoves = self.gamestate.getValidMoves() #Move Class

        self.font = p.font.SysFont('agencyfb', 40)
        self.gameOver = False
        self.animate = False #flag veriable when animate moves
        self.startGame = True #run for while loop
        self.sqSelected = () #it contains x,y cordinates 
        self.playerClicks = []
        self.moveMade = False #validMoves's a very expensive method, in this reason we should put a flag thus it won't be looping in every frame.
        self.clock = p.time.Clock()

        print ("in init p is :%s" ,id(p))

        super().__init__()

    def display_data(self, data_package):
        " it sends the data to client"
        self.data = data_package
    
    #draw pieces, board, texts
    def animateMove(self, move, WIN, board, clokc):
        global Colors
        dR = move.endRow - move.startRow
        dC = move.endColumn - move.startColumn
        framePerSquare = 10 # frames to move one square
        frameCount = (abs(dR) + abs(dC)) * framePerSquare
        for frame in range(frameCount+1):
            r, c = move.startRow + dR*frame/frameCount, move.startColumn + dC*frame/frameCount
            self.Redraw()
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
            self.clock.tick(60)

    def Redraw(self):
        global Colors
        Colors = [p.Color("white"), p.Color("darkgrey")]
        # board
        for r in range(SIZE):
            for c in range(SIZE):
                color = Colors[(r + c) % 2] 
                p.draw.rect(WIN, color,(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
                
        """ highlight the moves"""
        if self.sqSelected != ():
            row, col = self.sqSelected
            if self.gamestate.board[row][col][0] == ('w' if self.gamestate.whiteToMoveOn else 'b'):
                surface = p.Surface((SQ_SIZE, SQ_SIZE))
                surface.set_alpha(100) # transparency value 
                surface.fill(p.Color('blue'))
                WIN.blit(surface, (col*SQ_SIZE, row*SQ_SIZE))
                # highlight moves from that square
                surface.fill(p.Color('yellow'))
                for move in self.validMoves:
                    if move.startRow == row and move.startColumn == col:
                        WIN.blit(surface, (move.endColumn * SQ_SIZE, move.endRow * SQ_SIZE))

        " draw pieces upon the board"
        for r in range(SIZE):
            for c in range(SIZE):
                if self.gamestate.board[r][c] != "--" :
                    WIN.blit(images[self.gamestate.board[r][c]], (c * SQ_SIZE, r * SQ_SIZE))
                    
        " check game ending"
        if self.gamestate.checkMate:
            self.gameOver = True
            if self.gamestate.whiteToMoveOn:
                textObj = self.font.render("BLACK WINS BY CHECKMATE", 1,  (0, 0, 0))
                WIN.blit(textObj, (WIDTH/2 - textObj.get_width()/2, HEIGHT/2 - textObj.get_height()/2))
            else:
                textObj = self.font.render("WHITE WINS BY CHECKMATE", 1,  (0, 0, 0))
                WIN.blit(textObj, (WIDTH/2 - textObj.get_width()/2, HEIGHT/2 - textObj.get_height()/2))
        elif self.gamestate.staleMate:
            self.gameOver = True
            textObj = self.font.render("STALEMATE", 1, (0, 0, 0))
            WIN.blit(textObj, (WIDTH/2 - textObj.get_width()/2, HEIGHT/2 - textObj.get_height()/2))

        p.display.update()
    
    def undoPieces(self):
        self.gamestate.undoMove()
        self.moveMade = True
        self.animate = False

    def restartGame(self):
        self.gamestate = object.GameState()
        self.validMoves = self.gamestate.getValidMoves()
        self.sqSelected = ()
        self.playerClicks = []
        self.moveMade =False
        self.animate = False

    # game engine runs in the function 
    def run(self):
        read_thread = ReadThread(self)
        write_thread = WriteThread(self)

        read_thread.start()
        write_thread.start()

        print ("in run p is :%s" ,id(p))


        while self.startGame:
            # client has own self.gameState and self.validMoves
            # creates playerClicks in every two click
            # afterwards it creates a datapackage consisting of gamestate and moves
            # when data_package is not null it sends data to server via write_thread.send_data
            # it's able to get new data from server

            #keys = p.key.get_pressed()
            #event handler
            for event in p.event.get():
                if event.type == p.QUIT:
                   self.startGame = False
            # mouse handler
                elif event.type == p.MOUSEBUTTONDOWN:
                    if not self.gameOver:
                        position = p.mouse.get_pos()
                        row = (position[1])//SQ_SIZE
                        col = (position[0])//SQ_SIZE
                        
                        if self.sqSelected == (row, col):
                            self.sqSelected = ()
                            self.playerClicks = []
                        else:
                            self.sqSelected = (row, col)
                            self.playerClicks.append(self.sqSelected)

                        if len(self.playerClicks) == 2:
                            #object.Move class moves changes pieces
                            self.moves = object.Move(self.playerClicks[0], self.playerClicks[1], self.gamestate.board)

                            # following data transfering lines 
                            data_package = (self.gamestate, self.moves)

                            while data_package != None:
                                write_thread.send_data(data_package)

                            self.gamestate, self.moves = self.data

                            if self.moves in self.validMoves:
                                self.gamestate.makeMove(self.moves)
                                self.moveMade = True
                                self.animate = True
                                self.sqSelected = () # restart
                                self.playerClicks = []

                                if not self.moveMade:
                                    self.playerClicks = [self.sqSelected]

                # key handler
                elif event.type == p.KEYDOWN:
                    if event.key == p.K_z:
                        self.undoPieces()
                      
                    if event.key == p.K_r: # reset the board
                       self.restartGame()

            if self.moveMade:
                self.animateMove(self.gamestate.moveLog[-1], WIN, self.gamestate.board, self.clock)
                self.validMoves = self.gamestate.getValidMoves()
                self.moveMade = False

            self.clock.tick(60)
            self.Redraw()
            p.display.flip()
        
        read_thread.join()
        write_thread.join()

if __name__ == "__main__":
    client = Client()
    client.start()
p.quit()


