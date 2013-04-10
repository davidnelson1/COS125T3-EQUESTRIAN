import pygame, time, sys
from pygame.locals import *

#Constants
BLACK = (0, 0, 0) #Color code
FPS = 30 #The interval between frames
PLAYER_Y_SIZE = 40 #The pixel sizes of the player sprite
PLAYER_X_SIZE = 40
SCREEN_WIDTH = 800 #The values that determine the window size
SCREEN_HEIGHT = 600

pygame.init()
pygame.display.set_caption("Horse Game, Version 1")

#This class tracks data related to the player.
#There should only be one instance of this class.
class Player:
    def __init__(self, parent, horiz_dir):
        self.parent = parent
        #loads the player image and scales it to the required size
        self.image = pygame.transform.scale(pygame.image.load("testhorse.png"), (PLAYER_X_SIZE, PLAYER_Y_SIZE))
        self.rect = self.image.get_rect()
        self.rect.left = 240
        self.rect.top = 240
        self.horiz_dir = horiz_dir
    def move(self, xm, ym): #adjusts the player's position
        self.rect.left = self.rect.left + xm
        self.rect.top = self.rect.top + ym
    def input_check(self): #currently adjusts player movement direction
        if pygame.key.get_pressed()[K_LEFT]:
            self.horiz_dir = -1
        elif pygame.key.get_pressed()[K_RIGHT]:
            self.horiz_dir = 1
        else:
            self.horiz_dir = 0

#This class ties together the game window and all other top-level class instances.
#There should only be one instance of this class.
class Controller:
    def __init__(self, width, height): #This generates most other top-level class instances.
        self.window = pygame.display.set_mode([width, height])
        self.player = Player(self, 0)
        self.mainClock = pygame.time.Clock()
    def update_all(self): #Updates all updatable entities
        self.update_player()
        self.update_window()
    def update_window(self): #Updates the display
        self.window.fill(BLACK)
        self.window.blit(self.player.image,self.player.rect)
        pygame.display.update()
    def update_player(self): #Updates the player's position
        self.player.input_check()
        if self.player.horiz_dir == -1:
            self.player.move(-5, 0)
        elif self.player.horiz_dir == 1:
            self.player.move(5, 0)
    def run(self): #The main loop
        STOP = False
        while not STOP:
            self.mainClock.tick(FPS)
            self.update_all()
            for event in pygame.event.get():
                if event.type == QUIT:
                    STOP = True
                    pygame.quit()
                
                    

bwin = Controller(SCREEN_WIDTH, SCREEN_HEIGHT)
bwin.run()
