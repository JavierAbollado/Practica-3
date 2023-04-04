# Versión 3 - Multijugador

Es una mini version multijugador de la versión 3 del main. He eliminado todas las otras carpetas, pero porque es solo para guardar la versión no voy a hacer 
ningún commit de ramas. Era para ver un poco cómo funcionaban las conexiones. Me ha funcionado desde el mismo ordenador (será como en clase que estabamos con 
la misma yo que se qué) aunque al cerrar las ventanas se ralla un poco.

Es solo una prueba de mantener una sala main, y pasar a los jugadores únicamente la imagen del juego.
- sala.py : se encarga de todo el juego (únicamente recibe de los jugadores los movimientos de sus paletas)
- plpayer.py : cada jugador solo checkea las teclas de su teclado para el movimiento de su pala. Para actualizar la pantalla recibe directamente el screen de la sala.
Al parecer es bastante ineficiente lo de mandar la imagen completa, por lo que lo suyo es que cada uno tenga su partida y reciba la info con 
diccionarios rollo "mover_derecha" y cosas de esas, como habéis estado haciendo.
