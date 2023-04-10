# Versión 3 - Multijugador

 - Es funcional.
 - Gráficos de la versión 3 del main. 
 - Es una prueba de mantener una sala main, y los jugadores únicamente controlan el movimiento de sus paletas.
    - sala.py : se encarga de la lógica del entorno del juego (únicamente recibe de los jugadores los movimientos de sus paletas).
    - player.py : cada jugador solo checkea las teclas de su teclado para el movimiento de su pala. Para actualizar la pantalla recibe los cambios de la sala y del otro jugador, lo actualiza en su juego y refresca la pantalla.
 - Actualizaciones: para pasar la información tenemos ciertos códigos para cada acción. Para acceder rápidamente a cada objeto (en nuestro caso bolas y bloques) he añadido un identificador único para cada uno. Así creo un diccionario en el display de los jugadores donde las *keys* son el id.
