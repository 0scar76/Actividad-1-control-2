import socket
import sockeTCP
impost sys

if __name__ == "__main__":

    if len(sys.argv) == 4:
        ip = sys.argv[1]
        port = sys.argv[2]
        message = sys.argv[3]
    
    else:
        print("Uso: python3 cliente.py <ip-servidor> <puerto> <mensaje>")
        sys.exit(0)
