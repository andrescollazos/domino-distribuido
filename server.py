# Autores:
# Andrés Felipe Lopez
# Caroina Raigosa Hernandez
# Felipe Ramirez

# coding=utf-8
import socket
import time
import pygame
import sys
import threading
import random

# Clase para las fichas, tiene que ver con la logica de llenado
# El jugador solo recibe una orden de pintar una ficha en una posición
class Ficha:
    # Iniciar
    def __init__(self, ficha, pos = ("", "")):
        ficha = ficha.split(",")
        self.valor_izq = ficha[0]   # Valor superior
        self.valor_der = ficha[1]   # Valor Inferior
        self.ficha_izq = None         # Ficha que tiene al lado del valor superior
        self.ficha_der = None         # Fichaque tiene al lado del valor inferior
        self.parada = None
        self.pos_izq = pos[0]
        self.pos_der = pos[1]

    # Metodo para imprimir el objeto por pantalla:
    def __str__(self):
        return self.valor_izq + "," + self.valor_der

    # Metodo para retornar el objeto:
    def retFicha(self):
        return self.valor_izq + "," + self.valor_der + ";" + self.pos_izq + ";" + self.pos_der

class TimeServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.servidor_tiempo = time.time()
        self.continuar = True # Ciclo de juego
        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self.server_sock.bind((host, port))
        except socket.error as e:
            print(str(e))
            sys.exit()

        self.server_sock.listen(10)
        self.iniciado = False
        self.limite_jugadores = 4
        self.lista_conexiones = [self.server_sock]
        self.jugadores = 0
        self.lista_jugadores = {}# Diccionario de jugadores con sus sockets
        self.lista_turnos = []   # Lista de turnos (Orden de los turnos)
        self.tiene_turno = ""    # Conocer quien tiene el turno
        self.primer_turno = True # Verificar primera jugada como 6:6
        self.numero_pasos = 0    # Si se reciben 4 mensaje de paso de turno se determina el ganador
        #self.dim_pantalla = "900,600" # Es decision del jugador escoger sus dimensiones
        self.fichas = []
        self.fichas_jugadas = [] # Fichas jugadas en tablero
        self.fichas_jugadores = []
        #for ficha in self.fichas:
        #    print ficha ," :", self.fichas[ficha]

    # Este metodo permite iniciar el servidor, genera las fichas del juego y
    # recibe las conexiones
    def iniciar(self):
        print "* SERVER DICE: Generar fichas de juego..."
        for i in range(7):
            for j in range(7):
                ficha = str(i) + "," + str(j)
                if not(ficha in self.fichas or (str(j) + "," + str(i)) in self.fichas):
                    #ruta_imagen = str(i) + ".png," + str(j) + ".png"
                    self.fichas.append(ficha)
                    print "#",
        print "\n* SERVER DICE: Fichas generadas correctamente..."
        print self.fichas
        self.fichas_temporales = self.fichas

        print "* SERVER DICE: Esperando jugadores {0}:{1}".format(self.host, self.port)
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
        try:
            new_sock, addr = self.server_sock.accept() # Recibe peticion de conexion
        except:
            self.server_sock.close()
        if self.jugadores < self.limite_jugadores: # Comprueba la cantidad de jugadores
            print "* SERVER DICE: Recibida conexion de Jugador #{1} : {0}".format(addr, self.jugadores + 1)
            self.lista_conexiones.append(new_sock)
            self.jugadores = self.jugadores + 1
            self.sincronizar()  # Cada que se recibe una nueva conexion, el servidor
                                # utiliza el algoritmo de Berkeley para sincronizar
                                # la hora local de los jugadores.
        else:
            print "* SERVER DICE: NO SE ACEPTAN MAS CONEXIONES"
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
        print "* SERVER DICE: NUEVO TIEMPO: {0}".format(tiempo_acumulado)
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
        print "* SERVER DICE: Lista de Jugadores: "
        #print self.lista_jugadores
        for jugador in self.lista_jugadores:
            print "\t* ", jugador #, ":", self.lista_jugadores[jugador]

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
            # Guardar registro de las fichas
            registro = [llave, fichas_jugador]
            self.fichas_jugadores.append(registro)
            sock_jugador = self.lista_jugadores[llave]
            ack = "" # Acuse de recibo
            if sock_jugador != self.server_sock:
                # Enviar dimensiones de la pantalla y fichas del jugador
                #print "MANDANDO EL INIT A: ", llave
                while not(ack == "ack"):
                    print "* SERVER DICE: Jugador ", llave, " no ha inciado correctamente..."
                    sock_jugador.send("init " + fichas_jugador)
                    ack = sock_jugador.recv(1024)
                print "* SERVER DICE: Jugador ", llave, " inicio correctamente, creando hilo..."
            # Una vez iniciado el conjunto de jugadores, se procede a llamar al metodo
            # juego(), el cual permite la interaccion con cada uno de los jugadores
            jugador = threading.Thread(target = self.juego, args = (llave, ))
            hilos.append(jugador)

        print "* SERVER DICE: COMENZANDO JUEGO..."
        print "* FICHAS POR JUGADOR: "
        for fichas_jug in self.fichas_jugadores:
            print "\t* Jugador ", fichas_jug[0], ": \n\t\t* ", fichas_jug[1]
        time.sleep(7)
        for hilo in hilos:
            hilo.start() # Iniciar hilo

    # Metodo para dar la orden a los jugadores que coloquen una ficha en sus tableros
    def colocar(self, ficha): # ficha -> Es la que el servidor va a ordenar que todos coloquen
        mensaje = ""
        # Si se trata de la primera jugada, la ficha tendra una posicion valida
        if len(ficha.pos_izq) > 0 and len(ficha.pos_der) > 0:
            mensaje = "coloque " + ficha.retFicha()
            #return mensaje
            #sock.send(mensaje)
        else:
            # Comprobar si se puede colocar una ficha
            print "* SERVER DICE: Buscando encajar jugada ", ficha.valor_izq, ":", ficha.valor_der
            for fich in self.fichas_jugadas:
                print "  * Comparar con Ficha: ", fich.valor_izq, ":", fich.valor_der, "--->"
                # Cuando hay una ficha con el lado superior libre:
                if fich.ficha_izq == None:
                    print "\t* Disponible lado izquierdo ..."
                    if fich.valor_izq == ficha.valor_izq:
                        print "\t* Lado izquierdo con cuerda con lado izquierdo de ficha!"
                        fich.ficha_izq = ficha # La ficha ya colocada referencia esta nueva

                        # Calcular la posicion de la nueva ficha:
                        print "\t* Posicion Ficha: ", fich.pos_izq, " tipo: ", type(fich.pos_izq)
                        pos_sup = fich.pos_izq.split(",")
                        ficha.pos_izq = str(int(pos_sup[0]) - 34) + "," + str(pos_sup[1])
                        ficha.pos_der = str(int(pos_sup[0]) - 68) + "," + str(pos_sup[1])
                        ficha.ficha_izq = fich
                        mensaje = "coloque " + ficha.retFicha()
                        break

                    elif fich.valor_izq == ficha.valor_der:
                        print "\t* Lado izquierdo con cuerda con lado derecho de ficha!"
                        fich.ficha_izq = ficha

                        # Calcular la posicion de la nueva ficha:
                        print "\t* Posicion Ficha: ", fich.pos_izq, " tipo: ", type(fich.pos_izq)
                        pos_sup = fich.pos_izq.split(",")
                        ficha.pos_der = str(int(pos_sup[0]) - 34) + "," + str(pos_sup[1])
                        ficha.pos_izq = str(int(pos_sup[0]) - 68) + "," + str(pos_sup[1])
                        ficha.ficha_der = fich
                        mensaje = "coloque " + ficha.retFicha()
                        break

                # Cuando hay una ficha con el lado inferior libre:
                elif fich.ficha_der == None:
                    print "\t* Disponible lado derecho ..."
                    if fich.valor_der == ficha.valor_izq:
                        print "\t* Lado derecho con cuerda con lado izquierdo de ficha!"
                        fich.ficha_der = ficha

                        # Calcular la posicion de la nueva ficha:
                        print "\t* Posicion Ficha: ", fich.pos_der, " tipo: ", type(fich.pos_der)
                        pos_der = fich.pos_der.split(",")
                        ficha.pos_izq = str(int(pos_der[0])) + "," + str(int(pos_der[1]) + 34)
                        ficha.pos_der = str(int(pos_der[0])) + "," + str(int(pos_der[1]) + 68)
                        ficha.ficha_izq = fich
                        mensaje = "coloque " + ficha.retFicha()
                        break
                    elif fich.valor_der == ficha.valor_der:
                        print "\t* Lado derecho con cuerda con lado derecho de ficha!"
                        fich.ficha_der = ficha

                        # Calcular la posicion de la nueva ficha:
                        print "\t* Posicion Ficha: ", fich.pos_der, " tipo: ", type(fich.pos_der)
                        pos_der = fich.pos_der.split(",")
                        ficha.pos_izq = str(int(pos_der[0])) + "," + str(int(pos_der[1]) + 68)
                        ficha.pos_der = str(int(pos_der[0])) + "," + str(int(pos_der[1]) + 34)
                        ficha.ficha_der = fich
                        mensaje = "coloque " + ficha.retFicha()
                        break

        # Agregar a la lista de fichas jugadas:
        #if not(ficha in self.fichas_jugadas):
        if len(mensaje) > 0:
            self.fichas_jugadas.append(ficha)
            return mensaje
        else:
            return "desaprobado ."

    def juego(self, llave):
        sock = self.lista_jugadores[llave]
        # Mandar quien posee el turno
        while self.continuar:
            # El servidor verifica que si el hilo del jugador posea el turno
            if llave == self.tiene_turno:
                time.sleep(2) # Regular la velocidad de los hilos para no generar inconsistencias
                jugada = ""
                while not(jugada != "ack" and jugada != ''):
                    sock.send("turno .") # Enviar orden de que realice una jugada
                    jugada = sock.recv(1024) # Esperar la jugada
                jugada = jugada.split(" ")
                #print "Enviado TURNO a ", llave
                print "* SERVER DICE: Jugador ", llave, " quiere realizar la jugada: ", jugada

                # Realizar la jugada
                if jugada[0] == 'jugada':
                    self.numero_pasos = 0
                    # Verificar que se trate de la primera jugada:
                    if self.primer_turno:
                        while self.primer_turno:
                            if jugada[1] == '6,6':
                                mensaje = self.colocar(Ficha(jugada[1], ('400,50', '400,80')))
                                print "* SERVER DICE: Mensaje a enviar -> ", mensaje
                                for sock_jug in self.lista_jugadores:
                                    nom = sock_jug
                                    sock_jug = self.lista_jugadores[sock_jug]
                                    # Enviar el mensaje de colocar la ficha
                                    # No continua la ejecucion hasta no recibir un ack
                                    ack = "" # Acuse de recibo
                                    while not(ack == "ack"):
                                        print "\t* Mandado a ", nom ," ..."
                                        sock_jug.send(mensaje)
                                        ack = sock_jug.recv(1024)
                                        print "\t* Recibiendo ack ? : ", ack, " ..."

                                self.primer_turno = False
                                # Eliminar ficha del registro de fichas:
                                for fich in self.fichas_jugadores:
                                    if fich[0] == llave:
                                        fich[1] = fich[1].replace('6,6', '')
                            else:
                                sock.send("desaprobado primera")
                                jugada = sock.recv(1024).split(" ")
                    else:
                        mensaje = self.colocar(Ficha(jugada[1]))
                        if mensaje != "desaprobado .":
                            print "* SERVER DICE: Mensaje a enviar --> ", mensaje
                            for sock_jug in self.lista_jugadores:
                                nom = sock_jug
                                sock_jug = self.lista_jugadores[sock_jug]
                                # No continua la ejecucion hasta no recibir un ack
                                ack = "" # Acuse de recibo
                                while not(ack == "ack"):
                                    print "\t* Mandando a ", nom, " ..."
                                    sock_jug.send(mensaje)
                                    ack = sock_jug.recv(1024)
                                    print "\t* Recibiendo ack ? : ", ack, " ..."
                            # Eliminar ficha del registro de fichas:
                            for fich in self.fichas_jugadores:
                                if fich[0] == llave:
                                    fich[1] = fich[1].replace(jugada[1], '')

                                    # Si la longitud de la cadena de fichas es igual a 7
                                    # es decir ";;;;;;;" es porque ya tiro todas sus fichas
                                    # Y debe ser declarado Ganador del juego
                                    if len(fich[1]) == 7:
                                        mensaje = "GANO " + llave
                                        print "* SERVER DICE: Ganador de la partida: ", llave
                                        # Informar a todos los Jugadores que hay un ganador
                                        for sock_jug in self.lista_jugadores:
                                            nom = sock_jug
                                            sock_jug = self.lista_jugadores[sock_jug]
                                            ack = ""
                                            while not(ack == "ack"):
                                                print "\t* Mandando a ", nom, "..."
                                                sock_jug.send(mensaje)
                                                ack = sock_jug.recv(1024)
                                                print "\t* Recibiendo ack ? : ", ack, " ..."
                                        # Cerrar la conexion
                                        self.continuar = False
                        else:
                            # Enviar mensaje de desaprobacion:
                            sock.send(mensaje)
                elif jugada[0] == 'PASO':
                    self.numero_pasos += 1
                    mensaje = ""
                    # Ningun jugador puede hacer una jugada, se determinara el ganador:
                    if self.numero_pasos == self.limite_jugadores:
                        print "* SERVER DICE: No hay más posibilidades de jugadas ..."
                        print "\t* BUSCANDO EL QUE TENGA EL MENOR PUNTAJE EN SUS FICHAS ..."
                        puntos = [-1, -1, -1, -1]
                        # Realizar la sumatoria de los puntos de todos los jugadores
                        for i, fich in enumerate(self.fichas_jugadores):
                            print "\t* Jugador ", fich[0], " puntos:",
                            # Obtener los numeros de la cadena de las fichas del jugador i
                            cad_fichas = fich[1].replace(";", ",").split(",")
                            puntos[i] = 0
                            for num in cad_fichas:
                                try:
                                    num = int(num)
                                except:
                                    num = 0
                                puntos[i] += num
                            print puntos[i], self.fichas_jugadores[i][0]
                        # Encontrar el menor
                        menor = puntos[0] # Se parte del hecho que el menor esta en la primera posicion
                        for i, elem in enumerate(puntos):
                            if elem < menor and (elem >= 0):
                                menor = elem
                        llave_v = self.fichas_jugadores[puntos.index(menor)][0]
                        mensaje = "GANO " + llave_v
                        print "* SERVER DICE: Ganador de la partida: ", llave_v
                        # Informar a todos los Jugadores que hay un ganador
                        for sock_jug in self.lista_jugadores:
                            nom = sock_jug
                            sock_jug = self.lista_jugadores[sock_jug]
                            ack = ""
                            while not(ack == "ack"):
                                print "\t* Mandando a ", nom, "..."
                                sock_jug.send(mensaje)
                                ack = sock_jug.recv(1024)
                                print "\t* Recibiendo ack ? : ", ack, " ..."
                        # Cerrar la conexion
                        self.continuar = False


                # No cambia de turno hasta que el jugador no haga una jugada balida
                if mensaje != "desaprobado .":
                    # Entregar el turno a alguien mas
                    act = self.lista_turnos.index(llave) # Saber la posicion del jugador
                    # En caso de que sea el ultimo de la lista, dar el turno al primero
                    if act == len(self.lista_turnos) - 1:
                        self.tiene_turno = self.lista_turnos[0]
                    else:
                        # En caso contrario pasar al jugador que llego despues
                        self.tiene_turno = self.lista_turnos[act + 1]
                    print "* SERVER DICE: Enviare el turno a : ", self.tiene_turno
                    time.sleep(2)
            else:
                # En caso de no tener el turno, el servidor enviara al jugador
                # el nombre del jugador que tiene el turno
                sock.send("posee " + self.tiene_turno)
                time.sleep(2)
        self.server_sock.close()

if __name__ == '__main__':
    server = TimeServer(str(sys.argv[1]), int(sys.argv[2]))
    server.iniciar()
#    exit()
