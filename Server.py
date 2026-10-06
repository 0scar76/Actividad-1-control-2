import socket
import socketTCP
import sys 

BUFF_SIZE = 16

if __name__ == "__main__":
    SERVER_IP = "localhost"
    SERVER_PORT = 8000
    SERVER_ADDRESS = (SERVER_IP, SERVER_PORT)
    
    server_socketTCP = socketTCP.SocketTCP()
    server_socketTCP.bind(SERVER_ADDRESS)
    print("socket creado")

    str = b""
#    print(type(str))
    while True:
        client_socket, client_address = server_socketTCP.accept()
#        print("esperando mensaje")
#        msg, add = server_socketTCP.recv(BUFF_SIZE)
#        print(f"Recibi el mensaje: {msg}")
#        str += msg
#        print(f"El archivo (por ahora) es: \n{str}")
