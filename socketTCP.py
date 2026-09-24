import socket
import random

class SocketTCP:
    def init(self):
        self.ip = None
        self.port = None
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.seq_num = None
        self.msg = None

    def parse_segment(message):
        SYN = 0
        ACK = 0
        FIN = 0

        flags = message[0]
        if (flags == 4) or (flags == 6):
            SYN = 1
        if (flags == 2) or (flags == 3) or (flags == 6):
            ACK = 1
        if (flags == 1) or (flags == 3):
            FIN = 1

        seq = message[1:5]

        data = message[5:len(message)]

        parsed_message = {
            "SYN": SYN,
            "ACK": ACK,
            "FIN": FIN,
            "seq": seq,
            "data": data
        }
        return parsed_message

    def create_segment(parsed_message):
        flags = 0
        if parsed_message["SYN"]:
            if parsed_message["ACK"]:
                flags = 6
            else:
                flags = 4
        elif parsed_message["ACK"]:
            if parsed_message["FIN"]:
                flags = 3
            else:
                flags = 2
        elif parsed_message["FIN"]:
            flags = 1
        flags = flags.to_bytes(1)

        seq = parsed_message["seq"]

        data = parsed_message["data"]

        final_message = flags + seq + data
        return final_message

    def connect(address):
        data = {
            "msg": "",
            "seq": f"{random.randint(0, 100)}"
        }
        return data

    def bind(address):
        pass

    def accept():
        pass

    def recv(buff_size):
        pass

    def send(message):
        pass