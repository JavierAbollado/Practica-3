from constantes import *
import random

class Player:

    def __init__(self, side):
        self.side = side
        if side == PLAYER_1:
            self.pos = [SIZE[0]//4, SIZE[1] - 10]
        else:
            self.pos = [3*SIZE[0]//4, SIZE[1] - 10]

    def get_pos(self):
        return self.pos

    def get_side(self):
        return self.side

    def moveLeft(self):
        self.pos[0] -= DELTA
        if self.pos[0] < 0:
            self.pos[0] = 0

    def moveRight(self):
        self.pos[0] += DELTA
        if self.pos[0] > SIZE[0]:
            self.pos[0] = SIZE[0]

    def __str__(self):
        return f"P<{SIDES[self.side], self.pos}>"


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


class Ball(pygame.sprite.Sprite):
    def __init__(self, velocity, color, pos, id):
        super().__init__()

        print("Ball", id)

        self.velocity = velocity
        self.color = color
        self.id = id
        self.pos = pos 
        
        self.image = pygame.Surface((BALL_SIZE, BALL_SIZE))
        self.image.fill(BLACK)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        color = RED if self.color == 0 else BLUE
        pygame.draw.circle(self.image, color, (BALL_SIZE//2, BALL_SIZE//2), BALL_SIZE//2)

    def change_color(self): # {0,1} -> {1,0}
        self.color = 1 - self.color
        color = RED if self.color == 0 else BLUE
        pygame.draw.circle(self.image, color, (BALL_SIZE//2, BALL_SIZE//2), BALL_SIZE//2)

    def bounce(self, AXIS):
        self.velocity[AXIS] = -self.velocity[AXIS]

    def collide_player(self, AXIS=Y):
        self.bounce(AXIS)
        for _ in range(3):
            self.update()

    def update(self):
        # actualizar posicion
        self.pos[X] += self.velocity[X]
        self.pos[Y] += self.velocity[Y]
        self.rect.centerx, self.rect.centery = self.pos
        # checkear que no se salga de la pantalla
        pos = self.pos
        if pos[Y] <= 0:
            self.bounce(Y)
        if pos[X] <= 0 or pos[X] >= SIZE[X]:
            self.bounce(X)
        elif pos[Y] > SIZE[Y]:
            self.kill()


class Block(pygame.sprite.Sprite): 
       
    def __init__(self, pos, id): #, color=None, level=None):  # color € {0,1} -> rojo y azul
        super().__init__()

        self.pos = pos
        self.id = id

        # el color y el nivel, como es random y se va a generar desde distintos ordenadores, 
        # tenemos que hacer que sea siempre el mismo dependiendo de su "id" que es único, 
        # así inicializamos una secuencia de nº aleatorios fija con "seed(id)".
        random.seed(self.id)
        self.color = random.randint(0,1) # 2 colores € {0,1}
        self.level = random.randint(0,3) # X niveles € {0,1,...}
        
        # gráficos del bloque
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


class BlockNewBalls(pygame.sprite.Sprite): 
       
    def __init__(self, pos, id): 
        super().__init__()
        self.id = id
        self.pos = pos
        self.level = 0
        self.image = pygame.Surface(BLOCK_SIZE)
        self.image.fill(BLACK)
        self.image.blit(IM_block_new_balls, (0.1*BLOCK_SIZE[0], 0.1*BLOCK_SIZE[1]))
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = pos
        
    def get_shot(self):
        if self.level == 0:
            super().kill()
        else:
            self.level -= 1

class GameOver(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = IM_gameover
        self.rect = self.image.get_rect()
        self.rect.center = (SIZE[0]//2, SIZE[1]//2)
    def draw(self, screen):
        screen.blit(self.image, self.rect)


class LevelComplete(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = IM_levelcompleted
        self.rect = self.image.get_rect()
        self.rect.center = (SIZE[0]//2, SIZE[1]//2)
    def draw(self, screen):
        screen.blit(self.image, self.rect)


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
        ############################################################################################
        # Antes (aquí) añadíamos 2 bolas directamente, ahora necesitamos darle un "id" a cada bola,
        # por lo que para tener organizado, vamos a llamar directamente a la función "add_new_balls"
        # pasandole el id inicial.
        ############################################################################################
        j = 0
        id_block = 0
        while 0.1*SIZE[0] + (j+1)*BLOCK_SIZE[0] < 0.9*SIZE[0]:
            i = 0
            while 0.1*SIZE[1] + (i+1)*BLOCK_SIZE[1] < 0.25*SIZE[1]:
                if id_block % 1 == 0:
                    block = Block((0.1*SIZE[0] + j*BLOCK_SIZE[0], 0.1*SIZE[1] + i*BLOCK_SIZE[1]), id=id_block)
                    self.blocks.add(block)
                id_block += 1
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
        self.end = False

    # "n" indica el nº de bolas que queremos añadir al juego, 
    # el color de cada bola será aleatorio (entre azul y rojo)
    # le pasamos el "id" actual del juego, y para cada bola nueva le sumamos +1, al final retornamos el "id" actualizado. 
    def add_new_balls(self, n, id):
        for i in range(n):
            # el mismo razonamiento que el bloque -> seed(id) para ser único para cada bola
            random.seed(id+i)
            a = random.randint(2,10)
            b = random.randint(1,a-1)
            pos = [ (SIZE[0]*b)//a, SIZE[1]//2 ]
            velocity = [BALL_VEL[0] * (-1)**random.randint(0,1), -BALL_VEL[1]]
            color = random.randint(0,1)
            ball = Ball(velocity=velocity, color=color, pos=pos, id=id+i)
            self.balls.add(ball)
            self.all_sprites.add(ball)
        return id + n
    
    # añadir bloque especial al juego (si chocan con el aparecen más bolas)
    def add_blocknewballs(self, id):
        b = BlockNewBalls(id=id, pos=((SIZE[0]-BLOCK_SIZE[0])//2, (SIZE[1]-BLOCK_SIZE[1])//2))
        self.blocks_new_balls.add(b)
        self.all_sprites.add(b)

    def get_player(self, side):
        return self.players[side]

    def game_over(self, win):
        self.win = win
        self.end = True

    def is_ended(self):
        return self.end

    def is_running(self):
        return self.running

    def stop(self):
        self.running = False

    def moveRight(self, player):
        self.players[player].moveRight()

    def moveLeft(self, player):
        self.players[player].moveLeft()
        
    #####################################################
    # quitamos "movements()" y lo introducimos 
    # directamente en el update de cada bola (más lógico) 
    #####################################################
