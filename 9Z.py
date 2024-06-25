'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
#############################################################################
 ____   ____  ________  _______     ______   _____   ___   ____  _____  
|_  _| |_  _||_   __  ||_   __ \  .' ____ \ |_   _|.'   `.|_   \|_   _| 
  \ \   / /    | |_ \_|  | |__) | | (___ \_|  | | /  .-.  \ |   \ | |   
   \ \ / /     |  _| _   |  __ /   _.____`.   | | | |   | | | |\ \| |   
    \ ' /     _| |__/ | _| |  \ \_| \____) | _| |_\  `-'  /_| |_\   |_  
     \_/     |________||____| |___|\______.'|_____|`.___.'|_____|\____| 

  __        ____       ____    
 /  |     .'    '.   .'    '.  
 `| |    |  .--.  | |  .--.  | 
  | |    | |    | | | |    | | 
 _| |_  _|  `--'  |_|  `--'  | 
|_____|(_)'.____.'(_)'.____.'  
                               
#############################################################################
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''


from pygame import *
from random import randint
from time import sleep as wait
from math import ceil
import numpy
import webbrowser
import json

save = dict()
with open('save.json',encoding='utf-8') as data:
    save = json.load(data)
    data.close()
    
def saveData():
    with open('save.json','w',encoding='utf-8') as file:
        json.dump(save,file)

winx = 900
winy = 900

pixel = winx/9

difficulty = 'easy'
rest = 60
wavelength = 40
exp = 1
intervals = 0

counter = 0
gametime = 0

state = 'title'
gamestate = 'resting'
game = True

mixer.init()
soundClick = mixer.Sound('sounds/sfx/click.wav')
soundPlay = mixer.Sound('sounds/sfx/play.wav')
soundHit = mixer.Sound('sounds/sfx/hit.wav')
soundPlace = mixer.Sound('sounds/sfx/place.wav')
soundShoot = mixer.Sound('sounds/sfx/shoot.wav')
soundDie = mixer.Sound('sounds/sfx/die.wav')

mixer.set_num_channels(8)
musicTitleScreen = mixer.Sound('sounds/music/titleScreen.wav')
musicMainGame = mixer.Sound('sounds/music/mainGame.wav')
mixer.Channel(7).play(musicTitleScreen,-1,fade_ms=1000)

window = display.set_mode((winx,winy))
display.set_caption('9Z')

tiles = []
solids = []
breakables = []
structures = []
shootable = []
grasses = []
traps = []
zombies = []
bullets = []
walls = []

transitions = list()

transitions2 = list()
t2trans1 = 0
t2trans2 = 0

woodnum = 0
stonenum = 0
diamondnum = 0

wave = 1

class tile(sprite.Sprite):
    def __init__(self,X,Y,w,h,col,trans,remove=False):
        self.w = w
        self.h = h
        self.x = X
        self.y = Y
        self.rect = Rect(0,0,self.w,self.h)
        self.colour = col
        self.ogcolour = col
        self.transparency = trans
        self.surface = Surface((w,h))
        self.surface.set_alpha(trans)
        self.build = True
        if not remove:
            tiles.append(self)
    def draw(self):
        global window
        draw.rect(self.surface,self.colour,self.rect)
        self.surface.set_alpha(self.transparency)
        window.blit(self.surface,(self.x,self.y))
    def scroll(self,movement,direction='v'):
        if direction == 'h':
            self.x += movement
        else:
            self.y += movement
    def checkCollision(self,obj):
        return Rect.colliderect(self.rect,obj)
    
class mountain(tile):
    def __init__(self,X,Y,w,h,col,trans,remove=False):
        super().__init__(X,Y,w,h,col,trans,remove)
        solids.append(self)
        self.build = False

class water(tile):
    def __init__(self,X,Y,w,h,col,trans,remove=False):
        super().__init__(X,Y,w,h,col,trans,remove)
        solids.append(self)

class wood(tile):
    def __init__(self,X,Y,w,h,col,trans,remove=False):
        super().__init__(X,Y,w,h,col,trans,remove)
        breakables.append(self)
        self.health = 100
    def displayHealth(self):
        if self.health <= 0:
            global woodnum
            woodnum += 4
            breakables.remove(self)
            self.ogcolour = (randint(0,50),randint(150,255),randint(0,100))
            self.colour = self.ogcolour
            grasses.append(self)
        else:
            qwey = list(self.ogcolour)
            for i in range(len(qwey)): 
                qwey[i] *= self.health/100
            self.colour = tuple(qwey)

class woodWall(tile):
    def __init__(self,X,Y,w,h,col,trans,parent,remove=False):
        super().__init__(X,Y,w,h,col,trans,remove)
        structures.append(self)
        solids.append(self)
        walls.append(self)
        breakables.append(self)
        self.health = 100
        self.parent = parent
        grasses.remove(self.parent)
    def displayHealth(self):
        if self.health <= 0:
            breakables.remove(self)
            tiles.remove(self)
            solids.remove(self)
            structures.remove(self)
            grasses.append(self.parent)
        else:
            qwey = list(self.ogcolour)
            for i in range(len(qwey)): 
                qwey[i] *= self.health/100
            self.colour = tuple(qwey)
    def die(self):
        for i in bullets:
            if i.x == self.x and i.y == self.y:
                bullets.remove(i)
                tiles.remove(i)

class woodHalfWall(tile):
    def __init__(self,X,Y,w,h,col,trans,parent,remove=False):
        super().__init__(X,Y,w,h,col,trans,remove)
        structures.append(self)
        solids.append(self)
        shootable.append(self)
        breakables.append(self)
        self.health = 50
        self.parent = parent
        grasses.remove(self.parent)
    def displayHealth(self):
        if self.health <= 0:
            breakables.remove(self)
            tiles.remove(self)
            solids.remove(self)
            structures.remove(self)
            shootable.remove(self)
            grasses.append(self.parent)
        else:
            qwey = list(self.ogcolour)
            for i in range(len(qwey)): 
                qwey[i] *= self.health/50
            self.colour = tuple(qwey)

class stone(tile):
    def __init__(self,X,Y,w,h,col,trans,remove=False):
        super().__init__(X,Y,w,h,col,trans,remove)
        breakables.append(self)
        self.health = 200
    def displayHealth(self):
        if self.health <= 0:
            global stonenum
            stonenum += 4
            breakables.remove(self)
            self.ogcolour = (randint(0,50),randint(150,255),randint(0,100))
            self.colour = self.ogcolour
            grasses.append(self)
        else:
            qwey = list(self.ogcolour)
            for i in range(len(qwey)): 
                qwey[i] *= self.health/200
            self.colour = tuple(qwey)

class stoneWall(tile):
    def __init__(self,X,Y,w,h,col,trans,parent,remove=False):
        super().__init__(X,Y,w,h,col,trans,remove)
        structures.append(self)
        solids.append(self)
        walls.append(self)
        breakables.append(self)
        self.health = 200
        self.parent = parent
        grasses.remove(self.parent)
    def displayHealth(self):
        if self.health <= 0:
            breakables.remove(self)
            tiles.remove(self)
            solids.remove(self)
            structures.remove(self)
            grasses.append(self.parent)
        else:
            qwey = list(self.ogcolour)
            for i in range(len(qwey)): 
                qwey[i] *= self.health/200
            self.colour = tuple(qwey)
    def die(self):
        for i in bullets:
            if i.x == self.x and i.y == self.y:
                bullets.remove(i)
                tiles.remove(i)

