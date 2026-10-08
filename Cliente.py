import socket
import socketTCP

client_socketTCP = socketTCP.SocketTCP()
client_socketTCP.connect(("localhost", 8000))
# test 1
message = "Mensje de len=16".encode()
client_socketTCP.send(message)
# test 2
message = "Mensaje de largo 19".encode()
client_socketTCP.send(message)
# test 3
message = "Mensaje de largo 19".encode()
client_socketTCP.send(message)