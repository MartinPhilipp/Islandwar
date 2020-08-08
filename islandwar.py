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
import sys
import time
import math
import islandwar_levels as Levels
import islandwar_menu as Menu


def structurize_text(text, linelength):
    """returns a list containing strings with the split up textstring with less or equal chars than the linelength"""
    struct_text = []
    textline = ""
    words = text.split()
    for word in words:
        if len(textline + word) <= linelength:
            textline += word + " "
        elif len(word) > linelength:
            struct_text.append(textline)
            textline = ""
            for char in word:
                if len(textline) < (linelength-1):
                    textline += char
                else:
                    textline += "-"
                    struct_text.append(textline)
                    textline = "" + char
            textline += " "
        else:
            struct_text.append(textline)
            textline = "" + word + " "
    struct_text.append(textline)
    return struct_text

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

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
    """This class is used to store all game related variables"""
    quit_game = False
    difficulty = 0
    language = "English" #"English" or "German"
    graphic = "J" #either "J", "J2" or "I" for different designs
    speed = 1  #Speed of the game
    level = 1
    player = 1  #Amount of players
    ship_size = (50,20) #default ship size
    for l in Levels.levels.keys():
        if int(l) <= 0:
            level -= 1 #for every tutorial level we go one level below 0
    enemy_color = [(255,0,0),(255,165,0)]
    player_color = (0,255,0)
    neutral_color = (0,0,255)
    gamemodes = ["Conquer","Defend","Collect"]
    gamemode = "Conquer"
    player_wood = 0
    player_wood_int = 0
    player_iron = 0
    player_iron_int = 0
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
    motivation_e = ["Don't give up!", "Try again!", "Good luck the next time!"]
    motivation_d = ["Nicht aufgeben!", "Versuch es noch einmal", "Viel Glück beim nächsten Mal!"]
    
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

class Mouse(pygame.sprite.Sprite):
    def __init__(self, radius = 50, color=(255,0,0), x=320, y=240,
                    startx=100,starty=100, control="mouse", ):
        """create a (black) surface and paint a blue Mouse on it"""
        self._layer=10
        pygame.sprite.Sprite.__init__(self,self.groups)
        self.radius = radius
        self.color = color
        self.startx = startx
        self.starty = starty
        self.x = x
        self.y = y
        self.dx = 0
        self.dy = 0
        self.r = color[0]
        self.g = color[1]
        self.b = color[2]
        self.delta = -10
        self.age = 0
        self.pos = pygame.mouse.get_pos()
        self.move = 0
        self.tail=[]
        self.create_image()
        self.rect = self.image.get_rect()
        self.control = control # "mouse" "keyboard1" "keyboard2"
        self.pushed = False

    def create_image(self):

        self.image = pygame.surface.Surface((self.radius*0.5, self.radius*0.5))
        delta1 = 12.5
        delta2 = 25
        if self.r < 151:
            self.r = 151
        w = self.radius*0.5 / 100.0
        h = self.radius*0.5 / 100.0
        # pointing down / up
        for y in (0,2,4):
            pygame.draw.line(self.image,(self.r-delta2,self.g,self.b),
                         (35*w,0+y),(50*w,15*h+y),2)
            pygame.draw.line(self.image,(self.r-delta2,self.g,self.b),
                         (50*w,15*h+y),(65*w,0+y),2)
            pygame.draw.line(self.image,(self.r-delta2,self.g,self.b),
                         (35*w,100*h-y),(50*w,85*h-y),2)
            pygame.draw.line(self.image,(self.r-delta2,self.g,self.b),
                         (50*w,85*h-y),(65*w,100*h-y),2)
        # pointing right / left                 
        for x in (0,2,4):
            pygame.draw.line(self.image,(self.r-delta2,self.g,self.b),
                         (0+x,35*h),(15*w+x,50*h),2)
            pygame.draw.line(self.image,(self.r-delta2,self.g,self.b),
                         (15*w+x,50*h),(0+x,65*h),2)
            
            pygame.draw.line(self.image,(self.r-delta2,self.g,self.b),
                         (100*w-x,35*h),(85*w-x,50*h),2)
            pygame.draw.line(self.image,(self.r-delta2,self.g,self.b),
                         (85*w-x,50*h),(100*w-x,65*h),2)
        self.image.set_colorkey((0,0,0))
        self.rect=self.image.get_rect()
        self.rect.center = self.x, self.y

    def update(self, seconds):
        if self.control == "mouse":
            self.x, self.y = pygame.mouse.get_pos()
        elif self.control == "keyboard1":
            pressed = pygame.key.get_pressed()
            delta = 9
            if pressed[pygame.K_w]:
                self.y -= delta
            if pressed[pygame.K_s]:
                self.y += delta
            if pressed[pygame.K_a]:
                self.x -= delta
            if pressed[pygame.K_d]:
                self.x += delta
        elif self.control == "keyboard2":
            pressed = pygame.key.get_pressed()
            delta = 9
            if pressed[pygame.K_UP]:
                self.y -= delta
            if pressed[pygame.K_DOWN]:
                self.y += delta
            if pressed[pygame.K_LEFT]:
                self.x -= delta
            if pressed[pygame.K_RIGHT]:
                self.x += delta
        elif self.control == "joystick1":
            pass
        elif self.control == "joystick2":
            pass
        if self.x < 0:
            self.x = 0
        elif self.x > Viewer.width:
            self.x = Viewer.width
        if self.y < 0:
            self.y = 0
        elif self.y > Viewer.height:
            self.y = Viewer.height
        self.tail.insert(0,(self.x,self.y))
        self.tail = self.tail[:128]
        self.rect.center = self.x, self.y
        self.r += self.delta   # self.r can take the values from 255 to 101
        if self.r < 151:
            self.r = 151
            self.delta = 10
        if self.r > 255:
            self.r = 255
            self.delta = -10
        self.create_image()

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
        if Game.player == 1:
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

    def _overwrite_parameters(self):
        if self.size == None:
            self.size = 100 

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
        
    def update(self, seconds):
        Island.update(self, seconds)
        if self.empire_color == Game.player_color:
            Game.player_wood += 0.3 * seconds * Game.speed
            if Game.player_wood >= Game.player_wood_int +1:
                Game.player_wood_int +=1
                Flytext(x=self.pos.x, y=-self.pos.y-self.size/2, text="+1 Wood", color=(254, 254, 254), dy=-10)
        elif self.empire_color == Game.enemy_color[0]:
            Game.enemy1_wood += 0.3 * seconds * Game.speed
        elif self.empire_color == Game.enemy_color[1]:
            Game.enemy2_wood += 0.3 * seconds * Game.speed
        else:
            pass

