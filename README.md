# JUEGO DE DOMINO DISTRIBUIDO

## Imagenes del juego

* Servidor:
![servidor] (img/screenshots/server.png)

* Jugador desde terminal:
![jugador] (img/screenshots/jugador-term.png)

* Jugador parte grafica:
![jugadorG] (img/screenshots/jugador-1.png)

![jugadorG] (img/screenshots/jugador-2.png)

## Dependencias:
* Python
* Pygame
* Threading

## Objetivo  
El objetivo es desarrollar una aplicación software para un juego de dominó distribuido, de manera que los participantes puedan jugar en red desde su máquina como si fuera un juego centralizado.

### Reglas del juego
Existen diversas versiones del juego del dominó. No obstante, ya que se trata de un juego conocido, el objetivo no es presentar con profundidad todos detalles inherentes al juego, sino determinar el conjunto de reglas básicas que serán aplicadas en la implementación del presente proyecto.

Naturalmente, el objetivo de un jugador es ganar la partida conforme los criterios que se presentan a continuación. Las reglas de juego que serán aplicadas son las siguientes:

* Los participantes van a jugar individualmente (en algunas versiones manuales de dominó, los jugadores se pueden agrupar en parejas aquí no es el caso).

* Cuando un participante ingresa al juego se le solicita nombre de usuario (los demás participantes podrán ver el nombre de los demás jugadores).

* El juego inicia una vez que cuatro jugadores hayan expresado su interés en participar en una partida, dicha partida consta de 28 fichas de dominó las cuales serán repartidas al azar (7 fichas a cada participante), debe existir un bloqueo para cualquier otro participante que desee ingresar al juego hasta que no se termine la partida actual.

* Cada jugador se le asignará un número entre 1 y 4 según orden de llegada. La partida la iniciará el jugador que tenga doble-seis (seis puntos en el lado derecho de la ficha y seis puntos en el lado izquierdo de la ficha); cuando un participante hace una jugada el turno se asignará en orden ascendente cíclico (Si la jugada la hace el jugador 2 el turno será para el jugador 3 y así sucesivamente, cuando la jugada la haga el participante 4 el turno iniciará nuevamente en el jugador 1.).

* En su turno, cada jugador colocará una de sus piezas con la restricción de que dos piezas solo pueden colocarse juntas cuando los cuadrados adyacentes (seguidos) son del mismo valor.

* Si se da el caso en que un jugador no puede colocar ninguna ficha en su turno, tendrá que pasar el turno al siguiente jugador.

* Cuando un jugador no tiene el turno, la opción de jugar es BLOQUEANTE.

* Todos los jugadores deben conocer quién tiene el turno.

* El final del juego estará determinada por dos situaciones: (A) el caso en que un jugador coloque la última de sus fichas y, por lo tanto, ganará la partida. (B) todos los jugadores tienen aún fichas, pero ninguno puede colocar ninguna de ellas. En este último caso, ganará la partida el jugador que tenga la menor suma de puntos en sus fichas.

### Licencia
El CODIGO FUENTE es publicado bajo la licencia [GNU GENERAL PUBLIC LICENSE Version 3](LICENSE)
