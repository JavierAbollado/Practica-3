import pygame
import sys, os
import socket
import pickle
import random

# teclas para mover las barras: {s,x} y {k,m}.

# colores
BLACK = (0, 0, 0)
GREY = (50,50,50)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255,255,0)
GREEN = (0,255,0)

BLUE_1 = (0, 50, 255)
BLUE_2 = (0, 0, 75)
RED_1 = (255, 0, 0)
RED_2 = (120, 0, 0)

COLORS_BLOCK = [[RED_1, RED_2], [BLUE_1, BLUE_2]]
PLAYER_COLOR = [RED, BLUE]

# ejes
X = 0
Y = 1
SIZE = (700, 525)

# player 
LEFT_PLAYER = 0
RIGHT_PLAYER = 1
PLAYER_HEIGHT = 60
PLAYER_WIDTH = 10

# ball & block
BALL_COLOR = WHITE
BALL_SIZE = 12
BLOCK_SIZE = 40
FPS = 60
DELTA = 5 #30
VEL_BALL_X, VEL_BALL_Y = 2, 3 # velocidad de la bola

SIDES = ["left", "right"]

class Player():
    def __init__(self, side):
        self.side = side
        if side == LEFT_PLAYER:
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

    def get_pos(self):
        return self.pos

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
                self.score[LEFT_PLAYER] += 1
                ball.bounce(X)
            elif pos[X]<0:
                self.score[RIGHT_PLAYER] += 1
                ball.bounce(X)


    def __str__(self):
        return f"G<{self.players[RIGHT_PLAYER]}:{self.players[LEFT_PLAYER]}:{self.ball}>"


class Paddle(pygame.sprite.Sprite):
    def __init__(self, player):
      super().__init__()
      self.image = pygame.Surface([PLAYER_WIDTH, PLAYER_HEIGHT])
      self.image.fill(BLACK)
      self.image.set_colorkey(BLACK)#drawing the paddle
      self.player = player
      color = PLAYER_COLOR[self.player.get_side()]
      self.color = 0 if self.player.get_side() == 0 else 1
      pygame.draw.rect(self.image, color, [0,0,PLAYER_WIDTH, PLAYER_HEIGHT])
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
        # pygame.draw.rect(self.image, BALL_COLOR, [0, 0, BALL_SIZE, BALL_SIZE])
        self.rect = self.image.get_rect()
        self.update()

    def change_color(self): # {0,1} -> {1,0}
        self.ball.color = 1 - self.ball.color

    def update(self):
        color = RED if self.ball.color == 0 else BLUE
        pygame.draw.circle(self.image, color, (BALL_SIZE//2, BALL_SIZE//2), BALL_SIZE//2)
        pos = self.ball.get_pos()
        self.rect.centerx, self.rect.centery = pos


class Block(pygame.sprite.Sprite):    
    def __init__(self, pos, color=None, level=None):  # color € {0,1} -> rojo y azul
        super().__init__()
        self.pos = pos
        self.color = color if color != None else random.randint(0,1) # 2 colores € {0,1}
        self.level = level if level != None else random.randint(0,1) # X niveles € {0,1,...}
        self.image = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE))
        self.image.fill(GREY)
        #self.image.set_colorkey(WHITE)
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = pos
        self.update()

    def update(self):
        pygame.draw.rect(self.image, COLORS_BLOCK[self.color][self.level], [BLOCK_SIZE*0.1, BLOCK_SIZE*0.1, BLOCK_SIZE*0.8, BLOCK_SIZE*0.8])



