import pygame
import time

from multiprocessing.connection import Listener
from multiprocessing import Process, Manager, Value, Lock
import traceback
import sys

from constantes import *
from sprites import *


class Sala():

    def __init__(self):

        # game
        self.game = Game()
        self.id_ball = self.game.add_new_balls(n=2, id=0)
        self.id_especial_blocks = 0

        # display
        self.quit = False
        self.clock =  pygame.time.Clock()  #FPS
        pygame.init()

    def analyze_events(self): # player_events
        
        # comprobar si ya hemos terminado
        if len(self.game.balls) == 0:
            self.game.game_over(win = False)
        if len(self.game.blocks) == 0:
            self.game.game_over(win = True)
        if not self.game.is_running():
            return []

        ####################################################################
        # Formato de los códigos: "x1-x2-x3" 
        #
        # donde,
        #    x1 = nombre del objeto afectado: ball, block, be
        #    x2 = id del objeto
        #    x3 = código de la acción a realizar
        #
        # códigos del x3 para cada objeto:
        #    ball:
        #       cc = change color
        #       c{X} = collide, con AXIS = X
        #    block:
        #       gs = get shot
        #    be:
        #       nº = nº de bolas a generar
        ####################################################################

        changes = []

        # Colisiones BOLA - PALA
        for ball, paddles in pygame.sprite.groupcollide(self.game.balls, self.game.paddles, False, False).items():
            paddle = paddles[0]
            if ball.color != paddle.color:
                ball.change_color()
                changes.append(f"ball-{ball.id}-cc")
            ball.collide_player()
            changes.append(f"ball-{ball.id}-c1")
        
        # colisiones BOLA - BLOQUE
        for ball, blocks in pygame.sprite.groupcollide(self.game.balls, self.game.blocks, False, False).items():
            block = blocks[0] # una bola solo puede chocar con un bloque a la vez  
            AXIS = Y if ((abs(block.rect.top - ball.rect.bottom) < block.rect.width*0.1)
                            or (abs(block.rect.bottom - ball.rect.top) < block.rect.width*0.1)) else X
            ball.collide_player(AXIS)
            changes.append(f"ball-{ball.id}-c{AXIS}")
            if ball.color == block.color:
                block.get_shot()
                changes.append(f"block-{block.id}-gs")

        # colisiones BOLA - BLOQUE_ESPECIAL 
        for ball, blocks in pygame.sprite.groupcollide(self.game.balls, self.game.blocks_new_balls, False, False).items():
            block = blocks[0] # una bola solo puede chocar con un bloque a la vez  
            AXIS = Y if ((abs(block.rect.top - ball.rect.bottom) < block.rect.width*0.1)
                            or (abs(block.rect.bottom - ball.rect.top) < block.rect.width*0.1)) else X
            ball.collide_player(AXIS)
            changes.append(f"ball-{ball.id}-c{AXIS}")
            self.id_ball = self.game.add_new_balls(n=3, id=self.id_ball)
            block.get_shot()
            changes.append(f"be-{block.id}-gs")

        self.game.all_sprites.update()

        return changes


def get_player_events(sala, conn, side):
    # command = conn.recv()
    events = conn.recv()
    # events = []
    # while command != "next":
    for command in events:
        # events.append(command)
        if command == "left":
            sala.game.moveLeft(PLAYERS[side])
        elif command == "right":
            sala.game.moveRight(PLAYERS[side])
        elif command == "quit":
            sala.game.stop()
        # ommand = conn.recv()
    return events


def send_events(events, conn):
    conn.send(events)
    #for ev in events:
    #    conn.send(ev)
    #conn.send("next")


def play(conn1, conn2):
    try:

        # crear sala
        sala = Sala()

        # mandar a cada jugador su "id"
        conn1.send(0)
        conn2.send(1)

        init = time.time()
        r = False

        # bucle de juego
        while sala.game.is_running():

            temp = []  # eventos temporales

            # crear bloque especial cada X segundos (si no hay otros)
            X = 20
            if time.time() - init > X and len(sala.game.blocks_new_balls) == 0:
                sala.game.add_blocknewballs(sala.id_especial_blocks)
                sala.id_especial_blocks += 1
                init = time.time()
                temp.append("new-be")

            # checkear los eventos de los jugadores
            player_events_1 = get_player_events(sala, conn1, 0)
            player_events_2 = get_player_events(sala, conn2, 1)
            send_events(player_events_1, conn2)
            send_events(player_events_2, conn1)

            # analizar los cambios de la sala
            changes = temp + sala.analyze_events()

            # enviar datos actualizados
            send_events(changes, conn1)
            send_events(changes, conn2)

    except:
        traceback.print_exc()

    finally:
        conn1.close()
        conn2.close()
        pygame.quit()


def main(ip_address):
    try:
        with Listener((ip_address, 6000),
                      authkey=b'secret password') as listener:
            n_player = 0
            connections = [None, None]
            while n_player < 2:
                print(f"accepting connection {n_player}")
                conn = listener.accept()
                connections[n_player] = conn
                n_player += 1
            game = Process(target=play, args=(connections[0], connections[1]))
            game.start()

    except Exception as e:
        traceback.print_exc()

if __name__=='__main__':
    ip_address = "192.168.1.81"
    if len(sys.argv)>1:
        ip_address = sys.argv[1]

    main(ip_address)