class stoneHalfWall(tile):
    def __init__(self,X,Y,w,h,col,trans,parent,remove=False):
        super().__init__(X,Y,w,h,col,trans,remove)
        structures.append(self)
        solids.append(self)
        shootable.append(self)
        breakables.append(self)
        self.health = 100
        self.parent = parent
        grasses.remove(self.parent)
    def displayHealth(self):
        if self.health <= 0:
            breakables.remove(self)
            tiles.remove(self)
            solids.remove(self)
            structures.remove(self)
            shootable.remove(self)
            grasses.append(self.parent)
        else:
            qwey = list(self.ogcolour)
            for i in range(len(qwey)): 
                qwey[i] *= self.health/100
            self.colour = tuple(qwey)

class stoneTrap(tile):
    def __init__(self,X,Y,w,h,col,trans,parent,remove=False):
        super().__init__(X,Y,w,h,col,trans,remove)
        structures.append(self)
        traps.append(self)
        breakables.append(self)
        self.health = 150
        self.parent = parent
        grasses.remove(self.parent)
    def displayHealth(self):
        if self.health <= 0:
            breakables.remove(self)
            tiles.remove(self)
            traps.remove(self)
            structures.remove(self)
            grasses.append(self.parent)
        else:
            qwey = list(self.ogcolour)
            for i in range(len(qwey)): 
                qwey[i] *= self.health/150
            self.colour = tuple(qwey)
    def hurt(self):
        for i in zombies:
            if i.x == self.x and i.y == self.y:
                soundHit.play()
                self.health -= 10
                i.health -= 50

class diamond(tile):
    def __init__(self,X,Y,w,h,col,trans,remove=False):
        super().__init__(X,Y,w,h,col,trans,remove)
        breakables.append(self)
        self.health = 300
    def displayHealth(self):
        if self.health <= 0:
            global diamondnum
            diamondnum += 4
            breakables.remove(self)
            self.ogcolour = (randint(0,50),randint(150,255),randint(0,100))
            self.colour = self.ogcolour
            grasses.append(self)
        else:
            qwey = list(self.ogcolour)
            for i in range(len(qwey)): 
                qwey[i] *= self.health/300
            self.colour = tuple(qwey)

class diamondWall(tile):
    def __init__(self,X,Y,w,h,col,trans,parent,remove=False):
        super().__init__(X,Y,w,h,col,trans,remove)
        structures.append(self)
        solids.append(self)
        walls.append(self)
        breakables.append(self)
        self.health = 300
        self.parent = parent
        grasses.remove(self.parent)
    def displayHealth(self):
        if self.health <= 0:
            breakables.remove(self)
            tiles.remove(self)
            solids.remove(self)
            structures.remove(self)
            grasses.append(self.parent)
        else:
            qwey = list(self.ogcolour)
            for i in range(len(qwey)): 
                qwey[i] *= self.health/300
            self.colour = tuple(qwey)
    def die(self):
        for i in bullets:
            if i.x == self.x and i.y == self.y:
                bullets.remove(i)
                tiles.remove(i)

class diamondHalfWall(tile):
    def __init__(self,X,Y,w,h,col,trans,parent,remove=False):
        super().__init__(X,Y,w,h,col,trans,remove)
        structures.append(self)
        solids.append(self)
        shootable.append(self)
        breakables.append(self)
        self.health = 150
        self.parent = parent
        grasses.remove(self.parent)
    def displayHealth(self):
        if self.health <= 0:
            breakables.remove(self)
            tiles.remove(self)
            solids.remove(self)
            structures.remove(self)
            shootable.remove(self)
            grasses.append(self.parent)
        else:
            qwey = list(self.ogcolour)
            for i in range(len(qwey)): 
                qwey[i] *= self.health/150
            self.colour = tuple(qwey)

class diamondTrap(tile):
    def __init__(self,X,Y,w,h,col,trans,parent,remove=False):
        super().__init__(X,Y,w,h,col,trans,remove)
        structures.append(self)
        traps.append(self)
        breakables.append(self)
        self.health = 225
        self.parent = parent
        grasses.remove(self.parent)
    def displayHealth(self):
        if self.health <= 0:
            breakables.remove(self)
            tiles.remove(self)
            traps.remove(self)
            structures.remove(self)
            grasses.append(self.parent)
        else:
            qwey = list(self.ogcolour)
            for i in range(len(qwey)): 
                qwey[i] *= self.health/225
            self.colour = tuple(qwey)
    def hurt(self):
        for i in zombies:
            if i.x == self.x and i.y == self.y:
                soundHit.play()
                self.health -= 10
                i.health -= 80

