
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr  2 20:14:46 2023

@author: davidp
"""

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
# load_image = lambda file_name, size : pygame.transform.scale(pygame.image.load(os.path.join("images", file_name)), size)
# load_rotate_image = lambda file_name, size, angle : pygame.transform.scale(pygame.transform.rotate(pygame.image.load(os.path.join("images", file_name)), angle), size)

# IM_background = load_image("blackbackground.png", SIZE)
# IM_gameover = load_image("gameover.png", (SIZE[0]//2, SIZE[1]//5))
# IM_block = [[load_image(f"rojo{i+1}.png", (10*BLOCK_SIZE[0]//8, 10*BLOCK_SIZE[1]//8)) for i in range(4)], 
#                     [load_image(f"azul{i+1}.png", (10*BLOCK_SIZE[0]//8, 10*BLOCK_SIZE[1]//8)) for i in range(4)]]
# IM_player = [load_rotate_image(name, PLAYER_SIZE, 270) for name in ["paleta_roja.png", "paleta_azul.png"]]


from multiprocessing.connection import Listener
from multiprocessing import Process, Manager, Value, Lock
import traceback
import sys

class Player():
    def __init__(self, side: int):
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
        self.pos[Y]    += DELTA
        if self.pos[Y]  > SIZE[Y]:
            self.pos[Y] = SIZE[Y]

    def moveUp(self):
        self.pos[Y]    -= DELTA
        if self.pos[Y]  < 0:
            self.pos[Y] = 0

    def __str__(self):
        return f"P<{SIDES[self.side], self.pos}>"

# Cada jugador solo interacciona con las bolas del otro color
# Esto se gestiona a nivel de jugador
# Jugador ve colision -> comprueba si es suya -> manda mensaje
# -> Interpretamos mensaje
class Ball():
    def __init__(self, velocity, color: int):  # color € {0,1} -> rojo y azul
        self.color = color
        self.pos=[ SIZE[X]//2, SIZE[Y]//2 ]
        self.velocity = velocity
        self.alive = True 
        # Probablemente esto deberia llegar en mensaje

    def get_pos(self):
        return self.pos

    # Probablemente esto deberia llegar en mensaje
    def kill(self):
        self.alive = False
    
    def get_status(self):
        return self.alive
    
    def get_color(self):
        return self.color

    def change_color(self):
        self.color = (self.color - 1)%2
    
    def update(self):
        self.pos[X] += self.velocity[X]
        self.pos[Y] += self.velocity[Y]

    def bounce(self, AXIS):
        self.velocity[AXIS] = -self.velocity[AXIS]

    # Reutilizable como collide block??
    def collide_player(self, AXIS=X):
        self.bounce(AXIS)
        for i in range(3):
            self.update()

    def __str__(self):
        return f"B<{self.pos}>"


class Game():
    def __init__(self, manager):
        self.players_s = manager.list([Player(i) for i in range(2)])
        
        self.ball_s = manager.list([Ball([-1*VEL_BALL_X, VEL_BALL_Y], color=0),
                       Ball([VEL_BALL_X, VEL_BALL_Y], color=1)])

        self.score_s = manager.list([0,0])

        #  1 <-> True; 0 <-> False
        self.running_s = Value('i', 1)
        
        self.block_lives = manager.dict()
        self.ball_info = manager.dict()
        # Cambiar esto por el numero correcto
        for i in range(12):
            # Es dos la vida inicial de un bloque?
            self.block_lives[i] = (2, i%2, (0,0))
        
        for i in range(len(list(self.ball_s))):
            self.ball_info[i] = (1, i%2, 700//2, 525//2)
            
        self.lock = Lock()

    # OK
    def get_player(self, side: int):
        return self.players_s[side]

    # OK
    def get_ball(self, color: int): 
        # Linea editada 
        return self.ball_s[0] if color == 0 else self.ball_s[1]

    def get_score(self):
        return list(self.score_s)

    # OK <-> stop()
    def game_over(self):
        self.running.value = 0

    # OK
    def is_running(self):
        return self.running_s.value == 1

    # OK
    # Player <-> Side € {0, 1}
    def moveUp(self, player: int):
        self.lock.acquire()
        p = self.players_s[player]
        p.moveUp()
        self.players_s[player] = p
        self.lock.release()

    def moveDown(self, player: int):
        self.lock.acquire()
        p = self.players_s[player]
        p.moveDown()
        self.players_s[player] = p
        self.lock.release()
        
    
    # Queda el equivalente a ball_colide(self, player)
    # OK
    def ball_collide(self, player: int, ball_index: int):
        self.lock.acquire()
        ball = self.ball_s[ball_index]
        ball.collide_player(player)
        self.ball[ball_index] = ball
        self.lock.release()
        
    # Falta ball collide bloque

    # OK
    def movements(self):
        self.lock.acquire()
        # Lineas originales de main
        # for ball in [self.ball_1, self.ball_2]:
        #     ball.update()
        #     pos = ball.get_pos()
        #     if pos[Y]<0 or pos[Y]>SIZE[Y]:
        #         ball.bounce(Y)
        #     if pos[X]>SIZE[X]:
        #         ball.bounce(X)
        #     elif pos[X]<0:
        #         ball.kill()

        for index, b in enumerate(list(self.ball_s)):
            ball = self.ball_s[index]
            ball.update()
            pos = ball.get_pos()
            if pos[Y]<0 or pos[Y]>SIZE[Y]:
                ball.bounce(Y)
            if pos[X]>SIZE[X]:
                ball.bounce(X)
            elif pos[X]<0:
                ball.kill()
            self.ball_s[index] = ball
                
        self.lock.release()

    def get_block_lives(self):
        return self.block_lives
    
    def set_block_lives(self, block_index):
        self.lock.acquire()
        p = self.block_lives[block_index]
        p -= 1
        self.block_lives[block_index] = p
        self.lock.release()
    
    def change_colors_g(self, ball_index: int):
        self.lock.acquire()
        # Version de si queremos guardar el color
        # ball_c = self.ball_s[ball_index].color
        # ball_c = (ball_c - 1)%2
        # self.ball[ball_index] = ball_c
        
        # Version que solo dice que ha cambiado el color
        ball_c = self.ball_s[ball_index].color
        ball_c = 1
        self.ball[ball_index] = ball_c
        self.lock.release()
        
    def colors_not_changed(self, ball_index: int):
        self.lock.acquire()
        ball_c = self.ball_s[ball_index].color
        ball_c = 0
        self.ball_s[ball_index].color = ball_c
        self.lock.release()
    # OK, revisar si falta mas informacion
    def get_info(self):
        info = {
            'pos_left_player': self.players_s[0].get_pos(),
            'pos_right_player': self.players_s[1].get_pos(),
            'score': list(self.score_s),
            'is_running': self.running_s.value == 1,
            # {id_bloque: (vida, {0 -> mismo color
            #                   , 1 -> cambio de color}, posicion), ..}
            'bloques_dict': dict(self.block_lives),  
            # {id_bola: (status, color, posicion), ..}
            'balls_dict'   : dict(self.ball_info)
            
        }
        return info

    def __str__(self):
        return f"G<{self.players_s[PLAYER_2]}:{self.players_s[PLAYER_1]}:{self.ball_s}>"

# OK
# Revisar si faltan comandos
# Observacion: las bolas deben ir nombradas como el side
# ball 0 <-> side 0 <-> player 0
def player(side: int, conn, game):
    try:
        # print(f"starting player {SIDESSTR[side]}:{game.get_info()}")
        conn.send( (side, game.get_info()) )
        while game.is_running():
            command = ""
            while command != "next":
                command = conn.recv()
                if command == "up":
                    game.moveUp(side)
                elif command == "down":
                    game.moveDown(side)
                # collide_p_b_X_Y, X : side, Y : ball_index
                # Combandos colision bola-pala
                for termination in [str(i)+"_"+str(j) 
                                    for i in range(2) for j in range(2)]:
                    partida = termination.split("_")
                    side = partida[-2]
                    ball_index = partida[-1]
                    if command == "collide_p_b_" + termination:
                        game.ball_collide(side, ball_index)
                        # mismo color y cambiamos al opuesto
                        if side == game.ball_s[ball_index].color:
                            game.change_colors_g(ball_index)
                        else:
                            game.colors_not_changed(ball_index)
                # Vamos a hacer lo mismo con los bloques
                # Comandos colision bola-bloque
                # Color va implicito en side
                # collide_b_b_X_Y_Z
                # X: jugador(side) Y: ball_index , Z : block_index
                # Supongamos la existencia de una constante inicial NBLOQUES
                NBLOQUES = 12 #MOVER A GLOBAL
                for termination in [str(side) + "_" +str(i) + "_" + str(j) 
                                    for i in range(2)
                                    for j in range(NBLOQUES)]:
                    partida = termination.split("_")
                    side = partida[-3]
                    ball_index = partida[-2]
                    block_index = partida[-1]
                    if command == "collide_b_b_" + termination:
                        # Bien def block collide? Creo que si
                        game.ball_collide(side, ball_index)
                        
                        # Si bola.color == bloque.color, bloque.vida -= 1
                        if game.ball_s[ball_index].color ==\
                        game.block_lives[block_index][1]:
                            game.set_block_lives(block_index)
                            pass

                if command == "quit":
                    game.game_over()

            if side == 1:
                game.move_ball()
            conn.send(game.get_info())
    except:
        traceback.print_exc()
        conn.close()
    finally:
        print(f"Game ended {game}")

# QUASI OK
# Seguramente falten adiciones
def main(ip_address):
    manager = Manager()
    # Lineas origianles main
    # try:
    #     game = Game()
    #     display = Display(game)

    #     while not display.quit:
    #         game.movements()
    #         display.analyze_events()
    #         display.refresh()
    #         display.tick()
    # finally:
    #     pygame.quit()
    try:
        with Listener((ip_address, 6000),
                      authkey=b'secret password') as listener:
            n_player = 0
            players = [None, None]
            game = Game(manager)
            while True:
                print(f"accepting connection {n_player}")
                conn = listener.accept()
                players[n_player] = Process(target=player,
                                            args=(n_player, conn, game))
                n_player += 1
                if n_player == 2:
                    players[0].start()
                    players[1].start()
                    n_player = 0
                    players = [None, None]
                    game = Game(manager)

    except Exception as e:
        traceback.print_exc()
if __name__=="__main__":
    ip_address = "127.0.0.1"
    if len(sys.argv)>1:
        ip_address = sys.argv[1]

    main(ip_address)
