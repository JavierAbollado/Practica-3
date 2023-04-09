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

        # display
        self.quit = False
        # self.screen = pygame.Surface(SIZE)
        # self.window = pygame.display.set_mode(SIZE)
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

        changes = []

#################################################################################################################
# Tengo que crear un id para cada bola y hacer una función (en Game) de añadir bolas tal que reciba el último "id"
# De ahí podemos mapear los casos con el id de la bola y luego
#  - cambiar color
#  - rebotar (tal dirección)
#  - bloque especial
#################################################################################################################

        # colisiones BOLA - PALA
        for ball, paddles in pygame.sprite.groupcollide(self.game.balls, self.game.paddles, False, False).items():
            paddle = paddles[0]
            if ball.color != paddle.color:
                ball.change_color()
            ball.collide_player() 
        
        # colisiones BOLA - BLOQUE
        for ball, blocks in pygame.sprite.groupcollide(self.game.balls, self.game.blocks, False, False).items():
            block = blocks[0]
            if ball.color == block.color:
                block.get_shot()
            AXIS = Y if ((abs(block.rect.top - ball.rect.bottom) < block.rect.width*0.1)
                            or (abs(block.rect.bottom - ball.rect.top) < block.rect.width*0.1)) else X
            ball.collide_player(AXIS)

        # colisiones BOLA - BLOQUE_ESPECIAL 
        for ball, blocks in pygame.sprite.groupcollide(self.game.balls, self.game.blocks_new_balls, False, True).items():
            for block in blocks:
                AXIS = Y if ((abs(block.rect.top - ball.rect.bottom) < block.rect.width*0.1)
                                or (abs(block.rect.bottom - ball.rect.top) < block.rect.width*0.1)) else X
                ball.collide_player(AXIS)
                self.game.add_new_balls(n=3)

        self.game.all_sprites.update()

        return changes


def get_player_events(sala, conn, side):
    command = ""
    events = []
    while command != "next":
        command = conn.recv()
        events.append(command)
        if command == "left":
            print(side)
            sala.game.moveLeft(PLAYERS[side])
        elif command == "right":
            sala.game.moveRight(PLAYERS[side])
        elif command == "quit":
            sala.game.stop()
    return events


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

            # crear bloque especial pasados X (= 3) segundos 
            if not r and time.time() - init > 3:
                b = BlockNewBalls(((SIZE[0]-BLOCK_SIZE[0])//2, (SIZE[1]-BLOCK_SIZE[1])//2))
                sala.game.blocks_new_balls.add(b)
                sala.game.all_sprites.add(b)
                r = True

            # checkear los eventos de los jugadores
            player_events_1 = get_player_events(sala, conn1, 0)
            conn2.send(player_events_1)
            player_events_2 = get_player_events(sala, conn2, 1)
            conn1.send(player_events_2)

            # realizar los movimientos del juego
            sala.game.movements()

            # analizar los cambios de la sala
            changes = sala.analyze_events()

            # enviar datos actualizados
            conn1.send(changes)
            conn2.send(changes)

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

if __name__=="__main__":
    main()
