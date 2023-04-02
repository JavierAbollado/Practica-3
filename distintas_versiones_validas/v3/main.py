import pygame
import socket
import pickle
import random
import time

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
        self.screen = pygame.display.set_mode(SIZE)
        self.clock =  pygame.time.Clock()  #FPS
        pygame.init()

    def analyze_events(self):

        # comprobar salir del juego
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit = True
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
        
        # mover palas
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            self.game.moveLeft(PLAYER_1)
        if keys[pygame.K_d]:
            self.game.moveRight(PLAYER_1)
        if keys[pygame.K_KP4]:
            self.game.moveLeft(PLAYER_2)
        if keys[pygame.K_KP6]:
            self.game.moveRight(PLAYER_2)
        
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


class Network:
    def __init__(self): ##this will connect to the server initially
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = '127.0.0.1' #server ip #<---
        self.port = 5555   #server port #<---
        self.addr = (self.server, self.port)
        self.p = self.connect()
    def getP(self):
        return self.p
    def connect(self):
        try:
            self.client.connect(self.addr)
            return pickle.loads(self.client.recv(2048))
        except:
            pass
    def send(self, data):
        try:
            self.client.send(pickle.dumps(data))
            return pickle.loads(self.client.recv(2048))
        except socket.error as e:
            print(e)


def main():
    try:
        display = Display()
        display.play()
    finally:
        pygame.quit()

if __name__=="__main__":
    main()
