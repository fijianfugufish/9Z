from pygame import *
from random import randint
import numpy

winx = 900
winy = 900

pixel = winx/9

difficulty = 'easy'

counter = 0

state = 'title'
game = True

window = display.set_mode((winx,winy))
display.set_caption('9Z')

tiles = []
solids = []
breakables = []

woodnum = 0
stonenum = 0
goldnum = 0

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
        else:
            qwey = list(self.ogcolour)
            for i in range(len(qwey)): 
                qwey[i] *= self.health/100
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
        else:
            qwey = list(self.ogcolour)
            for i in range(len(qwey)): 
                qwey[i] *= self.health/200
            self.colour = tuple(qwey)
            
class gold(tile):
    def __init__(self,X,Y,w,h,col,trans,remove=False):
        super().__init__(X,Y,w,h,col,trans,remove)
        breakables.append(self)
        self.health = 300
    def displayHealth(self):
        if self.health <= 0:
            global goldnum
            goldnum += 4
            breakables.remove(self)
            self.ogcolour = (randint(0,50),randint(150,255),randint(0,100))
            self.colour = self.ogcolour
        else:
            qwey = list(self.ogcolour)
            for i in range(len(qwey)): 
                qwey[i] *= self.health/300
            self.colour = tuple(qwey)
            
class player(tile):
    def __init__(self,X,Y,w,h,col,trans,remove=False):
        super().__init__(X,Y,w,h,col,trans,remove)
        self.hitboxes = []
        self.breaking = False
        self.building = False
    def move(self):
        cd = str(counter/10)
        if not ('.0' in cd and len(cd) == 3):
            return
        keysPressed = key.get_pressed()
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
    def create(self):
        keysPressed = key.get_pressed()
        
        if (keysPressed[K_b]):
            self.building = True
            
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
            col3t = list((255,255,0))
            for i in range(len(col3t)):
                if goldnum < 10:
                    col3t[i] *= goldnum/12
            col3 = tuple(col3t)
            
            draw.rect(window,col1,inv1)
            draw.rect(window,col2,inv2)
            draw.rect(window,col3,inv3)

            build1 = Rect(pixel*3,pixel*3,pixel,pixel)
            c1 = (125,125,20)
            build2 = Rect(pixel*4,pixel*3,pixel,pixel)
            c2 = (200,200,50)
            build3 = Rect(pixel*5,pixel*3,pixel,pixel)
            c3 = (175,175,175)
            build4 = Rect(pixel*5,pixel*4,pixel,pixel)
            c4 = (225,225,225)
            build5 = Rect(pixel*5,pixel*5,pixel,pixel)
            c5 = (235,235,0)
            build6 = Rect(pixel*4,pixel*5,pixel,pixel)
            c6 = (255,255,200)

            draw.rect(window,c1,build1)
            draw.rect(window,c2,build2)
            draw.rect(window,c3,build3)
            draw.rect(window,c4,build4)
            draw.rect(window,c5,build5)
            draw.rect(window,c6,build6)
        else:
            self.building = False
    def showHitboxes(self):
        for i in self.hitboxes:
            draw.rect(window,(255,0,0),i)
            
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
                    elif matrix[i][j] == (255,255,0):
                        pix = gold(pixel*(j-(len(matrix[i])//2)),pixel*(i-(len(matrix)//2)),pixel,pixel,matrix[i][j],255,False)
                    else:
                        pix = tile(pixel*(j-(len(matrix[i])//2)),pixel*(i-(len(matrix)//2)),pixel,pixel,matrix[i][j],255)
                else:
                    if matrix[len(matrix)-1] == 'green':
                        pix = tile(pixel*(j-(len(matrix[i])//2)),pixel*(i-(len(matrix)//2)),pixel,pixel,(randint(0,50),randint(150,255),randint(0,100)),255)
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
                    matrix[y][x] = (255,255,0)
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

clock = time.Clock()
FPS = 60

player = player(pixel*4,pixel*4,pixel,pixel,(225,225,190),255,True)

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
    [(),(),(),(),(),(),(),(),(),],
    [(),(),(),(255,255,0),(255,255,0),(255,255,0),(),(),(),],
    [(),(),(),(),(),(),(),(),(),],
    [(),(),(),(255,0,0),(255,0,0),(255,0,0),(),(),(),],
    [(),(),(),(),(),(),(),(),(),],
    [(),(),(),(200,0,255),(200,0,255),(200,0,255),(),(),(),],
    [(),(),(),(),(),(),(),(),(),],
    'grey',
    ]

decodeMatrix(titlescreen)

difficultyDisplay = tile(800,800,100,100,(0,255,0),255,True)

while game:
    counter += 1
    window.fill((50,50,50))

    ev = event.get()

    for i in breakables:
        i.displayHealth()
    
    for i in tiles:
        i.draw()
    
    if state == 'playing':
        player.destroy()
        player.create()
        player.move()
        player.draw()
    elif state == 'title':
        difficultyDisplay.draw()
    
    display.update()

    for e in ev:
        if e.type == QUIT:
            game = False
        if state == 'title':
            if e.type == MOUSEBUTTONDOWN:
                x,y = mouse.get_pos()
                if (x > (pixel)*3 and y > (pixel)*3) and (x < (pixel)*6 and y < (pixel)*4):
                    state = 'playing'
                    createPlayArea()
                if (x > (pixel)*3 and y > (pixel)*5) and (x < (pixel)*6 and y < (pixel)*6):
                    decodeMatrix(difficulties)
                    state = 'difficulties'
        elif state == 'difficulties':
            if e.type == MOUSEBUTTONDOWN:
                x,y = mouse.get_pos()
                if (x > (pixel)*3 and y > (pixel)) and (x < (pixel)*6 and y < (pixel)*2):
                    decodeMatrix(titlescreen)
                    state = 'title'
                    difficulty = 'easy'
                    difficultyDisplay.colour = (0,255,0)
                if (x > (pixel)*3 and y > (pixel)*3) and (x < (pixel)*6 and y < (pixel)*4):
                    decodeMatrix(titlescreen)
                    state = 'title'
                    difficulty = 'medium'
                    difficultyDisplay.colour = (255,255,0)
                if (x > (pixel)*3 and y > (pixel)*5) and (x < (pixel)*6 and y < (pixel)*6):
                    decodeMatrix(titlescreen)
                    state = 'title'
                    difficulty = 'hard'
                    difficultyDisplay.colour = (255,0,0)
                if (x > (pixel)*3 and y > (pixel)*7) and (x < (pixel)*6 and y < (pixel)*8):
                    decodeMatrix(titlescreen)
                    state = 'title'
                    difficulty = 'insane'
                    difficultyDisplay.colour = (200,0,255)

    clock.tick(FPS)

    display.update()
    if counter > 60:
        counter = 0
    
quit()
