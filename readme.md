# Practica_3

Esta es una versión de la práctica tiene:

* 2 Palas

* 2 Bolas, una roja y una azul

* 24 bloques de color aleatorio, los bloques tienen 2 vidas

* Si una bola roja colisiona con la pala azul, la bola cambia de color, análogo en el otro caso.

* Controles  player_1: (↑, ↓)  player_2: (k, m)

## Índice

- [Descripción](#Descripción)
- [Requisitos](#Requisitos)
- [Ayuda](#Ayuda)

## Descripción

Esta versión sigue un esquema más primitivo naïve de comunicación:
* El esquema es el siguiente: juador dectecta evento (local) -> gestión de evento (sala) 

    -> envia nuevas posiciones (sala) -> dibuja con la información nueva (local)
    
* ¿Qué problemas puede tener esto?
    envia evento falso (cheater) -> gestión evento (sala)
    
    -> envia nuevas posiciones con trampa (sala)
    
    -> dibuja con la informacin nueva (cheater + no cheater)
    

## Como empezar a jugar

### Requisitos

* Python3 
* Version de Linux basada en Debian (Recomendado)
* Liberías no incluidas en Anaconda: Multiprocessing, PyGame, Paho-mqtt



### Ejecutar el juego

* Un dispositvo hará de sala, en una terminal ejecutará:
```
python3 sala_test.py  <ipv4_equipo_1>
```
* El resto de dispositivos, en la misma red, pueden conectarse con:
```
python3 practica_3_player.py  <ipv4_equipo_1>
```
## Ayuda

Cualquier bug abrid una issue


## Autores:

 - **Francisco Javier Abollado**
 - **David Parro Plaza**
 - **Juan Alvarez Noseque ;)**
