# Versión 3 - Multijugador

Es una mini version multijugador de la versión 3 del main. He eliminado todas las otras carpetas, pero porque es solo para guardar la versión no voy a hacer 
ningún commit de ramas. Era para ver un poco cómo funcionaban las conexiones. 

Todavía sin probar.

Es una prueba de mantener una sala main, y los jugadores únicamente controlan el movimiento de sus paletas.
- sala.py : se encarga de la lógica del entorno del juego (únicamente recibe de los jugadores los movimientos de sus paletas).
- player.py : cada jugador solo checkea las teclas de su teclado para el movimiento de su pala. Para actualizar la pantalla recibe los cambios de la sala y del otro jugador, lo actualiza en su juego y refresca la pantalla.
