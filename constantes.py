import pygame
import os

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
PLAYER_COLOR = [RED_1, BLUE]

# ejes
X = 0
Y = 1
SIZE = (525, 700)

# player 
LEFT_PLAYER = 0
RIGHT_PLAYER = 1
PLAYER_HEIGHT = 60
PLAYER_WIDTH = 10
PLAYER_1 = 0
PLAYER_2 = 1
PLAYER_SIZE = (PLAYER_HEIGHT, PLAYER_WIDTH)

# ball & block
BALL_COLOR = WHITE
BALL_SIZE = 12
BLOCK_SIZE =[40,40]
FPS = 60
DELTA = 30 
VEL_BALL_X, VEL_BALL_Y = 2, 2 # velocidad de la bola
SIDES = ["left", "right"]


SIDESSTR = ["left", "right"]


# images
load_image = lambda file_name, size : pygame.transform.scale(pygame.image.load(os.path.join("images", file_name)), size)
load_rotate_image = lambda file_name, size, angle : pygame.transform.scale(pygame.transform.rotate(pygame.image.load(os.path.join("images", file_name)), angle), size)

IM_background = load_image("blackbackground.png", SIZE)
IM_gameover = load_image("gameover.png", (SIZE[0]//2, SIZE[1]//5))
IM_block = [[load_image(f"rojo{i+1}.png", (10*BLOCK_SIZE[0]//8, 10*BLOCK_SIZE[1]//8)) for i in range(4)], [load_image(f"azul{i+1}.png", (10*BLOCK_SIZE[0]//8, 10*BLOCK_SIZE[1]//8)) for i in range(4)]]
IM_player = [load_rotate_image(name, PLAYER_SIZE, 90) for name in ["paleta_roja.png", "paleta_azul.png"]]