class player(tile):
    def __init__(self,X,Y,w,h,col,trans,remove=False):
        super().__init__(X,Y,w,h,col,trans,remove)
        self.health = 100
        self.ogcolour = col
        self.hitboxes = []
        self.breaking = False
        self.building = False
        self.mcd = 0
        self.dir = 'up'
    def move(self):
        keysPressed = key.get_pressed()
        if (keysPressed[K_a]):
            self.dir = 'left'
        if (keysPressed[K_d]):
            self.dir = 'right'
        if (keysPressed[K_w]):
            self.dir = 'up'
        if (keysPressed[K_s]):
            self.dir = 'down'
        if self.mcd < 10:
            return
        self.mcd = 0
        global tiles
        if (keysPressed[K_a]):
            if not self.breaking and not self.building:
                collided = False
                leftBox = Rect((pixel*4.5)-pixel,pixel*4.5,30,30)
                self.hitboxes.append(leftBox)
                for i in solids:
                    collided = Rect.colliderect(i.surface.get_rect(topleft=(i.x,i.y)),leftBox) or collided
                #self.showHitboxes()
                for i in tiles:
                    if not collided:
                        i.scroll(pixel*1,'h')
                    else:
                        break
                self.hitboxes.remove(leftBox)
            elif self.breaking and not self.building:
                collided = False
                leftBox = Rect((pixel*4.5)-pixel,pixel*4.5,30,30)
                for i in breakables:
                    collided = Rect.colliderect(i.surface.get_rect(topleft=(i.x,i.y)),leftBox) or collided
                    if collided:
                        soundHit.play()
                        i.health -= 10
                        break
        if (keysPressed[K_d]):
            if not self.breaking and not self.building: 
                collided = False
                rightBox = Rect((pixel*4.5)+pixel,pixel*4.5,30,30)
                self.hitboxes.append(rightBox)
                for i in solids:
                    collided = Rect.colliderect(i.surface.get_rect(topleft=(i.x,i.y)),rightBox) or collided
                #self.showHitboxes()
                for i in tiles:
                    if not collided:
                        i.scroll(pixel*-1,'h')
                    else:
                        break
                self.hitboxes.remove(rightBox)
            elif self.breaking and not self.building:
                collided = False
                rightBox = Rect((pixel*4.5)+pixel,pixel*4.5,30,30)
                for i in breakables:
                    collided = Rect.colliderect(i.surface.get_rect(topleft=(i.x,i.y)),rightBox) or collided
                    if collided:
                        soundHit.play()
                        i.health -= 10
                        break
        if (keysPressed[K_w]):
            if not self.breaking and not self.building:
                collided = False
                upBox = Rect((pixel*4.5),(pixel*4.5)-pixel,30,30)
                self.hitboxes.append(upBox)
                for i in solids:
                    collided = Rect.colliderect(i.surface.get_rect(topleft=(i.x,i.y)),upBox) or collided
                #self.showHitboxes()
                for i in tiles:
                    if not collided:
                        i.scroll(pixel*1)
                    else:
                        break
                self.hitboxes.remove(upBox)
            elif self.breaking and not self.building:
                collided = False
                upBox = Rect((pixel*4.5),(pixel*4.5)-pixel,30,30)
                for i in breakables:
                    collided = Rect.colliderect(i.surface.get_rect(topleft=(i.x,i.y)),upBox) or collided
                    if collided:
                        soundHit.play()
                        i.health -= 10
                        break
        if (keysPressed[K_s]):
            if not self.breaking and not self.building:
                collided = False
                downBox = Rect((pixel*4.5),(pixel*4.5)+pixel,30,30)
                self.hitboxes.append(downBox)
                for i in solids:
                    collided = Rect.colliderect(i.surface.get_rect(topleft=(i.x,i.y)),downBox) or collided
                #self.showHitboxes()
                for i in tiles:
                    if not collided:
                        i.scroll(pixel*-1)
                    else:
                        break
                self.hitboxes.remove(downBox)
            elif self.breaking and not self.building:
                collided = False
                downBox = Rect((pixel*4.5),(pixel*4.5)+pixel,30,30)
                for i in breakables:
                    collided = Rect.colliderect(i.surface.get_rect(topleft=(i.x,i.y)),downBox) or collided
                    if collided:
                        soundHit.play()
                        i.health -= 10
                        break
    def destroy(self):
        keysPressed = key.get_pressed()
        hey1 = Surface((0,0))
        hey2 = Surface((0,0))
        hey3 = Surface((0,0))
        hey4 = Surface((0,0))
        if (keysPressed[K_q]) and not self.building:
            self.breaking = True
            hey1 = Surface((pixel,pixel))
            hey2 = Surface((pixel,pixel))
            hey3 = Surface((pixel,pixel))
            hey4 = Surface((pixel,pixel))
        else:
            self.breaking = False
        
        draw.rect(hey1,(255,0,0),Rect(0,0,pixel,pixel))
        hey1.set_alpha(170)
        window.blit(hey1,(pixel*3,pixel*4))
        draw.rect(hey2,(255,0,0),Rect(0,0,pixel,pixel))
        hey2.set_alpha(170)
        window.blit(hey2,(pixel*5,pixel*4))
        draw.rect(hey3,(255,0,0),Rect(0,0,pixel,pixel))
        hey3.set_alpha(170)
        window.blit(hey3,(pixel*4,pixel*3))
        draw.rect(hey4,(255,0,0),Rect(0,0,pixel,pixel))
        hey4.set_alpha(170)
        window.blit(hey4,(pixel*4,pixel*5))
    def create(self,ev):
        keysPressed = key.get_pressed()
        
        if (keysPressed[K_b]):
            self.building = True

            global woodnum
            global stonenum
            global diamondnum
            
            inv1 = Rect(0,pixel*8,pixel,pixel)
            inv2 = Rect(pixel,pixel*8,pixel,pixel)
            inv3 = Rect(pixel*2,pixel*8,pixel,pixel)

            col1t = list((75,75,0))
            for i in range(len(col1t)):
                if woodnum < 10:
                    col1t[i] *= woodnum/12
            col1 = tuple(col1t)
            col2t = list((100,100,100))
            for i in range(len(col2t)):
                if stonenum < 10:
                    col2t[i] *= stonenum/12
            col2 = tuple(col2t)
            col3t = list((0,200,255))
            for i in range(len(col3t)):
                if diamondnum < 10:
                    col3t[i] *= diamondnum/12
            col3 = tuple(col3t)
            
            draw.rect(window,col1,inv1)
            draw.rect(window,col2,inv2)
            draw.rect(window,col3,inv3)

            disp1 = Rect(pixel*8,pixel*8,pixel,pixel)

            dangerLevel = (0,255,0)
            if gamestate == 'danger':
                dangerLevel = (255,0,0)
            
            draw.rect(window,dangerLevel,disp1)

            leave = Rect(0,0,pixel,pixel)
            draw.rect(window,(255,255,255),leave)

            for e in ev:
                if e.type == MOUSEBUTTONDOWN:
                    x,y = mouse.get_pos()
                    if (x > 0 and y > 0) and (x < (pixel) and y < (pixel)):
                        gameOver()
            
            build1 = Rect(pixel*3,pixel*3,pixel,pixel)
            c1 = (0,0,0)
            if woodnum >= 2:
                c1 = (125,125,20)
            build2 = Rect(pixel*4,pixel*3,pixel,pixel)
            c2 = (0,0,0)
            if woodnum >= 1:
                c2 = (200,200,50)
            build3 = Rect(pixel*5,pixel*3,pixel,pixel)
            c3 = (0,0,0)
            if stonenum >= 2:
                c3 = (175,175,175)
            build4 = Rect(pixel*5,pixel*4,pixel,pixel)
            c4 = (0,0,0)
            if stonenum >= 1:
                c4 = (225,225,225)
            build5 = Rect(pixel*5,pixel*5,pixel,pixel)
            c5 = (0,0,0)
            if diamondnum >= 2:
                c5 = (100,150,255)
            build6 = Rect(pixel*4,pixel*5,pixel,pixel)
            c6 = (0,0,0)
            if diamondnum >= 1:
                c6 = (0,255,255)
            build7 = Rect(pixel*3,pixel*5,pixel,pixel)
            c7 = (0,0,0)
            if stonenum >= 3:
                c7 = (225,90,0)
            build8 = Rect(pixel*3,pixel*4,pixel,pixel)
            c8 = (0,0,0)
            if diamondnum >= 3:
                c8 = (160,0,255)

            if (keysPressed[K_1]) and c1 != (0,0,0):
                draw.rect(window,c1,build2)
                draw.rect(window,c1,build4)
                draw.rect(window,c1,build6)
                draw.rect(window,c1,build8)
                if (keysPressed[K_w]):
                    canplace = False
                    parentTile = None
                    for i in tiles:
                        if i.x == pixel*4 and i.y == pixel*3 and i in grasses:
                            canplace = True
                            parentTile = i
                            break
                    if canplace:
                        struct = woodWall(pixel*4,pixel*3,pixel,pixel,c1,255,parentTile)
                        woodnum -= 2
                        soundPlace.play()
                elif (keysPressed[K_a]):
                    canplace = False
                    parentTile = None
                    for i in tiles:
                        if i.x == pixel*3 and i.y == pixel*4 and i in grasses:
                            canplace = True
                            parentTile = i
                            break
                    if canplace:
                        struct = woodWall(pixel*3,pixel*4,pixel,pixel,c1,255,parentTile)
                        woodnum -= 2
                        soundPlace.play()
                elif (keysPressed[K_d]):
                    canplace = False
                    parentTile = None
                    for i in tiles:
                        if i.x == pixel*5 and i.y == pixel*4 and i in grasses:
                            canplace = True
                            parentTile = i
                            break
                    if canplace:
                        struct = woodWall(pixel*5,pixel*4,pixel,pixel,c1,255,parentTile)
                        woodnum -= 2
                        soundPlace.play()
                elif (keysPressed[K_s]):
                    canplace = False
                    parentTile = None
                    for i in tiles:
                        if i.x == pixel*4 and i.y == pixel*5 and i in grasses:
                            canplace = True
                            parentTile = i
                            break
                    if canplace:
                        struct = woodWall(pixel*4,pixel*5,pixel,pixel,c1,255,parentTile)
                        woodnum -= 2
                        soundPlace.play()
            elif (keysPressed[K_2]) and c2 != (0,0,0):
                draw.rect(window,c2,build2)
                draw.rect(window,c2,build4)
                draw.rect(window,c2,build6)
                draw.rect(window,c2,build8)
                if (keysPressed[K_w]):
                    canplace = False
                    parentTile = None
                    for i in tiles:
                        if i.x == pixel*4 and i.y == pixel*3 and i in grasses:
                            canplace = True
                            parentTile = i
                            break
                    if canplace:
                        struct = woodHalfWall(pixel*4,pixel*3,pixel,pixel,c2,255,parentTile)
                        woodnum -= 1
                        soundPlace.play()
                elif (keysPressed[K_a]):
                    canplace = False
                    parentTile = None
                    for i in tiles:
                        if i.x == pixel*3 and i.y == pixel*4 and i in grasses:
                            canplace = True
                            parentTile = i
                            break
                    if canplace:
                        struct = woodHalfWall(pixel*3,pixel*4,pixel,pixel,c2,255,parentTile)
                        woodnum -= 1
                        soundPlace.play()
                elif (keysPressed[K_d]):
                    canplace = False
                    parentTile = None
                    for i in tiles:
                        if i.x == pixel*5 and i.y == pixel*4 and i in grasses:
                            canplace = True
                            parentTile = i
                            break
                    if canplace:
                        struct = woodHalfWall(pixel*5,pixel*4,pixel,pixel,c2,255,parentTile)
                        woodnum -= 1
                        soundPlace.play()
                elif (keysPressed[K_s]):
                    canplace = False
                    parentTile = None
                    for i in tiles:
                        if i.x == pixel*4 and i.y == pixel*5 and i in grasses:
                            canplace = True
                            parentTile = i
                            break
                    if canplace:
                        struct = woodHalfWall(pixel*4,pixel*5,pixel,pixel,c2,255,parentTile)
                        woodnum -= 1
                        soundPlace.play()
            elif (keysPressed[K_3]) and c3 != (0,0,0):
                draw.rect(window,c3,build2)
                draw.rect(window,c3,build4)
                draw.rect(window,c3,build6)
                draw.rect(window,c3,build8)
                if (keysPressed[K_w]):
                    canplace = False
                    parentTile = None
                    for i in tiles:
                        if i.x == pixel*4 and i.y == pixel*3 and i in grasses:
                            canplace = True
                            parentTile = i
                            break
                    if canplace:
                        struct = stoneWall(pixel*4,pixel*3,pixel,pixel,c3,255,parentTile)
                        stonenum -= 2
                        soundPlace.play()
                elif (keysPressed[K_a]):
                    canplace = False
                    parentTile = None
                    for i in tiles:
                        if i.x == pixel*3 and i.y == pixel*4 and i in grasses:
                            canplace = True
                            parentTile = i
                            break
                    if canplace:
                        struct = stoneWall(pixel*3,pixel*4,pixel,pixel,c3,255,parentTile)
                        stonenum -= 2
                        soundPlace.play()
                elif (keysPressed[K_d]):
                    canplace = False
                    parentTile = None
                    for i in tiles:
                        if i.x == pixel*5 and i.y == pixel*4 and i in grasses:
                            canplace = True
                            parentTile = i
                            break
                    if canplace:
                        struct = stoneWall(pixel*5,pixel*4,pixel,pixel,c3,255,parentTile)
                        stonenum -= 2
                        soundPlace.play()
                elif (keysPressed[K_s]):
                    canplace = False
                    parentTile = None
                    for i in tiles:
                        if i.x == pixel*4 and i.y == pixel*5 and i in grasses:
                            canplace = True
                            parentTile = i
                            break
                    if canplace:
                        struct = stoneWall(pixel*4,pixel*5,pixel,pixel,c3,255,parentTile)
                        stonenum -= 2
                        soundPlace.play()
            elif (keysPressed[K_4]) and c4 != (0,0,0):
                draw.rect(window,c4,build2)
                draw.rect(window,c4,build4)
                draw.rect(window,c4,build6)
                draw.rect(window,c4,build8)
                if (keysPressed[K_w]):
                    canplace = False
                    parentTile = None
                    for i in tiles:
                        if i.x == pixel*4 and i.y == pixel*3 and i in grasses:
                            canplace = True
                            parentTile = i
                            break
                    if canplace:
                        struct = stoneHalfWall(pixel*4,pixel*3,pixel,pixel,c4,255,parentTile)
                        stonenum -= 1
                        soundPlace.play()
                elif (keysPressed[K_a]):
                    canplace = False
                    parentTile = None
                    for i in tiles:
                        if i.x == pixel*3 and i.y == pixel*4 and i in grasses:
                            canplace = True
                            parentTile = i
                            break
                    if canplace:
                        struct = stoneHalfWall(pixel*3,pixel*4,pixel,pixel,c4,255,parentTile)
                        stonenum -= 1
                        soundPlace.play()
                elif (keysPressed[K_d]):
                    canplace = False
                    parentTile = None
                    for i in tiles:
                        if i.x == pixel*5 and i.y == pixel*4 and i in grasses:
                            canplace = True
                            parentTile = i
                            break
                    if canplace:
                        struct = stoneHalfWall(pixel*5,pixel*4,pixel,pixel,c4,255,parentTile)
                        stonenum -= 1
                        soundPlace.play()
                elif (keysPressed[K_s]):
                    canplace = False
                    parentTile = None
                    for i in tiles:
                        if i.x == pixel*4 and i.y == pixel*5 and i in grasses:
                            canplace = True
                            parentTile = i
                            break
                    if canplace:
                        struct = stoneHalfWall(pixel*4,pixel*5,pixel,pixel,c4,255,parentTile)
                        stonenum -= 1
                        soundPlace.play()
            elif (keysPressed[K_5]) and c5 != (0,0,0):
                draw.rect(window,c5,build2)
                draw.rect(window,c5,build4)
                draw.rect(window,c5,build6)
                draw.rect(window,c5,build8)
                if (keysPressed[K_w]):
                    canplace = False
                    parentTile = None
                    for i in tiles:
                        if i.x == pixel*4 and i.y == pixel*3 and i in grasses:
                            canplace = True
                            parentTile = i
                            break
                    if canplace:
                        struct = diamondWall(pixel*4,pixel*3,pixel,pixel,c5,255,parentTile)
                        diamondnum -= 2
                        soundPlace.play()
                elif (keysPressed[K_a]):
                    canplace = False
                    parentTile = None
                    for i in tiles:
                        if i.x == pixel*3 and i.y == pixel*4 and i in grasses:
                            canplace = True
                            parentTile = i
                            break
                    if canplace:
                        struct = diamondWall(pixel*3,pixel*4,pixel,pixel,c5,255,parentTile)
                        diamondnum -= 2
                        soundPlace.play()
                elif (keysPressed[K_d]):
                    canplace = False
                    parentTile = None
                    for i in tiles:
                        if i.x == pixel*5 and i.y == pixel*4 and i in grasses:
                            canplace = True
                            parentTile = i
                            break
                    if canplace:
                        struct = diamondWall(pixel*5,pixel*4,pixel,pixel,c5,255,parentTile)
                        diamondnum -= 2
                        soundPlace.play()
                elif (keysPressed[K_s]):
                    canplace = False
                    parentTile = None
                    for i in tiles:
                        if i.x == pixel*4 and i.y == pixel*5 and i in grasses:
                            canplace = True
                            parentTile = i
                            break
                    if canplace:
                        struct = diamondWall(pixel*4,pixel*5,pixel,pixel,c5,255,parentTile)
                        diamondnum -= 2
                        soundPlace.play()
            elif (keysPressed[K_6]) and c6 != (0,0,0):
                draw.rect(window,c6,build2)
                draw.rect(window,c6,build4)
                draw.rect(window,c6,build6)
                draw.rect(window,c6,build8)
                if (keysPressed[K_w]):
                    canplace = False
                    parentTile = None
                    for i in tiles:
                        if i.x == pixel*4 and i.y == pixel*3 and i in grasses:
                            canplace = True
                            parentTile = i
                            break
                    if canplace:
                        struct = diamondHalfWall(pixel*4,pixel*3,pixel,pixel,c6,255,parentTile)
                        diamondnum -= 1
                        soundPlace.play()
                elif (keysPressed[K_a]):
                    canplace = False
                    parentTile = None
                    for i in tiles:
                        if i.x == pixel*3 and i.y == pixel*4 and i in grasses:
                            canplace = True
                            parentTile = i
                            break
                    if canplace:
                        struct = diamondHalfWall(pixel*3,pixel*4,pixel,pixel,c6,255,parentTile)
                        diamondnum -= 1
                        soundPlace.play()
                elif (keysPressed[K_d]):
                    canplace = False
                    parentTile = None
                    for i in tiles:
                        if i.x == pixel*5 and i.y == pixel*4 and i in grasses:
                            canplace = True
                            parentTile = i
                            break
                    if canplace:
                        struct = diamondHalfWall(pixel*5,pixel*4,pixel,pixel,c6,255,parentTile)
                        diamondnum -= 1
                        soundPlace.play()
                elif (keysPressed[K_s]):
                    canplace = False
                    parentTile = None
                    for i in tiles:
                        if i.x == pixel*4 and i.y == pixel*5 and i in grasses:
                            canplace = True
                            parentTile = i
                            break
                    if canplace:
                        struct = diamondHalfWall(pixel*4,pixel*5,pixel,pixel,c6,255,parentTile)
                        diamondnum -= 1
                        soundPlace.play()
            elif (keysPressed[K_7]) and c7 != (0,0,0):
                draw.rect(window,c7,build2)
                draw.rect(window,c7,build4)
                draw.rect(window,c7,build6)
                draw.rect(window,c7,build8)
                if (keysPressed[K_w]):
                    canplace = False
                    parentTile = None
                    for i in tiles:
                        if i.x == pixel*4 and i.y == pixel*3 and i in grasses:
                            canplace = True
                            parentTile = i
                            break
                    if canplace:
                        struct = stoneTrap(pixel*4,pixel*3,pixel,pixel,c7,255,parentTile)
                        stonenum -= 3
                        soundPlace.play()
                elif (keysPressed[K_a]):
                    canplace = False
                    parentTile = None
                    for i in tiles:
                        if i.x == pixel*3 and i.y == pixel*4 and i in grasses:
                            canplace = True
                            parentTile = i
                            break
                    if canplace:
                        struct = stoneTrap(pixel*3,pixel*4,pixel,pixel,c7,255,parentTile)
                        stonenum -= 3
                        soundPlace.play()
                elif (keysPressed[K_d]):
                    canplace = False
                    parentTile = None
                    for i in tiles:
                        if i.x == pixel*5 and i.y == pixel*4 and i in grasses:
                            canplace = True
                            parentTile = i
                            break
                    if canplace:
                        struct = stoneTrap(pixel*5,pixel*4,pixel,pixel,c7,255,parentTile)
                        stonenum -= 3
                        soundPlace.play()
                elif (keysPressed[K_s]):
                    canplace = False
                    parentTile = None
                    for i in tiles:
                        if i.x == pixel*4 and i.y == pixel*5 and i in grasses:
                            canplace = True
                            parentTile = i
                            break
                    if canplace:
                        struct = stoneTrap(pixel*4,pixel*5,pixel,pixel,c7,255,parentTile)
                        stonenum -= 3
                        soundPlace.play()
            elif (keysPressed[K_8]) and c8 != (0,0,0):
                draw.rect(window,c8,build2)
                draw.rect(window,c8,build4)
                draw.rect(window,c8,build6)
                draw.rect(window,c8,build8)
                if (keysPressed[K_w]):
                    canplace = False
                    parentTile = None
                    for i in tiles:
                        if i.x == pixel*4 and i.y == pixel*3 and i in grasses:
                            canplace = True
                            parentTile = i
                            break
                    if canplace:
                        struct = diamondTrap(pixel*4,pixel*3,pixel,pixel,c8,255,parentTile)
                        diamondnum -= 3
                        soundPlace.play()
                elif (keysPressed[K_a]):
                    canplace = False
                    parentTile = None
                    for i in tiles:
                        if i.x == pixel*3 and i.y == pixel*4 and i in grasses:
                            canplace = True
                            parentTile = i
                            break
                    if canplace:
                        struct = diamondTrap(pixel*3,pixel*4,pixel,pixel,c8,255,parentTile)
                        diamondnum -= 3
                        soundPlace.play()
                elif (keysPressed[K_d]):
                    canplace = False
                    parentTile = None
                    for i in tiles:
                        if i.x == pixel*5 and i.y == pixel*4 and i in grasses:
                            canplace = True
                            parentTile = i
                            break
                    if canplace:
                        struct = diamondTrap(pixel*5,pixel*4,pixel,pixel,c8,255,parentTile)
                        diamondnum -= 3
                        soundPlace.play()
                elif (keysPressed[K_s]):
                    canplace = False
                    parentTile = None
                    for i in tiles:
                        if i.x == pixel*4 and i.y == pixel*5 and i in grasses:
                            canplace = True
                            parentTile = i
                            break
                    if canplace:
                        struct = diamondTrap(pixel*4,pixel*5,pixel,pixel,c8,255,parentTile)
                        diamondnum -= 3
                        soundPlace.play()
            else:
                draw.rect(window,c1,build1)
                draw.rect(window,c2,build2)
                draw.rect(window,c3,build3)
                draw.rect(window,c4,build4)
                draw.rect(window,c5,build5)
                draw.rect(window,c6,build6)
                draw.rect(window,c7,build7)
                draw.rect(window,c8,build8)
        else:
            self.building = False
    def shoot(self):
        if self.mcd < 10:
            return
        keysPressed = key.get_pressed()
        if (keysPressed[K_SPACE]):
            soundShoot.play()
            bul = bullet(self.x,self.y,pixel,pixel,(255,255,0),255,self)
    def displayHealth(self):
        if self.health <= 0:
            soundDie.play()
            gameOver()
        else:
            qwey = list(self.ogcolour)
            for i in range(len(qwey)): 
                qwey[i] *= self.health/100
            self.colour = tuple(qwey)
    def showHitboxes(self):
        for i in self.hitboxes:
            draw.rect(window,(255,0,0),i)
    def cooldowns(self):
        self.mcd += 1

