import socket
import random

MAX_PACKET_SIZE = 16

class SocketTCP:
    def __init__(self):
        self.sckt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sckt.settimeout(5)
        
        self.remote_address = None
        self.message_remaining = b''
        self.len_msg = 0
        self.len_sended = 0
        self.message_seq = 0
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

        seq = int.from_bytes(message[1:5])
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
                int.from_bytes(second_shake[1:5]) != (self.message_seq + 1))):
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
                "seq": (int.from_bytes(first_shake[1:5]) + 1),
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
            new_sckt.message_seq = int.from_bytes(third_shake[1:5])
            return new_sckt, (self.ip, new_port)
        else:
            print("No se pudo aceptar una conexión")
            return

    def recv(self, buff_size):
        if self.len_msg == 0:
            attempts = 10
            first_message, sender = self.sckt.recvfrom(5 + 16)

            while (attempts > 0 and sender != self.remote_address):
                first_message, sender = self.sckt.recvfrom(5 + 16)
                attempts -= 1

            if (attempts <= 0):
                print("No se pudo recibir un mensaje de la dirección esperada")
                return b""
            parsed_first = self.parse_segment(first_message)
            print("recibi:", parsed_first)

            if self.message_seq != parsed_first["seq"]:
                print(self.message_seq)
                print(parsed_first["seq"])
    
                print("No coincide el numero de secuencia (1)")
                return b''

            if parsed_first["FIN"] == 1:
                self.recv_close()
                print("se recibio mensaje de cierre")
                return b''

            self.len_msg = int.from_bytes(parsed_first["data"])
            self.message_seq += len(parsed_first["data"])

            first_response = {
                "SYN": 0,
                "ACK": 1,
                "FIN": 0,
                "seq": self.message_seq,
                "data": b''
            }

            self.sckt.sendto(self.create_segment(first_response), self.remote_address)
            print("envie:", first_response)

        message = b''
        while (len(message) != min(self.len_msg, buff_size)):
            if self.message_remaining != b'':
                if len(self.message_remaining) >= min(self.len_msg, buff_size):
                    message += self.message_remaining[0:min(self.len_msg, buff_size)]
                    self.message_remaining = self.message_remaining[min(self.len_msg, buff_size):]
                else:
                    message += self.message_remaining
                    self.message_remaining = b''
                continue

            attempts = 10
            act_message, sender = self.sckt.recvfrom(5 + 16)
    
            while (attempts > 0 and sender != self.remote_address):
                act_message, sender = self.sckt.recvfrom(5 + 16)
                attempts -= 1
    
            if (attempts <= 0):
                print("No se pudo recibir un mensaje de la dirección esperada")
                return b""

            parsed_act = self.parse_segment(act_message)
            print("recibi:", parsed_act)

            if self.message_seq != parsed_act["seq"]:
                print(self.message_seq)
                print(parsed_act["seq"])
    
                print("No coincide el numero de secuencia (2)")
                return b''

            if parsed_act["FIN"] == 1:
                self.recv_close()
                print("se recibio mensaje de cierre")
                return b''

            if len(parsed_act["data"] + message) > min(self.len_msg, buff_size):
                self.message_remaining = parsed_act["data"][min(self.len_msg, buff_size) - len(message):]
                message += parsed_act["data"][0:min(self.len_msg, buff_size) - len(message)]
            else:
                message += parsed_act["data"]
            self.message_seq += len(parsed_act["data"])
            self.len_sended += len(message)

            acknowledge = {
                "SYN": 0,
                "ACK": 1,
                "FIN": 0,
                "seq": self.message_seq,
                "data": b''
            }

            self.sckt.sendto(self.create_segment(acknowledge), self.remote_address)
            print("envie:", acknowledge)

            if self.len_sended >= self.len_msg:
                self.len_msg = 0
                self.len_sended = 0
                break

        print("se acabo recv")
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
        print("envie:", first_message)

        attempts = 10
        first_response, sender = self.sckt.recvfrom(5 + 16)

        while (attempts > 0 and sender != self.remote_address):
            first_response, sender = self.sckt.recvfrom(5 + 16)
            attempts -= 1

        if (attempts <= 0):
            print("No se pudo enviar un mensaje de la dirección esperada")
            return

        parsed_response = self.parse_segment(first_response)
        print("recibi:", parsed_response)

        if parsed_response["seq"] != self.message_seq + len(first_message["data"]):
            print(self.message_seq)
            print(len(first_message["data"]))
            print(parsed_response["seq"])
            print(self.message_seq + len(first_message["data"]))

            print("No coincide el numero de secuencia (1)")
            return
        
        new_seq = parsed_response["seq"]
        self.message_seq = new_seq
        
        start = 0
        chunk = message[0:MAX_PACKET_SIZE]

        while (start < msg_len):
            parsed_message = {
                "SYN": 0,
                "ACK": 0,
                "FIN": 0,
                "seq": self.message_seq,
                "data": chunk.encode("utf-8") if type(chunk) == str else chunk
            }

            final_message = self.create_segment(parsed_message)
            self.sckt.sendto(final_message, self.remote_address)
            print("envie:", parsed_message)

            attempts = 10
            act_response, sender = self.sckt.recvfrom(5 + 16)
    
            while (attempts > 0 and sender != self.remote_address):
                act_response, sender = self.sckt.recvfrom(5 + 16)
                attempts -= 1
    
            if (attempts <= 0):
                print("No se pudo enviar un mensaje de la dirección esperada")
                return

            parsed_response = self.parse_segment(act_response)
            print("recibi:", parsed_response)

            if parsed_response["seq"] != self.message_seq + len(chunk):
                print(self.message_seq)
                print(len(first_message["data"]))
                print(parsed_response["seq"])
                print(self.message_seq + len(first_message["data"]))

                print("No coincide el numero de secuencia (2)")
                return

            
            start += MAX_PACKET_SIZE
            chunk = message[start:(start + MAX_PACKET_SIZE)]

            new_seq = parsed_response["seq"]
            self.message_seq = new_seq

        print("se acabo send")
        return 

    def close(self):
        try:
            attempts = 3
            last_response, sender = self.sckt.recvfrom(5 + 16)

            while (attempts > 0 and sender != self.remote_address):
                last_response, sender = self.sckt.recvfrom(5 + 16)
                attempts -= 1

            if (attempts <= 0):
                print("No se pudo recibir un mensaje de la dirección esperada")
                return

            parsed_response = self.parse_segment(last_response)
            print("recibi:", parsed_response)

            if parsed_response["seq"] != self.message_seq:
                print(self.message_seq)
                print(parsed_response["seq"])

                print("No coincide el numero de secuencia (1)")
                return

            self.message_seq += 1
            if parsed_response["FIN"] == 0:
                print("yo hago el cierre")

                msg_close = {
                    "SYN": 0,
                    "ACK": 0,
                    "FIN": 1,
                    "seq": self.message_seq,
                    "data": b''
                }

                self.sckt.sendto(self.create_segment(msg_close), self.remote_address)
                print("envie:", msg_close)

                attempts = 3
                finack, sender = self.sckt.recvfrom(5 + 16)

                while (attempts > 0 and sender != self.remote_address and parsed_finack["seq"] != self.message_seq + 1):
                    finack, sender = self.sckt.recvfrom(5 + 16)
                    attempts -= 1

                if (attempts <= 0):
                    print("Se acabaron los intentos, asumo que el otro quiere cerrar conexion")

                    self.sckt.close()
                    print("se cerro la conexion")
                    return

                parsed_finack = self.parse_segment(finack)
                print("recibi:", parsed_finack)

                self.message_seq = parsed_finack["seq"] + 1

                acknowledge = {
                    "SYN": 0,
                    "ACK": 1,
                    "FIN": 0,
                    "seq": self.message_seq,
                    "data": b''
                }

                self.sckt.sendto(self.create_segment(acknowledge), self.remote_address)
                print("envie:", acknowledge)

                self.sckt.close()
                print("se cerro la conexion")

            else: # yo no hago el cierre, quedo algo pendiente pero yo no quiero mas
                self.recv_close()
        except TimeoutError:
            print("yo hago el cierre")

            msg_close = {
                "SYN": 0,
                "ACK": 0,
                "FIN": 1,
                "seq": self.message_seq,
                "data": b''
            }

            self.sckt.sendto(self.create_segment(msg_close), self.remote_address)
            print("envie:", msg_close)

            attempts = 3
            finack, sender = self.sckt.recvfrom(5 + 16)

            while (attempts > 0 and sender != self.remote_address and parsed_finack["seq"] != self.message_seq + 1):
                finack, sender = self.sckt.recvfrom(5 + 16)
                attempts -= 1

            if (attempts <= 0):
                print("Se acabaron los intentos, asumo que el otro quiere cerrar conexion")

                self.sckt.close()
                print("se cerro la conexion")
                return

            parsed_finack = self.parse_segment(finack)
            print("recibi:", parsed_finack)

            self.message_seq = parsed_finack["seq"] + 1

            acknowledge = {
                "SYN": 0,
                "ACK": 1,
                "FIN": 0,
                "seq": self.message_seq,
                "data": b''
            }

            self.sckt.sendto(self.create_segment(acknowledge), self.remote_address)
            print("envie:", acknowledge)

            self.sckt.close()
            print("se cerro la conexion")

        return

    def recv_close(self):
        print("yo recibo el cierre")

        msg_close = {
            "SYN": 0,
            "ACK": 1,
            "FIN": 1,
            "seq": self.message_seq,
            "data": b''
        }

        self.sckt.sendto(self.create_segment(msg_close), self.remote_address)
        print("envie:", msg_close)

        attempts = 10
        fin, sender = self.sckt.recvfrom(5 + 16)

        while (attempts > 0 and sender != self.remote_address):
            fin, sender = self.sckt.recvfrom(5 + 16)
            attempts -= 1

        if (attempts <= 0):
            print("No se pudo recibir un mensaje de la dirección esperada")
            return

        recv_fin = self.parse_segment(fin)
        print("recibi:", recv_fin)

        self.sckt.close()
        print("se cerro la conexion")

        return
