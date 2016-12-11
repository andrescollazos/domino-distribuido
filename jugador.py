import socket
import sys
import time
import pygame

if __name__ == '__main__':
    host, port = 'localhost', 3000

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print "Conectandose a {0}:{1}".format(host, port)
    try:
        sock.connect((host, port))
    except socket.error as e:
        print(str(e))
    try:
        while True:
            # El jugador puede recibir diferentes mensajes:
            # [orden, argumentos] -> Es la forma de los mensajes que se reciben
            data  = sock.recv(1000).split(' ')
            #print "Recibiendo del servidor: {0}".format(data)
            if data[0] == 'get':# Esta orden le indica al jugador que debe enviar
                                # el desface entre su hora local y la del servidor
                desface = time.time() - float(data[1])
                sock.sendall(str(desface))
            elif data[0] == 'post': # Esta orden le indica al jugador que debe
                                    # actualizar su hora local
                tiempo_local = float(data[1])
                print "TIEMPO NUEVO: {0}".format(tiempo_local)
            elif data[0] == '': # Esta orden le indica al jugador que ha terminado
                break           # Su conexion con el servidor
            elif data[0] == 'name': # Esta orden le indica al jugador que debe
                                    # Enviar su nombre de usuario al servidor
                try:
                    # El jugador puede pasar su nombre de usuario como un argumento
                    # al correr el programa. Ej: python jugador.py "CAROLINA"
                    usuario = str(sys.argv[1])
                except:
                    # En caso contrario el jugador ingresara por teclado su usuario.
                    usuario = raw_input("Digita tu nombre de usuario: ")
                sock.sendall(usuario)
            elif data[0] == 'repetido': # Esta orden indica que debe enviar otro nombre de usuario
                usuario = raw_input("Nombre de Usuario ya existe. Escoge otro: ")
                sock.sendall(usuario)
            elif data[0] == 'init': # Esta orden indica que puede inciar el juego
                pygame.init()
                dimension = data[1].split(",") # Recibe las dimensiones de la pantalla
                dimension = (int(dimension[0]), int(dimension[1])) #Convierte a entero
                pantalla = pygame.display.set_mode(dimension) # Crea la pantalla
                pygame.display.set_caption("DOMINO") # Nombre de la ventana
                pantalla.blit(pygame.image.load("img/inicio.png"), (0, 0)) # Imagen inicial
                pygame.display.flip()

                # Recibe sus fichas de juego


    except socket.error as e:
        print(str(e))
    finally:
        print "Cerrando la conexion!"
        sock.close()
