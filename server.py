import socket
import time

class TimeServer:
    def __init__(self, host, port):
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
        print "Esperando conexiones {0}:{1}".format(host, port)

    def iniciar(self):
        try:
            while True:
                self.aceptar_conexion()
        except socket.error as e:
            print "Error ", # coding=utf-8
        finally:
            self.server_sock.close()

    def sincronizar(self):
        tiempo_acumulado = 0
        tiempo_local = time.time()
        for sock in self.lista_conexiones:
            if sock != self.server_sock:
                inicio = time.time()
                sock.send("get " + str(time.time())) # send current time
                cliente_desface = float(sock.recv(4094))
                fin = time.time()
                cliente_desface += ((fin - inicio) / 2) # + (time of sending)
                tiempo_acumulado += tiempo_local + cliente_desface
                #print "client offset: {0}".format(cliente_desface)
        #print "current_time: {0}".format(tiempo_local)
        print "NUEVO TIEMPO: {0}".format(tiempo_acumulado)
        print "CANTIDAD DE JUGADORES: ", self.jugadores
        avg = (tiempo_acumulado + tiempo_local) / (len(self.lista_conexiones))
        for sock in self.lista_conexiones:
            if sock != self.server_sock:
                sock.send("post " + str(avg))

        if self.jugadores == self.limite_jugadores:
            self.iniciar_partida()

    def aceptar_conexion(self):
        new_sock, addr = self.server_sock.accept()
        if self.jugadores < self.limite_jugadores:
            print "Nueva conexion de {0}".format(addr)
            self.lista_conexiones.append(new_sock)
            self.jugadores = self.jugadores + 1
            self.sincronizar()
        else:
            print "NO SE ACEPTAN MAS CONEXIONES"
            new_sock.send("")

    def iniciar_partida(self):
        #print "Lista de conectados:"
        #print self.lista_conexiones
        for sock in self.lista_conexiones:
            if sock != self.server_sock:
                sock.send("name .")
                nombre_jugador = sock.recv(1024)
                self.lista_jugadores.update({nombre_jugador:sock})

        print "Lista de Jugadores: "
        #print self.lista_jugadores
        for jugador in self.lista_jugadores:
            print jugador, ":", self.lista_jugadores[jugador]

if __name__ == '__main__':
    server = TimeServer('localhost', 5000)
    server.iniciar()
