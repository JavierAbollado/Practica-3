# Práctica 3 - Juego multijugador (2 jugadores)

 - **Francisco Javier Abollado**
 - **David Parro Plaza**
 - **Juan Alvarez San Romualdo**
 
# Índice 

 - [Distribución de archivos](#id0)
 - [Descripción del juego](#id1)
 - [Comunicación : Player 1 - Sala - Player 2](#id2)
 - [Codificación de acciones](#id3)
 - [Extra](#id4)
      
# Distribución de archivos <a name=id0></a>

 - sala.py: script que ejecuta la sala. Ejecución:

```
{directorio actual} python3 sala.py {ip del ordenador}
```

 - player.py: script que ejecuta cada uno de los jugadores para jugar. Ejecución:

```
{directorio actual} python3 player.py {ip del ordenador de la sala}
```

 - sprites.py: script con los objetos princpales del juego. La mayoria de ellos heredan del objeto *pygame.Sprite*.
 - constantes.py: contiene las variables globales del juego, como las velocidades de la bola y los jugadores. Así como los gráficos del juego (imagenes de los bloques, palas, y fondos).
 - images/: carpetas con las imagenes necesarias para el juego. También tenemos en el una carpeta *pruebas* dónde están los gif que observamos en este README.
 
# Descripción del juego <a name=id1></a>

Se trata de una versión modificada del Arkanoid. En ella nos encontramos 2 paletas (una para cada jugador) cada una de un color distinto, rojo y azul. Por otro lado están las bolas y los bloques que queremos destruir, los cuales ambos pueden ser de dos colores distintos, rojo y azul, siendo estos elegidos de forma aleatoria. Una vez introducido esto, definimos las siguiente reglas:

 - Cada bloque tiene 4 vidas.
 - Si una bola choca con una paleta de color *X* entonces la bola pasa a ser de dicho color. Es decir, si tenía el mismo color no sucede nada y si era del color opuesto, entonces se cambiará.
 - Un bloque solo puede ser golpeado por una bola del mismo color. Es decir, si una bola de color azul golpea a un bloque de color rojo, no sucede nada, por el contrario si la bola es de color rojo, entonces el bloque será "golpeado" y tendrá una vida menos. 
 
 Aquí podemos observar un pequeño ejemplo de cómo funcionaría:

<div style="text-align:center;">
  <image src="/images/resumen/ejemplo.gif" style="width:100%; height:12cm;">
</div>

# Comunicación : Player 1 - Sala - Player 2 <a name=id2></a>

Para tener conectados los dos jugadores y la sala principal procederemos de la siguente manera:


## Player

Se encarga de checkear las acciones de su pala (moverse a izquierda o derecha). Esta información se la pasa a la sala y la sala se encarga de pasarla al otro jugador y de actualizarla en su display. Por otro lado recibe las acciones procesadas por la sala y se encarga de descodificarlas y realizar las respectivas actualizaciones necesarias.

## Sala

Controla el núcleo de juego, las acciones principales como los choques entre bloques y bolas y los choques con las palas son controlados por la sala principal. El sentido de esta modificación es que si dejamos estas acciones a los jugadores, cada vez que ocurra algo será detectado doblemente (una por cada jugador), además podría pasar que uno detecte una acción y otro no (aunque luego sería procesado por la sala al comunicarse). Esta información será pasada a los jugadores en un formato de códigos que explicaremos en la siguiente sección. 
 
El núcleo de juego se hace en una única función *play* controlada por un solo proceso, al contrario que en la versión principal que tiene una proceso para cada jugador. Con esto aseguramos la exclusión mutua en el objeto *Game* ya que solo accede a él un único proceso. Por lo que no es necesario introducir un *Lock()* y controlar con un *acquaire()* y *release()* cada una de las funciones, ya que pasarían a ser no críticas. En el siguiente apartado, ilustraré como se consigue esta comunicación entre ambos jugadores y la sala. 
 
## Comunicación 
 
La sala comienza el juego con un proceso *game* que ejecuta el target *play()* en donde se encuentra el bucle de juego con las comunicaciones entre la sala y los jugadores. Para ello se pasa como argumento al *play* ambas conexiones para poder controlarlos. 

 ```python
game = Process(target=play, args=(connections[0], connections[1]))
game.start()
 ```
 
 **A) Parte 1 [antes del bucle de juego]**
 
   - Sala: comenzamos la partida comunicando a cada jugador su id. Para ello la sala manda un *send(id)* a ambos jugadores. 
 
   - Player: cada jugador por separado recibe su id.
 
 **B) Parte 2 [bucle de juego]**
 
 Voy a comentar las acciones por pares. Cada send() necesita en recv() por parte de la otra conexión, y viceversa, cada recv() necesita que la otra conexión le halla mandado un send() para poder recibirla. En caso de no tener esta paridad abría un problema de inanición pues uno se quedaría bloqueado esperando a recibir algo. Asi comentaremos las acciones por pares (Jn, Sn) para que se entienda qué información se está recibiendo y de dónde. Tener en cuenta que la sala hará dos envios y dos recivos por cada recivo y envio del script del player respectivamente, ya que son dos. 
 
   **J1.** Jugador manda sus eventos (movimientos de la pala o salir del juego)
 
   **S1.** Sala recibe eventos de ambos jugadores.
 
   **S2.** Sala envía eventos de un jugador al otro, respectivamente.
 
   **J2.** Jugador recibe eventos del otro jugador (enviados por la sala).
 
   **S3.** Sala actualiza eventos en el display principal. Esto es la función principal del juego **analize_events** que se encarga de comprobar todas las colisiones y golpeos de las pelotas. Una vez analizados envia los cambios a los jugadores.
 
   **J3.** Jugador recibe los cambios de la sala y los actualiza, para ello tener la función **update_from_sala** (las codificaciones y descodificaciones se explicaran en el siguiente apartado). Finalmente cada jugador hace un refresh del display para actualizar por pantalla los cambios.

<div style="text-align:center;">
  <image src="/images/resumen/sala.jpg" style="width:48%; height:15cm;">
  <image src="/images/resumen/player.jpg" style="width:48%; height:15cm;">
</div>

# Codificación de acciones <a name=id3></a>

Existen dos tipos de acciones:

### 1. Acciones sobre objetos existentes

Código: "x1-x2-x3"

donde,
   - x1 = nombre del objeto afectado: ball, block, be
   - x2 = id del objeto
   - x3 = código de la acción a realizar
   
códigos del x3 para cada objeto:
   - ball:
      - cc = change color
      - c{X} = collide, con AXIS = X
   - block:
      - gs = get shot
   - be:
      - gs = get shot (crea X=3 bolas nuevas)


### 2. Creación de nuevo objetos

Código: x1-x2 

donde, 
   - x1 = "new", 
   - x2 = nombre del nuevo objeto 

códigos de x2: 
   - be : crear el bloque especial


# Extra <a name=id4></a>

### Pruebas con el bloque especial:

El *bloque especial* es un bloque el cual si colisiona alguna bola del juego con el genera 3 bolas nuevas y este se destruye en el momento. Probamos las siguientes características en el juego para observar cómo la generación de nuevas bolas no genera problemas entre los dos jugadores, 

 - Añadir cada *x* segundos añadimos un bloque especial nuevo (si el otro se destruye).
 - Ver que los *id* no se bloquean y el random.seed(id) funciona perfectamente con un número indefinido de bolas.

<div style="text-align:center;">
  <image src="/images/resumen/colisiones_con_bloque_especial.gif" style="width:100%; height:12cm;">
</div>
