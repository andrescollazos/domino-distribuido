# coding=utf-8
import socket
import sys
import time
import pygame
import threading

NEGRO = (0, 0, 0)
VERDE_tono1 = (25, 80, 58)
VERDE_tono2 = (23, 128, 86)

# Se crea una clase para trabajar mejor con los hilos
class Jugador:
    def __init__(self):
        self.username = ""  # Nombre de usuario
        self.fichas = ""    # Fichas que posee
        self.puntero = 0    # Cuadrado que indica en que ficha esta parado
        self.data = ""      # Informacion recibida del servidor
        self.continuar = True # Ciclo del juego
        # Socket que comunica el jugador con el servidor
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.posee_turno = "" # Quien posee el turno (cadena)
        # Variable que indica si se tiene el turno. Esta variable la usamos para
        # bloquear desde el lado del jugador, aunque se modificase esta varible
        # por parte del jugador. El servidor, confirmaria si de verdad tiene el
        # turno o no.
        self.tengo_turno = False

    # Metodo que permite la conexion entre el jugador y el servidor
    def conectarse(self, host, port):
        print "Conectandose a {0}:{1}".format(host, port)
        try:
            self.sock.connect((host, port)) # Establecer conexion
        except socket.error as e:
            print(str(e))
        try:
            # Ciclo para permanente recepcion y envio de informacion al servidor
            while True:
                # El jugador puede recibir diferentes mensajes:
                # [orden, argumentos] -> Es la forma de los mensajes que se reciben
                self.data  = self.sock.recv(1000).split(' ')
                if self.data[0] == "": # Si se recibe mensaje vacio se termina el juego
                    self.continuar = False
                    break
        except:
            print "ERROR"
            #print(str(e))
        finally:
            print "Cerrando la conexion!"
            self.sock.close()

    # Metodo que permite mover el puntero que indica que ficha va a ser seleccionada
    def moverseFichas(self, pantalla, direccion = ''):
        imagen_puntero = pygame.image.load("img/puntero.png") # Cargar imagen
        if direccion == 'der':
            self.puntero += 1
            if self.puntero > len(self.fichas): # Hacer recorrido ciclico
                # Debe moverse a la primera posicion:
                self.puntero = 0
        elif direccion == 'izq':
            self.puntero -= 1
            if self.puntero < 0:
                self.puntero = len(self.fichas)
        posicion = (50 + self.puntero*65, 400)
        pantalla.blit(imagen_puntero, posicion)
        pygame.display.flip()

    # Metodo que permite mostrar las fichas que el jugador posee en un momento dado
    def mostrarFichas(self, pantalla):
        for i, ficha in enumerate(self.fichas):
            ficha = ficha.split(",")
            # Cargar imagenes de las fichas
            ruta_ficha00 = "img/" + ficha[0] + ".png"
            ruta_ficha01 = "img/" + ficha[1] + ".png"

            # Ubicar un cuadrado de bajo de otro para formar la ficha
            posicion00 = (50 + i*65, 425)
            posicion01 = (50 + i*65, 505)

            ficha00, ficha01 = pygame.image.load(ruta_ficha00), pygame.image.load(ruta_ficha01)
            # Hacer que la imagen sea mas grande
            ficha00 = pygame.transform.scale(ficha00, [60, 80])
            ficha01 = pygame.transform.scale(ficha01, [60, 80])

            pantalla.blit(ficha00, posicion00)
            pantalla.blit(ficha01, posicion01)
            pygame.display.flip()

    # Metodo que limpia la pantalla
    def limpiarPantalla(self, pantalla):
        pantalla.fill((0, 0, 0))
        pygame.draw.rect(pantalla, VERDE_tono2, [0, 0, 800, 400])
        pygame.draw.rect(pantalla, VERDE_tono1, [0, 400, 800, 200])
        indicaciones = pygame.image.load("img/indicaciones.png")

        fuente = pygame.font.Font(None, 20)
        # Indicar quien tiene el turno.
        # Si sale "El jugador posee el turno", es que la persona que esta jugando
        # tiene el turno actualmente.
        texto = "El jugador " + self.posee_turno + " posee el turno"
        texto = fuente.render(texto, 1, NEGRO)

        pantalla.blit(texto, (10, 5))
        pantalla.blit(indicaciones, (515, 425))
        pygame.display.flip()

# En caso de que un jugador intente tirar una ficha o pasar el turno, cuando no
# tenga el turno, se mostrara la siguiente advertencia
def mostrarAdvertencia(pantalla):
    advertencia = pygame.image.load("img/advertencia.png")
    pantalla.blit(advertencia, (100, 50))
    pygame.display.flip()