class Iron_Island(Island):

    def __init__(self, **kwargs):
        Island.__init__(self, **kwargs)
    
    def _overwrite_parameters(self):
        if self.size == None:
            self.size = 100 

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

    def update(self, seconds):
        Island.update(self, seconds)
        if self.empire_color == Game.player_color:
            Game.player_iron += 0.3 * seconds * Game.speed
            if Game.player_iron >= Game.player_iron_int +1:
                Game.player_iron_int +=1
                Flytext(x=self.pos.x, y=-self.pos.y-self.size/2, text="+1 Iron", color=(254, 254, 254), dy=-10)
        elif self.empire_color == Game.enemy_color[0]:
            Game.enemy1_iron += 0.3 * seconds * Game.speed
        elif self.empire_color == Game.enemy_color[1]:
            Game.enemy2_iron += 0.3 * seconds * Game.speed
        else:
            pass
        
class Ship_Island(Island):

    def __init__(self, **kwargs):
        Island.__init__(self, **kwargs)
    
    def _overwrite_parameters(self):
        if self.size == None:
            self.size = 100 

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
        
    def update(self, seconds):
        Island.update(self, seconds)
        if self.empire_color == Game.player_color:
            if Game.player_iron >= 5 and Game.player_wood >= 5:
                Game.player_iron -= 5
                Game.player_iron_int -= 5
                Game.player_wood -= 5
                Game.player_wood_int -= 5 
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
    
    def _overwrite_parameters(self):
        if self.size == None:
            self.size = 200 
    
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
    
    def update(self, seconds):
        Island.update(self, seconds)
        