class bullet(tile):
    def __init__(self,X,Y,w,h,col,trans,parent,remove=False):
        super().__init__(X,Y,w,h,col,trans,remove)
        self.orientation = parent.dir
        bullets.append(self)
    def move(self):
        if self.orientation == 'up':
            self.y -= pixel
        elif self.orientation == 'down':
            self.y += pixel
        elif self.orientation == 'left':
            self.x -= pixel
        elif self.orientation == 'right':
            self.x += pixel
        if self.x < 0 or self.x > 1000 or self.y < 0 or self.y > 1000:
            bullets.remove(self)
            tiles.remove(self)

class zombie(tile):
    def __init__(self,X,Y,w,h,col,trans,remove=False):
        super().__init__(X,Y,w,h,col,trans,remove)
        self.health = 100
        self.ogcolour = col
        zombies.append(self)
        solids.append(self)
        self.mcd = 0
        self.hitboxes = []
    def move(self,target):
        if self.mcd < 60:
            return
        self.mcd = 0
        solidical = zombies + [target] + structures
        for i in traps:
            solidical.remove(i)
        if self.x > target.x:
            collided = False
            leftBox = Rect((self.x+30)-(pixel/2),(self.y+30),30,30)
            self.hitboxes.append(leftBox)
            #self.showHitboxes()
            self.hitboxes.remove(leftBox)
            collidedWith = None
            for i in solidical:
                if i == self:
                    continue
                collided = Rect.colliderect(i.surface.get_rect(topleft=(i.x,i.y)),leftBox) or collided
                if collided:
                    collidedWith = i
                    break
            if not collided:
                self.x -= pixel
            elif not collidedWith in zombies:
                try:
                    collidedWith.health -= 10
                    soundHit.play()
                    if collidedWith in walls:
                        self.health -= 20
                except:
                    pass
        if self.x < target.x:
            collided = False
            rightBox = Rect((self.x+30)+(pixel/2),(self.y+30),30,30)
            self.hitboxes.append(rightBox)
            #self.showHitboxes()
            self.hitboxes.remove(rightBox)
            collidedWith = None
            for i in solidical:
                if i == self:
                    continue
                collided = Rect.colliderect(i.surface.get_rect(topleft=(i.x,i.y)),rightBox) or collided
                if collided:
                    collidedWith = i
                    break
            if not collided:
                self.x += pixel
            elif not collidedWith in zombies:
                try:
                    collidedWith.health -= 10
                    soundHit.play()
                    if collidedWith in walls:
                        self.health -= 20
                except:
                    pass
        if self.y > target.y:
            collided = False
            upBox = Rect((self.x+30),(self.y+30)-(pixel/2),30,30)
            self.hitboxes.append(upBox)
            #self.showHitboxes()
            self.hitboxes.remove(upBox)
            collidedWith = None
            for i in solidical:
                if i == self:
                    continue
                collided = Rect.colliderect(i.surface.get_rect(topleft=(i.x,i.y)),upBox) or collided
                if collided:
                    collidedWith = i
                    break
            if not collided:
                self.y -= pixel
            elif not collidedWith in zombies:
                try:
                    collidedWith.health -= 10
                    soundHit.play()
                    if collidedWith in walls:
                        self.health -= 20
                except:
                    pass
        if self.y < target.y:
            collided = False
            downBox = Rect((self.x+30),(self.y+30)+(pixel/2),30,30)
            self.hitboxes.append(downBox)
            #self.showHitboxes()
            self.hitboxes.remove(downBox)
            collidedWith = None
            for i in solidical:
                if i == self:
                    continue
                collided = Rect.colliderect(i.surface.get_rect(topleft=(i.x,i.y)),downBox) or collided
                if collided:
                    collidedWith = i
                    break
            if not collided:
                self.y += pixel
            elif not collidedWith in zombies:
                try:
                    collidedWith.health -= 10
                    soundHit.play()
                    if collidedWith in walls:
                        self.health -= 20
                except:
                    pass
    def die(self):
        for i in bullets:
            if i.x == self.x and i.y == self.y:
                bullets.remove(i)
                tiles.remove(i)
                self.health -= 10
                soundHit.play()
    def displayHealth(self):
        if self.health <= 0:
            zombies.remove(self)
            tiles.remove(self)
            solids.remove(self)
        else:
            qwey = list(self.ogcolour)
            for i in range(len(qwey)): 
                qwey[i] *= self.health/100
            self.colour = tuple(qwey)
    def cooldowns(self):
        self.mcd += 1
    def showHitboxes(self):
        for i in self.hitboxes:
            draw.rect(window,(0,0,255),i,2)
        
