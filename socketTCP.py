import socket

class SocketTCP:
    def init(self):
        self.ip = None
        self.port = None
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.seq_num = None
        self.msg = None

    def bind(address):
        pass

    def accept():
        pass

    def recv(buff_size):
        pass

    def send(message):
        pass
