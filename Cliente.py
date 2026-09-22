import socket
import socketTCP
import sys

MAX_PACKET_SIZE = 16 

if __name__ == "__main__":
    if len(sys.argv) == 4:
        ip = sys.argv[1]
        port = sys.argv[2] 
    else:
        print("Uso: python3 cliente.py <ip-servidor> <puerto>")
        sys.exit(0)

    mensaje = input("Introduzca el mensaje a enviar")
    mensaje = mensaje.encode("utf-8")