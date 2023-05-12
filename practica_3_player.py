from multiprocessing.connection import Client
import traceback
import pygame
import random
import sys, os
from constantes import *


class Player():
    # side € {0, 1}
    def __init__(self, side: int):
        self.side = side
        self.pos  = [0,0]

    def get_pos(self):
        return self.pos

    def get_side(self):
        return self.side

    def set_pos(self, pos):
        self.pos = pos

    def __str__(self):
        return f"P<{SIDES[self.side], self.pos}>"

class Ball():
    def __init__(self, ball_id: int, color: int):
        self.color   = color
        self.pos     = [None, None]
        self.ball_id = ball_id
        self.status = 1

    def get_pos(self):
        return self.pos

    def set_status(self, status):
        self.status = status

    def set_pos(self, pos):
        self.pos = pos

    def get_color(self):
        return self.color

    def set_color(self, color):
        self.color = color

    def __str__(self):
        return f"B<{self.pos}>"


class Block():
    def __init__(self, block_id: int, color: int):
        self.pos      = [0,0]
        self.color    = None
        self.vidas    = None
        self.block_id = block_id

    def get_pos(self):
        return self.pos

    def set_pos(self, pos):
        self.pos = pos

    def set_vidas(self, vidas):
        self.vidas = vidas

    def get_color(self):
        return self.color

    def set_color(self, color: int):
        self.color = color

    def __str__(self):
        return f"B<{self.pos}>"