# MAIN del juego
def main():
    jugador = Jugador() # Crear objeto jugador
    iniciar = False     # Variable que indica que el juego va a comenzar
    poseedor_act = ""   # Conocer quien tiene actualmente el turno

    # Se busca que el jugador pueda interactuar con su juego de manera continua
    # Pero al establecer la conexion con el servidor, mientras recibe datos, esto
    # es bloqueante. Es por esto que tiramos un hilo para interactuar con el servidor
    conexion = threading.Thread(target = jugador.conectarse, args = ('localhost', 3000))
    conexion.start() # Iniciar hilo

    while jugador.continuar:
        #print " NO ME BLOQUEO ----"
        # El jugador puede recibir diferentes mensajes:
        # [orden, argumentos] -> Es la forma de los mensajes que se reciben
        if type(jugador.data) == type([]) and len(jugador.data) > 0: # Se debe comprobar que el data sea una lista
            if jugador.data[0] == 'get':# Esta orden le indica al jugador que debe enviar
                                # el desface entre su hora local y la del servidor
                desface = time.time() - float(jugador.data[1])
                jugador.sock.sendall(str(desface))
                jugador.data = []
            elif jugador.data[0] == 'post': # Esta orden le indica al jugador que debe
                                    # actualizar su hora local
                tiempo_local = float(jugador.data[1])
                jugador.data = []
                print "TIEMPO NUEVO: {0}".format(tiempo_local)
                jugador.data = []
            elif jugador.data[0] == '': # Esta orden le indica al jugador que ha terminado
                break           # Su conexion con el servidor
            elif jugador.data[0] == 'name': # Esta orden le indica al jugador que debe
                                    # Enviar su nombre de usuario al servidor
                try:
                    # El jugador puede pasar su nombre de usuario como un argumento
                    # al correr el programa. Ej: python jugador.py "CAROLINA"
                    usuario = str(sys.argv[1])
                except:
                    # En caso contrario el jugador ingresara por teclado su usuario.
                    usuario = raw_input("Digita tu nombre de usuario: ")
                jugador.sock.sendall(usuario)
                jugador.data = []
            elif jugador.data[0] == 'repetido': # Esta orden indica que debe enviar otro nombre de usuario
                usuario = raw_input("Nombre de Usuario ya existe. Escoge otro: ")
                jugador.sock.sendall(usuario)
                jugador.data = []
            elif jugador.data[0] == 'init': # Esta orden indica que puede inciar el juego
                pygame.init()
                print "Data inicial: ", jugador.data
                iniciar = True
                dimension = jugador.data[1].split(",") # Recibe las dimensiones de la pantalla
                dimension = (int(dimension[0]), int(dimension[1])) #Convierte a entero
                pantalla = pygame.display.set_mode(dimension) # Crea la pantalla
                pygame.display.set_caption("DOMINO") # Nombre de la ventana
                pantalla.blit(pygame.image.load("img/inicio.png"), (0, 0)) # Imagen inicial
                pygame.display.flip()
                time.sleep(3)
                jugador.limpiarPantalla(pantalla)
                # Recibe sus fichas de juego
                print "Me tocaron las fichas: ",
                jugador.fichas = jugador.data[2].split(";")
                jugador.fichas.remove(jugador.fichas[0])
                print jugador.fichas
                jugador.mostrarFichas(pantalla)
                jugador.data = []
            elif jugador.data[0] == 'posee':
                # Cambiar el poseedor del turno
                if poseedor_act != jugador.data[1]:
                    jugador.posee_turno = jugador.data[1]
                    jugador.limpiarPantalla(pantalla) # Limpiar pantalla
                    jugador.mostrarFichas(pantalla)   # Mostar las fichas
                    jugador.moverseFichas(pantalla)   # Mostrar el puntero de ficha
                    poseedor_act = jugador.data[1]
                jugador.data = []
            elif jugador.data[0] == 'turno':
                jugador.tengo_turno = True
                jugador.posee_turno = ""
                poseedor_act = ""
                jugador.limpiarPantalla(pantalla) # Limpiar pantalla
                jugador.mostrarFichas(pantalla)   # Mostar las fichas
                jugador.moverseFichas(pantalla)   # Mostrar el puntero de ficha
                print "HE RECIBIDO EL TURNO", jugador.tengo_turno
                jugador.data = []
        if iniciar:
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
                        jugador.limpiarPantalla(pantalla)
                        jugador.mostrarFichas(pantalla)
                        jugador.moverseFichas(pantalla, 'izq')
                    # Mover izquierda!
                    if event.key == pygame.K_RIGHT:
                        print "Moviendo a la der"
                        jugador.limpiarPantalla(pantalla)
                        jugador.mostrarFichas(pantalla)
                        jugador.moverseFichas(pantalla, 'der')
                    # Jugar ficha!
                    if event.key == pygame.K_RETURN:
                        if jugador.tengo_turno:
                            print "Seleccionando Ficha"
                            jugador.sock.sendall("FICHA")
                            jugador.data = []
                            jugador.tengo_turno = False
                        else:
                            print "No tienes el turno"
                            mostrarAdvertencia(pantalla)
                    # Pasar turno
                    if event.key == pygame.K_p:
                        if jugador.tengo_turno:
                            print "Pasando el turno"
                            jugador.sock.sendall("PASO")
                            jugador.data = []
                            jugador.tengo_turno = False
                        else:
                            print "No tienes el turno no puedes pasar"
                            mostrarAdvertencia(pantalla)
                # En caso de soltar una tecla
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT:
                        pass
                    if event.key == pygame.K_RIGHT:
                        pass


if __name__ == '__main__':
    main()
