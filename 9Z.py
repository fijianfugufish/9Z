from pygame import *
from random import randint

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

class tile(sprite.Sprite):
    def __init__(self,X,Y,w,h,col,trans,remove=False):
        self.w = w
        self.h = h
        self.x = X
        self.y = Y
        self.collisionRect = Rect(0,0,self.w,self.h)
        self.rect = Rect(0,0,w,h)
        self.colour = col
        self.transparency = trans
        self.surface = Surface((w,h))
        self.surface.set_alpha(trans)
        self.solid = False
        if not remove:
            global tiles
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
    
class mountain(tile):
    def __init__(self,X,Y,w,h,col,trans,remove=False):
        super().__init__(X,Y,w,h,col,trans,remove)
        self.solid == True
        
class player(tile):
    def __init__(self,X,Y,w,h,col,trans,remove=False):
        super().__init__(X,Y,w,h,col,trans,remove)
    def move(self):
        cd = str(counter/10)
        if not ('.0' in cd and len(cd) == 3):
            return
        keysPressed = key.get_pressed()
        global tiles
        if (keysPressed[K_a]):
            for i in tiles:
                if not i.solid and not i.collisionRect.collidepoint((pixel*5.5)-pixel,pixel*5.5):
                    i.scroll(pixel*1,'h')
        if (keysPressed[K_d]):
            for i in tiles:
                if not i.solid and not i.collisionRect.collidepoint((pixel*5.5)+pixel,pixel*5.5):
                    i.scroll(pixel*-1,'h')
        if (keysPressed[K_w]):
            for i in tiles:
                if not i.solid and not i.collisionRect.collidepoint((pixel*5.5),(pixel*5.5)-pixel):
                    i.scroll(pixel*1)
        if (keysPressed[K_s]):
            for i in tiles:
                if not i.solid and not i.collisionRect.collidepoint((pixel*5.5),(pixel*5.5)+pixel):
                    i.scroll(pixel*-1)

def decodeMatrix(matrix):
    tiles.clear()
    for i in range(len(matrix)-1):
        for j in range(len(matrix[i])):
            if state == 'playing':
                if matrix[i][j] != ():
                    if matrix[i][j] == (50,50,50):
                        pix = mountain(pixel*(j-(len(matrix[i])//2)),pixel*(i-(len(matrix)//2)),pixel,pixel,matrix[i][j],255)
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
    matrix = []
    section1 = []
    section2 = []
    for i in range(x):
        section1.append((50,50,50))
    section2.append((50,50,50))
    for i in range(x-2):
        section2.append(())
    section2.append((50,50,50))
    matrix.append(section1)
    for i in range(y-2):
        matrix.append(section2)
    matrix.append(section1)
    matrix.append('green')
    return matrix

def createPlayArea():
    matrix = generateMatrix(36,36)

    decodeMatrix(matrix)

clock = time.Clock()
FPS = 60

player = player(400,400,pixel,pixel,(250,250,205),255,True)

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
    window.fill((255,255,255))

    ev = event.get()
    
    for i in tiles:
        i.draw()
    
    if state == 'playing':
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
