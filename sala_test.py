
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from multiprocessing.connection import Listener
from multiprocessing import Process, Manager, Value, Lock
import random
import traceback
import sys
from constantes import *

class Player():
    """
    Clase Asociada al jugador:
        Comienza siempre en posicion fija
        El desplazamiento se modifica en la variable DELTA en constantes.py
    """
    def __init__(self, side: int):
        self.side = side
        if side == PLAYER_1:
            self.pos = [10, SIZE[Y]//4]
        else:
            self.pos = [10, 3*SIZE[Y]//4]

    def get_pos(self):
        return self.pos

    def get_side(self):
        return self.side

    def moveDown(self):
        self.pos[Y]    += DELTA
        if self.pos[Y]  > SIZE[Y]:
            self.pos[Y] = SIZE[Y]

    def moveUp(self):
        self.pos[Y]    -= DELTA
        if self.pos[Y]  < 0:
            self.pos[Y] = 0

    def __str__(self):
        return f"P<{SIDES[self.side], self.pos}>"


# Jugador ve colision -> comprueba si es suya -> manda mensaje
# -> Interpretamos mensaje
class Ball():
    """
    Cada bola tiene en su constructor (velocidad, color)
    Velocidad: int, todas las bolas tienen la misma
    Color    : Una inicializa en azul otra en rojo
    
        Metodos:
            Son metodos que se llaman en funcion de los eventos del juego
            Se puede asumir que su semantica es su nombre
    """
    def __init__(self, velocity: int, color: int):  # color € {0,1} -> rojo y azul
        self.color = color
        self.pos=[ (SIZE[X]//4)*self.color + SIZE[X]//3
                  , (SIZE[Y]//4)*self.color + SIZE[Y]//3 ]
        self.velocity = velocity
        self.alive = 1

    def get_pos(self):
        return self.pos

    def kill(self):
        self.alive = 0

    def get_status(self):
        return self.alive

    def get_color(self):
        return self.color

    def change_color(self):
        self.color = (self.color - 1)%2

    def update(self):
        self.pos[X] += self.velocity[X]
        self.pos[Y] += self.velocity[Y]

    def bounce(self, AXIS: int):
        self.velocity[AXIS] = -self.velocity[AXIS]

    def collide_player(self, side):
        self.bounce(X)
        for _ in range(3):
            self.update()

    def __str__(self):
        return f"B<{self.pos}>"


class Game():
    
    """
    Inicializa:
        2 Jugadores: A cada uno se le asocia un numero
        2 Bolas    : una de cada color
        24 Bloques : colores aleatorios
    """
    def __init__(self, manager):
        self.players_s = manager.list([Player(i) for i in range(2)])

        self.ball_s = manager.list([Ball([-1*VEL_BALL_X, VEL_BALL_Y], color=0)
                                    , Ball([VEL_BALL_X, VEL_BALL_Y], color=1)])


        #  1 <-> True; 0 <-> False
        self.running_s = Value('i', 1)

        self.block_lives = manager.dict()
        self.ball_info = manager.dict()
        for i in range(24):
            rand_color = random.randint(0,1)
            if i < 12:
                self.block_lives[i] = (2
                                       , rand_color%2
                                       , [600 + 40*(i%2), 20 + 40*i])
            else:
                self.block_lives[i] = (2
                                       , rand_color%2
                                       , [600 + 40*((1+(i%12))%2)
                                          , 20 + 40*(i%12)])

        for i in range(len(list(self.ball_s))):
            self.ball_info[i] = (1, self.ball_s[i].color
                                 , [self.ball_s[i].pos[0]
                                 , self.ball_s[i].pos[1]])

        self.lock = Lock()

    def get_player(self, side: int):
        return self.players_s[side]

    def get_ball(self, color: int):
        return self.ball_s[0] if color == 0 else self.ball_s[1]


    def game_over(self):
        self.running_s.value = 0

    def is_running(self):
        return self.running_s.value == 1

    # Player <-> Side € {0, 1}
    def moveUp(self, player: int):
        self.lock.acquire()
        p = self.players_s[player]
        p.moveUp()
        self.players_s[player] = p
        self.lock.release()

    def moveDown(self, player: int):
        self.lock.acquire()
        player = player
        p = self.players_s[player]
        p.moveDown()
        self.players_s[player] = p
        self.lock.release()

    # Queda el equivalente a ball_colide(self, player)
    def ball_collide(self, player: int, ball_index: int):
        self.lock.acquire()
        ball = self.ball_s[ball_index]

        ball.collide_player(player)
        self.ball_s[ball_index] = ball
        self.lock.release()


    def movements(self):
        self.lock.acquire()

        for index, b in enumerate(list(self.ball_s)):
            ball = self.ball_s[index]
            ball.update()
            pos = ball.get_pos()
            if pos[Y]<0 or pos[Y]>SIZE[Y]:
                ball.bounce(Y)
            if pos[X]>SIZE[X]:
                ball.bounce(X)
            elif pos[X]<0:
                ball.kill()
            self.ball_s[index] = ball
            self.ball_info[index] = (ball.get_status()
                                     , ball.get_color()
                                     , ball.get_pos())
        self.lock.release()

    def get_block_lives(self):
        return self.block_lives

    def set_block_lives(self, block_index: int):
        self.lock.acquire()
        p = self.block_lives[block_index]
        p = (self.block_lives[block_index][0]-1
             , self.block_lives[block_index][1]
             , self.block_lives[block_index][2])
        self.block_lives[block_index] = p
        self.lock.release()

    def change_colors_g(self, ball_index: int):
        self.lock.acquire()
        ball   = self.ball_s[ball_index]
        ball.change_color()
        self.ball_s[ball_index]  = ball
        self.lock.release()


    def get_info(self):
        info = {

            'pos_left_player': self.players_s[0].get_pos(),
            'pos_right_player': self.players_s[1].get_pos(),
            'is_running': self.running_s.value == 1,
            # {id_bloque: (vida, {0 -> mismo color
            #                   , 1 -> cambio de color}, posicion), ..}
            'bloques_dict': dict(self.block_lives),
            # {id_bola: (status, color, posicion), ..}
            'balls_dict'   : dict(self.ball_info)

        }
        return info

    def __str__(self):
        return f"G<{self.players_s[PLAYER_2]}:{self.players_s[PLAYER_1]}:{self.ball_s}>"


def player(side: int, conn, game):
    try:
        conn.send( (side, game.get_info()) )
        while game.is_running():
            command = ""
            while command != "next":
                command = conn.recv()
                if command == "up":
                    game.moveUp(side)
                elif command == "down":
                    game.moveDown(side)
                # collide_p_b_X_Y, X : side, Y : ball_index
                # Combandos colision bola-pala
                for termination in [str(side)+"_"+str(j)
                                    for j in range(2)]:
                    partida = termination.split("_")
                    # Son str hay que cambiar tipo a int
                    side_info = int(partida[-2])
                    ball_index = int(partida[-1])
                    if command == "collide_p_b_" + termination :
                        game.ball_collide(side_info, ball_index)
                        # mismo color y cambiamos al opuesto
                        if side_info != game.ball_s[ball_index].color:
                            game.change_colors_g(ball_index)
                        # else:
                        #     game.colors_not_changed(ball_index)
                # Vamos a hacer lo mismo con los bloques
                # Comandos colision bola-bloque
                # Color va implicito en side
                # collide_b_b_X_Y_Z
                # X: jugador(side) Y: ball_index , Z : block_index
                # Supongamos la existencia de una constante inicial NBLOQUES
                NBLOQUES = 24 
                for termination in [str(side) + "_" + str(i) + "_" + str(j)
                                    for i in range(2)
                                    for j in range(NBLOQUES)]:
                    partida = termination.split("_")
                    # Son str hay que convertir a int
                    side = int(partida[-3])
                    ball_index = int(partida[-2])
                    block_index = int(partida[-1])
                    if command == "collide_b_b_" + termination:

                        game.ball_collide(side, ball_index)
                        # Si bola.color == bloque.color, bloque.vida -= 1
                        if game.ball_s[ball_index].color != game.block_lives[block_index][1]:
                            game.set_block_lives(block_index)

                if command == "quit":
                    game.game_over()
            if side == 1:
                game.movements()
            conn.send(game.get_info())
    except:
        traceback.print_exc()
        conn.close()
    finally:
        print(f"Game ended {game}")

def main(ip_address):
    manager = Manager()

    try:
        with Listener((ip_address, 6000),
                      authkey=b'secret password') as listener:
            n_player = 0
            players = [None, None]
            game = Game(manager)
            while True:
                print(f"accepting connection {n_player}")
                conn = listener.accept()
                players[n_player] = Process(target=player,
                                            args=(n_player, conn, game))
                n_player += 1
                if n_player == 2:
                    players[0].start()
                    players[1].start()
                    n_player = 0
                    players = [None, None]
                    game = Game(manager)

    except Exception as e:
        traceback.print_exc()
if __name__=="__main__":
    ip_address = "127.0.0.1"
    if len(sys.argv)>1:
        ip_address = sys.argv[1]

    main(ip_address)
