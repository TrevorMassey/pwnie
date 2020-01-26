import socket
import re
from threading import Thread
import importlib
import parser


class Proxy2Server(Thread):

    def __init__(self, host, port):
        super().__init__()
        self.host, self.port = host, port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.connect((host, port))
        self.game = None

    def run(self):
        while True:
            try:
                data = self.server.recv(4096)
                if data:
                    # print(f"{self.port} <- {data[:100].hex()}")       
                    importlib.reload(parser)
                    parser.parse(data, 1)
                    self.game.sendall(data)
            except Exception as e:
                print(e)


class Game2Proxy(Thread):

    def __init__(self, host, port):
        super().__init__()
        self.server = None
        self.host, self.port = host, port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((host, port))
        self.socket.listen(1)
        print('before accept')
        self.game, self.game_addr = self.socket.accept()
        print(self.game_addr)

    def run(self):
        
        while True:
            try:
                data = self.game.recv(4096)
                if data:
                    # print(f"{self.port} -> {data[:100].hex()}")
                    importlib.reload(parser)
                    parser.parse(data, 0)
                    self.server.sendall(data)
            except Exception as e:
                print(e)


class Proxy(Thread):

    def __init__(self, from_host, to_host, port):
        super().__init__()
        self.from_host = from_host
        self.to_host = to_host
        self.port = port

    def run(self):

        while True:
            print(f"proxy{self.port} setting up")
            self.g2p = Game2Proxy(self.from_host, self.port)
            self.p2s = Proxy2Server(self.to_host, self.port)
            print(f"proxy{self.port} connected")
            self.g2p.server = self.p2s.server
            self.p2s.game = self.g2p.game

            self.g2p.start()
            self.p2s.start()


SERVER_HOST = "ec2-15-222-169-12.ca-central-1.compute.amazonaws.com"
FROM_HOST = '0.0.0.0'
FROM_HOST = socket.gethostname()
MASTER_PORT = 3333
print(FROM_HOST)
FROM_HOST = '0.0.0.0'
master_server = Proxy(FROM_HOST, SERVER_HOST, MASTER_PORT)
master_server.start()

game_servers = list()
for port in range(3000, 3006):
    _game_server = Proxy(FROM_HOST, SERVER_HOST, port)
    _game_server.start()
    game_servers.append(_game_server)

