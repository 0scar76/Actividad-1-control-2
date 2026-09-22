import socket
#import sockeTCP
import sys

MAX_PACKET_SIZE = 16

if __name__ == "__main__":
    SERVER_IP = "localhost"
    SERVER_PORT = 8000
    SERVER_ADRESS = (SERVER_IP, SERVER_PORT)
    
    client_socket_UDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    mensaje = input("Introduzca el mensaje a enviar\n")
    mensaje = mensaje.encode("utf-8")

    start = 0
    chunk = mensaje[0:MAX_PACKET_SIZE]

    while (len(chunk) != 0):
           client_socket_UDP.sendto(chunk, SERVER_ADRESS)
           start += MAX_PACKET_SIZE
           chunk = mensaje[start:(start + MAX_PACKET_SIZE)]
           print(start)
           print(chunk)