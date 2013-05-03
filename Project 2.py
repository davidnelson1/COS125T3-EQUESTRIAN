"""Sound help courtesy of http://thepythongamebook.com/en:pygame:step010"""

import pygame, time, sys, os #import required modules
from pygame.locals import *

#Constants
BLACK = (0, 0, 0) #Color codes
WHITE = (255, 255, 255)
FPS = 40 #The frame rate
SCREEN_WIDTH = 800 #The values that determine the window size
SCREEN_HEIGHT = 600
SOUND_ENABLED = "y" #y to enable sound, n to disable
TERRAIN_X_SIZE = SCREEN_WIDTH / 10 #The pixel size of a standard terrain block
TERRAIN_Y_SIZE = SCREEN_HEIGHT / 10
PLAYER_X_SIZE = 2 * TERRAIN_X_SIZE / 3 #The pixel sizes of the player sprite
PLAYER_Y_SIZE = 2 * TERRAIN_Y_SIZE / 3
PLAYER_SPEED_RATIO = 15.0 #The number of frames it takes the player to travel 1 block
ENEMY_X_SIZE = [TERRAIN_X_SIZE / 2, 2 * TERRAIN_X_SIZE / 3, 2 * TERRAIN_X_SIZE / 3] #The pixel sizes of the enemy sprites
ENEMY_Y_SIZE = [TERRAIN_Y_SIZE / 2, TERRAIN_Y_SIZE / 2, 2 * TERRAIN_Y_SIZE / 3]
ENEMY_SPEED_RATIO = [10.0, 30.0, 10.0] #The number of frames it takes each enemy to travel 1 block
BG_WIDTH = 8 * SCREEN_WIDTH #The pixel size of the background
BG_HEIGHT = 2 * SCREEN_HEIGHT

if SOUND_ENABLED == "y": #start pygame, and the mixer if sound is enabled
    pygame.mixer.pre_init(44100, -16, 2, 2048)
    pygame.init()
    pygame.mixer.init()
elif SOUND_ENABLED == "n":
    pygame.init()
else:
    sys.exit()
pygame.display.set_caption("Sugar Steed") #Add the title

