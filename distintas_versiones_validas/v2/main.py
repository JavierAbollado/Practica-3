import pygame
import socket
import pickle
import random

from constantes import *

class Player():
    def __init__(self, side):
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
        self.pos[Y] += DELTA
        if self.pos[Y] > SIZE[Y]:
            self.pos[Y] = SIZE[Y]

    def moveUp(self):
        self.pos[Y] -= DELTA
        if self.pos[Y] < 0:
            self.pos[Y] = 0

    def __str__(self):
        return f"P<{SIDES[self.side], self.pos}>"

class Ball():
    def __init__(self, velocity, color):  # color € {0,1} -> rojo y azul
        self.color = color
        self.pos=[ SIZE[X]//2, SIZE[Y]//2 ]
        self.velocity = velocity
        self.alive = True

    def get_pos(self):
        return self.pos
    
    def kill(self):
        self.alive = False

    def update(self):
        self.pos[X] += self.velocity[X]
        self.pos[Y] += self.velocity[Y]

    def bounce(self, AXIS):
        self.velocity[AXIS] = -self.velocity[AXIS]

    def collide_player(self, AXIS=X):
        self.bounce(AXIS)
        for i in range(3):
            self.update()

    def __str__(self):
        return f"B<{self.pos}>"


class Game():
    def __init__(self):
        self.players = [Player(i) for i in range(2)]
        self.ball_1 = Ball([-1*VEL_BALL_X, VEL_BALL_Y], color=0)
        self.ball_2 = Ball([VEL_BALL_X, VEL_BALL_Y], color=1)
        self.score = [0,0]
        self.running = True

    def get_player(self, side):
        return self.players[side]

    def get_ball(self, color):
        return self.ball_1 if color == 0 else self.ball_2

    def get_score(self):
        return self.score

    def game_over(self):
        self.running = False

    def is_running(self):
        return self.running

    def stop(self):
        self.running = False

    def moveUp(self, player):
        self.players[player].moveUp()

    def moveDown(self, player):
        self.players[player].moveDown()

    def movements(self):
        for ball in [self.ball_1, self.ball_2]:
            ball.update()
            pos = ball.get_pos()
            if pos[Y]<0 or pos[Y]>SIZE[Y]:
                ball.bounce(Y)
            if pos[X]>SIZE[X]:
                ball.bounce(X)
            elif pos[X]<0:
                ball.kill()


    def __str__(self):
        return f"G<{self.players[PLAYER_2]}:{self.players[PLAYER_1]}:{self.ball}>"


class Paddle(pygame.sprite.Sprite):
    def __init__(self, player):
        super().__init__()
        self.player = player
        self.color = self.player.side
        self.image = IM_player[self.color]
        self.rect = self.image.get_rect()
        self.update()

    def update(self):
        pos = self.player.get_pos()
        self.rect.centerx, self.rect.centery = pos

    def __str__(self):
        return f"S<{self.player}>"


class BallSprite(pygame.sprite.Sprite):
    def __init__(self, ball):
        super().__init__()
        self.ball = ball
        self.image = pygame.Surface((BALL_SIZE, BALL_SIZE))
        self.image.fill(BLACK)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.update()

    def change_color(self): # {0,1} -> {1,0}
        self.ball.color = 1 - self.ball.color

    def update(self):
        if not self.ball.alive:
            self.kill()
        color = RED if self.ball.color == 0 else BLUE
        pygame.draw.circle(self.image, color, (BALL_SIZE//2, BALL_SIZE//2), BALL_SIZE//2)
        pos = self.ball.get_pos()
        self.rect.centerx, self.rect.centery = pos


class Block(pygame.sprite.Sprite):    
    def __init__(self, pos, color=None, level=None):  # color € {0,1} -> rojo y azul
        super().__init__()
        self.pos = pos
        self.color = color if color != None else random.randint(0,1) # 2 colores € {0,1}
        self.level = level if level != None else random.randint(0,3) # X niveles € {0,1,...}
        self.image = pygame.Surface(BLOCK_SIZE)
        self.image.fill(BLACK)
        self.image.blit(IM_block[self.color][self.level], (0.1*BLOCK_SIZE[0], 0.1*BLOCK_SIZE[1]))
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = pos
        self.update()

    def get_shot(self):
        if self.level == 0:
            self.kill()
        else:
            self.level -= 1
        self.image.blit(IM_block[self.color][self.level], (0.1*BLOCK_SIZE[0], 0.1*BLOCK_SIZE[1]))

    def update(self):
        pass

class GameOver(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = IM_gameover
        self.rect = self.image.get_rect()
        self.rect.center = (SIZE[0]//2, SIZE[1]//2)
    def draw(self, screen):
        screen.blit(self.image, self.rect)



class Display():
    def __init__(self, game):

        self.quit = False
        self.game = game
        self.gameover = GameOver()

        # sprite groups
        self.paddles = pygame.sprite.Group()
        self.balls = pygame.sprite.Group()
        self.blocks = pygame.sprite.Group()

        # añadir sprites
        for padlle in [Paddle(self.game.get_player(i)) for i in range(2)]:
            self.paddles.add(padlle)
        for ball in [BallSprite(self.game.get_ball(color=i)) for i in range(2)]:
            self.balls.add(ball)
        j = 0
        while 0.75*SIZE[0] + (j+1)*BLOCK_SIZE[0] < 0.9*SIZE[0]:
            i = 0
            while 0.1*SIZE[1] + (i+1)*BLOCK_SIZE[1] < 0.9*SIZE[1]:
                block = Block((0.75*SIZE[0] + j*BLOCK_SIZE[0], 0.1*SIZE[1] + i*BLOCK_SIZE[1]))
                self.blocks.add(block)
                i += 1
            j += 1

        # unificar sprites
        self.all_sprites = pygame.sprite.Group()
        self.all_sprites.add(self.paddles)
        self.all_sprites.add(self.balls)
        self.all_sprites.add(self.blocks)

        # pantalla principal
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
        if not self.game.is_running():
            return
        
        # mover palas
        keys = pygame.key.get_pressed()
        if keys[pygame.K_s]:
            self.game.moveUp(PLAYER_1)
        if keys[pygame.K_x]:
            self.game.moveDown(PLAYER_1)
        if keys[pygame.K_k]:
            self.game.moveUp(PLAYER_2)
        if keys[pygame.K_m]:
            self.game.moveDown(PLAYER_2)
        
        # colisiones BOLA - PALA
        for ball, paddles in pygame.sprite.groupcollide(self.balls, self.paddles, False, False).items():
            paddle = paddles[0]
            if ball.ball.color != paddle.color:
                ball.change_color()
            ball.ball.collide_player()
        
        # colisiones BOLA - PALA
        for ball, blocks in pygame.sprite.groupcollide(self.balls, self.blocks, False, False).items():
            block = blocks[0]
            if ball.ball.color == block.color:
                block.get_shot()
            AXIS = Y if ((abs(block.rect.top - ball.rect.bottom) < block.rect.width*0.1)
                            or (abs(block.rect.bottom - ball.rect.top) < block.rect.width*0.1)) else X
            ball.ball.collide_player(AXIS)
        if len(self.balls) == 0:
            self.game.game_over()
        self.all_sprites.update()

    def refresh(self):
        if not self.game.is_running():
            self.gameover.draw(self.screen)
        else:
            self.screen.blit(IM_background, (0, 0))
            self.all_sprites.draw(self.screen)
        pygame.display.flip()

    def tick(self):
        self.clock.tick(FPS)

    @staticmethod
    def quit():
        pygame.quit()

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
        game = Game()
        display = Display(game)

        while not display.quit:
            game.movements()
            display.analyze_events()
            display.refresh()
            display.tick()
    finally:
        pygame.quit()

if __name__=="__main__":
    main()
