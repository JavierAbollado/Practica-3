from multiprocessing.connection import Client
import traceback
import pygame
import numpy as np
import sys, os

from constantes import FPS, SIZE

SIDES = ["left", "right"]
SIDESSTR = ["left", "right"]

class Player_Display:

    def __init__(self, side):
        pygame.init()
        self.side = side
        self.screen = pygame.display.set_mode(SIZE)
        self.clock =  pygame.time.Clock()  #FPS
        self.runnig = True
    
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
            events.append("left")
        if keys[pygame.K_KP6]:
            events.append("right")

        return events
    
    def is_running(self):
        return self.runnig

    def stop(self):
        self.runnig = False
    
    def update(self, screen):
        self.screen.blit(screen, (0, 0))
        pygame.display.flip()
        # self.clock.tick(FPS)
    
    @staticmethod
    def quit():
        pygame.quit()


def recv_screen(conn):
    data = conn.recv_bytes()
    pixels = np.frombuffer(data, dtype=np.uint8)
    image = pygame.surfarray.make_surface(pixels.reshape((SIZE[1], SIZE[0], 3)))
    return image


def main(ip_address):
    try:
        with Client((ip_address, 6000), authkey=b'secret password') as conn:
            
            # recibir conexion
            side = conn.recv()
            print(side)
            # screen = conn.recv() 
            print(f"I am playing {SIDESSTR[side]}")
            
            # inciar display
            myDisplay = Player_Display(side)

            # comenzar partida
            while myDisplay.is_running():
                events = myDisplay.analyze_events()
                for ev in events:
                    conn.send(ev)
                conn.send("next")
                screen = recv_screen(conn)
                myDisplay.update(screen)
    except:
        traceback.print_exc()
    finally:
        pygame.quit()


if __name__=="__main__":
    ip_address = "192.168.1.81"
    if len(sys.argv)>1:
        ip_address = sys.argv[1]
    main(ip_address)
