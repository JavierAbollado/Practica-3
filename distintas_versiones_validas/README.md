# Versión 1

 - La más parecida al ping pong del profesor.
- Mantengo un solo script y los sprites originales.
- Añado algún objeto. *Block* es el objeto que tiene cada uno de los bloques que hay que destruir, estos tienes niveles, 
cuanto mayor se este, más veces habrá que golpearlo para destruirlo.

# Versión 2

- Añado fotos al juego.
- Sigue siendo de lado. 
- Mejoro las colisiones y los sprites. Los agrupo y hago las actualizaciones para un solo grupo unificado.
- Si las bolas tocan el final se mueren. Si perdemos todas las bolas perdemos el juego.

# Versión 3

 - Hago una distribución en los scripts más separada. 
 - Unifico clases como *Ball* y *BallSprite* en una sola. 
 - Añado a *Game* todos los sprites y componentes del juego y *Display* solo se ocupa de las actualizaciones por cada frame. 
 - También unifico las funciones del *Display* en una sola *play()* para poder jugar una partida. 
 - Por otro lado, muevo el juego de forma vertical para ser más intuitivo.
 - Por último, añado nuevas clases especiales como *BlockNewBalls* para hacer objetos especiales. En este caso, si le golpeas al bloque salen nuevas pelotas.