#This class tracks data related to the player.
#There should only be one instance of this class.
class Player:
    def __init__(self, parent, x_veloc):
        self.parent = parent
        #loads the player animations and scales them to the required size
        self.image = []
        for anim_frame in range(12):
            self.image.append(pygame.transform.scale(pygame.image.load("anim\player" + str(anim_frame) + ".png"), (PLAYER_X_SIZE, PLAYER_Y_SIZE)))
        self.rect = self.image[0].get_rect() #obtain a box around the player
        self.rect.left = (SCREEN_WIDTH / 2) - (self.rect.width / 2) #place the player in the center of the screen
        self.rect.top = (SCREEN_HEIGHT / 2) - (self.rect.height / 2)
        self.x_veloc = x_veloc #initialize player velocities
        self.y_veloc = 0.0
        self.x = 0 #initialize player's "actual" position and animation value
        self.y = 0
        if SOUND_ENABLED == "y": #Load player sounds
            self.injure_sound = pygame.mixer.Sound(r"Sounds\Hurt.wav")
            self.jump_sound = pygame.mixer.Sound(r"Sounds\Jump.wav")
        self.anim_frame = 3 #The player's starting animation frame
        self.falling = False #initialize gravity-related variables
        self.just_landed = False
    def move(self, xm, ym): #adjusts the player's position
        self.x = self.x + xm
        self.y = self.y + ym
        self.parent.parallax[0] = self.parent.parallax[0] - xm / 5 #adjust the background
        if self.parent.parallax[0] <= -BG_WIDTH: #loop the background if it would scroll off the screen
            self.parent.parallax[0] = self.parent.parallax[0] + BG_WIDTH
        elif self.parent.parallax[0] >= 0:
            self.parent.parallax[0] = self.parent.parallax[0] - BG_WIDTH
    def determine_animation_frame(self): #figure out what frame the player should display
        if self.falling == True: #if falling, display one of two falling frames
            if self.x_veloc < 0:
                self.anim_frame = 0
            elif self.x_veloc > 0:
                self.anim_frame = 1
        else:
            if self.x_veloc < 0: #if moving left, loop through four left-walking frames
                if self.anim_frame >= 4 and self.anim_frame <= 6:
                    if self.parent.frame_tick % (10 / abs(self.x_veloc)) == 0: #increment the frame based on the clock timer and player speed
                        self.anim_frame = self.anim_frame + 1
                elif self.anim_frame == 7:
                    if self.parent.frame_tick % (10 / abs(self.x_veloc)) == 0:
                        self.anim_frame = self.anim_frame - 3
                else:
                    self.anim_frame = 4
            elif self.x_veloc > 0: #if walking right, loop through four right-walking frames
                if self.anim_frame >= 8 and self.anim_frame <= 10:
                    if self.parent.frame_tick % (10 / abs(self.x_veloc)) == 0:
                        self.anim_frame = self.anim_frame + 1
                elif self.anim_frame == 11:
                    if self.parent.frame_tick % (10 / abs(self.x_veloc)) == 0:
                        self.anim_frame = self.anim_frame - 3
                else:
                    self.anim_frame = 8
            else: #if not moving at all, select one of two idle frames
                if (self.anim_frame >= 4 and self.anim_frame <= 7) or self.anim_frame == 0:
                    self.anim_frame = 2
                elif (self.anim_frame >= 8 and self.anim_frame <= 11) or self.anim_frame == 1:
                    self.anim_frame = 3
    def input_check(self): #adjusts player movement direction
        if pygame.key.get_pressed()[K_LSHIFT]: #increases the player's movement speed if shift is held
            adjust_length = 2
        else:
            adjust_length = 1
        if pygame.key.get_pressed()[K_LEFT]: #moves the player left or right
                self.x_veloc = -adjust_length
        elif pygame.key.get_pressed()[K_RIGHT]:
                self.x_veloc = adjust_length
        else: #makes the player stop moving when not attempting to move
            self.x_veloc = 0
        if pygame.key.get_pressed()[K_UP] and self.falling == False and self.just_landed == False: #allows jumping while on the ground
            self.falling = True
            self.y_veloc = -TERRAIN_Y_SIZE / 4.5
            if SOUND_ENABLED == "y": #play the jump sound
                self.jump_sound.play()
    def gravity(self): #checks if the player has collided with the terrain
        if self.falling == False: #if the player is not falling and is not standing on a block, begin falling
            if self.just_landed == True: #This adds a waiting frame between possible jumps to prevent a collision issue
                self.just_landed = False
            for terrain in self.parent.terrain_list:
                if terrain.ID <= 9 and nearby(self, terrain): #check if the block is collideable
                    if Rect(self.x, self.y, self.rect.width, self.rect.height).colliderect(terrain.rect) and self.y <= terrain.rect.top: #if stuck in the ground, unstick the player
                        self.y = self.y - TERRAIN_Y_SIZE / 24
                        return
                    elif Rect(self.x, self.y + TERRAIN_Y_SIZE / 24, self.rect.width, self.rect.height).colliderect(terrain.rect): #if standing on a block, continue not falling
                        return
            self.falling = True #if in midair, start falling
            return
        else: #if the player is falling
            self.y_veloc = self.y_veloc + TERRAIN_Y_SIZE / 60.0 #accelerate downward
            if self.y_veloc > TERRAIN_Y_SIZE: #If falling too fast, die
                self.parent.death()
            if int(self.y_veloc) == 0: #prevent a division-by-zero
                step = 1
            else:
                step = int(self.y_veloc / abs(self.y_veloc))
            for dist in range(step, int(self.y_veloc), step): #Check for collisions, and end fall if one is detected
                for terrain in self.parent.terrain_list:
                    if nearby(self, terrain):
                        if Rect(self.x, self.y + dist, self.rect.width, self.rect.height).colliderect(terrain.rect):
                            if terrain.ID <= 9:
                                self.falling = False
                                self.y_veloc = 0.0
                                self.y = self.y + dist #Places the player at the point of collision
                                self.just_landed = True
                                return
        self.move(0, self.y_veloc) #Actually move the player
    def movement_check(self): #checks to see if the player is allowed to continue moving, and stops or moves them as appropriate
        self.move((self.x_veloc * TERRAIN_X_SIZE / PLAYER_SPEED_RATIO), 0)
        for terrain in self.parent.terrain_list:
            if nearby(self, terrain):
                if Rect(self.x, self.y - TERRAIN_Y_SIZE / 24, self.rect.width, self.rect.height).colliderect(terrain.rect) and self.y <= terrain.rect.top + TERRAIN_Y_SIZE:
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
        self.anim_frame = 2
    def move(self, xm, ym): #moves the enemy, and their rectangle to match
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
                    if Rect(self.x, self.y, self.rect.width, self.rect.height).colliderect(terrain.rect) and self.y <= terrain.rect.top: #if stuck in the ground, unstick the player
                        self.y = self.y - TERRAIN_Y_SIZE / 24
                        return
                    if Rect(self.rect.left, self.rect.top + TERRAIN_Y_SIZE / 24, self.rect.width, self.rect.height).colliderect(terrain.rect):
                        return
            self.falling = True
            return
        else: #if the enemy is falling
            self.y_veloc = self.y_veloc + TERRAIN_Y_SIZE / 60.0 #accelerate downward
            if self.y_veloc > TERRAIN_Y_SIZE / 2: #If an enemy falls too fast, kill it
                self.death()
            if int(self.y_veloc) == 0:
                step = 1
            else:
                step = int(self.y_veloc / abs(self.y_veloc))
            for dist in range(step*2, int(self.y_veloc), step*2): #Check for collisions, and end fall if one is detected
                for terrain in self.parent.terrain_list:
                    if Rect(self.rect.left, self.rect.top + dist, self.rect.width, self.rect.height).colliderect(terrain.rect):
                        if terrain.ID <= 9:
                            self.falling = False
                            self.y_veloc = 0.0
                            self.y = self.y + dist
                            self.just_landed = True
                            return
                        elif terrain.ID <= 19:
                            self.death()
                            return
        self.move(0, self.y_veloc) #Actually move the enemy
    def AI(self): #Perform enemy behavior based on ID
        if self.ID == 0: #Perform snake behavior
            if not self.parent.player.falling and not self.falling: #Chase the player while both are grounded
                if self.parent.player.x <= self.rect.left + SCREEN_WIDTH / 2 + self.rect.width and self.rect.left <= self.parent.player.x: #If the snake is onscreen to the left, it heads right
                    if self.parent.player.x - self.x < TERRAIN_X_SIZE / ENEMY_SPEED_RATIO[self.ID]:
                        self.x_veloc = (self.parent.player.x - self.x) / (TERRAIN_X_SIZE / ENEMY_SPEED_RATIO[self.ID]) #keep pace with the player rather than shoot ahead
                    else:
                        self.x_veloc = 1
                elif self.parent.player.x >= self.rect.left - SCREEN_WIDTH / 2 - self.parent.player.rect.width and self.rect.left >= self.parent.player.x: #If the snake is onscreen to the right, it heads left
                    if self.x - self.parent.player.x < TERRAIN_X_SIZE / ENEMY_SPEED_RATIO[self.ID]:
                        self.x_veloc = (self.parent.player.x - self.x) / (TERRAIN_X_SIZE / ENEMY_SPEED_RATIO[self.ID])
                    else:
                        self.x_veloc = -1
                else:
                    self.x_veloc = 0
        elif self.ID == 1: #Perform bear behavior
            if not self.falling:
                if self.x_veloc == 0: #After stopping, switch directions and start moving again
                    self.x_veloc = self.next_direction
                    self.next_direction = -self.next_direction
        elif self.ID == 2: #Perform wolf behavior
            if not self.falling:
                if self.parent.frame_tick % (FPS * 2) == 0: #Jump forward every 2 seconds
                    self.x_veloc = self.next_direction
                    self.y_veloc = -TERRAIN_Y_SIZE / 4.5
                    self.falling = True
                    self.dir_swapped = False
                else:
                    self.x_veloc = 0
            else: #Switch directions after being stopped
                if self.x_veloc == 0 and self.falling == True and self.dir_swapped == False:
                    self.next_direction = -self.next_direction
                    self.dir_swapped = True             
    def death(self): #Kill the enemy
        death_x = self.rect.left - self.parent.player.x + self.parent.player.rect.left
        death_y = self.rect.top - self.parent.player.y + self.parent.player.rect.top
        if death_x <= SCREEN_WIDTH and death_x >= 0 and death_y <= SCREEN_HEIGHT and death_y >= 0 and SOUND_ENABLED == "y": #If on-screen, play the death sound
            self.parent.enemy_sounds[self.ID].play(maxtime = 1000)
        self.parent.enemy_list.remove(self)
    def determine_animation_frame(self): #Determine the correct enemy frame
        if self.falling == True: #If midair, select one of two midair frames
            if self.x_veloc < 0:
                self.anim_frame = 0
            elif self.x_veloc > 0:
                self.anim_frame = 1
        else:
            if self.x_veloc < 0: #If grounded and walking left, loop through three left-walking frames
                if self.anim_frame >= 4 and self.anim_frame <= 5:
                    if self.parent.frame_tick % (10) == 0: #Increment the frame based on the game timer
                        self.anim_frame = self.anim_frame + 1
                elif self.anim_frame == 6:
                    if self.parent.frame_tick % (10) == 0:
                        self.anim_frame = self.anim_frame - 2
                else:
                    self.anim_frame = 4
            elif self.x_veloc > 0: #If grounded and walking right, loop through three right-walking frames
                if self.anim_frame >= 7 and self.anim_frame <= 8:
                    if self.parent.frame_tick % (10) == 0:
                        self.anim_frame = self.anim_frame + 1
                elif self.anim_frame == 9:
                    if self.parent.frame_tick % (10) == 0:
                        self.anim_frame = self.anim_frame - 2
                else:
                    self.anim_frame = 7
            else: #If motionless, select one of two idle frames
                if (self.anim_frame >= 4 and self.anim_frame <= 7) or self.anim_frame == 0:
                    self.anim_frame = 2
                elif (self.anim_frame >= 8 and self.anim_frame <= 11) or self.anim_frame == 1:
                    self.anim_frame = 3
    def movement_check(self): #checks to see if the enemy is allowed to continue moving, and stops or moves them as appropriate
        self.move((self.x_veloc * TERRAIN_X_SIZE / ENEMY_SPEED_RATIO[self.ID]), 0)
        for terrain in self.parent.terrain_list:
            if Rect(self.rect.left, self.rect.top - TERRAIN_Y_SIZE / 24, self.rect.width, self.rect.height).colliderect(terrain.rect):
                if terrain.ID <= 9: #If the block is collideable, prevent collision
                    self.move((-self.x_veloc * TERRAIN_X_SIZE / ENEMY_SPEED_RATIO[self.ID]), 0)
                    self.x_veloc = 0
                    return
                elif terrain.ID <= 19: #If the block is lethal, kill enemy
                    self.death()
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
        self.game_end = False #Flag for beating the last level
        self.window = pygame.display.set_mode([width, height]) #the game window
        self.player = Player(self, 0)
        self.mainClock = pygame.time.Clock()
        self.score = 0
        self.lost_score = 0
        self.terrain_textures = []
        self.font = pygame.font.SysFont("", 48)
        self.splash = pygame.transform.scale(pygame.image.load(r"anim\splash.png"), (SCREEN_WIDTH, SCREEN_HEIGHT)) #the opening screen
        for ID in range(22): #Add the terrain texture list to memory
            self.terrain_textures.append(self.create_terrain_texture(ID))
        self.enemy_textures = []
        self.create_enemy_textures()
        self.enemy_sounds = []
        if SOUND_ENABLED == "y": #load enemy sounds and music
            for ID in range(3):
                self.enemy_sounds.append(pygame.mixer.Sound("Sounds\eHurt" + str(ID) + ".wav"))
            pygame.mixer.music.load("Sounds\music.wav")
        self.terrain_list = []
        self.enemy_list = []
        self.background_texture = pygame.transform.scale(pygame.image.load(r"anim\Background.png"), (BG_WIDTH, BG_HEIGHT)) #The background image
        self.parallax = [0, -SCREEN_HEIGHT] #The values that determine where to draw the background
        self.parallax_old = [0, -SCREEN_HEIGHT] #The values that determine where the background was when you began a level
        self.level = 1
        self.load_level(self.level)
        self.messages = pygame.transform.scale(pygame.image.load(r"anim\Victory.png"), (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 8))
        self.messages_rect = self.messages.get_rect()
    def update_all(self): #Updates all updatable entities
        self.update_player()
        self.update_enemies()
        self.update_window()
        self.frame_tick = self.frame_tick + 1
        if self.lost_score > 0: #slowly decrements your score
            self.lost_score = self.lost_score - 2
            self.score = self.score - 2
        return self.game_end
    def update_window(self): #Updates the display
        self.draw_stuff()
        pygame.display.update() #Move drawn objects to the screen
    def update_enemies(self): #Updates each enemy
        if self.frame_tick % (FPS * 3) == 0:  #Spawn bears from bear caves every 3 seconds
            for terrain in self.terrain_list:
                if terrain.ID == 21:
                    self.enemy_list.append(Enemy(self, 1, terrain.rect.left / TERRAIN_X_SIZE, (terrain.rect.top) / TERRAIN_Y_SIZE + 1.0/2))
        for enemy in self.enemy_list:
            enemy.gravity()
            enemy.AI()
            enemy.movement_check()
            enemy.determine_animation_frame()
    def draw_stuff(self):
        self.window.blit(self.background_texture, Rect(self.parallax[0], self.parallax[1], 0, 0)) #Draw the background twice
        self.window.blit(self.background_texture, Rect(self.parallax[0] + BG_WIDTH, self.parallax[1], 0, 0))
        for terrain in self.terrain_list: #Draw each terrain object
            if terrain.ID <= 21: #Excludes script terrain from the draw procedure
                    draw_x = terrain.rect.left - self.player.x + self.player.rect.left #place the terrain based on the player's locatioin
                    draw_y = terrain.rect.top - self.player.y + self.player.rect.top
                    if draw_x <= SCREEN_WIDTH and draw_x >= -TERRAIN_X_SIZE and draw_y <= SCREEN_HEIGHT and draw_y >= -TERRAIN_Y_SIZE:
                        self.window.blit(self.terrain_textures[terrain.ID], Rect(draw_x, draw_y, TERRAIN_X_SIZE, TERRAIN_Y_SIZE + 1))
        self.window.blit(self.player.image[self.player.anim_frame], self.player.rect) #Draw the player
        for enemy in self.enemy_list: #Draw each enemy if onscreen
            draw_x = enemy.rect.left - self.player.x + self.player.rect.left
            draw_y = enemy.rect.top - self.player.y + self.player.rect.top
            if draw_x <= SCREEN_WIDTH and draw_x >= -TERRAIN_X_SIZE and draw_y <= SCREEN_HEIGHT and draw_y >= -TERRAIN_Y_SIZE:
                self.window.blit(self.enemy_textures[enemy.ID * 10 + enemy.anim_frame], Rect(draw_x, draw_y, ENEMY_X_SIZE[enemy.ID], ENEMY_Y_SIZE[enemy.ID]))
        #Produce and draw the HUD
        clock_text = self.font.render("Level " + str(self.level) + ", Time: "  + str(int((FPS*60 - self.frame_tick)/FPS)), True, BLACK)
        clock_rect = clock_text.get_rect()
        score_text = self.font.render("Score: " + str(self.score), True, BLACK)
        score_rect = score_text.get_rect()
        self.window.fill(WHITE, Rect(0, 0, SCREEN_WIDTH, score_rect.height))
        self.window.blit(clock_text, Rect(0, 0, 0, 0))
        self.window.blit(score_text, Rect(SCREEN_WIDTH - score_rect.width, 0, 0, 0))
    def update_player(self): #Updates the player's position
        self.player.input_check() #Checks the player's input
        self.player.gravity() #Simulates gravity and downward collision detection
        self.player.movement_check() #Horizontal movement and associated collision detection
        self.player.determine_animation_frame() #Select the correct player image
        if (FPS*60 - self.frame_tick) <= 0:
            self.death()
    def create_terrain_texture(self, ID): #Generates a preloaded terrain texture for convenient access
        return pygame.transform.scale(pygame.image.load(r"Terrain\Terrain" + str(ID) + ".png"), (TERRAIN_X_SIZE, TERRAIN_Y_SIZE + 1)) #+1 prevents a horizontal tearing issue
    def create_enemy_textures(self): #Generates preloaded enemy textures for convenient access
        for ID in range(0, 3): #load a texture for each frame for each enemy
            for frame in range(10):
                self.enemy_textures.append(pygame.transform.scale(pygame.image.load(r"anim\enemy" + str(ID) + "-" + str(frame) + ".png"), (ENEMY_X_SIZE[ID], ENEMY_Y_SIZE[ID])))
    def load_level(self, level_num): #Reads a given level and builds appropriate terrain
        self.terrain_list = [] #Remove old terrain
        self.enemy_list = [] #Remove old enemies
        self.frame_tick = 0 #Reset the frame counter
        self.player.y_veloc = 0 #Prevent carry-over of a jump
        try:
            terrain_raw = open(r"Level Data\Level " + str(level_num) + ".txt", "r") #Access the level file
        except: #If there is no such level
            self.game_end = True
            return
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
                elif int(terrain_obj_split[0]) >= 23 and int(terrain_obj_split[0]) <= 25: #spawn an enemy at each enemy block
                    self.enemy_list.append(Enemy(self, int(terrain_obj_split[0]) - 23, int(terrain_obj_split[1]), int(terrain_obj_split[2])))
    def death(self): #If the player dies, reset the level
        if SOUND_ENABLED == "y":
            pygame.mixer.music.pause()
            self.player.injure_sound.play()
        for iterate in range(20, 0, -1): #this loop is the black-screen death effect
            self.window.fill(BLACK)
            pygame.display.update()
            self.mainClock.tick(FPS)
        self.load_level(self.level)
        self.lost_score = 50
        self.parallax = []
        self.parallax.append(self.parallax_old[0])
        self.parallax.append(self.parallax_old[1])
        pygame.mixer.music.unpause()
    def victory(self): #If the player succeeds, load the next level
        for iterate in range(45): #this loop is the victory animation
            self.draw_stuff()
            self.window.blit(self.messages, Rect(SCREEN_WIDTH / 4, 7 * SCREEN_HEIGHT / 16, 0, 0), Rect(0, 0, iterate * self.messages_rect.width / 45, self.messages_rect.height))
            pygame.display.update()
            self.mainClock.tick(FPS)
        while (FPS*60 - self.frame_tick)/FPS > 1: #Swap the time remaining to the score
            self.frame_tick = self.frame_tick + FPS / 2
            self.score = self.score + FPS / 4
            self.draw_stuff()
            self.window.blit(self.messages, Rect(SCREEN_WIDTH / 4, 7 * SCREEN_HEIGHT / 16, 0, 0), Rect(0, 0, iterate * self.messages_rect.width / 45, self.messages_rect.height))
            pygame.display.update()
        self.score = self.score + int((FPS*60 - self.frame_tick) / 4)
        self.draw_stuff()
        self.window.blit(self.messages, Rect(SCREEN_WIDTH / 4, 7 * SCREEN_HEIGHT / 16, 0, 0), Rect(0, 0, iterate * self.messages_rect.width / 45, self.messages_rect.height))
        pygame.display.update()
        self.level = self.level + 1
        self.load_level(self.level)
        self.parallax_old = self.parallax
    def run(self): #The main loop
        while True:
            STOP = False
            self.window.blit(self.splash, Rect(0, 0, 0, 0)) #Display the splash screen
            pygame.display.update()
            while not STOP: #Display the splash screen until spacebar is pressed
                for event in pygame.event.get():
                    if event.type == KEYDOWN:
                        if event.key == K_SPACE:
                            STOP = True
                            if SOUND_ENABLED == "y": #play the startup sound
                                pygame.mixer.Sound(r"Sounds\Open.wav").play()
                            self.window.fill(BLACK) #Clear the screen
                            pygame.display.update()
                            for i in range(20): #Wait a bit
                                self.mainClock.tick(FPS)
            STOP = False
            pygame.mixer.music.play(-1) #Start the music
            while not STOP: #the game loop
                self.mainClock.tick(FPS) #Wait until the next frame
                STOP = self.update_all() #Update, and determine if the game was beaten
                for event in pygame.event.get(): #If the window is closed, exit
                    if event.type == QUIT:
                        STOP = True
                        pygame.quit()
                        sys.exit()
            STOP = False
            victor_text1 = self.font.render("Congratulations, you have prevailed!", True, WHITE) #Generate the end game text
            victor_rect1 = victor_text1.get_rect()
            victor_text2 = self.font.render("You have had your fill of sugar cubes.", True, WHITE)
            victor_rect2 = victor_text2.get_rect()
            victor_text3 = self.font.render("Your final score was " + str(self.score) + ".", True, WHITE)
            victor_rect3 = victor_text3.get_rect()
            victor_text4 = self.font.render("Press space to return to the title screen.", True, WHITE)
            victor_rect4 = victor_text4.get_rect()
            victor_text5 = self.font.render("Press any other key to quit.", True, WHITE)
            victor_rect5 = victor_text5.get_rect()
            while not STOP: #The victory screen
                self.window.fill(BLACK) #Draw the relevant info
                self.window.blit(victor_text1, Rect(SCREEN_WIDTH / 2 - victor_rect1.width / 2, SCREEN_HEIGHT / 2 - victor_rect3.height / 2 - victor_rect2.height - victor_rect1.height, 0, 0))
                self.window.blit(victor_text2, Rect(SCREEN_WIDTH / 2 - victor_rect2.width / 2, SCREEN_HEIGHT / 2 - victor_rect3.height / 2 - victor_rect2.height, 0, 0))
                self.window.blit(victor_text3, Rect(SCREEN_WIDTH / 2 - victor_rect3.width / 2, SCREEN_HEIGHT / 2 - victor_rect3.height / 2, 0, 0))
                self.window.blit(victor_text4, Rect(SCREEN_WIDTH / 2 - victor_rect4.width / 2, SCREEN_HEIGHT / 2 + victor_rect3.height / 2, 0, 0))
                self.window.blit(victor_text5, Rect(SCREEN_WIDTH / 2 - victor_rect5.width / 2, SCREEN_HEIGHT / 2 + victor_rect3.height / 2 + victor_rect4.height, 0, 0))
                pygame.display.update() #Flip the screen
                self.mainClock.tick(FPS)
                for event in pygame.event.get():
                    if event.type == KEYDOWN: #If spacebar is hit, start over
                        if event.key == K_SPACE:
                            STOP = True
                            self.game_end = False
                            self.level = 1
                            self.score = 0
                            self.load_level(self.level)
                        else: #End the game if another key is hit
                            pygame.quit()
                            sys.exit()
def nearby(entity, terrain):
    """
    Determines if an entity object and a terrain object are in a certain range of each other. Returns True if so, and False otherwise.
    """
    if ((entity.x - terrain.rect.left) * (entity.x - terrain.rect.left) + (entity.y - terrain.rect.top) * (entity.y - terrain.rect.top)) / TERRAIN_X_SIZE <= TERRAIN_X_SIZE + TERRAIN_Y_SIZE:
        return True
    return False

bwin = Controller(SCREEN_WIDTH, SCREEN_HEIGHT) #Create the controller
bwin.run() #Start the program
