import socket
import time
import pygame
import sys
import threading

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
        self.dim_pantalla = "800,600"
        self.fichas = {}
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
                    ruta_imagen = str(i) + ".png," + str(j) + ".png"
                    self.fichas.update({ficha:ruta_imagen})
                    print "#",
        print "\nFichas generadas correctamente..."

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

        # MOSTRAR EN EL SERVIDOR LOS JUGADORES QUE SE CONECTARON
        print "Lista de Jugadores: "
        #print self.lista_jugadores
        for jugador in self.lista_jugadores:
            print jugador, ":", self.lista_jugadores[jugador]

        # Una vez iniciado el conjunto de jugadores, se procede a llamar al metodo
        # juego(), el cual permite la interaccion con cada uno de los jugadores
        for sock_jugador in self.lista_jugadores:
            # Se crea un hilo de juego para cada uno de los jugadores
            jugador = threading.Thread(target = self.juego, args = (sock_jugador, ))
            jugador.start() # Iniciar hilo

    def juego(self, sock):
        # El sock que es recibido, es la llave que apunta al socket en el conjunto de
        # jugadores, nos interesa trabajar con el socket, no con la llave.
        llave = sock
        sock = self.lista_jugadores[llave]

        # Se la manda al jugador las dimensiones de la pantalla del juego
        if sock != self.server_sock:
            sock.send("init " + self.dim_pantalla)

if __name__ == '__main__':
    server = TimeServer('localhost', 3000)
    server.iniciar()
