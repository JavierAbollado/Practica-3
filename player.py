from multiprocessing.connection import Client
import traceback
import pygame
import numpy as np
import sys, os, time

from constantes import *
from sprites import Game, GameOver, LevelComplete, BlockNewBalls

SIDES = ["left", "right"]
SIDESSTR = ["left", "right"]



class Player_Display():

    def __init__(self, side):

        # game
        self.side = side
        self.other_side = 1 - side
        self.game = Game()
        self.gameover = GameOver()
        self.levelcompleted = LevelComplete()

        # display
        self.quit = False
        self.screen = pygame.display.set_mode(SIZE)
        self.clock =  pygame.time.Clock()  #FPS
        pygame.init()

    # Checkear solamente los movimientos de nuestra paleta (y el "quit")
    def analyze_events(self):
        
        events = []

        # salir del juego
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                events.append("quit")
                self.stop()
        
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
        pass
    
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
        if not self.game.is_running():
            if self.game.win:
                self.levelcompleted.draw(self.screen)
            else:
                self.gameover.draw(self.screen)
        # Si no, actualizar la partida 
        else:
            self.screen.blit(IM_background, (0, 0))
            self.game.all_sprites.draw(self.screen)
        self.window.blit(self.screen, (0,0))
        pygame.display.flip()
        self.tick()

    def tick(self):
        self.clock.tick(FPS)


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
                for ev in events:
                    conn.send(ev)
                conn.send("next")
                
                # recibir los cambios del otro jugador
                player_changes = conn.recv()
                myDisplay.update_from_player(player_changes)
                
                # recibir los cambios de la sala
                changes = conn.recv()
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
