import socket
import socketTCP
import sys

MAX_PACKET_SIZE = 16

if __name__ == "__main__":
    SERVER_IP = "localhost"
    SERVER_PORT = 8000
    SERVER_ADDRESS = (SERVER_IP, SERVER_PORT)
    
    client_socketTCP = socketTCP.SocketTCP()
    client_socketTCP.connect(SERVER_ADDRESS)
    
#    mensaje = input("Introduzca el mensaje a enviar\n")
#    mensaje = mensaje.encode("utf-8")
#    
#    if len(mensaje) > 11:
#        print("Mensaje muy largo")
#        sys.exit(0)
#    
#    start = 0
#    chunk = mensaje[0:MAX_PACKET_SIZE]
#
#    while (len(chunk) != 0):
#        client_socketTCP.send(chunk)
#        start += MAX_PACKET_SIZE
#        chunk = mensaje[start:(start + MAX_PACKET_SIZE)]
#        print(start)
#        print(chunk)
