import pygame, time, sys
from pygame.locals import *

#Constants
BLACK = (0, 0, 0) #Color code
FPS = 40 #The frame rate
PLAYER_X_SIZE = 40 #The pixel sizes of the player sprite
PLAYER_Y_SIZE = 40
SCREEN_WIDTH = 800 #The values that determine the window size
SCREEN_HEIGHT = 600
TERRAIN_X_SIZE = 80 #The pixel size of a standard terrain block
TERRAIN_Y_SIZE = 60
PLAYER_SPEED_RATIO = 20.0

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
        self.x = 1 * TERRAIN_X_SIZE + .5 * PLAYER_X_SIZE + .0 #starting coordinates
        self.y = 2 * TERRAIN_Y_SIZE + .0 #the method for these will change with level generation
        self.rect.left = self.x
        self.rect.top = self.y
        self.horiz_dir = horiz_dir
        self.falling = False
        self.y_veloc = 0.0
    def move(self, xm, ym): #adjusts the player's position
        self.x = self.x + xm
        self.y = self.y + ym
    def input_check(self): #adjusts player movement direction
        if pygame.key.get_pressed()[K_LEFT]:
            self.horiz_dir = -1
        elif pygame.key.get_pressed()[K_RIGHT]:
            self.horiz_dir = 1
        else:
            self.horiz_dir = 0
        if pygame.key.get_pressed()[K_UP] and self.falling == False: #allows jumping while on the ground
            self.falling = True
            self.y_veloc = -TERRAIN_Y_SIZE / 5
    def gravity(self): #checks if the player has collided with the terrain
        if self.falling == False: #if the player is not falling and is not standing on a block, begin falling
            for terrain in self.parent.terrain_list:
                if self.rect.colliderect(terrain.rect):
                    return
            self.falling = True
            return
        else: #if the player is falling
            self.y_veloc = self.y_veloc + TERRAIN_Y_SIZE / 60 #accelerate downward
            for dist in range(0, int(self.y_veloc)): #Check for collisions, and end fall if one is detected
                for terrain in self.parent.terrain_list:
                    if Rect(self.x, self.y + dist, self.rect.width, self.rect.height).colliderect(terrain.rect):
                        self.falling = False
                        self.y_veloc = 0.0
                        self.y = self.y + dist
                        return
        self.move(0, self.y_veloc) #Actually move the player
    def movement_check(self): #checks to see if the player is allowed to continue moving, and stops or moves them as appropriate
        self.move((self.horiz_dir * TERRAIN_X_SIZE / PLAYER_SPEED_RATIO), 0)
        for terrain in self.parent.terrain_list:
            if Rect(self.x + (self.horiz_dir * TERRAIN_X_SIZE / PLAYER_SPEED_RATIO), self.y - TERRAIN_Y_SIZE / 24, self.rect.width, self.rect.height).colliderect(terrain.rect):
                self.move((-self.horiz_dir * TERRAIN_X_SIZE / PLAYER_SPEED_RATIO), 0)
                self.horiz_dir = 0
                return
                    

#This class tracks the locations and types of terrain data.
#There should be as many instances as dictated by the level.
class Terrain:
    def __init__(self, parent, terrain_ID, x_coord, y_coord):
        self.parent = parent
        self.ID = terrain_ID
        self.rect = Rect(0, 0, TERRAIN_X_SIZE, TERRAIN_Y_SIZE)
        self.rect.left = x_coord * TERRAIN_X_SIZE
        self.rect.top = y_coord * TERRAIN_Y_SIZE

#This class ties together the game window and all other top-level class instances.
#There should only be one instance of this class.
class Controller:
    def __init__(self, width, height): #This generates most other top-level class instances.
        self.window = pygame.display.set_mode([width, height])
        self.player = Player(self, 0)
        self.mainClock = pygame.time.Clock()
        self.terrain_textures = []
        for ID in range(1): #Add the terrain texture list to memory
            self.terrain_textures.append(self.create_terrain_texture(ID))
        self.terrain_list = []
        self.terrain_list.append(Terrain(self, 0, 1, 3))
        self.terrain_list.append(Terrain(self, 0, 2, 3))
        self.terrain_list.append(Terrain(self, 0, 3, 3))
        self.terrain_list.append(Terrain(self, 0, 4, 4))
        self.terrain_list.append(Terrain(self, 0, 5, 4))
        self.terrain_list.append(Terrain(self, 0, 6, 3))
    def update_all(self): #Updates all updatable entities
        self.update_player()
        self.update_window()
    def update_window(self): #Updates the display
        self.window.fill(BLACK) #Clear the screen
        self.window.blit(self.player.image, self.player.rect) #Draw the player
        for terrain in self.terrain_list: #Draw each terrain object
            self.window.blit(self.terrain_textures[terrain.ID], terrain.rect)
        pygame.display.update() #Move drawn objects to the screen
    def update_player(self): #Updates the player's position
        self.player.rect.left = self.player.x #Update the player's apparent location
        self.player.rect.top = self.player.y #to match their actual location
        self.player.input_check() #Checks the player's input
        self.player.gravity() #Simulates gravity and downward collision detection
        if self.player.horiz_dir != 0:
            self.player.movement_check() #Horizontal movement and associated collision detection
    def create_terrain_texture(self, ID): #Generates a preloaded terrain texture for convenient access
        return pygame.transform.scale(pygame.image.load("Terrain" + str(ID) + ".png"), (TERRAIN_X_SIZE, TERRAIN_Y_SIZE))
    def run(self): #The main loop
        STOP = False
        while not STOP: 
            self.mainClock.tick(FPS) #Wait until the next frame
            self.update_all()
            for event in pygame.event.get(): #If the window is closed, exit pygame
                if event.type == QUIT:
                    STOP = True
                    pygame.quit()


bwin = Controller(SCREEN_WIDTH, SCREEN_HEIGHT)
bwin.run()