class Ship(VectorSprite):
    
    def __init__(self, **kwargs):
        VectorSprite.__init__(self, **kwargs)
        if "destination" not in kwargs:
            self.destination = None
        if "empire_color" not in kwargs:
            self.empire_color = (0,0,255)
    
    def _overwrite_parameters(self):
        self.size = Game.ship_size
        
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
        self.island_selected_1 = []
        self.island_selected_2 = []
        self.level_win_screen = False
        self.level_lose_screen = False
        self.player_win_screen = False
        self.level_draw_screen = False
        #self.end_game = False
        #self.newlevel = False
        #self.end_gametime = 0
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
        li_e = ["back"]
        li_d = ["zurück"]
        for i in pygame.display.list_modes():
            # li is something like "(800, 600)"
            pair = str(i)
            comma = pair.find(",")
            x = pair[1:comma]
            y = pair[comma+2:-1]
            li_e.append(str(x)+"x"+str(y))
            li_d.append(str(x)+"x"+str(y))
        Menu.menu_e["Screenresolution"] = li_e
        Menu.menu_d["Auflösung"] = li_d
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
        print("Path: ", resource_path("Ship.png"))
        #print(os.path.join("data", "player_ship.png"))
        
        #Viewer.images["ship"] = pygame.image.load(os.path.join("data", "Ship.png")).convert_alpha()
        try:
            Viewer.images["ship"] = pygame.image.load(resource_path(os.path.join("data", "Ship.png"))).convert_alpha()
        except:
            Viewer.images["ship"] = pygame.image.load(resource_path("Ship.png")).convert_alpha()
        #Viewer.images["player_ship"] = pygame.image.load(os.path.join("data", "player_ship.png")).convert_alpha()
        try:
            Viewer.images["player_ship"] = pygame.image.load(resource_path(os.path.join("data", "player_ship.png"))).convert_alpha()
        except:
            Viewer.images["player_ship"] = pygame.image.load(resource_path("player_ship.png")).convert_alpha()
        #Viewer.images["red_empire_ship"] = pygame.image.load(os.path.join("data", "red_empire_ship.png")).convert_alpha()
        Viewer.images["red_empire_ship"] = pygame.image.load(resource_path(os.path.join("data", "red_empire_ship.png"))).convert_alpha()
        #Viewer.images["ship_island"] = pygame.image.load(os.path.join("data", "ship_island.png")).convert_alpha()
        Viewer.images["ship_island"] = pygame.image.load(resource_path(os.path.join("data", "ship_island.png"))).convert_alpha()
        if Game.graphic == "I":
            #Viewer.images["main_island"] = pygame.image.load(os.path.join("data", "main_island.png")).convert_alpha()
            #Viewer.images["wood_island"] = pygame.image.load(os.path.join("data", "wood_island.png")).convert_alpha()
            #Viewer.images["iron_island"] = pygame.image.load(os.path.join("data", "iron_island.png")).convert_alpha()
            Viewer.images["main_island"] = pygame.image.load(resource_path(os.path.join("data", "main_island.png"))).convert_alpha()
            Viewer.images["wood_island"] = pygame.image.load(resource_path(os.path.join("data", "wood_island.png"))).convert_alpha()
            Viewer.images["iron_island"] = pygame.image.load(resource_path(os.path.join("data", "iron_island.png"))).convert_alpha()
        elif Game.graphic == "J":
            #Viewer.images["main_island"] = pygame.image.load(os.path.join("data", "main_island2.png")).convert_alpha()
            #Viewer.images["wood_island"] = pygame.image.load(os.path.join("data", "wood_island2.png")).convert_alpha()
            #Viewer.images["iron_island"] = pygame.image.load(os.path.join("data", "iron_island2.png")).convert_alpha()
            Viewer.images["main_island"] = pygame.image.load(resource_path(os.path.join("data", "main_island2.png"))).convert_alpha()
            Viewer.images["wood_island"] = pygame.image.load(resource_path(os.path.join("data", "wood_island2.png"))).convert_alpha()
            Viewer.images["iron_island"] = pygame.image.load(resource_path(os.path.join("data", "iron_island2.png"))).convert_alpha()
        elif Game.graphic == "J2":
            #Viewer.images["main_island"] = pygame.image.load(os.path.join("data", "main_island2.png")).convert_alpha()
            #Viewer.images["wood_island"] = pygame.image.load(os.path.join("data", "wood_island3.png")).convert_alpha()
            #Viewer.images["iron_island"] = pygame.image.load(os.path.join("data", "iron_island3.png")).convert_alpha()
            Viewer.images["main_island"] = pygame.image.load(resource_path(os.path.join("data", "main_island2.png"))).convert_alpha()
            Viewer.images["wood_island"] = pygame.image.load(resource_path(os.path.join("data", "wood_island3.png"))).convert_alpha()
            Viewer.images["iron_island"] = pygame.image.load(resource_path(os.path.join("data", "iron_island3.png"))).convert_alpha()
        Viewer.images["main_island"] = pygame.transform.scale(Viewer.images["main_island"], (200, 200))
        
    def clean_up(self):
        for i in Game.islandgroup:
            i.kill()
        for s in self.shipgroup:
            s.kill()
        for g in Game.groups:
            g.empty()
        for f in self.flytextgroup:
            f.kill()
            
    def update_gamevariables(self):
        """Updates the counter for islands and ships of player and enemies."""
        Game.player_ships = 0
        Game.player_islands = 0
        Game.player_island_types = [0,0,0,0]
        Game.enemy_ships = 0
        Game.enemy_islands = 0
        Game.enemy_island_types = [0,0,0,0]
        #Game.enemy2_island_types = [0,0,0,0]
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
        print(Game.level)
        self.level_win_screen = False
        self.level_lose_screen = False
        self.player_win_screen = False
        self.level_draw_screen = False
        Game.player_iron = 0
        Game.player_iron_int = 0
        Game.player_wood = 0
        Game.player_wood_int = 0
        Game.enemy1_iron = 0
        Game.enemy1_wood = 0
        Game.enemy2_iron = 0
        Game.enemy2_wood = 0
        self.clean_up()
        #self.island_selected = []
        self.island_selected_1 = []
        self.island_selected_2 = []
        
        if Game.player == 1:
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
                
            try:  #try to kill mouse from multiplayer mode
                del(self.mouse1)
                del(self.mouse2)
            except:
                print("No mouse to kill")

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
                    
            if "Game mode" in level.keys() and level["Game mode"] in Game.gamemodes:
                Game.gamemode = level["Game mode"]
            else:
                Game.gamemode = "Conquer"
        
        elif Game.player == 2: #1 vs. 1
            Game.level = random.randint(1,11)  #random level with two empires
            level = Levels.create_sprites(Game.level)
            
            p_ships = int(level["Main_islands"][0][2])
            for x in range(len(level["Main_islands"])):
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
            
            Game.gamemode = "Conquer"
            self.mouse1 = Mouse(control='keyboard1', color=Game.player_color)
            self.mouse2 = Mouse(control="keyboard2", color=[255,0,0])
        
        
        if "Ships" in level.keys():
            Game.ship_size = level["Ships"]
        else:
            Game.ship_size = (50,20)
        
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
        self.mousegroup = pygame.sprite.Group()
        
        VectorSprite.groups = self.allgroup
        Flytext.groups = self.allgroup, self.flytextgroup
        Ship.groups = self.allgroup, self.shipgroup
        Wood_Island.groups = self.allgroup, Game.islandgroup, Game.wood_islandgroup
        Iron_Island.groups = self.allgroup, Game.islandgroup, Game.iron_islandgroup
        Ship_Island.groups = self.allgroup, Game.islandgroup, Game.ship_islandgroup, Game.nonresource_islandgroup
        Main_Island.groups = self.allgroup, Game.islandgroup, Game.main_islandgroup, Game.nonresource_islandgroup
        Mouse.groups = self.allgroup, self.mousegroup
        
        
        # ------ player1,2,3: mouse, keyboard, joystick ---
        #self.mouse1 = Mouse(control="mouse", color=(255,0,0))
        #self.mouse2 = Mouse(control='keyboard1', color=(255,255,0))
        #self.mouse3 = Mouse(control="keyboard2", color=(255,0,255))
        #self.mouse4 = Mouse(control="joystick1", color=(255,128,255))
        #self.mouse5 = Mouse(control="joystick2", color=(255,255,255))
        
        self.new_level()

    def send_ship(self, mouse_pos, island_selected, empire_color):
        """Tries to send a ship from one island to another."""
        for i in Game.islandgroup:
            dist = distance((i.pos[0],i.pos[1]), (mouse_pos[0],-mouse_pos[1]))
            if dist < i.size/2:
                if len(island_selected) != 0: #Island selected?
                    for s in Game.islandgroup: #Which island is selected?
                        if (island_selected[0],island_selected[1]) == s.pos:
                            if distance((island_selected[0],island_selected[1]), i.pos) != 0: #is selected island != target island?
                                if s.empire_color == empire_color: #is it your island?
                                    if s.ships > 0: #are there any ships?
                                        s.ships -= 1
                                        v = i.pos - pygame.math.Vector2(s.pos.x, s.pos.y)
                                        m = v.normalize() * 30
                                        move = pygame.math.Vector2(m)
                                        start = v.normalize() * (s.size//2 + 25)# 25 = length of ship
                                        e = pygame.math.Vector2(1,0)
                                        angle = e.angle_to(m)
                                        Ship(pos=pygame.math.Vector2(island_selected[0],island_selected[1])+start, destination=i.pos, move=move, angle=angle, empire_color=s.empire_color)
                                        break
    
    def menu_run(self):
        """Not The mainloop"""
        if Game.quit_game == True:
            return
        running = True
        #pygame.mouse.set_visible(False)
        self.menu = True
        while running:
            if Game.language == "English":
                settings = Menu.menu_e
                descr = Menu.descr_e
            elif Game.language == "German":
                settings = Menu.menu_d
                descr = Menu.descr_d
            #pygame.mixer.music.pause()
            milliseconds = self.clock.tick(self.fps)
            seconds = milliseconds / 1000
            text = settings[Menu.name][Menu.cursor]
            # -------- events ------
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    Game.quit_game = True
                    running = False
                # ------- pressed and released key ------
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return
                        #running = False
                    if event.key == pygame.K_UP:
                        Menu.cursor -= 1
                        Menu.cursor = max(0, Menu.cursor) # not < 0
                        #Viewer.menusound.play()
                    if event.key == pygame.K_DOWN:
                        Menu.cursor += 1
                        Menu.cursor = min(len(settings[Menu.name])-1,Menu.cursor) # not > menu entries
                        #Viewer.menusound.play()
                    if event.key == pygame.K_RETURN:
                        if text == "End the game" or text == "Beenden":
                            Game.quit_game = True
                            running = False
                        elif text in settings:
                            # changing to another menu
                            Menu.history.append(text) 
                            Menu.name = text
                            Menu.cursor = 0
                        elif text == "Play" or text == "Spielen":
                            running = False
                        elif text == "back" or text == "zurück":
                            Menu.history = Menu.history[:-1] # remove last entry
                            Menu.cursor = 0
                            Menu.name = Menu.history[-1] # get last entry
                        elif Menu.name == "Language" or Menu.name == "Sprache":
                            if text == "German" or text == "Deutsch":
                                Game.language = "German"
                                Menu.history = ["main"]
                                Menu.cursor = 0
                                Menu.name = "main"
                                self.menu_run()
                                return
                            elif text == "English" or text == "Englisch":   
                                Game.language = "English"
                                Menu.history = ["main"]
                                Menu.cursor = 0
                                Menu.name = "main"
                                self.menu_run()
                                return
                        elif Menu.name == "Screenresolution" or Menu.name == "Auflösung":
                            # text is something like 800x600
                            t = text.find("x")
                            if t != -1:
                                x = int(text[:t])
                                y = int(text[t+1:])
                                Viewer.width = x
                                Viewer.height = y
                                self.set_screenresolution()
                                self.prepare_sprites()
                        elif Menu.name == "Graphics" or Menu.name == "Grafik":
                            if text == "Ines' design" or text == "Ines Entwurf":
                                Game.graphic = "I"
                                self.load_graphics()
                                self.new_level()
                            elif text == "Julia's design" or text == "Julias Entwurf":
                                Game.graphic = "J"
                                self.load_graphics()
                                self.new_level()
                            elif text == "Julia's design 2" or text == "Julias 2.Entwurf":
                                Game.graphic = "J2"
                                self.load_graphics()
                                self.new_level()
                        elif Menu.name == "Multiplayer" or Menu.name == "Mehrspieler":
                            if text == "Single player" or text == "Einzelspieler":
                                Game.player = 1
                                Game.level = 1
                                self.new_level()
                            elif text == "1 vs. 1":
                                Game.player = 2
                                self.new_level()
                                return
                        elif Menu.name == "Game speed" or Menu.name == "Geschwindigkeit":
                            if text == "Slow" or text == "Langsam":
                                Game.speed = 0.5
                            elif text == "Normal":
                                Game.speed = 1
                            elif text == "Fast" or text == "Schnell":
                                Game.speed = 3
                            elif text == "Really fast" or text == "Sehr schnell":
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
                        elif Menu.name == "Fullscreen" or "Vollbildschirm":
                            if text == "True" or text == "Ja":
                                #Viewer.menucommandsound.play()
                                Viewer.fullscreen = True
                                self.set_screenresolution()
                            elif text == "False" or text == "Nein":
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
            
            pygame.draw.rect(self.screen,(170,170,170),(200,90,350,450))
            pygame.draw.rect(self.screen,(200,200,200),(600,90,350,450))
            pygame.draw.rect(self.screen,(230,230,230),(1000,90,350,450))
            
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
            menu = settings[Menu.name]
            for y, item in enumerate(menu):
                write(self.screen, text=item, x=Viewer.width//2-500, y=100+y*50, color=(255,255,255), fontsize=30)
            # --- cursor ---
            write(self.screen, text="-->", x=Viewer.width//2-600, y=100+ Menu.cursor * 50, color=(0,0,0), fontsize=30)
            # ---- descr ------
            if text in descr:
                lines = structurize_text(descr[text], Menu.linelength)
                for y, line in enumerate(lines):
                    write(self.screen, text=line, x=Viewer.width//2-100, y=100+y*30, color=(255,0,255), fontsize=20)
            elif text[0:6] == "Level ":
                if text[6:] in Levels.levels.keys():
                    try:
                        if Game.language == "English":
                            lines = structurize_text(Levels.levels[text[6:]]["descr_e"],Menu.linelength)
                        elif Game.language == "German":
                            lines = structurize_text(Levels.levels[text[6:]]["descr_d"],Menu.linelength)
                    except:
                        lines = []
                    for y, line in enumerate(lines):
                        write(self.screen, text=line, x=Viewer.width//2-100, y=100+y*30, color=(255,0,255), fontsize=20)
            elif text[0:9] == "Tutorial ":
                t = 0
                lines = []
                for l in Levels.levels.keys():
                    if int(l) <= 0:
                        t += 1
                try:
                    if Game.language == "English":
                        lines = structurize_text(Levels.levels[text[-1]-t]["descr_e"], Menu.linelength)
                    elif Game.language == "German":
                        lines = structurize_text(Levels.levels[text[-1]-t]["descr_d"], Menu.linelength)
                except:
                    lines = []
                for y, line in enumerate(lines):
                    write(self.screen, text=line, x=Viewer.width//2-100, y=100+y*30, color=(255,0,255), fontsize=20)
            elif text[0:8] == "Mission ":
                level = str(int(text[8:])+100)
                if level in Levels.levels.keys():
                    try:
                        if Game.language == "English":
                            lines = structurize_text(Levels.levels[level]["descr_e"],Menu.linelength)
                        elif Game.language == "German":
                            lines = structurize_text(Levels.levels[level]["descr_d"],Menu.linelength)
                    except:
                        lines = []
                    for y, line in enumerate(lines):
                        write(self.screen, text=line, x=Viewer.width//2-100, y=100+y*30, color=(255,0,255), fontsize=20)
           # ---- menu_images -----
            if text in Menu.menu_images:
                Viewer.images[Menu.menu_images[text]] = pygame.transform.scale(Viewer.images[Menu.menu_images[text]], (300, 300))
                self.screen.blit(Viewer.images[Menu.menu_images[text]], (1020,100))
                
            # -------- next frame -------------
            pygame.display.flip()
    
    def levelscreen_run(self):
        """Creates a small window showing informations for the following level/informing about the winner of the last level"""
        if Game.quit_game == True:
            return
        running = True
        oldleft, oldmiddle, oldright  = False, False, False
        if Game.language == "English":
            motivation = random.choice(Game.motivation_e)
        elif Game.language == "German":
            motivation = random.choice(Game.motivation_d)
        while running:
            #if Game.language == "English":
            #    settings = Menu.menu_e
            #    descr = Menu.descr_e
            #elif Game.language == "German":
            #    settings = Menu.menu_d
            #    descr = Menu.descr_d
            #pygame.mixer.music.pause()
            milliseconds = self.clock.tick(self.fps)
            seconds = milliseconds / 1000
            # -------- events ------
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    Game.quit_game = True
                    running = False
                # ------- pressed and released key ------
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.menu_run()
                        return
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
            
            
            boxlength = 100 #How many chars in a row
            pygame.draw.rect(self.screen,(170,170,170),(Viewer.width//10,Viewer.height//10,Viewer.width//1.25,Viewer.height//1.25))
            if self.level_win_screen:
                write(self.screen, text="You won the level!", x=Viewer.width//5, y=Viewer.height//5, color=(0,255,0), fontsize=50)
                pygame.draw.rect(self.screen,(0,200,200),(Viewer.width//2,Viewer.height//1.5,200,50))
                write(self.screen, "Continue", x=Viewer.width//2+10, y=Viewer.height//1.5+10)
                continue_button = [Viewer.width//2,Viewer.height//1.5,200,50]
            elif self.player_win_screen:
                if Game.enemy_ships == 0 and Game.enemy_islands == 0:
                    write(self.screen, text="The green Player wins!", x=Viewer.width//5, y=Viewer.height//5, color=(0,255,0), fontsize=50)
                elif Game.player_ships == 0 and Game.player_islands == 0:
                    write(self.screen, text="The red Player wins!", x=Viewer.width//5, y=Viewer.height//5, color=(0,255,0), fontsize=50)
                pygame.draw.rect(self.screen,(0,200,200),(Viewer.width//2,Viewer.height//1.5,200,50))
                write(self.screen, "Again!", x=Viewer.width//2+10, y=Viewer.height//1.5+10)
                continue_button = [Viewer.width//2,Viewer.height//1.5,200,50]
            elif self.level_lose_screen:
                pygame.draw.rect(self.screen,(0,200,200),(Viewer.width//2,Viewer.height//1.5,200,50))
                continue_button = [Viewer.width//2,Viewer.height//1.5,200,50]
                if Game.language == "English":
                    write(self.screen, text="You lost the level!", x=Viewer.width//5, y=Viewer.height//5, color=(0,255,0), fontsize=50)
                    #try:
                    #print("Game level: ", Game.level)
                    
                    for y, line in enumerate(structurize_text(Levels.levels[Game.level]["hint_e"],boxlength)):
                        write(self.screen, text=line, x=Viewer.width//5, y=Viewer.height//5+50+50*y, color=(0,255,0), fontsize=40)
                    #except:
                    #    for y, line in enumerate(structurize_text(motivation,boxlength)):
                    #        write(self.screen, text=line, x=Viewer.width//5, y=Viewer.height//5+50+50*y, color=(0,255,0), fontsize=40)
                    write(self.screen, "Try again", x=Viewer.width//2+10, y=Viewer.height//1.5+10)
                elif Game.language == "German":
                    write(self.screen, text="Du hast verloren!", x=Viewer.width//5, y=Viewer.height//5, color=(0,255,0), fontsize=50)
                    try:
                        for y, line in enumerate(structurize_text(Levels.levels[Game.level]["hint_d"],boxlength)):
                            write(self.screen, text=line, x=Viewer.width//5, y=Viewer.height//5+50+50*y, color=(0,255,0), fontsize=40)
                    except:
                        for y, line in enumerate(structurize_text(motivation,boxlength)):
                            write(self.screen, text=line, x=Viewer.width//5, y=Viewer.height//5+50+50*y, color=(0,255,0), fontsize=40)
                    write(self.screen, "Erneut versuchen", x=Viewer.width//2+10, y=Viewer.height//1.5+10)
            elif self.level_draw_screen:
                write(self.screen, text="No one wins!", x=Viewer.width//5, y=Viewer.height//5, color=(0,255,0), fontsize=50)
                pygame.draw.rect(self.screen,(0,200,200),(Viewer.width//2,Viewer.height//1.5,200,50))
                write(self.screen, "Play again", x=Viewer.width//2+10, y=Viewer.height//1.5+10)
                continue_button = [Viewer.width//2,Viewer.height//1.5,200,50]
                
            pygame.draw.rect(self.screen,(0,200,200),(Viewer.width//2-250,Viewer.height//1.5,210,50))
            write(self.screen, "Return to menu", x=Viewer.width//2-240, y=Viewer.height//1.5+10)
            return_button = [Viewer.width//2-250,Viewer.height//1.5,210,50]
            
            left,middle,right = pygame.mouse.get_pressed()
            if oldleft and not left:
                mouse_pos = pygame.mouse.get_pos()
                if mouse_pos[0] >= continue_button[0] and mouse_pos[0] <= (continue_button[0]+continue_button[2]):
                    if mouse_pos[1] >= continue_button[1] and mouse_pos[1] <= (continue_button[1]+continue_button[3]):
                        print("Next level!")
                        if self.level_win_screen or self.player_win_screen:
                            Game.level += 1
                        self.new_level()
                        running = False
                if mouse_pos[0] >= return_button[0] and mouse_pos[0] <= (return_button[0]+return_button[2]):
                    if mouse_pos[1] >= return_button[1] and mouse_pos[1] <= (return_button[1]+return_button[3]):
                        print("Menu!")
                        self.menu_run()
                        running = False
            #pygame.draw.rect(self.screen,(230,230,230),(1000,90,350,450))
            
            
            
            self.flytextgroup.draw(self.screen)
            
            oldleft, oldmiddle, oldright = left, middle, right
            
            # -------- next frame -------------
            pygame.display.flip()

    
    def run(self):
        """The mainloop"""
        if Game.quit_game == True:
            return
        running = True
        Viewer.fullscreen = True
        self.set_screenresolution()
        #pygame.mouse.set_visible(False)
        oldleft, oldmiddle, oldright  = False, False, False
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
                    if event.key == pygame.K_m:
                        self.menu_run()
                    if Game.player == 2:
                        if event.key == pygame.K_SPACE:  #Mouse 1 click
                            for i in Game.islandgroup:
                                dist = distance((i.pos[0],i.pos[1]), (self.mouse1.x,-self.mouse1.y))
                                if dist < i.size/2:
                                    self.island_selected_1 = [i.pos[0],i.pos[1],i.size]
                                    break
                                else:
                                    self.island_selected_1 = []
                        if event.key == pygame.K_LSHIFT:
                            self.send_ship((self.mouse1.x,self.mouse1.y), self.island_selected_1, Game.player_color)
                        if event.key == pygame.K_RCTRL:  #Mouse 2 click
                            for i in Game.islandgroup:
                                dist = distance((i.pos[0],i.pos[1]), (self.mouse2.x,-self.mouse2.y))
                                if dist < i.size/2:
                                    self.island_selected_2 = [i.pos[0],i.pos[1],i.size]
                                    break
                                else:
                                    self.island_selected_2 = []
                        if event.key == pygame.K_RSHIFT:
                            self.send_ship((self.mouse2.x, self.mouse2.y), self.island_selected_2, (255,0,0))
                    else:
                        if event.key == pygame.K_RIGHT:
                            Game.speed += 0.5
                        elif event.key == pygame.K_LEFT:
                            Game.speed -= 0.5
                            Game.speed = max(0,Game.speed)
                            if Game.speed == 0:
                                Flytext(x=Viewer.width//2,y=Viewer.height//2, text="Game paused", color=(0,0,0))
            # delete everything on screen
            self.screen.blit(self.background, (0, 0))  # macht alles weiß

            # ------------ pressed keys ------
            pressed_keys = pygame.key.get_pressed()

            # write text below sprites
            write(self.screen, "FPS: {:8.3}".format(
                self.clock.get_fps() ), x=10, y=10)
            write(self.screen, "Wood = {}".format(Game.player_wood_int), x=10,y=30)
            write(self.screen, "Iron = {}".format(Game.player_iron_int), x=10,y=50)
            write(self.screen, "Ships = {:.0f}".format(Game.player_ships), x=10,y=80)
            level = Game.level
            if level <= 0:
                for l in Levels.levels.keys():
                    if int(l) <= 0:
                        level += 1
                write(self.screen, "Tutorial {}".format(level), x=1280, y=30)
            else:
                write(self.screen, "Level {}".format(level), x=1280, y=30)

            self.allgroup.update(seconds)
            
            # -------------- write explanations for the current level on the screen ------------------
            #if str(Game.level) in Levels.levels.keys():
            try:
                if Game.language == "English":
                    lines = structurize_text(Levels.levels[str(Game.level)]["descr_e"],70)
                elif Game.language == "German":
                    lines = structurize_text(Levels.levels[str(Game.level)]["descr_d"],70)
            except:
                lines = []
            for y, line in enumerate(lines):
                write(self.screen, line, x=200, y=50+y*25)

            self.update_gamevariables()
            # ------------------win or lose --------------------
            #if self.end_gametime < self.playtime:
            #    if self.newlevel == True:
            #        self.newlevel = False
            #        Game.level += 1
            #        self.new_level()
            ##    elif self.end_game == True:
             #       break
            if Game.gamemode == "Conquer":
                if Game.enemy_ships == 0 and Game.enemy_islands == 0:
                    if Game.player == 1:
                        #Flytext(x = Viewer.width//2, y = Viewer.height//2, text = "You won the level!", fontsize=30, color=Game.player_color)
                        self.level_win_screen = True
                        self.levelscreen_run()
                    elif Game.player == 2:
                        #Flytext(x = Viewer.width//2, y = Viewer.height//2, text = "The green player wins!", fontsize=30, color=Game.player_color)
                        self.player_win_screen = True
                        self.levelscreen_run()
                elif Game.player_ships == 0 and Game.player_islands == 0:
                    if Game.player == 1:
                        #Flytext(x = Viewer.width//2, y = Viewer.height//2, text = "You lose!", fontsize=70, color=random.choice(Game.enemy_color))
                        self.level_lose_screen = True
                        self.levelscreen_run()
                    elif Game.player == 2:
                        #Flytext(x = Viewer.width//2, y = Viewer.height//2, text = "The red player wins!", fontsize=70, color=random.choice(Game.enemy_color))
                        self.player_win_screen = True
                        self.levelscreen_run()
                elif Game.player_ships == 0 and Game.enemy_ships == 0:
                    if (Game.player_island_types[2] == 0 and Game.player_wood < 5) or (Game.player_island_types[3] == 0 and Game.player_iron < 5) or Game.player_island_types[1] == 0:
                        if (Game.enemy_island_types[2] == 0 and Game.enemy1_wood < 5) or (Game.enemy_island_types[3] == 0 and Game.enemy1_iron < 5) or Game.enemy_island_types[1] == 0:
                            #Flytext(x = Viewer.width//2, y = Viewer.height//2, text = "No one wins!", fontsize=30, color=(0,0,0))
                            self.level_draw_screen = True
                            self.levelscreen_run()
            elif Game.gamemode == "Defend":
                print(Game.player_island_types[0])
                if Game.player_island_types[0] == 0:
                    #Flytext(x = Viewer.width//2, y = Viewer.height//2, text = "You lost your island!", fontsize=30, color=random.choice(Game.enemy_color))
                    #self.end_gametime = self.playtime + 2
                    self.level_lose_screen = True
                    self.levelscreen_run()
            #elif Game.gamemode == "Collect":
                
            # ------------------ click on island ---------------
            if Game.player == 1:
                left,middle,right = pygame.mouse.get_pressed()
                if oldright and not right:
                    mouse_pos = pygame.mouse.get_pos()
                    for i in Game.islandgroup:
                        dist = distance((i.pos[0],i.pos[1]), (mouse_pos[0],-mouse_pos[1]))
                        if dist < i.size/2:
                            self.island_selected_1 = [i.pos[0],i.pos[1],i.size]
                            break
                        else:
                            self.island_selected_1 = []
                # -------------- send ship ----------------
                if oldleft and not left:
                    mouse_pos = pygame.mouse.get_pos()
                    self.send_ship(mouse_pos, self.island_selected_1, Game.player_color)
                
                oldleft, oldmiddle, oldright = left, middle, right
                
            if self.island_selected_1:
                pygame.draw.circle(self.screen, (100,100,100), (int(self.island_selected_1[0]),-int(self.island_selected_1[1])), self.island_selected_1[2]//2+25)
            if self.island_selected_2:
                pygame.draw.circle(self.screen, (100,100,100), (int(self.island_selected_2[0]),-int(self.island_selected_2[1])), self.island_selected_2[2]//2+25)
                
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
