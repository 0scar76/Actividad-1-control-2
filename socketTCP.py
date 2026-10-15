import socket
import random

MAX_PACKET_SIZE = 16

class SocketTCP:
    def __init__(self):
        self.sckt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sckt.settimeout(5)
        self.last_send = None
        
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
        self.message_seq = random.randint(0, 100)

        first_shake = {
            "SYN": 1,
            "ACK": 0,
            "FIN": 0,
            "seq": self.message_seq,
            "data": b""
        }

        parsed_second = {
            "SYN": 0,
            "ACK": 0,
            "FIN": 0,
            "seq": self.message_seq,
            "data": b""
        }

        while parsed_second["SYN"] != 1 or parsed_second["ACK"] != 1 or parsed_second["seq"] != (self.message_seq + 1):
            self.sckt.sendto(self.create_segment(first_shake), address)
            print("envie:", first_shake)
            try:
                second_shake, server_address = self.sckt.recvfrom(5)
                parsed_second = self.parse_segment(second_shake)
                print("recibi:", parsed_second)
            except TimeoutError:
                print("no pude recibir")
                continue

        self.message_seq += 2

        third_shake = {
            "SYN": 0,
            "ACK": 1,
            "FIN": 0,
            "seq": self.message_seq,
            "data": b""
        }

        parsed_second_try = parsed_second
        
        while parsed_second == parsed_second_try:
            self.sckt.sendto(self.create_segment(third_shake), server_address)
            print("envie:", third_shake)
            try:
                second_shake_try, server_address = self.sckt.recvfrom(5)
                parsed_second_try = self.parse_segment(second_shake_try)
                print("recibi:", parsed_second_try)
            except TimeoutError:
                print("no recibi nada")
                break

        self.last_send = third_shake
        self.remote_address = server_address
        print(f"Se conecto a {address}")

    def bind(self, address):
        self.sckt.bind(address)
        self.ip, self.port = address

    def accept(self):
        parsed_first = {
            "SYN": 0,
            "ACK": 0,
            "FIN": 0,
            "seq": -1,
            "data": b""
        }

        while (parsed_first["SYN"] != 1 or parsed_first["ACK"] != 0):
            try:
                first_shake, server_address = self.sckt.recvfrom(5)
                parsed_first = self.parse_segment(first_shake)
                print("recibi:", parsed_first)
            except TimeoutError:
                print("no pude recibir")
                continue

        new_port = random.randint(8001, 9000)
        new_sckt = SocketTCP()
        new_sckt.bind((self.ip, new_port))
        self.message_seq = parsed_first["seq"] + 1

        second_shake = {
            "SYN": 1,
            "ACK": 1,
            "FIN": 0,
            "seq": self.message_seq,
            "data": b""
        }

        parsed_third = {
            "SYN": 0,
            "ACK": 0,
            "FIN": 0,
            "seq": -1,
            "data": b""
        }
        second_server = ""

        while (parsed_third["SYN"] != 0 or
                 parsed_third["ACK"] != 1 or
                 parsed_third["seq"] != self.message_seq + 1 or
                 second_server != server_address):
            new_sckt.sckt.sendto(self.create_segment(second_shake), server_address)
            print("envie:", second_shake)
            try:
                third_shake, second_server = new_sckt.sckt.recvfrom(5)
                parsed_third = self.parse_segment(third_shake)
                print("recibi:", parsed_third)
            except TimeoutError:
                print("no pude recibir")
                continue

        new_sckt.remote_address = server_address
        new_sckt.message_seq = parsed_third["seq"]
        print("se establecio conexion")
        return new_sckt, (self.ip, new_port)

    def recv(self, buff_size):
        while self.len_msg == 0:
            parsed_first = {
                "SYN": 0,
                "ACK": 0,
                "FIN": 0,
                "seq": -1,
                "data": b''
            }
            sender = ""

            while sender != self.remote_address or parsed_first["seq"] != self.message_seq:
                try:
                    first_message, sender = self.sckt.recvfrom(5 + 16)
                    parsed_first = self.parse_segment(first_message)
                    print("recibi:", parsed_first)
                    if parsed_first["FIN"] == 1:
                        self.recv_close()
                        print("se recibio mensaje de cierre")
                        return b''
                    if parsed_first["ACK"] == 1: #
                        continue
                    if parsed_first["seq"] > 0 and parsed_first["seq"] < self.message_seq and sender == self.remote_address:
                        self.sckt.sendto(self.create_segment(self.last_send), self.remote_address)
                        print("envie:", self.last_send)
                except TimeoutError:
                    continue

            self.len_msg = int.from_bytes(parsed_first["data"]) # si sali del while recibi el mensaje correcto
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

            self.last_send = first_response

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

            parsed_act = {
                "SYN": 0,
                "ACK": 0,
                "FIN": 0,
                "seq": self.message_seq - 1,
                "data": b''
            }
            sender = ""

            while sender != self.remote_address or parsed_act["seq"] != self.message_seq:
                try:
                    act_message, sender = self.sckt.recvfrom(5 + 16)
                    parsed_act = self.parse_segment(act_message)
                    print("recibi:", parsed_act)
                    if parsed_act["FIN"] == 1:
                        self.recv_close()
                        print("se recibio mensaje de cierre")
                        print("se acabo recv")
                        return b''
                    if parsed_act["seq"] < self.message_seq:
                        self.sckt.sendto(self.create_segment(self.last_send), self.remote_address)
                        print("envie:", self.last_send)
                except TimeoutError:
                    continue

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
            self.last_send = acknowledge

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

        parsed_response = {
            "SYN": 0,
            "ACK": 0,
            "FIN": 0,
            "seq": self.message_seq,
            "data": b''
        }
        sender = ""

        while sender != self.remote_address or parsed_response["seq"] != self.message_seq + len(first_message["data"]):
            self.sckt.sendto(self.create_segment(first_message), self.remote_address)
            print("envie:", first_message)
            try:
                first_response, sender = self.sckt.recvfrom(5 + 16)
                parsed_response = self.parse_segment(first_response)
                print("recibi:", parsed_response)
                if parsed_response["FIN"] == 1:
                    self.recv_close()
                    print("se recibio mensaje de cierre")
                    print("se acabo send")
                    return
                if parsed_response["SYN"] == 1 and parsed_response["ACK"] == 1:
                    self.sckt.sendto(self.create_segment(self.last_send), self.remote_address)
                    print("envie:", self.last_send)
            except TimeoutError:
                print("no recibi nada")
                continue
        
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

            parsed_response = {
                "SYN": 0,
                "ACK": 0,
                "FIN": 0,
                "seq": self.message_seq,
                "data": b""
            }
            sender = ""

            while sender != self.remote_address or parsed_response["seq"] != self.message_seq + len(chunk):
                self.sckt.sendto(self.create_segment(parsed_message), self.remote_address)
                print("envie:", parsed_message)
                try:
                    act_response, sender = self.sckt.recvfrom(5 + 16)
                    parsed_response = self.parse_segment(act_response)
                    print("recibi:", parsed_response)
                except TimeoutError:
                    print("no recibi nada")
                    continue
            
            start += MAX_PACKET_SIZE
            chunk = message[start:(start + MAX_PACKET_SIZE)]

            new_seq = parsed_response["seq"]
            self.message_seq = new_seq

        print("se acabo send")
        return 

    def close(self):
        try:
            attempts = 3
            parsed_response = {
                "SYN": 0,
                "ACK": 0,
                "FIN": 0,
                "seq": -1,
                "data": b""
            }
            sender = ""

            while (attempts > 0 and (sender != self.remote_address or parsed_response["seq"] != self.message_seq)):
                last_response, sender = self.sckt.recvfrom(5 + 16)
                parsed_response = self.parse_segment(last_response)
                print("recibi:", parsed_response)
                attempts -= 1

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

                parsed_finack = {
                    "SYN": 0,
                    "ACK": 0,
                    "FIN": 0,
                    "seq": -1,
                    "data": b""
                }
                sender = ""

                attempts = 3
                while attempts > 0 and (sender != self.remote_address or parsed_finack["seq"] != self.message_seq + 1 or parsed_finack["ACK"] != 1 or parsed_finack["FIN"] != 1):
                    self.sckt.sendto(self.create_segment(msg_close), self.remote_address)
                    print("envie:", msg_close)
                    attempts -= 1
                    try:
                        finack, sender = self.sckt.recvfrom(5 + 16)
                        parsed_finack = self.parse_segment(finack)
                        print("recibi:", parsed_finack)
                    except TimeoutError:
                        print("no recibi nada")
                        continue

                if (attempts <= 0):
                    print("Se acabaron los intentos, asumo que el otro quiere cerrar conexion")

                    self.sckt.close()
                    print("se cerro la conexion")
                    return

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

            parsed_finack = {
                "SYN": 0,
                "ACK": 0,
                "FIN": 0,
                "seq": -1,
                "data": b""
            }
            sender = ""
            
            attempts = 3
            while attempts > 0 and (sender != self.remote_address or parsed_finack["seq"] != self.message_seq + 1 or parsed_finack["ACK"] != 1 or parsed_finack["FIN"] != 1):
                self.sckt.sendto(self.create_segment(msg_close), self.remote_address)
                print("envie:", msg_close)
                attempts -= 1
                try:
                    finack, sender = self.sckt.recvfrom(5 + 16)
                    parsed_finack = self.parse_segment(finack)
                    print("recibi:", parsed_finack)
                except TimeoutError:
                    print("no recibi nada")
                    continue

            if (attempts <= 0):
                print("Se acabaron los intentos, asumo que el otro quiere cerrar conexion")

                self.sckt.close()
                print("se cerro la conexion")
                return

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

        recv_fin = {
            "SYN": 0,
            "ACK": 0,
            "FIN": 0,
            "seq": -1,
            "data": b""
        }
        sender = ""

        attempts = 3
        while attempts > 0 and (sender != self.remote_address or recv_fin["seq"] != self.message_seq + 1 or recv_fin["FIN"] != 1):
            self.sckt.sendto(self.create_segment(msg_close), self.remote_address)
            print("envie:", msg_close)
            attempts -= 1
            try:
                fin, sender = self.sckt.recvfrom(5 + 16)
                recv_fin = self.parse_segment(fin)
                print("recibi:", recv_fin)
            except TimeoutError:
                print("no recibi nada")
                continue

        if (attempts <= 0):
            print("Se acabaron los intentos, asumo que el otro quiere cerrar conexion")
        
            self.sckt.close()
            print("se cerro la conexion")
            return


        self.sckt.close()
        print("se cerro la conexion")

        return