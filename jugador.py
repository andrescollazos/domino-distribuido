# coding=utf-8
import socket
import sys
import time
import pygame
import threading

NEGRO = (0, 0, 0)
VERDE_tono1 = (25, 80, 58)
VERDE_tono2 = (23, 128, 86)
DIM = (900, 600)

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
        self.jugada = "" # Contiene la jugada que solicite
        self.fichas_jugadas = []

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
                #print "Data recibida: ", self.data
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
            if self.puntero > len(self.fichas) - 1: # Hacer recorrido ciclico
                # Debe moverse a la primera posicion:
                self.puntero = 0
        elif direccion == 'izq':
            self.puntero -= 1
            if self.puntero < 0:
                self.puntero = len(self.fichas) - 1
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

        # Mostrar las fichas que hay sobre el tablero
        for ficha in self.fichas_jugadas:
            pantalla.blit(ficha[0], ficha[1])
        pygame.display.flip()

    # Metodo que limpia la pantalla
    def limpiarPantalla(self, pantalla):
        pantalla.fill((0, 0, 0))
        pygame.draw.rect(pantalla, VERDE_tono2, [0, 0, DIM[0], 400])
        pygame.draw.rect(pantalla, VERDE_tono1, [0, 400, DIM[0], 200])
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

            # Esta orden le indica al jugador que debe enviar
            # el desface entre su hora local y la del servidor
            if jugador.data[0] == 'get':
                desface = time.time() - float(jugador.data[1])
                jugador.sock.sendall(str(desface))
                jugador.data = []

            # Esta orden le indica al jugador que debe
            # actualizar su hora local
            elif jugador.data[0] == 'post':
                tiempo_local = float(jugador.data[1])
                jugador.data = []
                print "TIEMPO NUEVO: {0}".format(tiempo_local)
                jugador.data = []

            # Esta orden le indica al jugador que ha terminado
            # Su conexion con el servidor
            elif jugador.data[0] == '':
                break

            # Esta orden le indica al jugador que debe
            # Enviar su nombre de usuario al servidor
            elif jugador.data[0] == 'name':
                try:
                    # El jugador puede pasar su nombre de usuario como un argumento
                    # al correr el programa. Ej: python jugador.py "CAROLINA"
                    usuario = str(sys.argv[1])
                except:
                    # En caso contrario el jugador ingresara por teclado su usuario.
                    usuario = raw_input("Digita tu nombre de usuario: ")
                jugador.sock.sendall(usuario)
                jugador.data = []

            # Esta orden indica que debe enviar otro nombre de usuario
            elif jugador.data[0] == 'repetido':
                usuario = raw_input("Nombre de Usuario ya existe. Escoge otro: ")
                jugador.sock.sendall(usuario)
                jugador.data = []

            # Esta orden indica que puede inciar el juego
            elif jugador.data[0] == 'init':
                pygame.init()
                print "Data inicial: ", jugador.data
                iniciar = True
                dimension = DIM #Convierte a entero
                pantalla = pygame.display.set_mode(dimension) # Crea la pantalla
                pygame.display.set_caption("DOMINO") # Nombre de la ventana
                pantalla.blit(pygame.image.load("img/inicio.png"), (0, 0)) # Imagen inicial
                pygame.display.flip()
                time.sleep(3)
                jugador.limpiarPantalla(pantalla)
                # Recibe sus fichas de juego
                print "Me tocaron las fichas: ",
                try:
                    jugador.fichas = jugador.data[1].split(";")
                    jugador.fichas.remove(jugador.fichas[0])
                except:
                    print "Ocurrio un error al recibir las fichas"
                    jugador.sock.close()
                print jugador.fichas
                jugador.mostrarFichas(pantalla)
                jugador.data = []

            # Esta orden le indica al jugador quien tiene el turno
            elif jugador.data[0] == 'posee':
                # Cambiar el poseedor del turno
                if poseedor_act != jugador.data[1]:
                    jugador.posee_turno = jugador.data[1]
                    jugador.limpiarPantalla(pantalla) # Limpiar pantalla
                    jugador.mostrarFichas(pantalla)   # Mostar las fichas
                    jugador.moverseFichas(pantalla)   # Mostrar el puntero de ficha
                    poseedor_act = jugador.data[1]
                jugador.data = []

            # Esta orden le indica al jugador que tiene el turno
            elif jugador.data[0] == 'turno':
                jugador.tengo_turno = True
                jugador.posee_turno = ""
                poseedor_act = ""
                jugador.limpiarPantalla(pantalla) # Limpiar pantalla
                jugador.mostrarFichas(pantalla)   # Mostar las fichas
                jugador.moverseFichas(pantalla)   # Mostrar el puntero de ficha
                print "Poseo el turno"#, jugador.tengo_turno
                jugador.data = []

            # Esta orden indica al jugador que coloque una ficha especifica en el tablero
            elif jugador.data[0] == 'coloque':
                print "Coloque la ficha: ", jugador.data[1], ".."
                # 6,6;400,50;400,80 Ejemplo de un data recibido
                # Colocar la ficha 6:6 en la posicion 400, 50
                data = jugador.data[1].split(";")
                ficha_d = data[0].split(",")
                sup = pygame.image.load("img/" + ficha_d[0] + ".png")
                inf = pygame.image.load("img/" + ficha_d[1] + ".png")

                pos_sup = data[1].split(",")
                pos_sup = (int(pos_sup[0]), int(pos_sup[1]))

                pos_inf = data[2].split(",")
                pos_inf = (int(pos_inf[0]), int(pos_inf[1]))

                jugador.fichas_jugadas.append((sup, pos_sup))
                jugador.fichas_jugadas.append((inf, pos_inf))

                # Quitar la ficha de las fichas del jugador
                if jugador.jugada == data[0]:
                    jugador.fichas.remove(jugador.jugada)
                    jugador.jugada = ""
                jugador.data = []

            # Esta orden indica que NO puede hacer la jugada
            elif jugador.data[0] == 'desaprobado':
                print "No puedes hacer esta jugada"
                jugador.jugada = ""
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
                        # El jugador debe tener el turno para poder hacer la jugada
                        if jugador.tengo_turno:
                            # Se selecciona la ficha que este apuntando el puntero
                            jugador.jugada = jugador.fichas[jugador.puntero]
                            print "Seleccionando: Ficha : {0} Valor: {1}".format(jugador.puntero, jugador.jugada)
                            # Mandar al servidor un mensaje de jugada
                            jugador.sock.sendall("jugada " + jugador.jugada)
                            jugador.data = []
                            jugador.tengo_turno = False # Se termina el turno
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
