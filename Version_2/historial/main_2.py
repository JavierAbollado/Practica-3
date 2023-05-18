import pygame
import socket
import pickle
import random
import os

# from constantes import *

# teclas para mover las barras: {s,x} y {k,m}.

# Me he puesto constantes en main para que no me de todo los warnings spyder
# Cuando este todo solucionado vuelvo a separarlo

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
PLAYER_1 = 0
PLAYER_2 = 1
PLAYER_SIZE = (15,70)

# ball & block
BALL_COLOR = WHITE
BALL_SIZE = 12
BLOCK_SIZE = (25,50)
FPS = 60
DELTA = 5 #30
VEL_BALL_X, VEL_BALL_Y = 2, 3 # velocidad de la bola

SIDES = ["left", "right"]

# images
load_image = lambda file_name, size : pygame.transform.scale(pygame.image.load(os.path.join("images", file_name)), size)
load_rotate_image = lambda file_name, size, angle : pygame.transform.scale(pygame.transform.rotate(pygame.image.load(os.path.join("images", file_name)), angle), size)

IM_background = load_image("blackbackground.png", SIZE)
IM_gameover = load_image("gameover.png", (SIZE[0]//2, SIZE[1]//5))
IM_block = [[load_image(f"rojo{i+1}.png", (10*BLOCK_SIZE[0]//8, 10*BLOCK_SIZE[1]//8)) for i in range(4)], 
                    [load_image(f"azul{i+1}.png", (10*BLOCK_SIZE[0]//8, 10*BLOCK_SIZE[1]//8)) for i in range(4)]]
IM_player = [load_rotate_image(name, PLAYER_SIZE, 270) for name in ["paleta_roja.png", "paleta_azul.png"]]

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

    def set_pos(self, pos):
        self.pos = pos
# Esto se gestion en sala
    # def moveDown(self):
    #     self.pos[Y] += DELTA
    #     if self.pos[Y] > SIZE[Y]:
    #         self.pos[Y] = SIZE[Y]

    # def moveUp(self):
    #     self.pos[Y] -= DELTA
    #     if self.pos[Y] < 0:
    #         self.pos[Y] = 0

    def __str__(self):
        return f"P<{SIDES[self.side], self.pos}>"

# La informacion deberia venir de sala
# Pero deberia haber una instancia local de la informacio i.e color
class Ball():
    # Velocity, Color, Alive  son  serverSide
    def __init__(self, color):  # color € {0,1} -> rojo y azul
        self.pos=[ SIZE[X]//2, SIZE[Y]//2 ]
        # Lineas originales de main
        self.color = color
        # self.velocity = velocity
        # self.alive = True
        
        # REVISAR SI NO HAY QUE INICIALIZARLO

    def get_pos(self):
        return self.pos
    
    def set_pos(self, pos):
        self.pos = pos

    # Lineas originales de main
    # Son operaciones de sala
    
    # def kill(self):
    #     self.alive = False

    # def update(self):
    #     self.pos[X] += self.velocity[X]
    #     self.pos[Y] += self.velocity[Y]

    # def bounce(self, AXIS):
    #     self.velocity[AXIS] = -self.velocity[AXIS]

    # def collide_player(self, AXIS=X):
    #     self.bounce(AXIS)
    #     for i in range(3):
    #         self.update()

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


    def set_pos_player(self, side, pos):
        self.players[side].set_pos(pos)

    def get_ball(self, color):
        return self.ball_1 if color == 0 else self.ball_2

    def set_ball_pos(self, pos):
        self.ball.set_pos(pos)

    # Legacy
    def get_score(self):
        return self.score
    # Legacy
    def set_score(self, score):
        self.score = score

    def game_over(self):
        self.running = False

    def is_running(self):
        return self.running

    # Legacy
    def stop(self):
        self.running = False

    # Lo hace sala
    # def moveUp(self, player):
    #     self.players[player].moveUp()

    # Lo hace sala
    # def moveDown(self, player):
    #     self.players[player].moveDown()

    # Lo hace sala
    # def movements(self):
    #     for ball in [self.ball_1, self.ball_2]:
    #         ball.update()
    #         pos = ball.get_pos()
    #         if pos[Y]<0 or pos[Y]>SIZE[Y]:
    #             ball.bounce(Y)
    #         if pos[X]>SIZE[X]:
    #             ball.bounce(X)
    #         elif pos[X]<0:
    #             ball.kill()

    # Documentar formato de game_info
    # Actualiza el display con la informacion de sala
    def update(self, gameinfo):
        self.set_pos_player(0, gameinfo['pos_left_player'])
        self.set_pos_player(1, gameinfo['pos_right_player'])
        self.set_ball_pos(gameinfo['pos_ball'])
        self.set_score(gameinfo['score'])
        self.running = gameinfo['is_running']
        
        
        
    def __str__(self):
        return f"G<{self.players[PLAYER_2]}:{self.players[PLAYER_1]}:{self.ball}>"


# OK
class Paddle(pygame.sprite.Sprite):
    # OK
    def __init__(self, player):
        super().__init__()
        self.player = player
        self.color = self.player.side
        self.image = IM_player[self.color]
        self.rect = self.image.get_rect()
        self.update()
    # OK
    def update(self):
        pos = self.player.get_pos()
        self.rect.centerx, self.rect.centery = pos
    # OK
    def __str__(self):
        return f"S<{self.player}>"


# Revisar
class BallSprite(pygame.sprite.Sprite):
    # OK
    def __init__(self, ball):
        super().__init__()
        self.ball = ball
        self.image = pygame.Surface((BALL_SIZE, BALL_SIZE))
        self.image.fill(BLACK)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.update()

    # Deberia ir dentro de update??
    def change_color(self): # {0,1} -> {1,0}
        self.ball.color = 1 - self.ball.color

    # OK
    def update(self):
        if not self.ball.alive:
            self.kill()
        color = RED if self.ball.color == 0 else BLUE
        # Esta linea deberia ir en __init__, no queremos dibujos en update
        pygame.draw.circle(self.image, color, (BALL_SIZE//2, BALL_SIZE//2), 
                           BALL_SIZE//2)
        pos = self.ball.get_pos()
        self.rect.centerx, self.rect.centery = pos

# Revisar
class Block(pygame.sprite.Sprite):    
    def __init__(self, pos, color=None, level=None):  # color € {0,1} -> rojo y azul
        super().__init__()
        self.pos = pos
        self.color = color if color != None else random.randint(0,1) # 2 colores € {0,1}
        self.level = level if level != None else random.randint(0,3) # X niveles € {0,1,...}
        self.image = pygame.Surface(BLOCK_SIZE)
        self.image.fill(BLACK)
        self.image.blit(IM_block[self.color][self.level], (0.1*BLOCK_SIZE[0],
                                                           0.1*BLOCK_SIZE[1]))
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = pos
        self.update()

    def get_shot(self):
        if self.level == 0:
            self.kill()
        else:
            self.level -= 1
        self.image.blit(IM_block[self.color][self.level], (0.1*BLOCK_SIZE[0],
                                                           0.1*BLOCK_SIZE[1]))

    # Update <-> get_shot en este caso?
    # Mirar si hay dibujos en get_shot
    def update(self):
        pass

# OK, metodo a llamar cuando self.running == 0
class GameOver(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = IM_gameover
        self.rect = self.image.get_rect()
        self.rect.center = (SIZE[0]//2, SIZE[1]//2)
    def draw(self, screen):
        screen.blit(self.image, self.rect)


# Construye la pantalla con la informacion que recibe
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
                block = Block((0.75*SIZE[0] + j*BLOCK_SIZE[0], 0.1*SIZE[1] +\
                               i*BLOCK_SIZE[1]))
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

    # Todas las operaciones que hace esto deberian estar en sala, copio funcion
    # LEGACY
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
        for ball, paddles in pygame.sprite.groupcollide(self.balls,
                                                        self.paddles,
                                                        False,
                                                        False).items():
            paddle = paddles[0]
            if ball.ball.color != paddle.color:
                ball.change_color()
            ball.ball.collide_player()
        
        # colisiones BOLA - Bloque
        for ball, blocks in pygame.sprite.groupcollide(self.balls,
                                                       self.blocks,
                                                       False,
                                                       False).items():
            block = blocks[0]
            if ball.ball.color == block.color:
                block.get_shot()
            AXIS = Y if ((abs(block.rect.top - ball.rect.bottom) <\
                          block.rect.width*0.1)
                            or (abs(block.rect.bottom - ball.rect.top) <\
                                block.rect.width*0.1)) else X
            ball.ball.collide_player(AXIS)
        if len(self.balls) == 0:
            self.game.game_over()
        self.all_sprites.update()
        
    # *** SIN TERMINAR ***
    # NOT OK
    def analyze_events_s(self):

        # comprobar salir del juego
        events = []
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                events.append("quit")
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q: # quit
                    events.append("quit")

        # mover palas
        keys = pygame.key.get_pressed()
        if keys[pygame.K_s]:
            events.append("up")
        if keys[pygame.K_x]:
            events.append("down")

        
        # ANADIR INDEX DE LAS KEYS DEL DICCIONARIO DEl COLLIDE
        # colisiones BOLA - PALA
        for ball, paddles in pygame.sprite.groupcollide(self.balls,
                                                        self.paddles,
                                                        False,
                                                        False).items():
            paddle = paddles[0]
            if ball.ball.color != paddle.color:
                # Modificar para indicar bola y color
                events.append("cambiar color")
            # Modificar para indicar que bola con que pala
            events.append("collide_bola_p")
        
        # colisiones BOLA - BLOQUE
        for ball, blocks in pygame.sprite.groupcollide(self.balls,
                                                       self.blocks,
                                                       False,
                                                       False).items():
            block = blocks[0]
            if ball.ball.color == block.color:
                events.append("bloque_golpeado")
            AXIS = Y if ((abs(block.rect.top - ball.rect.bottom) <\
                          block.rect.width*0.1)
                            or (abs(block.rect.bottom - ball.rect.top) <\
                                block.rect.width*0.1)) else X
            
            events.append("collision_bola_bloq")
    
        # Esto deberia hacerlo sala??
        if len(self.balls) == 0:
            self.game.game_over()
        self.all_sprites.update()

    # OK, representacion local
    def refresh(self):
        if not self.game.is_running():
            self.gameover.draw(self.screen)
        else:
            self.screen.blit(IM_background, (0, 0))
            self.all_sprites.draw(self.screen)
        pygame.display.flip()
    # OK
    def tick(self):
        self.clock.tick(FPS)

    # OK
    @staticmethod
    def quit():
        pygame.quit()

# Anadir conexion
# Anadir sistema de update de game en funcion de la informacion de sala

# NOT OK
def main(ip_address):
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
