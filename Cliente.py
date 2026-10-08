import socket
#import sockeTCP
import sys

MAX_PACKET_SIZE = 16

if __name__ == "__main__":
    SERVER_IP = "localhost"
    SERVER_PORT = 8000
    SERVER_ADDRESS = (SERVER_IP, SERVER_PORT)
    
    client_socket_UDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    mensaje = input("Introduzca el mensaje a enviar\n")
    flags = 6 # generico
    seq = 45 # generico
    final_mensaje = flags.to_bytes(1) + seq.to_bytes(4) + mensaje.encode("utf-8")


    start = 5
    chunk = final_mensaje[5:5+MAX_PACKET_SIZE]

    client_socket_UDP.sendto(final_mensaje[0:5], SERVER_ADDRESS)
    print("se envia el header TCP")

    while (len(chunk) != 0):
        client_socket_UDP.sendto(chunk.encode("utf-8") if type(chunk) == str else chunk, SERVER_ADDRESS)
        start += MAX_PACKET_SIZE
        chunk = final_mensaje[start:(start + MAX_PACKET_SIZE)]