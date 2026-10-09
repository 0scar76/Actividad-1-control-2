import socket
import random

MAX_PACKET_SIZE = 16

class SocketTCP:
    def __init__(self, sckt = None):
        if sckt is None:
            self.sckt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        else:
            self.sckt = sckt
        
        self.remote_address = None
        self.message_remaining = 0
        self.message_seq = 0
        self.recv_buffer = b""
        self.ip = None
        self.port = None

    def parse_segment(self, message):
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

        seq = int.from_bytes(message[1:5], "big")
        data = message[5:len(message)]

        parsed_message = {
            "SYN": SYN,
            "ACK": ACK,
            "FIN": FIN,
            "seq": seq,
            "data": data
        }

        return parsed_message

    def create_segment(self, parsed_message):
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
        seq = parsed_message["seq"].to_bytes(4)
        data = parsed_message["data"]
        final_message = flags + seq + data
        
        return final_message

    def connect(self, address):
        attempts = 10
        self.message_seq = random.randint(0, 100)

        first_shake = {
            "SYN": 1,
            "ACK": 0,
            "FIN": 0,
            "seq": self.message_seq,
            "data": b""
        }
        print(first_shake)
        
        self.sckt.sendto(self.create_segment(first_shake), address)
        second_shake, server_address = self.sckt.recvfrom(5)
        
        while (attempts > 0 and 
               (second_shake[0] != 6 or 
                int.from_bytes(second_shake[1:5], "big") != (self.message_seq + 1))):
            self.sckt.sendto(self.create_segment(first_shake), address)
            second_shake, server_address = self.sckt.recvfrom(5)
            attempts -= 1
        
        if (attempts > 0):
            self.message_seq += 2

            third_shake = {
                "SYN": 0,
                "ACK": 1,
                "FIN": 0,
                "seq": self.message_seq,
                "data": b""
            }
            
            self.sckt.sendto(self.create_segment(third_shake), server_address)
            self.remote_address = server_address

            print(third_shake)
        else:
            print(f"No se pudo conectar a {address}")
            
    def bind(self, address):
        self.sckt.bind(address)
        self.ip, self.port = address

    def accept(self):
        attempts = 10
        first_shake, address = self.sckt.recvfrom(5)
       
        while (attempts > 0 and first_shake[0] != 4):
            first_shake, address = self.sckt.recvfrom(5)
            attempts -= 1
        
        if (attempts > 0):
            new_port = random.randint(8001, 9000)
            new_sckt = SocketTCP() 
            new_sckt.bind((self.ip, new_port))       
 
            second_shake = {
                "SYN": 1,
                "ACK": 1,
                "FIN": 0,
                "seq": (int.from_bytes(first_shake[1:5], "big") + 1),
                "data": b""
            }
            print(second_shake)
            new_sckt.sckt.sendto(self.create_segment(second_shake), address)
        else:
            print("No se pudo aceptar una conexión")
            return

        third_shake, address = new_sckt.sckt.recvfrom(5)
        attempts = 10

        while (attempts > 0 and third_shake[0] != 2):
            third_shake, address = new_sckt.sckt.recvfrom(5)
            attempts -= 1
        
        if (attempts > 0):
            new_sckt.remote_address = address
            new_sckt.message_seq = int.from_bytes(third_shake[1:5], "big")
            return new_sckt, (self.ip, new_port)
        else:
            print("No se pudo aceptar una conexión")
            return
 
    def recv_original(self, buff_size):
        if (self.message_remaining == 0 and self.recv_buffer == b""):
            attempts = 10
            data, sender = self.sckt.recvfrom(5 + 16)

            while (attempts > 0 and sender != self.remote_address):
                data, sender = self.sckt.recvfrom(5 + 16)
                attempts -= 1

            if (attempts <= 0):
                print("No se pudo recibir un mensaje de la dirección esperada")
                return b""
                
            parsed_data = self.parse_segment(data)

            if (self.parse_segment(data)["FIN"] == 1):
                self.recv_close()
                return b""

            self.message_seq = parsed_data["seq"] + len(parsed_data["data"])
            self.message_remaining = int.from_bytes(parsed_data["data"], "big")

            acknowledge = {
                    "SYN": 0,
                    "ACK": 1,
                    "FIN": 0,
                    "seq": self.message_seq,
                    "data": b""
                    }
            
            self.sckt.sendto(self.create_segment(acknowledge), sender)

        while (len(self.recv_buffer) < buff_size and self.message_remaining > 0):
            attempts = 10
            message, messenger = self.sckt.recvfrom(5 + 16)
            
            while (attempts > 0 and messenger != self.remote_address):
                    message, messenger = self.sckt.recvfrom(5 + 16)
                    attempts -=1

            if (attempts <= 0):
                print("No se pudo recibir un mensaje de la dirección esperada")
                return b""
            
            acknowledge = {
                        "SYN": 0,
                        "ACK": 1,
                        "FIN": 0,
                        "seq": self.message_seq,
                        "data": b""
                        }

            attempts = 20
            while (attempts > 0 and
                   self.message_seq != self.parse_segment(message)["seq"]):
                self.sckt.sendto(self.create_segment(acknowledge), messenger)       
                message, messenger = self.sckt.recvfrom(5 + 16)
                while (attempts > 0 and messenger != self.remote_address):
                    message, messenger = self.sckt.recvfrom(5 + 16)
                    attempts -=1
                attempts -= 1
            
            if (attempts <= 0):
                print("No se pudo recibir un mensaje de la dirección esperada")
                return b""
            
            if (self.parse_segment(message)["FIN"] == 1):
                self.recv_close()
                return b""
 
            self.message_remaining -= len(self.parse_segment(message)["data"])
            self.message_seq += len(self.parse_segment(message)["data"])
            self.recv_buffer += self.parse_segment(message)["data"]

            acknowledge = {
                    "SYN": 0,
                    "ACK": 1,
                    "FIN": 0,
                    "seq": self.message_seq,
                    "data": b""
                    }
            
            self.sckt.sendto(self.create_segment(acknowledge), messenger)

        recived = self.recv_buffer[:buff_size]
        self.recv_buffer = self.recv_buffer[buff_size:]
        
        return recived

    def recv(self, buff_size):
        attempts = 10
        first_message, sender = self.sckt.recvfrom(5 + 16)

        while (attempts > 0 and sender != self.remote_address):
            first_message, sender = self.sckt.recvfrom(5 + 16)
            attempts -= 1

        if (attempts <= 0):
            print("No se pudo recibir un mensaje de la dirección esperada")
            return b""

        parsed_first = self.parse_segment(first_message)

        len_msg = parsed_first["data"]
        self.message_seq += len(len_msg)

        first_response = {
            "SYN": 0,
            "ACK": 1,
            "FIN": 0,
            "seq": self.message_seq,
            "data": b''
        }

        self.sckt.sendto(self.create_segment(first_response), self.remote_address)

        message = b''
        while (len(message) != min(int.from_bytes(len_msg), buff_size)):
            attempts = 10
            act_message, sender = self.sckt.recvfrom(5 + 16)
    
            while (attempts > 0 and sender != self.remote_address):
                act_message, sender = self.sckt.recvfrom(5 + 16)
                attempts -= 1
    
            if (attempts <= 0):
                print("No se pudo recibir un mensaje de la dirección esperada")
                return b""

            parsed_act = self.parse_segment(act_message)
            message += parsed_act["data"]
            self.message_seq += len(parsed_act["data"])

            acknowledge = {
                "SYN": 0,
                "ACK": 1,
                "FIN": 0,
                "seq": self.message_seq,
                "data": b''
            }

            self.sckt.sendto(self.create_segment(acknowledge), self.remote_address)

        return message

    def send(self, message):
        msg_len = len(message)

        first_message = {
            "SYN": 0,
            "ACK": 0,
            "FIN": 0,
            "seq": self.message_seq,
            "data": msg_len.to_bytes()
        }

        self.sckt.sendto(self.create_segment(first_message), self.remote_address)

        attempts = 10
        first_response, sender = self.sckt.recvfrom(5 + 16)

        while (attempts > 0 and sender != self.remote_address):
            first_response, sender = self.sckt.recvfrom(5 + 16)
            attempts -= 1

        if (attempts <= 0):
            print("No se pudo enviar un mensaje de la dirección esperada")
            return

        parsed_response = self.parse_segment(first_response)
        new_seq = parsed_response["seq"]
        self.message_seq = new_seq
        
        start = 0
        chunk = message[0:MAX_PACKET_SIZE]

        while (start < msg_len):

            parsed_message = {
                "SYN": 0,
                "ACK": 0,
                "FIN": 0,
                "seq": self.message_seq + start,
                "data": chunk.encode("utf-8") if type(chunk) == str else chunk
            }

            final_message = self.create_segment(parsed_message)
            self.sckt.sendto(final_message, self.remote_address)
            start += MAX_PACKET_SIZE
            chunk = message[start:(start + MAX_PACKET_SIZE)]

        return 

    def close(self):

        msg_close = {
            "SYN": 0,
            "ACK": 0,
            "FIN": 1,
            "seq": self.message_seq,
            "data": b''
        }

        msg_close = self.create_segment(msg_close)
        self.sckt.sendto(msg_close, self.remote_address)

        attempts = 10
        finack, _ = self.sckt.recvfrom(5)

        while (attempts > 0 and int.from_bytes(finack[0]) != 3):
                    finack, _ = self.sckt.recvfrom(5)
                    attempts -= 1

        if (attempts > 0):
            self.parse_segment(finack)



    def recv_close(self):

        msg_close = {
            "SYN": 0,
            "ACK": 1,
            "FIN": 1,
            "seq": self.message_seq,
            "data": b''
        }

        msg_close = self.create_segment(msg_close)

        pass
