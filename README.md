Comienzo de creación del README final de las ramas **conexion_gamma**, **sala_control** y **sala_control_2**.

# Práctica 3 - Juego multijugador (2 players)

 - **Francisco Javier Abollado**
 - **David Parro Plaza**
 - **Juan Alvarez Noseque ;)**
 
## Descripción del juego

Se trata de una versión modificada del Arkanoid. En ella nos encontramos 2 paletas (una para cada jugador) cada una de un color distinto, rojo y azul. Por otro lado están las bolas y los bloques que queremos destruir, los cuales ambos pueden ser de dos colores distintos, rojo y azul, siendo estos elegidos de forma aleatoria. Una vez introducido esto, definimos las siguiente reglas:

 - Cada bloque tiene 4 vidas.
 - Si una bola choca con una paleta de color *X* entonces la bola pasa a ser de dicho color. Es decir, si tenía el mismo color no sucede nada y si era del color opuesto, entonces se cambiará.
 - Un bloque solo puede ser golpeado por una bola del mismo color. Es decir, si una bola de color azul golpea a un bloque de color rojo, no sucede nada, por el contrario si la bola es de color rojo, entonces el bloque será "golpeado" y tendrá una vida menos. 
 
 Aquí podemos observar un pequeño ejemplo de cómo funcionaría:

<div style="text-align:center;">
  <image src="/images/resumen/ejemplo.gif" style="width:100%; height:12cm;">
</div>

## Codificación de acciones

## Extra 

### Pruebas con el bloque especial:

El *bloque especial* es un bloque el cual si colisiona alguna bola del juego con el genera 3 bolas nuevas y este se destruye en el momento. Probamos las siguientes características en el juego para observar cómo la generación de nuevas bolas no genera problemas entre los dos jugadores, 

 - Añadir cada *x* segundos añadimos un bloque especial nuevo (si el otro se destruye).
 - Ver que los *id* no se bloquean y el random.seed(id) funciona perfectamente con un número indefinido de bolas.

<div style="text-align:center;">
  <image src="/images/resumen/colisiones_con_bloque_especial.gif" style="width:100%; height:12cm;">
</div>
