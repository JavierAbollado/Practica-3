
"""
    Cuanto peor
     mejor para todos y cuanto peor para todos mejor,
     mejor para mí el suyo,
     beneficio político.
"""

from multiprocessing.connection import Client
import traceback
import pygame
import random
import sys, os
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


SIDESSTR = ["left", "right"]

class Player():
    def __init__(self, side):
        self.side = side
        self.pos = [None, None]

    def get_pos(self):
        return self.pos

    def get_side(self):
        return self.side

    def set_pos(self, pos):
        self.pos = pos

    def __str__(self):
        return f"P<{SIDES[self.side], self.pos}>"

class Ball():
    def __init__(self,ball_id,color):
        self.pos=[ None, None ]
        self.color = color
        self.ball_id=ball_id

    def get_pos(self):
        return self.pos

    def set_pos(self, pos):
        self.pos = pos
        
    def get_color(self):
        return self.color

    def set_color(self, color):
        self.color = color

    def __str__(self):
        return f"B<{self.pos}>"
    
    
class Block():
    def __init__(self,block_id,color):
        # self.pos=[ None, None ] 
        # DEBUGGING
        self.pos = [0,0]
        self.color = color
        self.block_id=block_id

    def get_pos(self):
        return self.pos

    def set_pos(self, pos):
        self.pos = pos
        
    def get_color(self):
        return self.color

    def set_color(self, color):
        self.color = color

    def __str__(self):
        return f"B<{self.pos}>"


class Game():
    def __init__(self):
        self.players = [Player(i) for i in range(2)]
        self.balls = [Ball(i,i) for i in range(2)]
        self.blocks = [Block(i, i%2) for i in range(12)]
        self.score = [0,0]
        self.running = True

    def get_player(self, side):
        return self.players[side]

    def set_pos_player(self, side, pos):
        self.players[side].set_pos(pos)
        
    def get_balls_id(self):
        return self.balls_id

    def set_balls_id(self,new_balls_id):
         self.balls_id= new_balls_id
    

    def get_ball(self,ball_id):
        return self.balls[ball_id]

    def set_ball_pos(self,ball_id, pos):
        self.balls[ball_id].set_pos(pos)

    def get_score(self):
        return self.score

    def set_score(self, score):
        self.score = score


    def update(self, gameinfo):
        self.set_balls_id()
        self.set_pos_player(LEFT_PLAYER, gameinfo['pos_left_player'])
        self.set_pos_player(RIGHT_PLAYER, gameinfo['pos_right_player'])
        self.set_ball_pos(0, gameinfo['pos_ball_0']) #Modificar para poner la otra bola
        self.set_ball_pos(1, gameinfo['pos_ball_1'])
        self.bloques_vivos=(gameinfo['bloques_vivos'])
        self.set_score(gameinfo['score'])
        self.running = gameinfo['is_running']

    def is_running(self):
        return self.running

    def stop(self):
        self.running = False

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
        self.ball_id=ball.ball_id
        self.color=ball.color
        self.image = pygame.Surface((BALL_SIZE, BALL_SIZE))
        self.image.fill(BLACK)
        self.image.set_colorkey(BLACK)
        pygame.draw.rect(self.image, self.color, [0, 0, BALL_SIZE, BALL_SIZE])
        self.rect = self.image.get_rect()
        self.update()

    def update(self):
        pos = self.ball.get_pos()
        self.rect.centerx, self.rect.centery = pos
        
        
        
class BlockSprite(pygame.sprite.Sprite):    
    def __init__(self, block):  # color € {0,1} -> rojo y azul
        super().__init__()
        self.block=block
        self.color=block.color
        self.pos = block.pos
        self.image = pygame.Surface(BLOCK_SIZE)
        self.image.fill(BLACK)
        pygame.draw.rect(self.image, self.color, [0, 0, BALL_SIZE, BALL_SIZE])
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = self.pos
        self.update()

   

    def update(self):
        pass



class Display():
    def __init__(self, game,side):
        self.quit = False
        self.game = game
        self.list_blocks=[i for i in range(12)]
        self.side=side
        self.color=side

        # sprite groups
        self.paddles = pygame.sprite.Group()
        self.same_c_balls = pygame.sprite.Group()
        self.diff_c_balls = pygame.sprite.Group()
        self.blocks = pygame.sprite.Group()

        # añadir sprites
        for padlle in [Paddle(self.game.get_player(i)) for i in range(2)]:
            self.paddles.add(padlle)
        
        for ball in [BallSprite(self.game.get_ball(i)) for i in range(2)]:
            if ball.color == self.color:
                self.same_c_balls.add(ball)
            else :
                self.diff_c_balls.add(ball)
            
        
        for block in [BlockSprite(self.game.get_block(i)) for i in self.list_blocks]:
            self.balls.add(ball) 
        
        self.all_sprites = pygame.sprite.Group()
        self.all_sprites.add(self.paddles)
        self.all_sprites.add(self.same_c_balls)
        self.all_sprites.add(self.diff_c_balls)
        self.all_sprites.add(self.blocks)

        self.screen = pygame.display.set_mode(SIZE)
        self.clock =  pygame.time.Clock()  #FPS
        self.background = pygame.image.load('background.png')
        pygame.init()

    def analyze_events(self, side):
        events = []
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    events.append("quit")
                elif event.key == pygame.K_UP:
                    events.append("up")
                elif event.key == pygame.K_DOWN:
                    events.append("down")
            elif event.type == pygame.QUIT:
                events.append("quit")
        

        
        # colisiones BOLA - PALA
        for ball, paddle in pygame.sprite.groupcollide(self.diff_c_balls, self.paddles[side], False, False).items():
            ball_id=ball.ball_id
            event= "collide_p_b_"+str(side)+"_"+str(ball_id)
            events.append(event)
  
        
        # colisiones BOLA - bloques
        for ball, blocks in pygame.sprite.groupcollide(self.same_c_balls, self.blocks, False, False).items():
            block=blocks[0]
            ball_id=ball.ball.ball_id
            color=ball.ball.color
            block_id=block.block.block_id
            event= "collide_b_b_"+str(color)+"_"+str(ball_id)+"_"+str(block_id)
            events.append(event)
        
        return events


    def refresh(self):
        self.all_sprites.update()
        self.screen.blit(self.background, (0, 0))
        score = self.game.get_score()
        font = pygame.font.Font(None, 74)
        text = font.render(f"{score[LEFT_PLAYER]}", 1, WHITE)
        self.screen.blit(text, (250, 10))
        text = font.render(f"{score[RIGHT_PLAYER]}", 1, WHITE)
        self.screen.blit(text, (SIZE[X]-250, 10))
        self.all_sprites.draw(self.screen)
        pygame.display.flip()

    def tick(self):
        self.clock.tick(FPS)

    @staticmethod
    def quit():
        pygame.quit()


def main(ip_address):
    try:
        with Client((ip_address, 6000), authkey=b'secret password') as conn:
            game = Game()
            side,gameinfo = conn.recv()
            print(f"I am playing {SIDESSTR[side]}")
            game.update(gameinfo)
            display = Display(game,side)
            while game.is_running():
                events = display.analyze_events(side)
                for ev in events:
                    conn.send(ev)
                    if ev == 'quit':
                        game.stop()
                conn.send("next")
                gameinfo = conn.recv()
                game.update(gameinfo)
                display.refresh()
                display.tick()
    except:
        traceback.print_exc()
    finally:
        pygame.quit()


if __name__=="__main__":
    ip_address = "25.16.183.216"
    if len(sys.argv)>1:
        ip_address = sys.argv[1]
    main(ip_address)