def decodeMatrix(matrix):
    tiles.clear()
    for i in range(len(matrix)-1):
        for j in range(len(matrix[i])):
            if state == 'playing':
                if matrix[i][j] != ():
                    if matrix[i][j] == (50,50,50):
                        pix = mountain(pixel*(j-(len(matrix[i])//2)),pixel*(i-(len(matrix)//2)),pixel,pixel,matrix[i][j],255,False)
                    elif matrix[i][j] == (0,100,255):
                        pix = water(pixel*(j-(len(matrix[i])//2)),pixel*(i-(len(matrix)//2)),pixel,pixel,matrix[i][j],255,False)
                    elif matrix[i][j] == (75,75,10):
                        pix = wood(pixel*(j-(len(matrix[i])//2)),pixel*(i-(len(matrix)//2)),pixel,pixel,matrix[i][j],255,False)
                    elif matrix[i][j] == (100,100,100):
                        pix = stone(pixel*(j-(len(matrix[i])//2)),pixel*(i-(len(matrix)//2)),pixel,pixel,matrix[i][j],255,False)
                    elif matrix[i][j] == (0,200,255):
                        pix = diamond(pixel*(j-(len(matrix[i])//2)),pixel*(i-(len(matrix)//2)),pixel,pixel,matrix[i][j],255,False)
                    else:
                        pix = tile(pixel*(j-(len(matrix[i])//2)),pixel*(i-(len(matrix)//2)),pixel,pixel,matrix[i][j],255)
                else:
                    if matrix[len(matrix)-1] == 'green':
                        pix = tile(pixel*(j-(len(matrix[i])//2)),pixel*(i-(len(matrix)//2)),pixel,pixel,(randint(0,50),randint(150,255),randint(0,100)),255)
                        grasses.append(pix)
                    elif matrix[len(matrix)-1] == 'grey':
                        pix = tile(pixel*(j-(len(matrix[i])//2)),pixel*(i-(len(matrix)//2)),pixel,pixel,(randint(40,50),randint(40,50),randint(40,50)),255)
            else:
                if matrix[i][j] != ():
                    pix = tile(pixel*(j),pixel*(i),pixel,pixel,matrix[i][j],255)
                else:
                    if matrix[len(matrix)-1] == 'green':
                        pix = tile(pixel*(j),pixel*(i),pixel,pixel,(randint(0,50),randint(150,255),randint(0,100)),255)
                    elif matrix[len(matrix)-1] == 'grey':
                        pix = tile(pixel*(j),pixel*(i),pixel,pixel,(randint(40,50),randint(40,50),randint(40,50)),255)

def generateMatrix(y,x):
    matrix = numpy.zeros((y,x)).tolist()
    for i in range(len(matrix)):
        for j in range(len(matrix[i])):
            if j == 0 or j == len(matrix[i])-1 or i == 0 or i == len(matrix)-1:
                matrix[i][j] = (50,50,50)
            elif not matrix[i][j] == (50,50,50):
                matrix[i][j] = ()
            else:
                matrix[i][j] = ()
    matrix.append('green')
    return matrix

def generateWater(matrix,amount,size):
    for i in range(amount):
        y,x = randint(0,len(matrix)-2),randint(0,len(matrix[1])-1)
        for somanyloops in range(size):
            for j in range(3):
                for v in range(3):
                    try:
                        if matrix[y+j-1][x+v-1] == ():
                            matrix[y+j-1][x+v-1] = (0,100,255)
                    except:
                        pass
            y += randint(-1,1)
            x += randint(-1,1)

def generateResources(matrix,amount):
    for i in range(amount):
        y,x = randint(0,len(matrix)-2),randint(0,len(matrix[1])-1)
        try:
            if matrix[y][x] == ():
                yo = randint(1,100)
                if yo < 50:
                    matrix[y][x] = (75,75,10)
                elif yo < 85:
                    matrix[y][x] = (100,100,100)
                else:
                    matrix[y][x] = (0,200,255)
        except:
            pass

def clearMiddle():
    for i in tiles:
        if i.x > 299 and i.x < 501 and i.y > 299 and i.y < 501:
            i.colour = (randint(0,50),randint(150,255),randint(0,100))
            try:
                breakables.remove(i)
            except:
                pass
            try:
                solids.remove(i)
            except:
                pass
            grasses.append(i)
            
def createPlayArea():
    global gameEmpty
    sizey = randint(36,80)
    sizex = randint(36,80)
    matrix = generateMatrix(sizey,sizex)
    stuff = (sizey * sizex)//100
    generateWater(matrix,stuff,stuff//2)
    generateResources(matrix,stuff*10)
    
    decodeMatrix(matrix)
    clearMiddle()

def startingTransition(speed):
    global transitions
    transitions.clear()
    player.displayHealth()
    for i in range(9):
        for j in range(9):
            pix = tile(pixel*j,pixel*i,pixel,pixel,(0,0,0),255,True)
            transitions.append(pix)
            for v in transitions:
                v.draw()
            display.update()
            wait(speed)
def startingTransitionEnd(speed):
    global transitions
    for i in range(81):
        for j in tiles:
            j.draw()
        player.draw()
        for v in transitions:
            v.draw()
        display.update()
        transitions.remove(transitions[0])
        wait(speed/2)
        
def endingTransition(speed):
    global transitions
    transitions.clear()
    w = wave
    for i in range(9):
        for j in range(9):
            col = (255,100,100)
            if w > 0:
                col = (100,255,100)
            pix = tile(pixel*j,pixel*i,pixel,pixel,col,255,True)
            w -= 1
            transitions.append(pix)
            player.draw()
            for v in transitions:
                v.draw()
            display.update()
            wait(speed)
def endingTransitionEnd(speed):
    global transitions
    for i in range(81):
        for j in tiles:
            j.draw()
        for v in transitions:
            v.draw()
        display.update()
        transitions.remove(transitions[0])
        wait(speed/2)

def waveStart(const):
    global waveStartTransition
    global t2trans1
    if t2trans1 <= 0:
        t2trans1 = 0
        return
    for i in range(len(waveStartTransition)):
        for j in range(len(waveStartTransition[i])):
            if waveStartTransition[i][j] == None:
                continue
            pix = tile(pixel*j,pixel*i,pixel,pixel,waveStartTransition[i][j],t2trans1,True)
            transitions2.append(pix)
    for i in transitions2:
        i.draw()
    t2trans1 -= const
    transitions2.clear()
def waveEnd(const):
    global waveEndTransition
    global t2trans2
    if t2trans2 <= 0:
        t2trans2 = 0
        return
    for i in range(len(waveStartTransition)):
        for j in range(len(waveStartTransition[i])):
            if waveStartTransition[i][j] == None:
                continue
            pix = tile(pixel*j,pixel*i,pixel,pixel,waveEndTransition[i][j],t2trans2,True)
            transitions2.append(pix)
    for i in transitions2:
        i.draw()
    t2trans2 -= const
    transitions2.clear()

def spawnZombie():
    posx,posy = randint(-10,10)*100,randint(-10,10)*100
    ran = randint(1,4)
    if ran == 1:
        posx = -1000
    elif ran == 2:
        posx = 1000
    elif ran == 3:
        posy = -1000
    elif ran == 4:
        posy = 1000
    z = zombie(posx,posy,pixel,pixel,(255,0,0),255)

def spawnZombies(amount):
    for i in range(amount):
        spawnZombie()

def stepGameState():
    global gametime
    global gamestate
    global wavelength
    global rest
    global intervals
    global wave
    global t2trans1
    global t2trans2
    gametime += 1
    print(gametime)
    if gametime // rest == 1:
        if gamestate == 'resting':
            gamestate = 'danger'
            t2trans1 = 255
            gametime = 0
    if gametime // wavelength == 1:
        if gamestate == 'danger':
            gamestate = 'resting'
            t2trans2 = 255
            gametime = 0
            wave += 1
    if gamestate == 'danger':
        intervals = 11
        if gametime % intervals == 0 and gametime < 33:
            spawnZombies(ceil(pow(wave,exp)/intervals))

def gameOver():
    global gametime
    global woodnum
    global stonenum
    global diamondnum
    global state
    global wave
    global difficulties

    mixer.Channel(7).fadeout(250)
    
    gametime = 0
    tiles.clear()
    solids.clear()
    breakables.clear()
    structures.clear()
    shootable.clear()
    grasses.clear()
    traps.clear()
    zombies.clear()
    bullets.clear()
    walls.clear()

    transitions.clear()

    woodnum = 0
    stonenum = 0
    diamondnum = 0

    if wave > 9:
        if difficulty == 'easy':
            save['difficultiesUnlocked']['medium'] = True
        if difficulty == 'medium':
            save['difficultiesUnlocked']['hard'] = True
        if difficulty == 'hard':
            save['difficultiesUnlocked']['insane'] = True
        if difficulty == 'insane':
            save['difficultiesUnlocked']['impossible'] = True

    saveData()

    difficulties = [
        [(),(),(),(),(),(),(),(),(),],
        [(),(),(),(0,255,0),(0,255,0),(0,255,0),(),(),(),],
        [(),(),(),(),(),(),(),(),(),],]
    if save['difficultiesUnlocked']['medium']:
        difficulties += [
            [(),(),(),(255,255,0),(255,255,0),(255,255,0),(),(),(),],
            [(),(),(),(),(),(),(),(),(),],]
    else:
        difficulties += [
            [(),(),(),(0,0,0),(0,0,0),(0,0,0),(),(),(),],
            [(),(),(),(),(),(),(),(),(),],]
    if save['difficultiesUnlocked']['hard']:
        difficulties += [
            [(),(),(),(255,0,0),(255,0,0),(255,0,0),(),(),(),],
            [(),(),(),(),(),(),(),(),(),],]
    else:
        difficulties += [
            [(),(),(),(0,0,0),(0,0,0),(0,0,0),(),(),(),],
            [(),(),(),(),(),(),(),(),(),],]
    if save['difficultiesUnlocked']['insane']:
        difficulties += [
            [(),(),(),(200,0,255),(200,0,255),(200,0,255),(),(),(),],
            [(),(),(),(),(),(),(),(),(),],
            'grey',]
    else:
        difficulties += [
            [(),(),(),(0,0,0),(0,0,0),(0,0,0),(),(),(),],
            [(),(),(),(),(),(),(),(),(),],'grey']

    soundDie.play()
    
    endingTransition(0.005)
    state = 'title'
    decodeMatrix(titlescreen)
    wait(1)
    endingTransitionEnd(0.005)
    mixer.Channel(7).play(musicTitleScreen,-1,fade_ms=1000)
    player.health = 100

    wave = 1
    
clock = time.Clock()
FPS = 60

player = player(pixel*4,pixel*4,pixel,pixel,(225,225,190),255,True)

waveEndTransition = [
    [(0,255,0),(0,255,0),(0,255,0),(0,255,0),(0,255,0),(0,255,0),(0,255,0),(0,255,0),(0,255,0),],
    [(0,255,0),None,None,None,None,None,None,None,(0,255,0),],
    [(0,255,0),None,None,None,None,None,None,None,(0,255,0),],
    [(0,255,0),None,None,None,None,None,None,None,(0,255,0),],
    [(0,255,0),None,None,None,None,None,None,None,(0,255,0),],
    [(0,255,0),None,None,None,None,None,None,None,(0,255,0),],
    [(0,255,0),None,None,None,None,None,None,None,(0,255,0),],
    [(0,255,0),None,None,None,None,None,None,None,(0,255,0),],
    [(0,255,0),(0,255,0),(0,255,0),(0,255,0),(0,255,0),(0,255,0),(0,255,0),(0,255,0),(0,255,0),],
    ]

waveStartTransition = [
    [(255,0,0),(255,0,0),(255,0,0),(255,0,0),(255,0,0),(255,0,0),(255,0,0),(255,0,0),(255,0,0),],
    [(255,0,0),None,None,None,None,None,None,None,(255,0,0),],
    [(255,0,0),None,None,None,None,None,None,None,(255,0,0),],
    [(255,0,0),None,None,None,None,None,None,None,(255,0,0),],
    [(255,0,0),None,None,None,None,None,None,None,(255,0,0),],
    [(255,0,0),None,None,None,None,None,None,None,(255,0,0),],
    [(255,0,0),None,None,None,None,None,None,None,(255,0,0),],
    [(255,0,0),None,None,None,None,None,None,None,(255,0,0),],
    [(255,0,0),(255,0,0),(255,0,0),(255,0,0),(255,0,0),(255,0,0),(255,0,0),(255,0,0),(255,0,0),],
    ]

titlescreen = [
    [(0,0,0),(0,0,0),(100,100,100),(100,100,100),(0,0,0),(0,0,0),(100,100,100),(100,100,100),(0,0,0),],
    [(100,100,100),(100,100,100),(),(0,0,0),(0,0,0),(),(100,100,100),(),(0,0,0),],
    [(),(),(),(),(),(),(),(),(),],
    [(),(),(),(255,255,0),(255,255,0),(255,255,0),(),(),(),],
    [(),(),(),(),(),(),(),(),(),],
    [(),(),(),(255,0,0),(255,0,0),(255,0,0),(),(),(),],
    [(),(),(),(),(),(),(),(),(),],
    [(),(),(),(0,0,255),(0,0,255),(0,0,255),(),(0,0,0),(0,0,0),],
    [(),(),(),(),(),(),(),(0,0,0),(),],
    'green',
    ]

difficulties = [
    [(),(),(),(),(),(),(),(),(),],
    [(),(),(),(0,255,0),(0,255,0),(0,255,0),(),(),(),],
    [(),(),(),(),(),(),(),(),(),],]
if save['difficultiesUnlocked']['medium']:
    difficulties += [
        [(),(),(),(255,255,0),(255,255,0),(255,255,0),(),(),(),],
        [(),(),(),(),(),(),(),(),(),],]
else:
    difficulties += [
        [(),(),(),(0,0,0),(0,0,0),(0,0,0),(),(),(),],
        [(),(),(),(),(),(),(),(),(),],]
if save['difficultiesUnlocked']['hard']:
    difficulties += [
        [(),(),(),(255,0,0),(255,0,0),(255,0,0),(),(),(),],
        [(),(),(),(),(),(),(),(),(),],]
else:
    difficulties += [
        [(),(),(),(0,0,0),(0,0,0),(0,0,0),(),(),(),],
        [(),(),(),(),(),(),(),(),(),],]
if save['difficultiesUnlocked']['insane']:
    difficulties += [
        [(),(),(),(200,0,255),(200,0,255),(200,0,255),(),(),(),],
        [(),(),(),(),(),(),(),(),(),],
        'grey',]
else:
    difficulties += [
        [(),(),(),(0,0,0),(0,0,0),(0,0,0),(),(),(),],
        [(),(),(),(),(),(),(),(),(),],'grey']

decodeMatrix(titlescreen)

difficultyDisplay = tile(800,800,100,100,(0,255,0),255,True)

while game:
    counter += 1
    window.fill((50,50,50))
    if counter == 60 and state == 'playing':
        stepGameState()
        for i in traps:
            i.hurt()
    ev = event.get()

    for i in breakables:
        i.displayHealth()
    
    for i in tiles:
        i.draw()

    for i in structures:
        if i in zombies:
            continue
        i.draw()   
        try:
            i.die()
        except:
            pass
        
    for i in bullets:
        i.draw()
        if counter % 3 == 0:
            i.move()
    
    if state == 'playing':
        player.destroy()
        player.create(ev)
        player.shoot()
        player.move()
        player.cooldowns()
        player.displayHealth()
        player.draw()
        for i in zombies:
            i.die()
            i.displayHealth()
            i.move(player)
            i.cooldowns()
            i.showHitboxes()
            i.draw()
    elif state == 'title':
        difficultyDisplay.draw()

    waveStart(5)
    waveEnd(5)
    
    display.update()

    for e in ev:
        if e.type == QUIT:
            game = False
        if state == 'title':
            if e.type == MOUSEBUTTONDOWN:
                x,y = mouse.get_pos()
                if (x > (pixel)*3 and y > (pixel)*3) and (x < (pixel)*6 and y < (pixel)*4):
                    soundPlay.play()
                    mixer.Channel(7).fadeout(250)
                    startingTransition(0.005)
                    state = 'playing'
                    createPlayArea()
                    mixer.Channel(7).play(musicMainGame,-1,fade_ms=1000)
                    startingTransitionEnd(0.005)
                if (x > (pixel)*3 and y > (pixel)*5) and (x < (pixel)*6 and y < (pixel)*6):
                    decodeMatrix(difficulties)
                    state = 'difficulties'
                    soundClick.play()
                if (x > (pixel)*3 and y > (pixel)*7) and (x < (pixel)*6 and y < (pixel)*8):
                    soundClick.play()
                    webbrowser.open('https://github.com/fijianfugufish/9Z/blob/main/how%20to%20play.md')
        elif state == 'difficulties':
            if e.type == MOUSEBUTTONDOWN:
                x,y = mouse.get_pos()
                if save['difficultiesUnlocked']['easy'] and (x > (pixel)*3 and y > (pixel)) and (x < (pixel)*6 and y < (pixel)*2):
                    decodeMatrix(titlescreen)
                    state = 'title'
                    difficulty = 'easy'
                    soundClick.play()
                    rest = 60
                    wavelength = 40
                    exp = 1
                    difficultyDisplay.colour = (0,255,0)
                if save['difficultiesUnlocked']['medium'] and  (x > (pixel)*3 and y > (pixel)*3) and (x < (pixel)*6 and y < (pixel)*4):
                    decodeMatrix(titlescreen)
                    state = 'title'
                    difficulty = 'medium'
                    soundClick.play()
                    rest = 50
                    wavelength = 40
                    exp = 2
                    difficultyDisplay.colour = (255,255,0)
                if save['difficultiesUnlocked']['hard'] and  (x > (pixel)*3 and y > (pixel)*5) and (x < (pixel)*6 and y < (pixel)*6):
                    decodeMatrix(titlescreen)
                    state = 'title'
                    difficulty = 'hard'
                    soundClick.play()
                    rest = 40
                    wavelength = 40
                    exp = 3
                    difficultyDisplay.colour = (255,0,0)
                if save['difficultiesUnlocked']['insane'] and  (x > (pixel)*3 and y > (pixel)*7) and (x < (pixel)*6 and y < (pixel)*8):
                    decodeMatrix(titlescreen)
                    state = 'title'
                    difficulty = 'insane'
                    soundClick.play()
                    rest = 30
                    wavelength = 40
                    exp = 4
                    difficultyDisplay.colour = (200,0,255)

    clock.tick(FPS)

    display.update()
    if counter > 60:
        counter = 0
    
quit()
