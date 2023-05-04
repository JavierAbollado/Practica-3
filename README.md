Comienzo de creación del README final de las ramas **conexion_gamma**, **sala_control** y **sala_control_2**.

# Práctica 3 - Juego multijugador (2 jugadares)

 - **Francisco Javier Abollado**
 - **David Parro Plaza**
 - **Juan Alvarez Noseque ;)**
 
# Índice 

 - [Distribución de archivos](#id0)
 - [Descripción del juego](#id1)
 - [Comunicación : Player 1 - Sala - Player 2](#id2)
 - [Codificación de acciones](#id3)
 - [Extra](#id4)
      
# Distribución de archivos <a name=id0></a>

*Luego pongo alguna pequeña indicación*

 - sala.py
 - player.py
 - sprites.py
 - constantes.py
 - images/
 
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

### Sala

Controla el núcleo de juego, las acciones principales como los choques entre bloques y bolas y los choques con las palas son controlados por la sala principal. El sentido de esta modificación es que si dejamos estas acciones a los juegadores, cada vez que ocurra algo será detectado doblemente (una por cada jugador), además podría pasar que uno detecte una acción y otro no (aunque luego sería procesado por la sala al comunicarse). Esta información será pasada a los jugadores en un formato de códigos que explicaremos en la siguiente sección. 

### Player

Se encarga de checkear las acciones de su pala (moverse a izquierda o derecha). Esta información se la pasa a la sala y la sala se encarga de pasarla al otro jugador y de actualizarla en su display. Por otro lado recibe las acciones procesadas por la sala y se encarga de descodificarlas y realizar las respectivas actualizaciones necesarias.

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