class Game():
    def __init__(self):
        self.players = [Player(i) for i in range(2)]
        self.balls   = [Ball(i,i) for i in range(2)]
        self.blocks  = [Block(i, i%2) for i in range(12)] \
                        + [Block(i, 0) for i in range(12, 24)]
        self.running = True

    def get_player(self, side: int):
        return self.players[side]

    def set_pos_player(self, side: int, pos):
        self.players[side].set_pos(pos)


    def get_ball(self,ball_id):
        return self.balls[ball_id]


    def get_block(self, block_id: int):
        return self.blocks[block_id]

    def set_block_vida(self, block_id: int, vida):
        self.blocks[block_id].set_vida(vida)

    def set_ball_pos(self, ball_id: int, pos):
        self.balls[ball_id].set_pos(pos)


    def update(self, gameinfo):
        """
        

        Parameters
        ----------
        gameinfo : Dict
            Recibe toda la informacion del analisis de evento de sala.

        Actualiza el sprite de forma que:
            Le da su nueva posicion
            Le da su posible nuevo color
            Le da su posible nuevo eje
            Actualiza las vidas de los bloques
                Los colores de los bloques depende de las vidas que le mandan
            
        -------
        None.

        """
        self.set_pos_player(LEFT_PLAYER, gameinfo['pos_left_player'])
        self.set_pos_player(RIGHT_PLAYER, gameinfo['pos_right_player'])
        self.running = gameinfo['is_running']
        self.balls_dict=(gameinfo['balls_dict'])
        self.blocks_dict = gameinfo['bloques_dict']
        for i in range(2):

            self.balls[i].set_pos(self.balls_dict[i][2])
            self.balls[i].set_status(self.balls_dict[i][0])
            self.balls[i].set_color(self.balls_dict[i][1])
            # Color bolas, si hay que hacer cambio (val = 1)
            # Alternamos el color
        # self.bloques_dict=(gameinfo['bloques_dict'])
        for i in range(24):

            self.blocks[i].set_vidas(self.blocks_dict[i][0])
            self.blocks[i].set_color(self.blocks_dict[i][1])
            self.blocks[i].set_pos(self.blocks_dict[i][2])


    def is_running(self):
        return self.running

    def stop(self):
        self.running = False

    def __str__(self):
        return f"G<{self.players[RIGHT_PLAYER]}:{self.players[LEFT_PLAYER]}:{self.ball}>"



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
        self.ball_id=ball.ball_id
        self.color=ball.color
        self.image = pygame.Surface((BALL_SIZE, BALL_SIZE))
        self.image.fill(BLACK)
        self.image.set_colorkey(BLACK)
        pygame.draw.rect(self.image, self.color, [0, 0, BALL_SIZE, BALL_SIZE])
        self.rect = self.image.get_rect()
        self.update()

    def update(self):
        if self.ball.status==0:
            self.kill()
        else:
            color = RED if self.ball.color == 0 else BLUE
            pygame.draw.circle(self.image, color
                               , (BALL_SIZE//2, BALL_SIZE//2)
                               , BALL_SIZE//2)
            pos = self.ball.get_pos()
            (self.rect.centerx, self.rect.centery) = pos

class BlockSprite(pygame.sprite.Sprite):
    def __init__(self, block):  # color € {0,1} -> rojo y azul
        super().__init__()
        self.block=block
        if block.color == 0:
               self.color = BLUE_1
        else:
                self.color = RED_1

        self.pos = block.pos
        self.image = pygame.Surface(BLOCK_SIZE)
        self.image.fill(self.color)
        pygame.draw.rect(self.image, BLACK, [0, 0, BLOCK_SIZE[0]
                                                  , BLOCK_SIZE[1]]
                                                  , 1)
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = self.pos
        self.update()


    def update(self):
        """
        Los colores de los bloques cambian en funcion de las vidas que les
        manda sala.

        """
        local_color = self.color
        if self.block.vidas == 0:
            self.kill()

        if self.block.color == 0 and self.block.vidas == 1:
            self.color = BLUE_2


        if self.block.color == 1 and self.block.vidas == 1:
            self.color = RED_2

        if local_color != self.color:
            self.image.fill(self.color)
            pygame.draw.rect(self.image, BLACK, [0, 0, BLOCK_SIZE[0]
                                                          , BLOCK_SIZE[1]]
                                                          , 1)
            self.rect = self.image.get_rect()
            self.rect.left, self.rect.top = self.pos



class Display():
    def __init__(self, game, side: int):
        self.quit        = False
        self.game        = game
        self.list_blocks = list(range(24))
        self.list_balls  = list(range(2))

        # sprite groups
        self.paddles = pygame.sprite.Group()
        self.balls   = pygame.sprite.Group()
        self.blocks  = pygame.sprite.Group()

        # añadir sprites
        for padlle in [Paddle(self.game.get_player(i)) for i in range(2)]:
            self.paddles.add(padlle)

        for ball in [BallSprite(self.game.get_ball(i))
                     for i in self.list_balls]:
            self.balls.add(ball)


        for block in [BlockSprite(self.game.get_block(i))
                      for i in self.list_blocks]:
            self.blocks.add(block)
        self.all_sprites = pygame.sprite.Group()
        self.all_sprites.add(self.paddles)
        self.all_sprites.add(self.balls)
        self.all_sprites.add(self.blocks)

        self.screen = pygame.display.set_mode(SIZE)
        self.clock =  pygame.time.Clock()  #FPS
        self.background = pygame.image.load("images/fondo_3.jpg")
        pygame.init()

    def analyze_events(self, side: int):
        events = []
        for event in pygame.event.get():
            if side == 1:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        events.append("quit")
                    elif event.key == pygame.K_UP:
                        events.append("up")
                    elif event.key == pygame.K_DOWN:
                        events.append("down")
                elif event.type == pygame.QUIT:
                    events.append("quit")
            if side == 0:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        events.append("quit")
                    elif event.key == pygame.K_k:
                        events.append("up")
                    elif event.key == pygame.K_m:
                        events.append("down")
                elif event.type == pygame.QUIT:
                    events.append("quit")



        # colisiones BOLA - PALA
        for ball, paddle in pygame.sprite.groupcollide(self.balls
                                                       , self.paddles
                                                       , False
                                                       , False).items():
            ball_id=ball.ball_id
            color=ball.ball.color

            side_info = str(paddle[0].player.get_side())
            if side_info == str(side):
                event= "collide_p_b_" + side_info + "_" + str(ball_id)
                events.append(event)


        # colisiones BOLA - bloques
        for ball, blocks in pygame.sprite.groupcollide(self.balls
                                                       , self.blocks
                                                       , False
                                                       , False).items():
            ball_id  = ball.ball.ball_id
            color    = ball.ball.color
            block_id = blocks[0].block.block_id
            if side == ball_id:
                event = "collide_b_b_" + str(side) + "_" + str(ball_id) +\
                    "_" + str(block_id)
                events.append(event)

        return events


    def refresh(self):
        self.all_sprites.update()
        self.screen.blit(self.background, (0, 0))
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
