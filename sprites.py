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
    def __init__(self, velocity, color):
        super().__init__()

        self.color = color
        a = random.randint(2,10)
        b = random.randint(1,a-1)
        self.pos= [ (SIZE[0]*b)//a, SIZE[1]//2 ]
        self.velocity = velocity
        # self.alive = True
        
        self.image = pygame.Surface((BALL_SIZE, BALL_SIZE))
        self.image.fill(BLACK)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.update()

    def change_color(self): # {0,1} -> {1,0}
        self.color = 1 - self.color

    def bounce(self, AXIS):
        self.velocity[AXIS] = -self.velocity[AXIS]

    def collide_player(self, AXIS=Y):
        self.bounce(AXIS)
        for _ in range(3):
            self.update()

    def update(self):
        self.pos[X] += self.velocity[X]
        self.pos[Y] += self.velocity[Y]
        # if not self.ball.alive:
        #     self.kill()
        color = RED if self.color == 0 else BLUE
        pygame.draw.circle(self.image, color, (BALL_SIZE//2, BALL_SIZE//2), BALL_SIZE//2)
        self.rect.centerx, self.rect.centery = self.pos


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


class BlockNewBalls(pygame.sprite.Sprite): 
       
    def __init__(self, pos): 
        super().__init__()
        self.pos = pos
        self.image = pygame.Surface(BLOCK_SIZE)
        self.image.fill(BLACK)
        self.image.blit(IM_block_new_balls, (0.1*BLOCK_SIZE[0], 0.1*BLOCK_SIZE[1]))
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = pos

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