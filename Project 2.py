import pygame, time, sys
from pygame.locals import *

#Constants
BLACK = (0, 0, 0) #Color code
FPS = 40 #The frame rate
SCREEN_WIDTH = 800 #The values that determine the window size
SCREEN_HEIGHT = 600
TERRAIN_X_SIZE = SCREEN_WIDTH / 10 #The pixel size of a standard terrain block
TERRAIN_Y_SIZE = SCREEN_HEIGHT / 10
PLAYER_X_SIZE = 2 * TERRAIN_X_SIZE / 3 #The pixel sizes of the player sprite
PLAYER_Y_SIZE = 2 * TERRAIN_Y_SIZE / 3
PLAYER_SPEED_RATIO = 15.0 #The number of frames it takes the player to travel 1 block
ENEMY_X_SIZE = [TERRAIN_X_SIZE / 2, TERRAIN_X_SIZE / 2, 2 * TERRAIN_X_SIZE / 3] #The pixel sizes of the enemy sprites
ENEMY_Y_SIZE = [TERRAIN_Y_SIZE / 4, 2 * TERRAIN_Y_SIZE / 3, 2 * TERRAIN_Y_SIZE / 3]
ENEMY_SPEED_RATIO = [10.0, 30.0, 20.0] #The number of frames it takes each enemy to travel 1 block

pygame.init()
pygame.display.set_caption("Horse Game, Version 5.0")

#This class tracks data related to the player.
#There should only be one instance of this class.
class Player:
    def __init__(self, parent, x_veloc):
        self.parent = parent
        #loads the player image and scales it to the required size
        self.image = pygame.transform.scale(pygame.image.load("testhorse.png"), (PLAYER_X_SIZE, PLAYER_Y_SIZE))
        self.rect = self.image.get_rect()
        self.rect.left = (SCREEN_WIDTH / 2) - (self.rect.width / 2)
        self.rect.top = (SCREEN_HEIGHT / 2) - (self.rect.height / 2)
        self.x_veloc = x_veloc
        self.x = 0
        self.y = 0
        self.falling = False
        self.just_landed = False
        self.y_veloc = 0.0
    def move(self, xm, ym): #adjusts the player's position
        self.x = self.x + xm
        self.y = self.y + ym
        self.parent.parallax[0] = self.parent.parallax[0] - xm / 5
        if self.parent.parallax[0] <= -2 * SCREEN_WIDTH:
            self.parent.parallax[0] = self.parent.parallax[0] + 2 * SCREEN_WIDTH
    def input_check(self): #adjusts player movement direction
        if pygame.key.get_pressed()[K_LSHIFT]: #increases the player's movement speed if shift is held
            adjust_length = 2
        else:
            adjust_length = 1
        if pygame.key.get_pressed()[K_LEFT]: #moves the player left or right
                self.x_veloc = -adjust_length
        elif pygame.key.get_pressed()[K_RIGHT]:
                self.x_veloc = adjust_length
        elif self.falling == False: #makes the player stop moving when grounded and not attempting to move
            self.x_veloc = 0
        if pygame.key.get_pressed()[K_UP] and self.falling == False and self.just_landed == False: #allows jumping while on the ground
            self.falling = True
            self.y_veloc = -TERRAIN_Y_SIZE / 4.5
    def gravity(self): #checks if the player has collided with the terrain
        if self.falling == False: #if the player is not falling and is not standing on a block, begin falling
            if self.just_landed == True: #This adds a waiting frame between possible jumps to prevent a collision issue
                self.just_landed = False
            for terrain in self.parent.terrain_list:
                if terrain.ID <= 9: #check if the block is collideable
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
                    if Rect(self.x, self.y, self.rect.width, self.rect.height).colliderect(terrain.rect):
                        if terrain.ID <= 9:
                            self.falling = False
                            self.y_veloc = 0.0
                            self.y = self.y - TERRAIN_Y_SIZE / 24
                            self.just_landed = True
                            return
                        elif terrain.ID <= 19:
                            self.parent.death()
                            return
                        elif terrain.ID == 20:
                            self.parent.victory()
                            return
                    elif Rect(self.x, self.y + dist, self.rect.width, self.rect.height).colliderect(terrain.rect):
                        if terrain.ID <= 9:
                            self.falling = False
                            self.y_veloc = 0.0
                            self.y = self.y + dist
                            self.just_landed = True
                            return
                        elif terrain.ID <= 19:
                            self.parent.death()
                            return
                        elif terrain.ID == 20:
                            self.parent.victory()
                            return
        self.move(0, self.y_veloc) #Actually move the player
    def movement_check(self): #checks to see if the player is allowed to continue moving, and stops or moves them as appropriate
        self.move((self.x_veloc * TERRAIN_X_SIZE / PLAYER_SPEED_RATIO), 0)
        for terrain in self.parent.terrain_list:
            if Rect(self.x, self.y - TERRAIN_Y_SIZE / 24, self.rect.width, self.rect.height).colliderect(terrain.rect):
                if terrain.ID <= 9: #If the block is collideable, prevent collision
                    self.move((-self.x_veloc * TERRAIN_X_SIZE / PLAYER_SPEED_RATIO), 0)
                    if self.x_veloc > 0:
                        self.x_veloc = self.x_veloc - 1
                        self.movement_check()
                    elif self.x_veloc < 0:
                        self.x_veloc = self.x_veloc + 1
                        self.movement_check()
                    return
                elif terrain.ID <= 19: #If the block is lethal, kill player
                    self.parent.death()
                    return
                elif terrain.ID == 20: #If the block is an end point, succeed and move to next level
                    self.parent.victory()
                    return
        for enemy in self.parent.enemy_list: #Check for enemy collisions
            if Rect(self.x, self.y, self.rect.width, self.rect.height).colliderect(enemy.rect):
                self.parent.death()

#Tracks the enemy behavior--is largely based on the Player class.
#Spawned in as necessary by script terrain.
class Enemy:
    def __init__(self, parent, enemy_ID, x_coord, y_coord):
        self.parent = parent
        self.ID = enemy_ID
        self.rect = Rect(x_coord * TERRAIN_X_SIZE, y_coord * TERRAIN_Y_SIZE, ENEMY_X_SIZE[self.ID], ENEMY_Y_SIZE[self.ID])
        self.x = x_coord * TERRAIN_X_SIZE
        self.y = y_coord * TERRAIN_Y_SIZE
        self.x_veloc = 0
        self.y_veloc = 0
        self.falling = False
        self.just_landed = False
        self.next_direction = -1 #This is only used by bears and wolves
        self.dir_swapped = True #This is used by wolves only
    def move(self, xm, ym):
        self.x = self.x + xm
        self.y = self.y + ym
        self.rect.left = self.x
        self.rect.top = self.y
    def gravity(self): #checks if the enemy has collided with the terrain
        if self.falling == False: #if the enemy is not falling and is not standing on a block, begin falling
            if self.just_landed == True: #This adds a waiting frame between possible jumps to prevent a collision issue
                self.just_landed = False
            for terrain in self.parent.terrain_list:
                if terrain.ID <= 9: #check if the block is collideable
                    if Rect(self.rect.left, self.rect.top + TERRAIN_Y_SIZE / 24, self.rect.width, self.rect.height).colliderect(terrain.rect):
                        return
            self.falling = True
            return
        else: #if the enemy is falling
            self.y_veloc = self.y_veloc + TERRAIN_Y_SIZE / 60.0 #accelerate downward
            if int(self.y_veloc) == 0:
                step = 1
            else:
                step = int(self.y_veloc / abs(self.y_veloc))
            for dist in range(step, int(self.y_veloc), step): #Check for collisions, and end fall if one is detected
                for terrain in self.parent.terrain_list:
                    if Rect(self.rect.left, self.rect.top + dist, self.rect.width, self.rect.height).colliderect(terrain.rect):
                        if terrain.ID <= 9:
                            self.falling = False
                            self.y_veloc = 0.0
                            self.y = self.y + dist
                            self.just_landed = True
                            return
                        elif terrain.ID <= 19:
                            self.parent.enemy_list.remove(self)
                            return
        self.move(0, self.y_veloc) #Actually move the enemy
    def AI(self):
        if self.ID == 0: #Perform snake behavior
            if not self.parent.player.falling and not self.falling: #Chase the player while both are grounded
                if self.parent.player.x <= self.rect.left + SCREEN_WIDTH / 2 + self.rect.width and self.rect.left <= self.parent.player.x:
                    if self.parent.player.x - self.x < TERRAIN_X_SIZE / ENEMY_SPEED_RATIO[self.ID]:
                        self.x_veloc = (self.parent.player.x - self.x) / (TERRAIN_X_SIZE / ENEMY_SPEED_RATIO[self.ID])
                    else:
                        self.x_veloc = 1
                elif self.parent.player.x >= self.rect.left - SCREEN_WIDTH / 2 - self.parent.player.rect.width and self.rect.left >= self.parent.player.x:
                    if self.x - self.parent.player.x < TERRAIN_X_SIZE / ENEMY_SPEED_RATIO[self.ID]:
                        self.x_veloc = (self.parent.player.x - self.x) / (TERRAIN_X_SIZE / ENEMY_SPEED_RATIO[self.ID])
                    else:
                        self.x_veloc = -1
                else:
                    self.x_veloc = 0
        elif self.ID == 1: #Perform bear behavior
            if not self.falling:
                if self.x_veloc == 0:
                    self.x_veloc = self.next_direction
                    self.next_direction = -self.next_direction
        elif self.ID == 2: #Perform wolf behavior
            if not self.falling:
                if self.parent.frame_tick % 80 == 0:
                    self.x_veloc = self.next_direction
                    self.y_veloc = -TERRAIN_Y_SIZE / 4.5
                    self.falling = True
                    self.dir_swapped = False
                else:
                    self.x_veloc = 0
            else:
                if self.x_veloc == 0 and self.falling == True and self.dir_swapped == False:
                    self.next_direction = -self.next_direction
                    self.dir_swapped = True
                    
    def movement_check(self): #checks to see if the enemy is allowed to continue moving, and stops or moves them as appropriate
        self.move((self.x_veloc * TERRAIN_X_SIZE / ENEMY_SPEED_RATIO[self.ID]), 0)
        for terrain in self.parent.terrain_list:
            if Rect(self.rect.left, self.rect.top - TERRAIN_Y_SIZE / 24, self.rect.width, self.rect.height).colliderect(terrain.rect):
                if terrain.ID <= 9: #If the block is collideable, prevent collision
                    self.move((-self.x_veloc * TERRAIN_X_SIZE / ENEMY_SPEED_RATIO[self.ID]), 0)
                    self.x_veloc = 0
                    return
                elif terrain.ID <= 19: #If the block is lethal, kill enemy
                    self.parent.enemy_list.remove(self)
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
        self.frame_tick = 0 #Used for bear spawning
        self.window = pygame.display.set_mode([width, height])
        self.player = Player(self, 0)
        self.mainClock = pygame.time.Clock()
        self.terrain_textures = []
        for ID in range(22): #Add the terrain texture list to memory
            self.terrain_textures.append(self.create_terrain_texture(ID))
        self.enemy_textures = []
        for ID in range(3):
            self.enemy_textures.append(self.create_enemy_texture(ID))
        self.terrain_list = []
        self.enemy_list = []
        self.background_texture = pygame.transform.scale(pygame.image.load(r"anim\Background.png"), (SCREEN_WIDTH * 2, SCREEN_HEIGHT * 2))
        self.parallax = [-SCREEN_WIDTH, -SCREEN_HEIGHT / 3]
        self.level = 1
        self.load_level(self.level)
        self.messages = pygame.transform.scale(pygame.image.load(r"anim\Victory.png"), (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 8))
        self.messages_rect = self.messages.get_rect()
    def update_all(self): #Updates all updatable entities
        self.update_player()
        self.update_enemies()
        self.update_window()
        self.frame_tick = self.frame_tick + 1
    def update_window(self): #Updates the display
        self.draw_stuff()
        pygame.display.update() #Move drawn objects to the screen
    def update_enemies(self):
        if self.frame_tick % 120 == 0:
            for terrain in self.terrain_list:
                if terrain.ID == 21:
                    self.enemy_list.append(Enemy(self, 1, terrain.rect.left / TERRAIN_X_SIZE, (terrain.rect.top) / TERRAIN_Y_SIZE + 1.0/3))
        for enemy in self.enemy_list:
            enemy.gravity()
            enemy.AI()
            enemy.movement_check()
    def draw_stuff(self):
        self.window.blit(self.background_texture, Rect(self.parallax[0], self.parallax[1], 0, 0)) #Draw the background
        self.window.blit(self.background_texture, Rect(self.parallax[0] + 2 * SCREEN_WIDTH, self.parallax[1], 0, 0))
        for terrain in self.terrain_list: #Draw each terrain object
            if terrain.ID <= 21: #Excludes script terrain from the draw procedure
                    draw_x = terrain.rect.left - self.player.x + self.player.rect.left #place the terrain based on the player's locatioin
                    draw_y = terrain.rect.top - self.player.y + self.player.rect.top
                    if draw_x <= SCREEN_WIDTH and draw_x >= -TERRAIN_X_SIZE and draw_y <= SCREEN_HEIGHT and draw_y >= -TERRAIN_Y_SIZE:
                        self.window.blit(self.terrain_textures[terrain.ID], Rect(draw_x, draw_y, TERRAIN_X_SIZE, TERRAIN_Y_SIZE + 1))
        self.window.blit(self.player.image, self.player.rect) #Draw the player
        for enemy in self.enemy_list: #Draw each enemy
            draw_x = enemy.rect.left - self.player.x + self.player.rect.left
            draw_y = enemy.rect.top - self.player.y + self.player.rect.top
            if draw_x <= SCREEN_WIDTH and draw_x >= -TERRAIN_X_SIZE and draw_y <= SCREEN_HEIGHT and draw_y >= -TERRAIN_Y_SIZE:
                self.window.blit(self.enemy_textures[enemy.ID], Rect(draw_x, draw_y, ENEMY_X_SIZE[enemy.ID], ENEMY_Y_SIZE[enemy.ID]))
    def update_player(self): #Updates the player's position
        self.player.input_check() #Checks the player's input
        self.player.gravity() #Simulates gravity and downward collision detection
        self.player.movement_check() #Horizontal movement and associated collision detection
    def create_terrain_texture(self, ID): #Generates a preloaded terrain texture for convenient access
        return pygame.transform.scale(pygame.image.load(r"Terrain\Terrain" + str(ID) + ".png"), (TERRAIN_X_SIZE, TERRAIN_Y_SIZE + 1)) #+1 prevents a horizontal tearing issue
    def create_enemy_texture(self, ID): #Generates a preloaded enemy texture for convenient access
        return pygame.transform.scale(pygame.image.load(r"anim\enemy" + str(ID) + ".png"), (ENEMY_X_SIZE[ID], ENEMY_Y_SIZE[ID])) #+1 prevents a horizontal tearing issue
    def load_level(self, level_num): #Reads a given level and builds appropriate terrain
        self.terrain_list = [] #Remove old terrain
        self.enemy_list = [] #Remove old enemies
        self.frame_tick = 0 #Reset the frame counter
        terrain_raw = open(r"Level Data\Level " + str(level_num) + ".txt", "r") #Access the level file
        done_cycling = False
        while not done_cycling:
            terrain_obj_raw = terrain_raw.readline()[:-1] #obtain a line (minus the newline character)
            if terrain_obj_raw == "":
                done_cycling = True
            else:
                terrain_obj_split = terrain_obj_raw.split() #split the line into its component numbers
                self.terrain_list.append(Terrain(self, int(terrain_obj_split[0]), int(terrain_obj_split[1]), int(terrain_obj_split[2]))) #use the split numbers to create a terrain object
                if int(terrain_obj_split[0]) == 22: #positions the player at a "start" terrain block
                    self.player.x = int(terrain_obj_split[1]) * TERRAIN_X_SIZE + .5 * PLAYER_X_SIZE
                    self.player.y = int(terrain_obj_split[2]) * TERRAIN_Y_SIZE
                elif int(terrain_obj_split[0]) >= 23 and int(terrain_obj_split[0]) <= 25:
                    self.enemy_list.append(Enemy(self, int(terrain_obj_split[0]) - 23, int(terrain_obj_split[1]), int(terrain_obj_split[2])))
    def death(self): #If the player dies, reset the level
        for iterate in range(20, 0, -1): #this loop is the death fade-from-white effect
            self.window.fill(BLACK)
            pygame.display.update()
            self.mainClock.tick(FPS)
        self.load_level(self.level)
    def victory(self): #If the player succeeds, load the next level
        for iterate in range(75): #this loop is the victory animation
            self.draw_stuff()
            self.window.blit(self.messages, Rect(SCREEN_WIDTH / 4, 7 * SCREEN_HEIGHT / 16, 0, 0), Rect(0, 0, iterate * self.messages_rect.width / 45, self.messages_rect.height))
            pygame.display.update()
            self.mainClock.tick(FPS)
        self.level = self.level + 1
        self.load_level(self.level)
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
