from multiprocessing.connection import Client
import traceback
import pygame
import sys, random, time

from constantes import *
from sprites import Game, Ball, GameOver, LevelComplete, BlockNewBalls

SIDES = ["left", "right"]
SIDESSTR = ["left", "right"]



class Player_Display():

    def __init__(self, side):

        # game
        self.side = side
        self.other_side = 1 - side
        self.game = Game()
        self.id_ball = self.game.add_new_balls(n=2, id=0)
        self.id_especial_blocks = 0
        self.gameover = GameOver()
        self.levelcompleted = LevelComplete()

        # crear diccionarios para que los cambios recibidos por la sala sean más fáciles de ejecutar 
        # Obs: las claves van a ser los "id" de cada objeto
        self.dict_blocks = dict()
        for block in self.game.blocks:
            self.dict_blocks[block.id] = block
        self.dict_balls = dict()
        for ball in self.game.balls:
            self.dict_balls[ball.id] = ball
        self.dict_especialblocks = dict()

        # display
        self.quit = False
        self.screen = pygame.display.set_mode(SIZE)
        self.clock =  pygame.time.Clock()  #FPS
        pygame.init()

    def is_running(self):
        return not self.quit

    def add_new_balls(self, n, id):
        for i in range(n):
            random.seed(id+i)
            a = random.randint(2,10)
            b = random.randint(1,a-1)
            pos = [ (SIZE[0]*b)//a, SIZE[1]//2 ]
            velocity = [BALL_VEL[0] * (-1)**random.randint(0,1), -BALL_VEL[1]]
            color = random.randint(0,1)
            ball = Ball(velocity=velocity, color=color, pos=pos, id=id+i)
            self.dict_balls[ball.id] = ball
            self.game.balls.add(ball)
            self.game.all_sprites.add(ball)
        return id + n

    # Checkear solamente los movimientos de nuestra paleta (y el "quit")
    def analyze_events(self):
        
        events = []

        # salir del juego
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                events.append("quit")
                self.game.stop()
        
        # mover palas
        keys = pygame.key.get_pressed()
        if keys[pygame.K_KP4]:
            self.game.moveLeft(PLAYERS[self.side])
            events.append("left")
        if keys[pygame.K_KP6]:
            events.append("right")
            self.game.moveRight(PLAYERS[self.side])

        return events
    
    # Actualizar las posiciones del juego según los nuevos cambios en la sala
    # "changes" es una lista de strings
    def update_from_sala(self, changes):

        ####################################################################
        # FORMATO DE LOS CÓDIGOS: 
        # 
        # Tipo 1) Acciones sobre objetos existentes: 
        # ------------------------------------------
        # 
        # Código: "x1-x2-x3"
        #
        # donde,
        #    x1 = nombre del objeto afectado: ball, block, be
        #    x2 = id del objeto
        #    x3 = código de la acción a realizar
        #
        # códigos del x3 para cada objeto:
        #    ball:
        #       cc = change color
        #       c{X} = collide, con AXIS = X
        #    block:
        #       gs = get shot
        #    be:
        #       gs = get shot (crea X=3 bolas nuevas)
        # 
        # 
        # Tipo 2) Creación de nuevo objetos: 
        # ----------------------------------
        # 
        # Código: x1-x2 
        # 
        # donde, 
        #    x1 = "new", 
        #    x2 = nombre del nuevo objeto 
        # 
        # códigos de x2: 
        #    be : crear el bloque especial
        ####################################################################

        for change in changes:

            l = change.split("-")

            # Códigos Tipo 2
            if l[0] == "new":

                name = l[1]

                if name == "be":
                    b = BlockNewBalls(id=self.id_especial_blocks, pos=((SIZE[0]-BLOCK_SIZE[0])//2, (SIZE[1]-BLOCK_SIZE[1])//2))
                    self.id_especial_blocks += 1
                    self.game.blocks_new_balls.add(b)
                    self.game.all_sprites.add(b)
                    self.dict_especialblocks[b.id] = b

            # Códigos Tipo 1
            else:

                name, id, code = l[0], int(l[1]), l[2]

                if name == "ball":
                    if code == "cc":
                        self.dict_balls[id].change_color()
                    elif code[-1] == "0":
                        self.dict_balls[id].collide_player(AXIS=0)
                    elif code[-1] == "1":
                        self.dict_balls[id].collide_player(AXIS=1)
                    else:
                        print("Codigo ", code, " no conocido!")

                elif name == "block":
                    if code == "gs":
                        self.dict_blocks[id].get_shot()
                    else:
                        print("Codigo ", code, " no conocido!")

                elif name == "be":

                    if code == "gs":
                        self.dict_especialblocks[id].get_shot()
                        try:
                            self.dict_especialblocks[id].kill()
                        except:
                            print("Fallo con be")
                        self.id_ball = self.add_new_balls(n=3, id=self.id_ball)
                    else:
                        print("Codigo ", code, " no conocido!")

                else:
                    print("Codigo ", code, " no conocido!")

    
    # Actualizar las posiciones del juego según los nuevos cambios del otro jugador
    # "changes" es una lista de strings
    def update_from_player(self, changes):
        for event in changes:
            if event == "quit":
                self.stop()
            elif event == "left":
                self.game.moveLeft(PLAYERS[self.other_side])
            elif event == "right":
                self.game.moveRight(PLAYERS[self.other_side])

    # Refrescar la pantalla (antes debemos hacer un update)
    def refresh(self):
        self.game.all_sprites.update()
        # Si alguno ha perdido poner activar "Fin del Juego"
        # Según hallas ganado o perdido te aparecerá un mensaje diferente. 
        if not self.game.is_ended():
            if self.game.win:
                self.levelcompleted.draw(self.screen)
            else:
                self.gameover.draw(self.screen)
        # Si no, actualizar la partida 
        else:
            self.screen.blit(IM_background, (0, 0))
            self.game.all_sprites.draw(self.screen)
        pygame.display.flip()
        self.tick()

    def tick(self):
        self.clock.tick(FPS)


def send_events(events, conn):
    # for ev in events:
    #    conn.send(ev)
    #conn.send("next")
    conn.send(events)


def receive_events(conn):
    # events = []
    # ev = conn.recv()
    events = conn.recv()
    #while ev != "next":
    #    events.append(ev)
    #    ev = conn.recv()
    return events


def main(ip_address):
    try:
        with Client((ip_address, 6000), authkey=b'secret password') as conn:
            
            # recibir conexion
            side = conn.recv()
            print(f"I am playing {SIDESSTR[side]}")
            
            # inciar display
            myDisplay = Player_Display(side)

            # comenzar partida
            while myDisplay.is_running():

                # analizar (y enviar a la sala) mis movimientos
                events = myDisplay.analyze_events()
                send_events(events, conn)
                
                # recibir los cambios del otro jugador
                player_changes = receive_events(conn)
                myDisplay.update_from_player(player_changes)
                
                # recibir los cambios de la sala
                changes = receive_events(conn)
                myDisplay.update_from_sala(changes)
                
                # actualizar pantalla
                myDisplay.refresh()

    except:
        traceback.print_exc()
    finally:
        pygame.quit()


if __name__=="__main__":
    ip_address = "192.168.1.81"
    if len(sys.argv)>1:
        ip_address = sys.argv[1]
    main(ip_address)
