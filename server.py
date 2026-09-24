import socket
import socketTCP
import sys

if __name__ = "__main__":
    SERVER_IP = "arenarium"
    SERVER_PORT = "8000"
    SERVER_ADRESS = (SERVER_IP, SERVER_PORT)
    
    server_socket_UDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket_UDP.bind(SERVER_ADRESS)

    while true:

