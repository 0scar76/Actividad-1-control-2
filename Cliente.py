import sys
import socketTCP

if __name__ == "__main__":
    SERVER_IP = ""
    SERVER_PORT = -1
    server_address = None
    debug = False

    if len(sys.argv) > 1:
        if len(sys.argv) == 3:
            SERVER_IP = sys.argv[1]
            SERVER_PORT = int(sys.argv[2])
            server_address = (SERVER_IP, SERVER_PORT)
        elif len(sys.argv) == 4 and sys.argv[3] in ["-d", "--debug"]:
            SERVER_IP = sys.argv[1]
            SERVER_PORT = int(sys.argv[2])
            server_address = (SERVER_IP, SERVER_PORT)
            debug = True
            print("Se activo el modo debug")
        else:
            print("Uso: python3 Cliente.py <ip_server> <port_server> [(-d | --debug)] < <file_name>")
            sys.exit(0)
    else:
        print("Uso: python3 Server.py <ip_server> <port_server> [(-d | --debug)] < <file_name>")
        sys.exit(0)
 
    message = sys.stdin.read().encode()
    if debug:
        print("Creando socketTCP...")
    client_socketTCP = socketTCP.SocketTCP(debug=debug)
    if debug:
        print("socketTCP creado")
        print(f"intentando conectar a {server_address}")
    client_socketTCP.connect(server_address)

    if debug:
        print("Voy a enviar el archivo")
    client_socketTCP.send(message)
    if debug:
        print("Termine de enviar el archivo")

    if debug:
        print("Voy a enviar las pruebas de recv y send")
    # test 1
    message = "Mensje de len=16".encode()
    client_socketTCP.send(message)
    # test 2
    message = "Mensaje de largo 19".encode()
    client_socketTCP.send(message)
    # test 3
    message = "Mensaje de largo 19".encode()
    client_socketTCP.send(message)
    if debug:
        print("Termine de enviar las pruebas, ver en el server si se recibieron bien")

    if debug:
        print("Voy a cerrar conexion")
    client_socketTCP.close()
