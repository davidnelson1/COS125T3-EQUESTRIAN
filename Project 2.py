import pygame, time, sys
from pygame.locals import *

#Constants
BLACK = (0, 0, 0) #Color code
FPS = 40 #The frame rate
SCREEN_WIDTH = 800 #The values that determine the window size
SCREEN_HEIGHT = 600
TERRAIN_X_SIZE = 80 #The pixel size of a standard terrain block
TERRAIN_Y_SIZE = 60
PLAYER_X_SIZE = 2 * TERRAIN_X_SIZE / 3 #The pixel sizes of the player sprite
PLAYER_Y_SIZE = 2 * TERRAIN_Y_SIZE / 3
PLAYER_SPEED_RATIO = 20.0
PLAYER_ACCEL_RATIO = 160.0

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
        self.rect.left = (SCREEN_WIDTH / 2) - (self.rect.width / 2)
        self.rect.top = (SCREEN_HEIGHT / 2) - (self.rect.height / 2)
        self.horiz_dir = horiz_dir
        self.falling = False
        self.just_landed = False
        self.y_veloc = 0.0
    def move(self, xm, ym): #adjusts the player's position
        self.x = self.x + xm
        self.y = self.y + ym
    def input_check(self): #adjusts player movement direction
        if pygame.key.get_pressed()[K_LEFT]:
            if self.horiz_dir >= -2 and self.falling == False:
                self.horiz_dir = self.horiz_dir - TERRAIN_X_SIZE / PLAYER_ACCEL_RATIO
        elif pygame.key.get_pressed()[K_RIGHT]:
            if self.horiz_dir <= 2 and self.falling == False:
                self.horiz_dir = self.horiz_dir + TERRAIN_X_SIZE / PLAYER_ACCEL_RATIO
        elif self.falling == False:
            self.horiz_dir = 0
        if pygame.key.get_pressed()[K_UP] and self.falling == False and self.just_landed == False: #allows jumping while on the ground
            self.falling = True
            self.y_veloc = -TERRAIN_Y_SIZE / 4.5
    def gravity(self): #checks if the player has collided with the terrain
        if self.falling == False: #if the player is not falling and is not standing on a block, begin falling
            if self.just_landed == True: #This adds a waiting frame between possible jumps to prevent a collision issue
                self.just_landed = False
            for terrain in self.parent.terrain_list:
                if Rect(self.x, self.y + TERRAIN_Y_SIZE / 24, self.rect.width, self.rect.height).colliderect(terrain.rect):
                    return
            self.falling = True
            return
        else: #if the player is falling
            self.y_veloc = self.y_veloc + TERRAIN_Y_SIZE / 60.0 #accelerate downward
            if int(self.y_veloc) == 0:
                step = 1
            else:
                step = int(self.y_veloc / abs(self.y_veloc))
            for dist in range(step, int(self.y_veloc), step): #Check for collisions, and end fall if one is detected
                for terrain in self.parent.terrain_list:
                    if Rect(self.x, self.y + dist, self.rect.width, self.rect.height).colliderect(terrain.rect):
                        self.falling = False
                        self.y_veloc = 0.0
                        self.y = self.y + dist
                        self.just_landed = True
                        return
        self.move(0, self.y_veloc) #Actually move the player
    def movement_check(self): #checks to see if the player is allowed to continue moving, and stops or moves them as appropriate
        self.move((self.horiz_dir * TERRAIN_X_SIZE / PLAYER_SPEED_RATIO), 0)
        for terrain in self.parent.terrain_list:
            if Rect(self.x + (self.horiz_dir * TERRAIN_X_SIZE / PLAYER_SPEED_RATIO), self.y - TERRAIN_Y_SIZE / 24, self.rect.width, self.rect.height).colliderect(terrain.rect):
                self.move((-self.horiz_dir * TERRAIN_X_SIZE / PLAYER_SPEED_RATIO), 0)
                if self.horiz_dir > 0:
                    self.horiz_dir = self.horiz_dir - TERRAIN_X_SIZE / PLAYER_ACCEL_RATIO
                    self.movement_check()
                elif self.horiz_dir < 0:
                    self.horiz_dir = self.horiz_dir + TERRAIN_X_SIZE / PLAYER_ACCEL_RATIO
                    self.movement_check()
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
        self.generate_terrain(1)
    def update_all(self): #Updates all updatable entities
        self.update_player()
        self.update_window()
    def update_window(self): #Updates the display
        self.window.fill(BLACK) #Clear the screen
        self.window.blit(self.player.image, self.player.rect) #Draw the player
        for terrain in self.terrain_list: #Draw each terrain object
            draw_x = terrain.rect.left - self.player.x + self.player.rect.left
            draw_y = terrain.rect.top - self.player.y + self.player.rect.top
            self.window.blit(self.terrain_textures[terrain.ID], Rect(draw_x, draw_y, TERRAIN_X_SIZE, TERRAIN_Y_SIZE))
        pygame.display.update() #Move drawn objects to the screen
    def update_player(self): #Updates the player's position
        self.player.input_check() #Checks the player's input
        self.player.gravity() #Simulates gravity and downward collision detection
        if self.player.horiz_dir != 0:
            self.player.movement_check() #Horizontal movement and associated collision detection
    def create_terrain_texture(self, ID): #Generates a preloaded terrain texture for convenient access
        return pygame.transform.scale(pygame.image.load("Terrain" + str(ID) + ".png"), (TERRAIN_X_SIZE, TERRAIN_Y_SIZE))
    def generate_terrain(self, level_num): #Reads a given level and builds appropriate terrain
        terrain_raw = open(r"Level Data\Level " + str(level_num) + ".txt", "r") #Access the level file
        done_cycling = False
        while not done_cycling:
            terrain_obj_raw = terrain_raw.readline()[:-1] #obtain a line (minus the newline character)
            if terrain_obj_raw == "":
                done_cycling = True
            else:
                terrain_obj_split = terrain_obj_raw.split() #split the line into its component numbers
                self.terrain_list.append(Terrain(self, int(terrain_obj_split[0]), int(terrain_obj_split[1]), int(terrain_obj_split[2]))) #use the split numbers to create a terrain object
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