class Display():
    def __init__(self, game):
        self.game = game
        self.paddles = [Paddle(self.game.get_player(i)) for i in range(2)]

        self.blocks = []
        j = 0
        while 0.75*SIZE[0] + j*(BLOCK_SIZE+5) + BLOCK_SIZE < 0.9*SIZE[0]:
            i = 0
            while 0.1*SIZE[1] + i*(BLOCK_SIZE+5) + BLOCK_SIZE < 0.9*SIZE[1]:
                block = Block((0.75*SIZE[0] + j*(BLOCK_SIZE+5), 0.1*SIZE[1] + i*(BLOCK_SIZE+5)))
                self.blocks.append(block)
                i += 1
            j += 1
        self.ball_1 = BallSprite(self.game.get_ball(color=0))
        self.ball_2 = BallSprite(self.game.get_ball(color=1))
        self.all_sprites = pygame.sprite.Group()
        self.paddle_group = pygame.sprite.Group()
        for block in self.blocks:
            self.all_sprites.add(block)
        for paddle  in self.paddles:
            self.all_sprites.add(paddle)
            self.paddle_group.add(paddle)
        self.all_sprites.add(self.ball_1)
        self.all_sprites.add(self.ball_2)

        self.screen = pygame.display.set_mode(SIZE)
        self.clock =  pygame.time.Clock()  #FPS
        # self.background = pygame.image.load('images/background.png')
        running = True
        pygame.init()

    def analyze_events(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_s]:
            self.game.moveUp(LEFT_PLAYER)
        if keys[pygame.K_x]:
            self.game.moveDown(LEFT_PLAYER)
        if keys[pygame.K_k]:
            self.game.moveUp(RIGHT_PLAYER)
        if keys[pygame.K_m]:
            self.game.moveDown(RIGHT_PLAYER)
        #################
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game.stop()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q: # quit
                    self.game.stop()
                # if event.key == pygame.K_s:
                #     self.game.moveUp(LEFT_PLAYER)
                # if event.key == pygame.K_x:
                #     self.game.moveDown(LEFT_PLAYER)
                # if event.key == pygame.K_k:
                #     self.game.moveUp(RIGHT_PLAYER)
                # if event.key == pygame.K_m:
                #     self.game.moveDown(RIGHT_PLAYER)
        # colisiones BOLA - PALA
        if pygame.sprite.collide_rect(self.ball_1, self.paddles[0]):
            if self.ball_1.ball.color != self.paddles[0].color:
                self.ball_1.change_color()
            self.ball_1.ball.collide_player()
        if pygame.sprite.collide_rect(self.ball_1, self.paddles[1]):
            if self.ball_1.ball.color != self.paddles[1].color:
                self.ball_1.change_color()
            self.ball_1.ball.collide_player()
        if pygame.sprite.collide_rect(self.ball_2, self.paddles[0]):
            if self.ball_2.ball.color != self.paddles[0].color:
                self.ball_2.change_color()
            self.ball_2.ball.collide_player()
        if pygame.sprite.collide_rect(self.ball_2, self.paddles[1]):
            if self.ball_2.ball.color != self.paddles[1].color:
                self.ball_2.change_color()
            self.ball_2.ball.collide_player()
        # if pygame.sprite.spritecollide(self.ball_1, self.paddle_group, False):
        #     self.game.get_ball(color=0).collide_player()
        # if pygame.sprite.spritecollide(self.ball_2, self.paddle_group, False):
        #     self.game.get_ball(color=1).collide_player()
        # colisiones BOLA - BLOQUE
        for i in range(len(self.blocks)):
            _break = False
            for color, ball in enumerate([self.ball_1, self.ball_2]):
                if pygame.sprite.collide_rect(self.blocks[i], ball):
                    AXIS = Y if ((abs(self.blocks[i].rect.top - ball.rect.bottom) < self.blocks[i].rect.width*0.1)
                                or (abs(self.blocks[i].rect.bottom - ball.rect.top) < self.blocks[i].rect.width*0.1)) else X
                    if ball.ball.color == self.blocks[i].color:
                        if self.blocks[i].level == 0:
                            self.blocks[i].kill()
                            del self.blocks[i]
                        else:
                            self.blocks[i].level -= 1
                    self.game.get_ball(color=color).collide_player(AXIS)
                    _break = True
                    break
            if _break: break
        self.all_sprites.update()

    def refresh(self):
        #self.screen.blit(self.background, (0, 0))
        self.screen.fill(WHITE)
        # score = self.game.get_score()
        # font = pygame.font.Font(None, 74)
        # text = font.render(f"{score[LEFT_PLAYER]}", 1, WHITE)
        # self.screen.blit(text, (250, 10))
        # text = font.render(f"{score[RIGHT_PLAYER]}", 1, WHITE)
        # self.screen.blit(text, (SIZE[X]-250, 10))
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

        while game.is_running():
            game.movements()
            display.analyze_events()
            display.refresh()
            display.tick()
    finally:
        pygame.quit()

if __name__=="__main__":
    main()
