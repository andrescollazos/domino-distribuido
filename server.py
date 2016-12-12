import socket
import time
import pygame
import sys
import threading
import random

class TimeServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.servidor_tiempo = time.time()
        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self.server_sock.bind((host, port))
        except socket.error as e:
            print(str(e))
            sys.exit()

        self.server_sock.listen(10)
        self.limite_jugadores = 3
        self.lista_conexiones = [self.server_sock]
        self.jugadores = 0
        self.lista_jugadores = {}
        self.lista_turnos = []
        self.tiene_turno = ""
        self.dim_pantalla = "800,600"
        self.fichas = []
        #for ficha in self.fichas:
        #    print ficha ," :", self.fichas[ficha]

    # Este metodo permite iniciar el servidor, genera las fichas del juego y
    # recibe las conexiones
    def iniciar(self):
        print "Generar fichas de juego..."
        for i in range(7):
            for j in range(7):
                ficha = str(i) + "," + str(j)
                if not(ficha in self.fichas or (str(j) + "," + str(i)) in self.fichas):
                    #ruta_imagen = str(i) + ".png," + str(j) + ".png"
                    self.fichas.append(ficha)
                    print "#",
        print "\nFichas generadas correctamente..."
        print self.fichas
        self.fichas_temporales = self.fichas

        print "Esperando jugadores {0}:{1}".format(self.host, self.port)
        try:
            while True:
                self.aceptar_conexion()
        except socket.error as e:
            print "Error ", # coding=utf-8
        finally:
            self.server_sock.close()

    # Este metodo acepta o rechaza una conexion, el servidor acepta una conexion
    # cuando aun no se ha completado la cantidad maxima de jugadores, que son 4
    # el servidor rechaza la conexion cuando hay ya cuatro jugadores
    def aceptar_conexion(self):
        new_sock, addr = self.server_sock.accept() # Recibe peticion de conexion
        if self.jugadores < self.limite_jugadores: # Comprueba la cantidad de jugadores
            print "Recibida conexion de Jugador #{1} : {0}".format(addr, self.jugadores + 1)
            self.lista_conexiones.append(new_sock)
            self.jugadores = self.jugadores + 1
            self.sincronizar()  # Cada que se recibe una nueva conexion, el servidor
                                # utiliza el algoritmo de Berkeley para sincronizar
                                # la hora local de los jugadores.
        else:
            print "NO SE ACEPTAN MAS CONEXIONES"
            new_sock.send("")

    # Metodo basado en el algoritmo de Berkeley para la sincronizacion de la hora local
    # de los jugadores
    def sincronizar(self):
        tiempo_acumulado = 0
        tiempo_local = time.time()
        for sock in self.lista_conexiones:
            if sock != self.server_sock:
                inicio = time.time()
                # El servidor envia su tiempo local al jugador
                sock.send("get " + str(time.time()))
                # Este lo responde con el desface
                cliente_desface = float(sock.recv(4094))
                fin = time.time()
                # Se agrega el tiempo que se demora en enviar y recibir la solicitud
                cliente_desface += ((fin - inicio) / 2)
                tiempo_acumulado += tiempo_local + cliente_desface
        print "NUEVO TIEMPO: {0}".format(tiempo_acumulado)
        avg = (tiempo_acumulado + tiempo_local) / (len(self.lista_conexiones))
        for sock in self.lista_conexiones:
            if sock != self.server_sock:
                sock.send("post " + str(avg))

        # En el caso de que se llegue al maximo de conexiones permitidas, el servidor
        # dara inciio a la partida llamando al metodo iniciar_partida()
        if self.jugadores == self.limite_jugadores:
            self.iniciar_partida()

    # Este metodo recolecta la informacion basica para iniciar la partida.
    # Le pregunta a todos los conectado que nombre de usuario van a usar
    # en caso de que este ya este, el servidor seguira preguntando hasta obtener
    # un nombre valido
    def iniciar_partida(self):
        for sock in self.lista_conexiones:
            if sock != self.server_sock:
                sock.send("name .")
                nombre_jugador = sock.recv(1024)
                while nombre_jugador in self.lista_jugadores:
                    sock.send("repetido .")
                    nombre_jugador = sock.recv(1024)

                self.lista_jugadores.update({nombre_jugador:sock})
                self.lista_turnos.append(nombre_jugador)

        # MOSTRAR EN EL SERVIDOR LOS JUGADORES QUE SE CONECTARON
        print "Lista de Jugadores: "
        #print self.lista_jugadores
        for jugador in self.lista_jugadores:
            print jugador, ":", self.lista_jugadores[jugador]

        # Se mandan las configuraciones inciales de manera secuencial:
        # Dimension de la pantalla de juego
        # 7 dominos para cada uno de los jugadores
        cantidad_fichas = len(self.fichas)
        hilos = []
        for sock_jugador in self.lista_jugadores:
            fichas_jugador = "" # Cadena que contiene las fichas
            for i in range(7):
                # Se genera una posicion random en el arreglo de fichas
                posicion = random.randrange(cantidad_fichas)
                # Se va generando una cadena que luciria asi:
                # Ejemplo: El jugador tendra las fichas cero y cero, la uno y cero,
                # la seis y cero, la tres y cuatro, etc... Se representa:
                # fichas_jugador = "0,0;1,0;6,0;3,4;4,5;6,6;2,1"
                fichas_jugador += ";" + self.fichas[posicion]

                # El jugador que tenga la ficha 6,6 es el primero en comenzar
                if self.fichas[posicion] == '6,6':
                    self.tiene_turno = sock_jugador

                self.fichas.remove(self.fichas[posicion])
                cantidad_fichas -= 1
            #print "Fichas del Jugador: ", sock_jugador
            #print fichas_jugador

            llave = sock_jugador
            sock_jugador = self.lista_jugadores[llave]
            if sock_jugador != self.server_sock:
                # Enviar dimensiones de la pantalla y fichas del jugador
                sock_jugador.send("init " + self.dim_pantalla + " " + fichas_jugador)

            # Una vez iniciado el conjunto de jugadores, se procede a llamar al metodo
            # juego(), el cual permite la interaccion con cada uno de los jugadores
            jugador = threading.Thread(target = self.juego, args = (llave, ))
            hilos.append(jugador)

        time.sleep(6)
        for hilo in hilos:
            hilo.start() # Iniciar hilo

    def juego(self, llave):
        sock = self.lista_jugadores[llave]
        # Mandar quien posee el turno
        while True:
            # El servidor verifica que si el hilo del jugador posea el turno
            if llave == self.tiene_turno:
                time.sleep(2)
                sock.send("turno .") # Enviar orden de que realice una jugada
                print "Enviado TURNO a ", llave
                jugada = sock.recv(1024) # Esperar la jugada
                print "Quieres realizar la jugada: ", jugada

                # Entregar el turno a alguien mas
                act = self.lista_turnos.index(llave) # Saber la posicion del jugador
                # En caso de que sea el ultimo de la lista, dar el turno al primero
                if act == len(self.lista_turnos) - 1:
                    self.tiene_turno = self.lista_turnos[0]
                else:
                    # En caso contrario pasar al jugador que llego despues
                    self.tiene_turno = self.lista_turnos[act + 1]
                print "Enviare el nuevo turno a : ", self.tiene_turno
            else:
                # En caso de no tener el turno, el servidor enviara al jugador
                # el nombre del jugador que tiene el turno
                sock.send("posee " + self.tiene_turno)
                time.sleep(2)

if __name__ == '__main__':
    server = TimeServer('localhost', 3000)
    server.iniciar()
