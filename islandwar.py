"""
author: Martin Philipp Schnabl
email: martin@schnabl.sc
contact: find me under MartinPhilipp on Github 
license: gpl, see http://www.gnu.org/licenses/gpl-3.0.de.html
download: from Github/Islandwar
idea: python3/pygame game, coordinating ship attacks
"""
import this
print("Praize!!!")
import pygame
import random
import os
import time
import math
import Islandwar_levels as Levels
import Islandwar_menu as Menu

def structurize_text(text, linelength):
    """returns a list containing strings with the split up text with less or equal chars than the linelength"""
    struct_text = []
    textline = ""
    words = text.split()
    for word in words:
        if len(textline + word) <= linelength:
            textline += word + " "
        else:
            struct_text.append(textline)
            textline = "" + word + " "
    struct_text.append(textline)
    return struct_text

def make_text(msg="pygame is cool", fontcolor=(255, 0, 255), fontsize=42, font="mono"):
    """returns pygame surface with text. You still need to blit the surface."""
    myfont = pygame.font.SysFont(font, fontsize, bold=True) #Needs font!=None, fontsize and bold=True, otherwise error in .exe running
    mytext = myfont.render(msg, True, fontcolor)
    mytext = mytext.convert_alpha()
    return mytext

def write(background, text, x=50, y=150, color=(0,0,0),
          fontsize=None, center=False):
        """write text on pygame surface. """
        if fontsize is None:
            fontsize = 24
        font = pygame.font.SysFont('mono', fontsize, bold=True)
        fw, fh = font.size(text)
        surface = font.render(text, True, color)
        if center: # center text around x,y
            background.blit(surface, (x-fw//2, y-fh//2))
        else:      # topleft corner is x,y
            background.blit(surface, (int(x),int(y)))
            
def distance(point_1=(0, 0), point_2=(0, 0)):
    """Returns the distance between two points"""
    return math.sqrt((point_1[0] - point_2[0]) ** 2 + (point_1[1] - point_2[1]) ** 2)

def elastic_collision(sprite1, sprite2):
        """elasitc collision between 2 VectorSprites (calculated as disc's).
           The function alters the dx and dy movement vectors of both sprites.
           The sprites need the property .mass, .radius, pos.x pos.y, move.x, move.y
           by Leonard Michlmayr"""
        if sprite1.static and sprite2.static:
            return 
        dirx = sprite1.pos.x - sprite2.pos.x
        diry = sprite1.pos.y - sprite2.pos.y
        sumofmasses = sprite1.mass + sprite2.mass
        sx = (sprite1.move.x * sprite1.mass + sprite2.move.x * sprite2.mass) / sumofmasses
        sy = (sprite1.move.y * sprite1.mass + sprite2.move.y * sprite2.mass) / sumofmasses
        bdxs = sprite2.move.x - sx
        bdys = sprite2.move.y - sy
        cbdxs = sprite1.move.x - sx
        cbdys = sprite1.move.y - sy
        distancesquare = dirx * dirx + diry * diry
        if distancesquare == 0:
            dirx = random.randint(0,11) - 5.5
            diry = random.randint(0,11) - 5.5
            distancesquare = dirx * dirx + diry * diry
        dp = (bdxs * dirx + bdys * diry) # scalar product
        dp /= distancesquare # divide by distance * distance.
        cdp = (cbdxs * dirx + cbdys * diry)
        cdp /= distancesquare
        if dp > 0:
            if not sprite2.static:
                sprite2.move.x -= 2 * dirx * dp
                sprite2.move.y -= 2 * diry * dp
            if not sprite1.static:
                sprite1.move.x -= 2 * dirx * cdp
                sprite1.move.y -= 2 * diry * cdp

class Game():
    quit_game = False
    difficulty = 0
    speed = 1
    level = 1
    ship_size = (50,20) #with pygame graphics: 50,10
    for l in Levels.levels.keys():
        if int(l) <= 0:
            level -= 1 #for every tutorial level we go one level below 0
    enemy_color = [(255,0,0),(255,165,0)]
    player_color = (0,255,0)
    neutral_color = (0,0,255)
    gamemodes = ["Conquer","Defend","Collect"]
    gamemode = "Conquer"
    player_wood = 0
    player_iron = 0
    player_ships = 0
    player_islands = 0
    player_island_types = [0,0,0,0] #amount of [main,ship,wood,iron] islands of player
    enemy_ships = 0
    enemy_islands = 0
    enemy1_wood = 0
    enemy1_iron = 0
    enemy2_wood = 0
    enemy2_iron = 0
    enemy_island_types = [0,0,0,0] #amount of [main,ship,wood,iron] islands of enemy
    wood_islandgroup = pygame.sprite.Group()
    iron_islandgroup = pygame.sprite.Group()
    ship_islandgroup = pygame.sprite.Group()
    main_islandgroup = pygame.sprite.Group()
    nonresource_islandgroup = pygame.sprite.Group()
    islandgroup = pygame.sprite.Group()
    groups = [wood_islandgroup,iron_islandgroup,ship_islandgroup,main_islandgroup,islandgroup]

        
class Flytext(pygame.sprite.Sprite):
    def __init__(self, x, y, text="hallo", color=(255, 0, 0),
                 dx=0, dy=-50, duration=2, acceleration_factor = 1.0, delay = 0, fontsize=22):
        """a text flying upward and for a short time and disappearing"""
        self._layer = 7  # order of sprite layers (before / behind other sprites)
        pygame.sprite.Sprite.__init__(self, self.groups)  # THIS LINE IS IMPORTANT !!
        self.text = text
        self.r, self.g, self.b = color[0], color[1], color[2]
        self.dx = dx
        self.dy = dy
        self.x, self.y = x, y
        self.duration = duration  # duration of flight in seconds
        self.acc = acceleration_factor  # if < 1, Text moves slower. if > 1, text moves faster.
        self.image = make_text(self.text, (self.r, self.g, self.b), fontsize)  # font 22 #------------------Error in the exe!!!-----------
        self.rect = self.image.get_rect()
        self.rect.center = (self.x, self.y)
        self.time = 0 - delay

    def update(self, seconds):
        self.time += seconds
        if self.time < 0:
            self.rect.center = (-100,-100)
        else:
            self.y += self.dy * seconds
            self.x += self.dx * seconds
            self.dy *= self.acc # slower and slower
            self.dx *= self.acc
            self.rect.center = (self.x,self.y)
            if self.time > self.duration:
                self.kill()      # remove Sprite from screen and from groups

class VectorSprite(pygame.sprite.Sprite):
    """base class for sprites. this class inherits from pygames sprite class"""
    number = 0
    numbers = {} # { number, Sprite }

    def __init__(self, **kwargs):
        self._default_parameters(**kwargs)
        pygame.sprite.Sprite.__init__(self, self.groups) #call parent class. NEVER FORGET !
        self.number = VectorSprite.number # unique number for each sprite
        VectorSprite.number += 1
        VectorSprite.numbers[self.number] = self
        self._overwrite_parameters()
        self.create_image()
        self.distance_traveled = 0 # in pixel
        self.rect.center = (int(self.pos.x), -int(self.pos.y))
        if self.angle != 0:
            self.set_angle(self.angle)
        self.start()
        
    def start(self):
        pass

    def _overwrite_parameters(self):
        """change parameters before create_image is called""" 
        pass

    def _default_parameters(self, **kwargs):    
        """get unlimited named arguments and turn them into attributes
           default values for missing keywords"""
        for key, arg in kwargs.items():
            setattr(self, key, arg)
        if "layer" not in kwargs:
            self._layer = 4
        else:
            self._layer = self.layer
        if "static" not in kwargs:
            self.static = False
        if "pos" not in kwargs:
            self.pos = pygame.math.Vector2(random.randint(0, Viewer.width),-50)
        if "move" not in kwargs:
            self.move = pygame.math.Vector2(0,0)
        if "radius" not in kwargs:
            self.radius = 5
        if "width" not in kwargs:
            self.width = self.radius * 2
        if "height" not in kwargs:
            self.height = self.radius * 2
        if "color" not in kwargs:       #self.color = None
            self.color = (random.randint(0,255), random.randint(0,255), random.randint(0,255))
        if "hitpoints" not in kwargs:
            self.hitpoints = 100
        self.hitpointsfull = self.hitpoints # makes a copy
        if "mass" not in kwargs:
            self.mass = 10
        if "damage" not in kwargs:
            self.damage = 10
        if "bounce_on_edge" not in kwargs:
            self.bounce_on_edge = False
        if "kill_on_edge" not in kwargs:
            self.kill_on_edge = False
        if "angle" not in kwargs:
            self.angle = 0 # facing right?
        if "max_age" not in kwargs:
            self.max_age = None
        if "max_distance" not in kwargs:
            self.max_distance = None
        if "picture" not in kwargs:
            self.picture = None
        if "bossnumber" not in kwargs:
            self.bossnumber = None
        if "kill_with_boss" not in kwargs:
            self.kill_with_boss = False
        if "sticky_with_boss" not in kwargs:
            self.sticky_with_boss = False
        if "mass" not in kwargs:
            self.mass = 15
        if "upkey" not in kwargs:
            self.upkey = None
        if "downkey" not in kwargs:
            self.downkey = None
        if "rightkey" not in kwargs:
            self.rightkey = None
        if "leftkey" not in kwargs:
            self.leftkey = None
        if "speed" not in kwargs:
            self.speed = None
        if "age" not in kwargs:
            self.age = 0 # age in seconds
        if "warp_on_edge" not in kwargs:
            self.warp_on_edge = False
        if "dangerhigh" not in kwargs:
            self.dangerhigh = False

    def kill(self):
        if self.number in self.numbers:
           del VectorSprite.numbers[self.number] # remove Sprite from numbers dict
        pygame.sprite.Sprite.kill(self)

    def create_image(self):
        if self.picture is not None:
            self.image = self.picture.copy()
        else:
            self.image = pygame.Surface((self.width,self.height))
            self.image.fill((self.color))
        self.image = self.image.convert_alpha()
        self.image0 = self.image.copy()
        self.rect= self.image.get_rect()
        self.width = self.rect.width
        self.height = self.rect.height

    def rotate(self, by_degree):
        """rotates a sprite and changes it's angle by by_degree"""
        self.angle += by_degree
        oldcenter = self.rect.center
        self.image = pygame.transform.rotate(self.image0, self.angle)
        self.image.convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = oldcenter

    def set_angle(self, degree):
        """rotates a sprite and changes it's angle to degree"""
        self.angle = degree
        oldcenter = self.rect.center
        self.image = pygame.transform.rotate(self.image0, self.angle)
        self.image.convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = oldcenter
        
    def ai(self):
        pass

    def update(self, seconds):
        """calculate movement, position and bouncing on edge"""
        #self.ai()
        # ----- kill because... ------
        if self.hitpoints <= 0:
            self.kill()
        if self.max_age is not None and self.age > self.max_age:
            self.kill()
        if self.max_distance is not None and self.distance_traveled > self.max_distance:
            self.kill()
        # ---- movement with/without boss ----
        if self.bossnumber is not None:
            if self.kill_with_boss:
                if self.bossnumber not in VectorSprite.numbers:
                    self.kill()
            if self.sticky_with_boss:
                boss = VectorSprite.numbers[self.bossnumber]
                #self.pos = v.Vec2d(boss.pos.x, boss.pos.y)
                self.pos = pygame.math.Vector2(boss.pos.x, boss.pos.y)
        self.pos += self.move * seconds * Game.speed
        self.distance_traveled += self.move.length() * seconds * Game.speed
        self.age += seconds
        self.wallbounce()
        self.rect.center = ( int(round(self.pos.x, 0)), -int(round(self.pos.y, 0)) )

    def wallbounce(self):
        # ---- bounce / kill on screen edge ----
        # ------- left edge ----
        if self.pos.x < 0:
            if self.kill_on_edge:
                self.kill()
            elif self.bounce_on_edge:
                self.pos.x = 0
                self.move.x *= -1
            elif self.warp_on_edge:
                self.pos.x = Viewer.width 
        # -------- upper edge -----
        if self.pos.y  > 0:
            if self.kill_on_edge:
                self.kill()
            elif self.bounce_on_edge:
                self.pos.y = 0
                self.move.y *= -1
            elif self.warp_on_edge:
                self.pos.y = -Viewer.height
        # -------- right edge -----                
        if self.pos.x  > Viewer.width:
            if self.kill_on_edge:
                self.kill()
            elif self.bounce_on_edge:
                self.pos.x = Viewer.width
                self.move.x *= -1
            elif self.warp_on_edge:
                self.pos.x = 0
        # --------- lower edge ------------
        if self.dangerhigh:
            y = self.dangerhigh
        else:
            y = Viewer.height
        if self.pos.y   < -y:
            if self.kill_on_edge:
                self.hitpoints = 0
                self.kill()
            elif self.bounce_on_edge:
                self.pos.y = -y
                self.move.y *= -1
            elif self.warp_on_edge:
                self.pos.y = 0

class Island(VectorSprite):
    def __init__(self, **kwargs):
        VectorSprite.__init__(self, **kwargs)
        if "empire_color" not in kwargs:
            self.empire_color = (0,255,0)
        if "ships" not in kwargs:
            self.ships = 0
        if "size" not in kwargs:
            self.size = 100
            
    def update(self, seconds):
        VectorSprite.update(self, seconds)
        if self.empire_color in Game.enemy_color:
            self.ai()
            
    def ai(self):
        if (Game.enemy_color[0] == self.empire_color and Game.enemy1_wood < 5) or (Game.enemy_color[1] == self.empire_color and Game.enemy2_wood < 5):
            if random.random() < (0.005*Game.speed):
                if self.ships > 0: #are there any ships?
                    target = []
                    for i in Game.wood_islandgroup:
                        d = distance(self.pos,i.pos)
                        if i.empire_color == self.empire_color:
                            continue
                        elif i.empire_color == Game.player_color:
                            if len(target) == 0:
                                target = [d+1000,i.pos]
                            elif target[0] > d+1000:
                                target = [d+1000,i.pos]
                        else:
                            if len(target) == 0:
                                target = [d,i.pos]
                            elif target[0] > d:
                                target = [d,i.pos]
                    if len(target) != 0:
                        self.ships -= 1
                        s = pygame.math.Vector2(self.pos[0],self.pos[1])
                        v = target[1] - s
                        m = v.normalize() * 30
                        move = pygame.math.Vector2(m)
                        start = v.normalize() * (self.size//2 + 25)# 25 = length of ship
                        e = pygame.math.Vector2(1,0)
                        angle = e.angle_to(m)
                        Ship(pos=self.pos+start, destination=target[1], move=move, angle=angle, empire_color=self.empire_color)
        if (Game.enemy_color[0] == self.empire_color and Game.enemy1_iron < 5) or (Game.enemy_color[1] == self.empire_color and Game.enemy2_iron < 5):
            if random.random() < (0.005*Game.speed):
                if self.ships > 0: #are there any ships?
                    target = []
                    for i in Game.iron_islandgroup:
                        d = distance(self.pos,i.pos)
                        if i.empire_color == self.empire_color:
                            continue
                        elif i.empire_color == Game.player_color:
                            if len(target) == 0:
                                target = [d+1000,i.pos]
                            elif target[0] > d+1000:
                                target = [d+1000,i.pos]
                        else:
                            if len(target) == 0:
                                target = [d,i.pos]
                            elif target[0] > d:
                                target = [d,i.pos]
                    if len(target) != 0:
                        self.ships -= 1
                        v = target[1] - self.pos
                        m = v.normalize() * 30
                        move = pygame.math.Vector2(m)
                        start = v.normalize() * (self.size//2 + 25)# 25 = length of ship
                        e = pygame.math.Vector2(1,0)
                        angle = e.angle_to(m)
                        Ship(pos=self.pos+start, destination=target[1], move=move, angle=angle, empire_color=self.empire_color)
        if (Game.enemy_color[0] == self.empire_color and Game.enemy1_iron > 5 and Game.enemy1_wood > 5) or (Game.enemy_color[1] == self.empire_color and Game.enemy2_iron > 5 and Game.enemy2_wood > 5):
            if random.random() < (0.005*Game.speed):
                if self.ships > 0: #are there any ships?
                    target = []
                    for i in Game.ship_islandgroup:
                        d = distance(self.pos,i.pos)
                        if i.empire_color == self.empire_color:
                            continue
                        elif i.empire_color == Game.player_color:
                            if len(target) == 0:
                                target = [d+1000,i.pos]
                            elif target[0] > d+1000:
                                target = [d+1000,i.pos]
                        else:
                            if len(target) == 0:
                                target = [d,i.pos]
                            elif target[0] > d:
                                target = [d,i.pos]
                    if len(target) != 0:
                        self.ships -= 1
                        v = target[1] - self.pos
                        m = v.normalize() * 30
                        move = pygame.math.Vector2(m)
                        start = v.normalize() * (self.size//2 + 25)# 25 = length of ship
                        e = pygame.math.Vector2(1,0)
                        angle = e.angle_to(m)
                        Ship(pos=self.pos+start, destination=target[1], move=move, angle=angle, empire_color=self.empire_color)
        if random.random() < ((0.0001 + Game.enemy_ships*0.0005) *Game.speed):
            if self.ships > 0: #are there any ships?
                    target = []
                    for i in Game.nonresource_islandgroup:
                        d = distance(self.pos,i.pos)
                        if i.empire_color == self.empire_color:
                            continue
                        elif i.empire_color == Game.player_color:
                            if len(target) == 0:
                                target = [d+1000,i.pos]
                            elif target[0] > d+1000:
                                target = [d+1000,i.pos]
                        else:
                            if len(target) == 0:
                                target = [d,i.pos]
                            elif target[0] > d:
                                target = [d,i.pos]
                    if len(target) != 0:
                        self.ships -= 1
                        v = target[1] - self.pos
                        m = v.normalize() * 30
                        move = pygame.math.Vector2(m)
                        start = v.normalize() * (self.size//2 + 25)# 25 = length of ship
                        e = pygame.math.Vector2(1,0)
                        angle = e.angle_to(m)
                        Ship(pos=self.pos+start, destination=target[1], move=move, angle=angle, empire_color=self.empire_color)
        

class Wood_Island(Island):
    
    def __init__(self, **kwargs):
        Island.__init__(self, **kwargs)
        #if "empire_color" not in kwargs:
        #    self.empire_color = (0,255,0)
        #if "ships" not in kwargs:
        #    self.ships = 0

    def _overwrite_parameters(self):
        if self.size == None:
            self.size = 100 
        #self.empire_color = (0,255,0)

    def create_image(self):
        self.image = pygame.Surface((self.size+20,self.size+20))
        pygame.draw.circle(self.image, self.empire_color, (self.size//2+10,self.size//2+10), self.size//2+10)
        pygame.draw.circle(self.image, (0,0,255), (self.size//2+10,self.size//2+10), self.size//2+3)
        Viewer.images["wood_island"] = pygame.transform.scale(Viewer.images["wood_island"], (self.size, self.size))
        self.image1 = Viewer.images["wood_island"]
        self.image.blit(self.image1, (10,10))
        self.image.set_colorkey((0,0,0))
        self.image0 = self.image.copy()
        self.rect = self.image.get_rect()
        #self.image = pygame.Surface((self.size,self.size))
        #pygame.draw.circle(self.image, self.empire_color, (self.size//2,self.size//2), self.size//2)
        #pygame.draw.circle(self.image, (0,128,0), (self.size//2,self.size//2), self.size//2-5)
        #write(self.image, "Wood production", x=5, y=40, fontsize=10, color=(1,1,1))
        #self.image.set_colorkey((0,0,0))
        #self.rect= self.image.get_rect()
        #self.image0 = self.image.copy()
        
    def update(self, seconds):
        Island.update(self, seconds)
        if self.empire_color == Game.player_color:
            Game.player_wood += 0.3 * seconds * Game.speed
        elif self.empire_color == Game.enemy_color[0]:
            Game.enemy1_wood += 0.3 * seconds * Game.speed
        elif self.empire_color == Game.enemy_color[1]:
            Game.enemy2_wood += 0.3 * seconds * Game.speed
        else:
            pass
        #write(self.image, "{}".format(self.ships), x=self.size-10, y=self.size-self.size//5,  fontsize=self.size//5, color=(255,0,0))
        
class Iron_Island(Island):

    def __init__(self, **kwargs):
        Island.__init__(self, **kwargs)
        #if "empire_color" not in kwargs:
        #    self.empire_color = (0,255,0)
        #if "ships" not in kwargs:
        #    self.ships = 0
    
    def _overwrite_parameters(self):
        if self.size == None:
            self.size = 100 
        #self.ships = 5
        #self.empire_color = (0,255,0)

    def create_image(self):
        self.image = pygame.Surface((self.size+20,self.size+20))
        pygame.draw.circle(self.image, self.empire_color, (self.size//2+10,self.size//2+10), self.size//2+10)
        pygame.draw.circle(self.image, (0,0,255), (self.size//2+10,self.size//2+10), self.size//2+3)
        Viewer.images["iron_island"] = pygame.transform.scale(Viewer.images["iron_island"], (self.size, self.size))
        self.image1 = Viewer.images["iron_island"]
        self.image.blit(self.image1, (10,10))
        self.image.set_colorkey((0,0,0))
        self.image0 = self.image.copy()
        self.rect = self.image.get_rect()
        #self.image = pygame.Surface((self.size,self.size))
        #pygame.draw.circle(self.image, self.empire_color, (self.size//2,self.size//2), self.size//2)
        #pygame.draw.circle(self.image, (100,100,100), (self.size//2,self.size//2), self.size//2-5)
        #write(self.image, "Iron production", x=5, y=40, fontsize=10, color=(1,1,1))
        #self.image.set_colorkey((0,0,0))
        #self.rect= self.image.get_rect()
        #self.image0 = self.image.copy()
        
    def update(self, seconds):
        Island.update(self, seconds)
        if self.empire_color == Game.player_color:
            Game.player_iron += 0.3 * seconds * Game.speed
        elif self.empire_color == Game.enemy_color[0]:
            Game.enemy1_iron += 0.3 * seconds * Game.speed
        elif self.empire_color == Game.enemy_color[1]:
            Game.enemy2_iron += 0.3 * seconds * Game.speed
        else:
            pass
        #write(self.image, "{}".format(self.ships), x=self.size-10, y=self.size-self.size//5,  fontsize=self.size//5, color=(255,0,0))
        
class Ship_Island(Island):

    def __init__(self, **kwargs):
        Island.__init__(self, **kwargs)
        #if "empire_color" not in kwargs:
        #    self.empire_color = (0,255,0)
        #if "ships" not in kwargs:
        #    self.ships = 0
    
    def _overwrite_parameters(self):
        if self.size == None:
            self.size = 100 
        #self.ships = 5
        #self.empire_color = (0,255,0)

    def create_image(self):
        self.image = pygame.Surface((self.size+20,self.size+20))
        pygame.draw.circle(self.image, self.empire_color, (self.size//2+10,self.size//2+10), self.size//2+10)
        pygame.draw.circle(self.image, (0,0,255), (self.size//2+10,self.size//2+10), self.size//2+3)
        Viewer.images["ship_island"] = pygame.transform.scale(Viewer.images["ship_island"], (self.size, self.size))
        self.image1 = Viewer.images["ship_island"]
        self.image.blit(self.image1, (10,10))
        self.image.set_colorkey((0,0,0))
        self.image0 = self.image.copy()
        self.rect = self.image.get_rect()
        #self.image = pygame.Surface((self.size,self.size))
        #pygame.draw.circle(self.image, self.empire_color, (self.size//2,self.size//2), self.size//2)
        #pygame.draw.circle(self.image, (140,100,20), (self.size//2,self.size//2), self.size//2-5)
        #write(self.image, "Ship production", x=5, y=40, fontsize=10, color=(1,1,1))
        #self.image.set_colorkey((0,0,0))
        #self.rect= self.image.get_rect()
        #self.image0 = self.image.copy()
        
    def update(self, seconds):
        Island.update(self, seconds)
        if self.empire_color == Game.player_color:
            if Game.player_iron >= 5 and Game.player_wood >= 5:
                Game.player_iron -= 5
                Game.player_wood -= 5
                ship_islands = []
                for i in Game.ship_islandgroup: 
                    if i.empire_color == Game.player_color:
                        ship_islands.append(i)
                random.choice(ship_islands).ships += 1
        elif self.empire_color == Game.enemy_color[0]:
            if Game.enemy1_iron >= 5 and Game.enemy1_wood >= 5:
                Game.enemy1_iron -= 5
                Game.enemy1_wood -= 5
                enemy1_ship_islands = []
                for i in Game.ship_islandgroup: 
                    if i.empire_color == Game.enemy_color[0]:
                        enemy1_ship_islands.append(i)
                random.choice(enemy1_ship_islands).ships += 1
        elif self.empire_color == Game.enemy_color[1]:
            if Game.enemy2_iron >= 5 and Game.enemy2_wood >= 5:
                Game.enemy2_iron -= 5
                Game.enemy2_wood -= 5
                enemy2_ship_islands = []
                for i in Game.ship_islandgroup: 
                    if i.empire_color == Game.enemy_color[1]:
                        enemy2_ship_islands.append(i)
                random.choice(enemy2_ship_islands).ships += 1
        else:
            pass
                
class Main_Island(Island):

    def __init__(self, **kwargs):
        Island.__init__(self, **kwargs)
        #if "empire_color" not in kwargs:
        #    self.empire_color = (0,255,0)
        #if "ships" not in kwargs:
        #    self.ships = 0

    
    def _overwrite_parameters(self):
        if self.size == None:
            self.size = 200 
        #self.size = 200
        #self.ships = 5
        #self.empire_color = (0,255,0)
    
    def create_image(self):
        self.image = pygame.Surface((self.size+20,self.size+20))
        pygame.draw.circle(self.image, self.empire_color, (self.size//2+10,self.size//2+10), self.size//2+10)
        pygame.draw.circle(self.image, (0,0,255), (self.size//2+10,self.size//2+10), self.size//2+3)
        Viewer.images["main_island"] = pygame.transform.scale(Viewer.images["main_island"], (self.size, self.size))
        self.image1 = Viewer.images["main_island"]
        self.image.blit(self.image1, (10,10))
        self.image.set_colorkey((0,0,0))
        self.image0 = self.image.copy()
        self.rect = self.image.get_rect()
        #self.image = pygame.Surface((self.size,self.size))
        #pygame.draw.circle(self.image, self.empire_color, (self.size//2,self.size//2), self.size//2)
        #pygame.draw.circle(self.image, (30,200,30), (self.size//2,self.size//2), self.size//2-5)
        #write(self.image, "Main Island", x=self.size//20, y=self.size//2, fontsize=self.size//10, color=(1,1,1))
        #self.image.set_colorkey((0,0,0))
        #self.rect= self.image.get_rect()
        #self.image0 = self.image.copy()
    
    def update(self, seconds):
        Island.update(self, seconds)
        #write(self.image, "{}".format(self.ships), x=self.size-30, y=self.size-self.size//5,  fontsize=self.size//5, color=(255,0,0))
        
class Ship(VectorSprite):
    
    def __init__(self, **kwargs):
        VectorSprite.__init__(self, **kwargs)
        if "destination" not in kwargs:
            self.destination = None
        if "empire_color" not in kwargs:
            self.empire_color = (0,0,255)
    
    def _overwrite_parameters(self):
        self.size = Game.ship_size
        #self.empire_color = (0,255,0)
        #self.destination = random.choice(Game.islands)
        
    def create_image(self):
        if self.empire_color == Game.player_color:
            Viewer.images["player_ship"] = pygame.transform.scale(Viewer.images["player_ship"], self.size)
            self.image = Viewer.images["player_ship"]
        elif self.empire_color == (255,0,0):
            Viewer.images["red_empire_ship"] = pygame.transform.scale(Viewer.images["red_empire_ship"], self.size)
            self.image = Viewer.images["red_empire_ship"]
        else:
            Viewer.images["ship"] = pygame.transform.scale(Viewer.images["ship"], self.size)
            self.image = Viewer.images["ship"]
        self.image0 = self.image.copy()
        self.rect = self.image.get_rect()
        #self.image = pygame.Surface(self.size)
        #pygame.draw.rect(self.image, (self.empire_color), (0,0,self.size[0],self.size[1]), 0)
        #pygame.draw.rect(self.image, (140,100,20), (5,2,self.size[0]-10,self.size[1]-4), 0)
        #self.image.set_colorkey((0,0,0))
        ##self.rect = self.image.get_rect()
        #self.image0 = self.image.copy()
        
    def radar(self):
        """Checks if an island is on a given position"""
        checkpos = self.pos + self.move*2
        for i in Game.islandgroup:
            if self.destination == i.pos:
                continue
            if distance(i.pos,checkpos) < i.size/2+30:
                return i        
        
    def find_way(self, island):
        """Calculates the shortest way around an island and returns +1 or -1 depending on the direction"""
        vector_island_to_destination = self.destination - island.pos #vector island-destination
        nvector_island_to_destination = pygame.math.Vector2(-vector_island_to_destination[1],vector_island_to_destination[0]) #vector with 90° to vector island-destination to the right
        vector_islandradius = nvector_island_to_destination.normalize() * island.size/2 #make nvector island-destination to length radius
        point_a = island.pos + vector_islandradius #calculate the first tangent to island through the destination right to the ship
        point_b = island.pos - vector_islandradius #calculate the second tangent to island through the destination left to the ship
        vector_i_a = vector_islandradius #vector from the middle of the island to point a
        vector_i_b = -vector_islandradius #vector from the middle of the island to point b
        vector_i_ship = self.pos - island.pos #vector from the island to the ship
        angle_a = ((vector_i_ship*vector_i_a)/vector_i_ship.length()*vector_i_a.length()) #angle between vector_i_ship and vector_i_a
        angle_b = ((vector_i_ship*vector_i_b)/vector_i_ship.length()*vector_i_b.length()) #angle between vector_i_ship and vector_i_b
        route_a_length = math.pi * 2 * island.size/2 * (angle_a/360) + (self.destination - point_a).length() #length of route around point a
        route_b_length = math.pi * 2 * island.size/2 * (angle_b/360) + (self.destination - point_b).length() #length of route around point b
        if route_a_length <= route_b_length:
            return -1
        else:
            return 1
    
    def update(self, seconds):
        VectorSprite.update(self, seconds)
        island = self.radar()
        if island:
            route = self.find_way(island)*Game.speed
            self.move.rotate_ip(route)
            angle = pygame.math.Vector2(1,0).angle_to(self.move)
            self.set_angle(angle)
        destination_vector = (self.destination - self.pos)
        angle_calculation = (self.move*destination_vector)/((self.move.length())*(destination_vector.length()))
        if angle_calculation > 1:       #minor error in the python calculations cause a number slightly above 1, this leads to gamecrash if you try to get the arccos from it
            angle_calculation = 1
        angle_move_destination = math.degrees(math.acos(angle_calculation))
        if angle_move_destination > 3:
            if not island:
                newangle_calculation = (self.move.rotate(-1)*destination_vector)/(self.move.rotate(-1).length()*destination_vector.length())
                if newangle_calculation > 1:
                    newangle_calculation = 1
                if math.degrees(math.acos(newangle_calculation)) < angle_move_destination:
                    self.move = self.move.rotate(-1*Game.speed)
                else:
                    self.move = self.move.rotate(1*Game.speed)
                angle = pygame.math.Vector2(1,0).angle_to(self.move)
                self.set_angle(angle)
        


class Viewer(object):
    width = 0
    height = 0
    images={}
    
    fullscreen = False

    def __init__(self, width=640, height=400, fps=30):
        """Initialize pygame, window, background, font,...
           default arguments """
        pygame.init()
        Viewer.width = width    # make global readable
        Viewer.height = height
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.DOUBLEBUF)
        self.background = pygame.Surface(self.screen.get_size()).convert()
        self.background.fill((255,255,255)) # fill background white
        self.clock = pygame.time.Clock()
        self.fps = fps
        self.playtime = 0.0
        self.click_indicator_time = 0
        self.last_click = 0
        self.island_selected = []
        self.end_game = False
        self.newlevel = False
        self.end_gametime = 0
        #self.time_to_draw = 0 #if there are no possible moves for a period of time, the game ends
        self.load_graphics()
        # ------ background images ------
        self.backgroundfilenames = [] # every .jpg file in folder 'data'
        try:
            for root, dirs, files in os.walk("data"):
                for file in files:
                    if file[-4:] == ".jpg" or file[-5:] == ".jpeg":
                        self.backgroundfilenames.append(file)
            random.shuffle(self.backgroundfilenames) # remix sort order
        except:
            print("no folder 'data' or no jpg files in it")
        # ------ joysticks ----
        pygame.joystick.init()
        self.joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
        for j in self.joysticks:
            j.init()
        self.prepare_sprites()
        self.loadbackground()
        # --- create screen resolution list ---
        li = ["back"]
        for i in pygame.display.list_modes():
            # li is something like "(800, 600)"
            pair = str(i)
            comma = pair.find(",")
            x = pair[1:comma]
            y = pair[comma+2:-1]
            li.append(str(x)+"x"+str(y))
        Menu.menu["Screenresolution"] = li
        self.set_screenresolution()

    def loadbackground(self):
        
        #try:
        #    self.background = pygame.image.load(os.path.join("data",
        #         self.backgroundfilenames[Viewer.wave %
        #         len(self.backgroundfilenames)]))
        #except:
        #    self.background = pygame.Surface(self.screen.get_size()).convert()
        #    self.background.fill((255,255,255)) # fill background white
        self.background = pygame.Surface(self.screen.get_size()).convert()
        self.background.fill((0,0,255))
        self.background = pygame.transform.scale(self.background,
                          (Viewer.width,Viewer.height))
        self.background.convert()
        
    def set_screenresolution(self):
        if Viewer.fullscreen:
             self.screen = pygame.display.set_mode((self.width, self.height), pygame.DOUBLEBUF|pygame.FULLSCREEN)
        else:
             self.screen = pygame.display.set_mode((self.width, self.height), pygame.DOUBLEBUF)
        self.loadbackground()
        
    def load_sprites(self):
        pass
        
    def load_graphics(self):
        Viewer.images["ship"] = pygame.image.load(os.path.join("data", "Ship.png")).convert_alpha()
        Viewer.images["player_ship"] = pygame.image.load(os.path.join("data", "player_ship.png")).convert_alpha()
        Viewer.images["red_empire_ship"] = pygame.image.load(os.path.join("data", "red_empire_ship.png")).convert_alpha()
        Viewer.images["main_island"] = pygame.image.load(os.path.join("data", "main_island.png")).convert_alpha()
        #Viewer.images["main_island"] = pygame.transform.scale(Viewer.images["main_island"], (200, 200))
        Viewer.images["wood_island"] = pygame.image.load(os.path.join("data", "wood_island.png")).convert_alpha()
        Viewer.images["iron_island"] = pygame.image.load(os.path.join("data", "iron_island.png")).convert_alpha()
        Viewer.images["ship_island"] = pygame.image.load(os.path.join("data", "ship_island.png")).convert_alpha()
        
    def clean_up(self):
        for i in Game.islandgroup:
            i.kill()
        for s in self.shipgroup:
            s.kill()
        for g in Game.groups:
            g.empty()
            
    def update_gamevariables(self):
        """Updates the counter for islands and ships of player and enemies."""
        Game.player_ships = 0
        Game.player_islands = 0
        Game.player_island_types = [0,0,0,0]
        Game.enemy_ships = 0
        Game.enemy_islands = 0
        Game.enemy1_island_types = [0,0,0,0]
        Game.enemy2_island_types = [0,0,0,0]
        for i in Game.islandgroup:
            if i.empire_color == Game.player_color:
                Game.player_ships += i.ships
                Game.player_islands += 1
                if i.__class__.__name__ == "Main_Island":
                    Game.player_island_types[0] += 1
                elif i.__class__.__name__ == "Ship_Island":
                    Game.player_island_types[1] += 1
                elif i.__class__.__name__ == "Wood_Island":
                    Game.player_island_types[2] += 1
                elif i.__class__.__name__ == "Iron_Island":
                    Game.player_island_types[3] += 1
            elif i.empire_color in Game.enemy_color:
                Game.enemy_ships += i.ships
                Game.enemy_islands += 1
                if i.__class__.__name__ == "Main_Island":
                    Game.enemy_island_types[0] += 1
                elif i.__class__.__name__ == "Ship_Island":
                    Game.enemy_island_types[1] += 1
                elif i.__class__.__name__ == "Wood_Island":
                    Game.enemy_island_types[2] += 1
                elif i.__class__.__name__ == "Iron_Island":
                    Game.enemy_island_types[3] += 1
        for s in self.shipgroup:
            if s.empire_color == Game.player_color:
                Game.player_ships += 1
            elif s.empire_color in Game.enemy_color:
                Game.enemy_ships += 1
        
    
    def new_level(self):
        try: 
            level = Levels.create_sprites(Game.level)
        except:
            print("-------------------------You won the game------------------------")
            Game.level = 1
            for l in Levels.levels.keys():
                if int(l) <= 0:
                    Game.level -= 1 #for every tutorial level we go one level below 0
            self.new_level()
            self.menu_run()
            return

        Game.player_iron = 0
        Game.player_wood = 0
        Game.enemy1_iron = 0
        Game.enemy1_wood = 0
        Game.enemy2_iron = 0
        Game.enemy2_wood = 0
        self.clean_up()
        self.island_selected = []

        for x in range(len(level["Main_islands"])):
            if level["Main_islands"][x][1] == Game.player_color:
                p_ships = int(level["Main_islands"][x][2]) + Game.difficulty
            else: 
                p_ships = level["Main_islands"][x][2]
            if len(level["Main_islands"][x]) == 4:
                i_size = level["Main_islands"][x][3]
            else:
                i_size = None #default size
            Main_Island(pos=pygame.math.Vector2(level["Main_islands"][x][0]), empire_color = level["Main_islands"][x][1], ships=p_ships, size=i_size)
        for x in range(len(level["Iron_islands"])):
            if len(level["Iron_islands"][x]) == 4:
                i_size = level["Iron_islands"][x][3]
            else:
                i_size = None #default size
            Iron_Island(pos=pygame.math.Vector2(level["Iron_islands"][x][0]), empire_color = level["Iron_islands"][x][1], ships=level["Iron_islands"][x][2], size=i_size)
        for x in range(len(level["Wood_islands"])):
            if len(level["Wood_islands"][x]) == 4:
                i_size = level["Wood_islands"][x][3]
            else:
                i_size = None #default size
            Wood_Island(pos=pygame.math.Vector2(level["Wood_islands"][x][0]), empire_color = level["Wood_islands"][x][1], ships=level["Wood_islands"][x][2], size=i_size)
        for x in range(len(level["Ship_islands"])):
            if len(level["Ship_islands"][x]) == 4:
                i_size = level["Ship_islands"][x][3]
            else:
                i_size = None #default size
            Ship_Island(pos=pygame.math.Vector2(level["Ship_islands"][x][0]), empire_color = level["Ship_islands"][x][1], ships=level["Ship_islands"][x][2], size=i_size)
        
        if "Ships" in level.keys():
            Game.ship_size = level["Ships"]
        else:
            Game.ship_size = (50,20)
        
        if "Game mode" in level.keys() and level["Game mode"] in Game.gamemodes:
            Game.gamemode = level["Game mode"]
        else:
            Game.gamemode = "Conquer"
        
        for i in Game.islandgroup:
                if i.empire_color == Game.player_color:
                    Game.player_ships += i.ships
                    Game.player_islands += 1
                elif i.empire_color in Game.enemy_color:
                    Game.enemy_ships += i.ships
                    Game.enemy_islands += 1
        
    def prepare_sprites(self):
        """painting on the surface and create sprites"""
        self.load_sprites()
        self.allgroup =  pygame.sprite.LayeredUpdates() # for drawing
        self.flytextgroup = pygame.sprite.Group()
        self.shipgroup = pygame.sprite.Group()
        
        VectorSprite.groups = self.allgroup
        Flytext.groups = self.allgroup, self.flytextgroup
        Ship.groups = self.allgroup, self.shipgroup
        Wood_Island.groups = self.allgroup, Game.islandgroup, Game.wood_islandgroup
        Iron_Island.groups = self.allgroup, Game.islandgroup, Game.iron_islandgroup
        Ship_Island.groups = self.allgroup, Game.islandgroup, Game.ship_islandgroup, Game.nonresource_islandgroup
        Main_Island.groups = self.allgroup, Game.islandgroup, Game.main_islandgroup, Game.nonresource_islandgroup
        
        self.new_level()

    def menu_run(self):
        """Not The mainloop"""
        running = True
        #pygame.mouse.set_visible(False)
        self.menu = True
        while running:
            #pygame.mixer.music.pause()
            milliseconds = self.clock.tick(self.fps) #
            seconds = milliseconds / 1000
            text = Menu.menu[Menu.name][Menu.cursor]
            # -------- events ------
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    Game.quit_game = True
                    running = False
                # ------- pressed and released key ------
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    if event.key == pygame.K_UP:
                        Menu.cursor -= 1
                        Menu.cursor = max(0, Menu.cursor) # not < 0
                        #Viewer.menusound.play()
                    if event.key == pygame.K_DOWN:
                        Menu.cursor += 1
                        Menu.cursor = min(len(Menu.menu[Menu.name])-1,Menu.cursor) # not > menu entries
                        #Viewer.menusound.play()
                    if event.key == pygame.K_RETURN:
                        if text == "End the game":
                            Game.quit_game = True
                            running = False
                        elif text in Menu.menu:
                            # changing to another menu
                            Menu.history.append(text) 
                            Menu.name = text
                            Menu.cursor = 0
                        elif text == "Play":
                            running = False
                        elif text == "back":
                            Menu.history = Menu.history[:-1] # remove last entry
                            Menu.cursor = 0
                            Menu.name = Menu.history[-1] # get last entry
                        elif Menu.name == "Screenresolution":
                            # text is something like 800x600
                            t = text.find("x")
                            if t != -1:
                                x = int(text[:t])
                                y = int(text[t+1:])
                                Viewer.width = x
                                Viewer.height = y
                                self.set_screenresolution()
                                self.prepare_sprites()
                        elif Menu.name == "Game speed":
                            if text == "Slow":
                                Game.speed = 0.5
                            elif text == "Normal":
                                Game.speed = 1
                            elif text == "Fast":
                                Game.speed = 3
                            elif text == "Really fast":
                                Game.speed = 5
                        elif Menu.name[0:6] == "Level ":
                            if text[6:] in Levels.levels.keys():
                                Game.level = int(text[6:])
                                self.new_level()
                                running = False
                        elif text[0:8] == "Mission ":
                            Game.level = int(text[8:]) + 100
                            self.new_level()
                            running = False
                        elif Menu.name == "Tutorial":
                            t = 0
                            for l in Levels.levels.keys():
                                if int(l) <= 0:
                                    t += 1
                            Game.level = (int(text[9:]))-t
                            self.new_level()
                            running = False
                        elif Menu.name == "Fullscreen":
                            if text == "True":
                                #Viewer.menucommandsound.play()
                                Viewer.fullscreen = True
                                self.set_screenresolution()
                            elif text == "False":
                                #Viewer.menucommandsound.play()
                                Viewer.fullscreen = False
                                self.set_screenresolution()
                            
                        
            # ------delete everything on screen-------
            self.screen.blit(self.background, (0, 0))
            
            # -------------- UPDATE all sprites -------             
            self.flytextgroup.update(seconds)

            # ----------- clear, draw , update, flip -----------------
            self.allgroup.draw(self.screen)
            for i in Game.islandgroup:
                if i.empire_color != Game.neutral_color:
                    write(self.screen, "{}".format(i.ships), x=i.pos[0]+i.size//2-10, y=-i.pos[1]+i.size//5+20,  fontsize=i.size//5, color=(i.empire_color))
                else:
                    if i.ships != 0:
                       write(self.screen, "{}".format(i.ships), x=i.pos[0]+i.size//2-10, y=-i.pos[1]+i.size//5+20,  fontsize=i.size//5, color=(1,1,1))
            
            pygame.draw.rect(self.screen,(170,170,170),(200,90,350,400))
            pygame.draw.rect(self.screen,(200,200,200),(600,90,350,400))
            pygame.draw.rect(self.screen,(230,230,230),(1000,90,350,400))
            
            self.flytextgroup.draw(self.screen)

            # --- paint menu ----
            # ---- name of active menu and history ---
            write(self.screen, text="You are here:", x=200, y=50, color=(0,255,255), fontsize=15)
            
            t = "main"
            for nr, i in enumerate(Menu.history[1:]):
                #if nr > 0:
                t+=(" > ")
                t+=(i)
            write(self.screen, text=t, x=200,y=70,color=(0,255,255), fontsize=15)
            # --- menu items ---
            menu = Menu.menu[Menu.name]
            for y, item in enumerate(menu):
                write(self.screen, text=item, x=Viewer.width//2-500, y=100+y*50, color=(255,255,255), fontsize=30)
            # --- cursor ---
            write(self.screen, text="-->", x=Viewer.width//2-600, y=100+ Menu.cursor * 50, color=(0,0,0), fontsize=30)
            # ---- descr ------
            if text in Menu.descr:
                lines = structurize_text(Menu.descr[text], Menu.linelength)
                for y, line in enumerate(lines):
                    write(self.screen, text=line, x=Viewer.width//2-100, y=100+y*30, color=(255,0,255), fontsize=20)
            elif text[0:6] == "Level ":
                if text[6:] in Levels.level_descriptions.keys():
                    lines = structurize_text(Levels.level_descriptions[text[6:]],Menu.linelength)
                    for y, line in enumerate(lines):
                        write(self.screen, text=line, x=Viewer.width//2-100, y=100+y*30, color=(255,0,255), fontsize=20)
            elif text[0:9] == "Tutorial ":
                t = 0
                lines = []
                for l in Levels.levels.keys():
                    if int(l) <= 0:
                        t += 1
                    lines = structurize_text(Levels.levels_descriptions[text[-1]-t], Menu.linelength)
                for y, line in enumerate(lines):
                    write(self.screen, text=line, x=Viewer.width//2-100, y=100+y*30, color=(255,0,255), fontsize=20)
            elif text[0:8] == "Mission ":
                level = str(int(text[8:])+100)
                if level in Levels.level_descriptions.keys():
                    lines = structurize_text(Levels.level_descriptions[level],Menu.linelength)
                    for y, line in enumerate(lines):
                        write(self.screen, text=line, x=Viewer.width//2-100, y=100+y*30, color=(255,0,255), fontsize=20)
           # ---- menu_images -----
            if text in Menu.menu_images:
                Viewer.images[Menu.menu_images[text]] = pygame.transform.scale(Viewer.images[Menu.menu_images[text]], (300, 300))
                self.screen.blit(Viewer.images[Menu.menu_images[text]], (1020,100))
                
            # -------- next frame -------------
            pygame.display.flip()
    
    def run(self):
        """The mainloop"""
        running = True
        Viewer.fullscreen = True
        self.set_screenresolution()
        #pygame.mouse.set_visible(False)
        oldleft, oldmiddle, oldright  = False, False, False
        self.snipertarget = None
        gameOver = False
        exittime = 0
        self.menu_run()
        running = True
    
        while running:
            if Game.quit_game:
                running = False
            milliseconds = self.clock.tick(self.fps) #
            seconds = milliseconds / 1000
            self.playtime += seconds
            
            if gameOver:
                if self.playtime > exittime:
                    running = False
                    
            # -------- events ------
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                # ------- pressed and released key ------
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.menu_run()
                    elif event.key == pygame.K_m:
                        self.menu_run()
            # delete everything on screen
            self.screen.blit(self.background, (0, 0))  # macht alles weiß

            # ------------ pressed keys ------
            pressed_keys = pygame.key.get_pressed()

            # write text below sprites
            write(self.screen, "FPS: {:8.3}".format(
                self.clock.get_fps() ), x=10, y=10)
            write(self.screen, "Wood = {:.0f}".format(Game.player_wood), x=10,y=30)
            write(self.screen, "Iron = {:.0f}".format(Game.player_iron), x=10,y=50)
            write(self.screen, "Ships = {:.0f}".format(Game.player_ships), x=10,y=80)
            level = Game.level
            if level <= 0:
                for l in Levels.levels.keys():
                    if int(l) <= 0:
                        level += 1
                write(self.screen, "Tutorial {}".format(level), x=1280, y=30)
            else:
                write(self.screen, "Level {}".format(level), x=1280, y=30)
            
            #for i in Game.islandgroup:--------------------------------------------------------------------------------------------------------------------
            #    if i.color != Game.neutral_color:
            #        write(self.screen, "{}".format(i.ships), x=i.pos[0], y=-i.pos[1],  fontsize=i.size//5, color=(255,0,0))
            #    else:
            #        if i.ships != 0:
            #            write(self.screen, "{}".format(i.ships), x=i.pos[0], y=-i.pos[1],  fontsize=i.size//5, color=(255,0,0))
            self.allgroup.update(seconds)
            
            # -------------- write explanations for the current level on the screen ------------------
            if str(Game.level) in Levels.level_descriptions.keys():
                lines = structurize_text(Levels.level_descriptions[str(Game.level)],70)
                for y, line in enumerate(lines):
                    write(self.screen, line, x=200, y=50+y*25)

            self.update_gamevariables()
            # ------------------win or lose --------------------
            if self.end_gametime < self.playtime:
                if self.newlevel == True:
                    self.newlevel = False
                    Game.level += 1
                    self.new_level()
                elif self.end_game == True:
                    break
                if Game.gamemode == "Conquer":
                    if Game.enemy_ships == 0 and Game.enemy_islands == 0:
                        Flytext(x = Viewer.width//2, y = Viewer.height//2, text = "You won the level!", fontsize=30, color=Game.player_color)
                        self.end_gametime = self.playtime + 5
                        self.newlevel = True
                    elif Game.player_ships == 0 and Game.player_islands == 0:
                        Flytext(x = Viewer.width//2, y = Viewer.height//2, text = "You lose!", fontsize=30, color=random.choice(Game.enemy_color))
                        self.end_gametime = self.playtime + 5
                        self.end_game == True
                    elif Game.player_ships == 0 and Game.enemy_ships == 0:
                        if (Game.player_island_types[2] == 0 and Game.player_island_types[3] == 0) or Game.player_island_types[1] == 0:
                            if (Game.enemy_island_types[2] == 0 and Game.enemy_island_types[3] == 0) or Game.enemy_island_types[1] == 0:
                                Flytext(x = Viewer.width//2, y = Viewer.height//2, text = "No one wins!", fontsize=30, color=(0,0,0))
                                self.end_gametime = self.playtime + 5
                                self.end_game == True
                #elif Game.gamemode == "Defend":
                    
                
            # ------------------ click on island ---------------
            left,middle,right = pygame.mouse.get_pressed()
            if oldright and not right:
                mouse_pos = pygame.mouse.get_pos()
                for i in Game.islandgroup:
                    dist = distance((i.pos[0],i.pos[1]), (mouse_pos[0],-mouse_pos[1]))
                    if dist < i.size/2:
                        self.island_selected = [i.pos[0],i.pos[1],i.size]
                        break
                    else:
                        self.island_selected = []
            # -------------- send ship ----------------
            if oldleft and not left:
                mouse_pos = pygame.mouse.get_pos()
                for i in Game.islandgroup:
                    dist = distance((i.pos[0],i.pos[1]), (mouse_pos[0],-mouse_pos[1]))
                    if dist < i.size/2:
                        if len(self.island_selected) != 0: #Island selected?
                            for s in Game.islandgroup: #Which island is selected?
                                if (self.island_selected[0],self.island_selected[1]) == s.pos:
                                    if distance((self.island_selected[0],self.island_selected[1]), i.pos) != 0: #is selected island != target island?
                                        if s.empire_color == Game.player_color: #is it your island?
                                            if s.ships > 0: #are there any ships?
                                                s.ships -= 1
                                                v = i.pos - pygame.math.Vector2(s.pos.x, s.pos.y)
                                                m = v.normalize() * 30
                                                move = pygame.math.Vector2(m)
                                                start = v.normalize() * (s.size//2 + 25)# 25 = length of ship
                                                e = pygame.math.Vector2(1,0)
                                                angle = e.angle_to(m)
                                                Ship(pos=pygame.math.Vector2(self.island_selected[0],self.island_selected[1])+start, destination=i.pos, move=move, angle=angle, empire_color=s.empire_color)
                                                break
            oldleft, oldmiddle, oldright = left, middle, right
                
            if self.island_selected:
                pygame.draw.circle(self.screen, (100,100,100), (int(self.island_selected[0]),-int(self.island_selected[1])), self.island_selected[2]//2+25)

            #-----------collision detection ------
            for i in Game.islandgroup:
                crashgroup = pygame.sprite.spritecollide(i, self.shipgroup,
                             False, pygame.sprite.collide_mask)
                for s in crashgroup:
                    if i.pos == s.destination:
                        if i.empire_color == s.empire_color:
                            i.ships += 1
                            s.kill()
                        else:
                            if i.ships != 0:
                                i.ships -= 1
                                s.kill()
                            else:
                                i.empire_color = s.empire_color
                                i.ships += 1
                                i.create_image()
                                i.rect=i.image.get_rect()
                                i.rect.center=(int(i.pos.x), -int(i.pos.y))
                                s.kill()
                    
                            # ----------- clear, draw , update, flip -----------------
            self.allgroup.draw(self.screen)
            for i in Game.islandgroup:
                if i.empire_color != Game.neutral_color:
                    write(self.screen, "{}".format(i.ships), x=i.pos[0]+i.size//2-10, y=-i.pos[1]+i.size//5+20,  fontsize=i.size//5, color=(i.empire_color))
                else:
                    if i.ships != 0:
                       write(self.screen, "{}".format(i.ships), x=i.pos[0]+i.size//2-10, y=-i.pos[1]+i.size//5+20,  fontsize=i.size//5, color=(1,1,1))
                 
                        
            # -------- next frame -------------
            pygame.display.flip()
        #-----------------------------------------------------
        pygame.mouse.set_visible(True)    
        pygame.quit()

if __name__ == '__main__':
    Viewer(1430,800).run()
