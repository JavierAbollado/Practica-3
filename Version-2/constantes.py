import pygame
import os

# teclas para mover las barras: {<,>} y {keypad 4, keypad 6}.

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

# ejes
X = 0
Y = 1

# general
SIZE = (700, 700) #525)
FPS = 60
DELTA = 10 # cantidad que se mueven las palas (velocidad)
SIDES = ["left", "right"]

# player 
PLAYERS = [0,1]
PLAYER_1 = 0
PLAYER_2 = 1
PLAYER_SIZE = (80,15) #(15,80)

# ball
BALL_COLOR = WHITE
BALL_SIZE = 12
BALL_VEL = (6,4)  #(2, 3) # velocidad de la bola

# block
BLOCK_SIZE = (55,25) # (25,55)


# images
image_path = "images"
load_image = lambda file_name, size : pygame.transform.scale(pygame.image.load(os.path.join(image_path, file_name)), size)
load_rotate_image = lambda file_name, size, angle : pygame.transform.scale(pygame.transform.rotate(pygame.image.load(os.path.join(image_path, file_name)), angle), size)

IM_background = load_image("background.jpg", SIZE)
IM_gameover = load_image("gameover.png", (SIZE[0]//2, SIZE[1]//7))
IM_levelcompleted = load_image("levelcompleted.png", (SIZE[0]//2,SIZE[1]//2))

IM_block = [[load_image(f"rojo{i+1}.png", (9*BLOCK_SIZE[0]//10, 9*BLOCK_SIZE[1]//10)) for i in range(4)], 
                    [load_image(f"azul{i+1}.png", (9*BLOCK_SIZE[0]//10, 9*BLOCK_SIZE[1]//10)) for i in range(4)]]
IM_player = [load_rotate_image(name, PLAYER_SIZE, 0) for name in ["paleta_roja.png", "paleta_azul.png"]]
IM_block_new_balls = load_rotate_image("block_new_balls.png", (9*BLOCK_SIZE[0]//10, 9*BLOCK_SIZE[1]//10), 0)
