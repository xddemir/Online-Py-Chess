import socket
import pickle
from threading import Thread
import object

class threadClient(Thread):
    def __init__(self, ip, port, conn, server):
        self.ip = ip
        self.port = port
        self.conn = conn
        self.server = server
        self.gameState = object.GameState()
        self.validMoves = self.gameState.getValidMoves()
        # it inits gameState and moves for player one and moves for player two
        super().__init__() # gets inheritance from Thread
        print("Started for ip: {} and port: {}".format(self.ip, self.port))

    def run(self):
        while True:
            data = pickle.loads(self.conn.recv(2048 * 10)) # (gameState, moves)
            if data[1] in self.validMoves:
                self.gameState = data[0]
                self.server.transfer_message(self, data)

    def notify(self, data):
        self.conn.send(pickle.dumps(data))

class Server(Thread): # takes inheritance from Thread
    def __init__(self):
        self.clients = []
        self.tempCords = []
        super().__init__()

    def transfer_message(self, sending_client, data):
        if sending_client not in self.clients:
            self.clients.append(sending_client)

        for client in self.clients:
            if sending_client is not client:
                client.notify(data)
    
    def run(self):
        TC_IP = "127.0.0.1"
        TC_PORT = 6666
        BUFFER_SIZE = 2048

        tcpServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcpServer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        tcpServer.bind((TC_IP, TC_PORT))

        while True:
            tcpServer.listen(4)
            print("server has started. waiting for clients...")
            (conn, (ip, port)) = tcpServer.accept()
            new_thread = threadClient(ip, port, conn, self)
            new_thread.start()
            self.clients.append(new_thread)
        
        for t in self.clients:
            t.join()

if __name__ == "__main__":
    server = Server()
    server.start()


            




