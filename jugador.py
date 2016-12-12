# coding=utf-8
import socket
import sys
import time
import pygame

NEGRO = (0, 0, 0)
VERDE_tono1 = (25, 80, 58)
VERDE_tono2 = (23, 128, 86)

def limpiarPantalla(pantalla):
    pantalla.fill((0, 0, 0))
    pygame.draw.rect(pantalla, VERDE_tono2, [0, 0, dimension[0], int(dimension[1]*(2.0/3))])
    pygame.draw.rect(pantalla, VERDE_tono1, [0, int(dimension[1]*(2.0/3)), dimension[0], int(dimension[1]*(1.0/3))])
    indicaciones = pygame.image.load("img/indicaciones.png")
    pantalla.blit(indicaciones, (515, 425))
    pygame.display.flip()

def mostrarFichas(pantalla, fichas):
    for i, ficha in enumerate(fichas):
        ficha = ficha.split(",")
        ruta_ficha00 = "img/" + ficha[0] + ".png"
        ruta_ficha01 = "img/" + ficha[1] + ".png"

        posicion00 = (50 + i*65, 425)
        posicion01 = (50 + i*65, 505)

        ficha00, ficha01 = pygame.image.load(ruta_ficha00), pygame.image.load(ruta_ficha01)
        ficha00 = pygame.transform.scale(ficha00, [60, 80])
        ficha01 = pygame.transform.scale(ficha01, [60, 80])

        pantalla.blit(ficha00, posicion00)
        pantalla.blit(ficha01, posicion01)
        pygame.display.flip()

if __name__ == '__main__':
    host, port = 'localhost', 3000

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print "Conectandose a {0}:{1}".format(host, port)
    try:
        sock.connect((host, port))
    except socket.error as e:
        print(str(e))
    try:
        continuar, iniciar = True, False
        while continuar:
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
                iniciar = True
                dimension = data[1].split(",") # Recibe las dimensiones de la pantalla
                dimension = (int(dimension[0]), int(dimension[1])) #Convierte a entero
                pantalla = pygame.display.set_mode(dimension) # Crea la pantalla
                pygame.display.set_caption("DOMINO") # Nombre de la ventana
                pantalla.blit(pygame.image.load("img/inicio.png"), (0, 0)) # Imagen inicial
                pygame.display.flip()
                time.sleep(3)
                limpiarPantalla(pantalla)
                # Recibe sus fichas de juego
                #print "Me tocaron las fichas: ",
                fichas = data[2].split(";")
                fichas.remove(fichas[0])
                #print fichas
                mostrarFichas(pantalla, fichas)

            if iniciar:
                if data[0] == 'turno':
                    print "YO TENGO EL TURNO"
                else:
                    print "NO TENGO EL TURNO. Ome"
                for event in pygame.event.get():
                    # EN CASO DE CERRAR LA PESTAÑA
                    if event.type == pygame.QUIT:
                        continuar = False
                        # Completar
                    # MOVIMIENTO ENTRE LAS FICHAS
                    if event.type == pygame.KEYDOWN:
                        # Mover derecha:
                        if event.key == pygame.K_LEFT:
                            print "Moviendo a la izq"
                        # Mover izquierda!
                        if event.key == pygame.K_RIGHT:
                            print "Moviendo a la der"
                        # Jugar ficha!
                        if event.key == pygame.K_RETURN:
                            print "Seleccionando Ficha"
                        # Pasar turno
                        if event.key == pygame.K_p:
                            print "Pasando el turno"
                    # En caso de soltar una tecla
                    if event.type == pygame.KEYUP:
                        if event.key == pygame.K_LEFT:
                            pass
                        if event.key == pygame.K_RIGHT:
                            pass

    except socket.error as e:
        print(str(e))
    finally:
        print "Cerrando la conexion!"
        sock.close()
