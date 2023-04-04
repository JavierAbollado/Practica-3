import pygame
import socket
import pickle
import random
import time

from multiprocessing.connection import Listener
from multiprocessing import Process, Manager, Value, Lock
import traceback
import sys

from constantes import *
from sprites import *


class Game:

    def __init__(self):

        # players
        self.players = [Player(i) for i in range(2)]

        # sprite groups
        self.paddles = pygame.sprite.Group()
        self.balls = pygame.sprite.Group()
        self.blocks = pygame.sprite.Group()
        self.blocks_new_balls = pygame.sprite.Group()

        # añadir sprites
        for i in range(2):
            paddle = Paddle(self.players[i])
            self.paddles.add(paddle)
        for _ in range(2):
            ball = Ball([BALL_VEL[0] * (-1)**random.randint(0,1), -BALL_VEL[1]], color=random.randint(0,1))
            self.balls.add(ball)
        j = 0
        while 0.1*SIZE[0] + (j+1)*BLOCK_SIZE[0] < 0.9*SIZE[0]:
            i = 0
            while 0.1*SIZE[1] + (i+1)*BLOCK_SIZE[1] < 0.25*SIZE[1]:
                block = Block((0.1*SIZE[0] + j*BLOCK_SIZE[0], 0.1*SIZE[1] + i*BLOCK_SIZE[1]))
                self.blocks.add(block)
                i += 1
            j += 1
        
        # unificar sprites
        self.all_sprites = pygame.sprite.Group()
        self.all_sprites.add(self.paddles)
        self.all_sprites.add(self.balls)
        self.all_sprites.add(self.blocks)

        # variables para info
        self.running = True
        self.win = False

    def add_new_balls(self, n=2):
        for _ in range(n):
            ball = Ball([BALL_VEL[0] * (-1)**random.randint(0,1), -BALL_VEL[1]], color=random.randint(0,1))
            self.balls.add(ball)
            self.all_sprites.add(ball)

    def get_player(self, side):
        return self.players[side]

    def game_over(self, win):
        self.win = win
        self.running = False

    def is_running(self):
        return self.running

    def stop(self):
        self.running = False

    def moveRight(self, player):
        self.players[player].moveRight()

    def moveLeft(self, player):
        self.players[player].moveLeft()

    def movements(self):
        for ball in self.balls: #[self.ball_1, self.ball_2]:
            pos = ball.pos
            if pos[Y]<0:
                ball.bounce(Y)
            if pos[X]<0 or pos[X]>SIZE[X]:
                ball.bounce(X)
            elif pos[Y]>SIZE[Y]:
                ball.kill()


class Display():

    def __init__(self):

        # game
        self.game = Game()
        self.gameover = GameOver()
        self.levelcompleted = LevelComplete()

        # display
        self.quit = False
        self.screen = pygame.Surface(SIZE)
        self.window = pygame.display.set_mode(SIZE)
        self.clock =  pygame.time.Clock()  #FPS
        pygame.init()

    def analyze_events(self):

        # comprobar salir del juego
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit = True
                self.game.stop()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q: # quit
                    self.game.stop()
        
        # comprobar si ya hemos terminado
        if len(self.game.balls) == 0:
            self.game.game_over(win = False)
        if len(self.game.blocks) == 0:
            self.game.game_over(win = True)
        if not self.game.is_running():
            return
        
        # # mover palas
        # keys = pygame.key.get_pressed()
        # if keys[pygame.K_a]:
        #     self.game.moveLeft(PLAYER_1)
        # if keys[pygame.K_d]:
        #     self.game.moveRight(PLAYER_1)
        # if keys[pygame.K_KP4]:
        #     self.game.moveLeft(PLAYER_2)
        # if keys[pygame.K_KP6]:
        #     self.game.moveRight(PLAYER_2)
        
        # colisiones BOLA - PALA
        for ball, paddles in pygame.sprite.groupcollide(self.game.balls, self.game.paddles, False, False).items():
            paddle = paddles[0]
            if ball.color != paddle.color:
                ball.change_color()
            ball.collide_player()
        
        # colisiones BOLA - PALA
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

    def refresh(self):
        if not self.game.is_running():
            if self.game.win:
                self.levelcompleted.draw(self.screen)
            else:
                self.gameover.draw(self.screen)
        else:
            self.screen.blit(IM_background, (0, 0))
            self.game.all_sprites.draw(self.screen)
        self.window.blit(self.screen, (0,0))
        pygame.display.flip()

    def tick(self):
        self.clock.tick(FPS)

    def play(self):
        t = time.time()
        r = False
        while not self.quit:
            if not r and time.time()-t > 3:
                b = BlockNewBalls(((SIZE[0]-BLOCK_SIZE[0])//2, (SIZE[1]-BLOCK_SIZE[1])//2))
                self.game.blocks_new_balls.add(b)
                self.game.all_sprites.add(b)
                r = True
            self.game.movements()
            self.analyze_events()
            self.refresh()
            self.tick()


def check_player_events(display, conn, side):
    command = ""
    while command != "next":
        command = conn.recv()
        if command == "left":
            print(side)
            display.game.moveLeft(PLAYERS[side])
        elif command == "right":
            display.game.moveRight(PLAYERS[side])
        elif command == "quit":
            display.game.stop()


def send_screen(conn, screen):
    pixels = pygame.surfarray.array3d(screen)
    data = pixels.tostring()
    conn.send_bytes(data)


def play(conn1, conn2):
    try:
        display = Display()

        conn1.send(0)
        conn2.send(1)

        t = time.time()
        r = False
        while display.game.is_running():
            if not r and time.time()-t > 3:
                b = BlockNewBalls(((SIZE[0]-BLOCK_SIZE[0])//2, (SIZE[1]-BLOCK_SIZE[1])//2))
                display.game.blocks_new_balls.add(b)
                display.game.all_sprites.add(b)
                r = True
            display.game.movements()
            display.analyze_events()
            check_player_events(display, conn1, 0)
            check_player_events(display, conn2, 1)
            display.refresh()
            send_screen(conn1, display.screen)
            send_screen(conn2, display.screen)
            display.tick()
        print("end")
        conn1.close()
        conn2.close()

    except:
        traceback.print_exc()
        conn1.close()
        conn2.close()

    finally:
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