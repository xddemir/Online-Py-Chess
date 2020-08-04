from threading import Thread
import object
import pickle
import pygame as p

# read data in order to pull data from server
class ReadThread(Thread):
    def __init__(self, client):
        self.client = client
        self.data = None
        self.BUFFER_SIZE = 2048
        super().__init__()
    
    def run(self):
        while True:
            data = pickle.loads(self.client.recv(self.BUFFER_SIZE * 10))
            if data:
                self.data = data   

# write data in order to send server
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

class client:
    # player environments
    def __init__(self):
        self.font = p.font.SysFont('Helvitca', 40, True, False)
        self.checkGameOver = False
        self.isAnimatemove = False 
        #run for while loop
        self.startGame = True 
        #it contains x,y cordinates 
        self.selectPosition = () 
        self.clicks_of_player = []
        #gameEngine class
        self.gameState = object.GameState() 
        self.validMoves = self.gameState.getValidMoves() 
        #client.validMoves's a very expensive method, in this reason we should put a flag thus it won't be looping in every frame.
        self.isMovingValid = False 