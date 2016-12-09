import socket
import sys
import time

if __name__ == '__main__':
    host, port = 'localhost', 5000

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print "Conectandose a {0}:{1}".format(host, port)
    try:
        sock.connect((host, port))
    except socket.error as e:
        print(str(e))
    try:
        while True:
            data  = sock.recv(1000).split(' ')
            #print "Recibiendo tiempo del servidor: {0}".format(data)
            if data[0] == 'get':
                desface = time.time() - float(data[1])
                #print "Tiempo local: {0}".format(desface)
                sock.sendall(str(desface))
                #print "Enviando tiempo al servidor"
            elif data[0] == 'post':
                tiempo_local = float(data[1])
                print "TIEMPO NUEVO: {0}".format(tiempo_local)
            elif data[0] == '':
                break
            elif data[0] == 'name':
                try:
                    usuario = str(sys.argv[1])
                except:
                    usuario = raw_input("Digita tu nombre de usuario: ")
                sock.sendall(usuario)
            elif data[0] == 'repetido':
                usuario = raw_input("Nombre de Usuario ya existe. Escoge otro: ")
                sock.sendall(usuario)


    except socket.error as e:
        print(str(e))
    finally:
        print "Cerrando la conexion!"
        sock.close()
