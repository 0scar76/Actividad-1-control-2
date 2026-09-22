import socket
import socketTCP
import sys

MAX_PACKET_SIZE = 16

if __name__ == "__main__":
    SERVER_IP = "arenarium"
    SERVER_PORT = "8000"
    SERVER_ADRESS = (SERVER_IP, SERVER_PORT)
    
    client_socket_UDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    if len(sys.argv) == 4:
        ip = sys.argv[1]
        port = sys.argv[2] 
    else:
        print("Uso: python3 cliente.py <ip-servidor> <puerto>")
        sys.exit(0)

    mensaje = input("Introduzca el mensaje a enviar")
    mensaje = mensaje.encode("utf-8")

    iteration = 0
    chunk = mensaje[iteration:(iteration + MAX_PACKET_SIZE)]

    while (len(chunk) != 0):
           client_socket_UDP.sendto(chunk, SERVER_ADRESS)
