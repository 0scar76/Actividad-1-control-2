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
            print("Uso: python3 Server.py <ip_server> <port_server> [(-d | --debug)] < <file_name>")
            sys.exit(0)
    else:
        print("Uso: python3 Server.py <ip_server> <port_server> [(-d | --debug)] < <file_name>")
        sys.exit(0)
    
    message = sys.stdin.read()

    if debug:
        print("Creando socketTCP...")
    server_socketTCP = socketTCP.SocketTCP(debug=debug)
    if debug:
        print("socketTCP creado")
        print("Bindeando y aceptando")
    server_socketTCP.bind(server_address)
    connection_socketTCP, new_address = server_socketTCP.accept()

    # primero deberia recibir el test del archivo
    if debug:
        print("Recibiendo el archivo...")
    buff_size = len(message.encode())//2 if len(message.encode()) % 2 == 0 else len(message.encode())//2 + 1
    message_part_1 = connection_socketTCP.recv(buff_size)
    message_part_2 = connection_socketTCP.recv(buff_size)
    print("File test received:", message_part_1 + message_part_2)
    if (message_part_1 + message_part_2) == message.encode(): print("File test: Passed")
    else: print("File test: Failed")

    if debug:
        print("Termine de recibir el archivo")
        print("Voy a recibir el test 1")

    # test 1
    buff_size = 16
    full_message = connection_socketTCP.recv(buff_size)
    print("Test 1 received:", full_message)
    if full_message == "Mensje de len=16".encode(): print("Test 1: Passed")
    else: print("Test 1: Failed")

    if debug:
        print("Termine de recibir el test 1")
        print("Voy a recibir el test 2")

    # test 2
    buff_size = 19
    full_message = connection_socketTCP.recv(buff_size)
    print("Test 2 received:", full_message)
    if full_message == "Mensaje de largo 19".encode(): print("Test 2: Passed")
    else: print("Test 2: Failed")

    if debug:
        print("Termine de recibir el test 2")
        print("Voy a recibir el test 3")

    # test 3
    buff_size = 14
    message_part_1 = connection_socketTCP.recv(buff_size)
    message_part_2 = connection_socketTCP.recv(buff_size)
    print("Test 3 received:", message_part_1 + message_part_2)
    if (message_part_1 + message_part_2) == "Mensaje de largo 19".encode(): print("Test 3: Passed")
    else: print("Test 3: Failed")

    if debug:
        print("Termine de recibir las pruebas, verificar que todas hayan pasado")

    if debug:
        print("Voy a cerrar conexion")
    connection_socketTCP.close()