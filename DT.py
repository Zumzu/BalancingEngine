import pygame_textinput
import pygame as game
from sys import exit

from Modules.Base import Unit
from Modules.Generator import findGun,findArmour

WIDTH=1429 #actively clean multiples of hexagons native resolution
HEIGHT=789

WOUNDCOLOR=(169,18,1)
GREYWOUNDCOLOR=(200,150,150)
DARKGREY=(30,30,30)

game.init() 

background=game.image.load('DT/Hexagons.png')
background=game.transform.scale(background,(WIDTH,HEIGHT))
screen = game.display.set_mode((WIDTH,HEIGHT)) 
background=background.convert_alpha()
game.display.set_caption("Damage Tracker Mk2")
game.display.set_icon(game.image.load('DT/EngineIco.png'))
monospacedLarge=game.font.SysFont('consolas',30)
monospaced=game.font.SysFont('consolas',20)
monospacedSmall=game.font.SysFont('consolas',15)
  
def updateArrows(events):
    for event in events:
        if event.type == game.KEYDOWN:
            if event.key == game.K_LEFT:
                pressedArrows[0]=True
            elif event.key == game.K_RIGHT:
                pressedArrows[1]=True
            elif event.key == game.K_UP:
                pressedArrows[2]=True
            elif event.key == game.K_DOWN:
                pressedArrows[3]=True

        if event.type == game.KEYUP:
            if event.key == game.K_LEFT:
                pressedArrows[0]=False
            elif event.key == game.K_RIGHT:
                pressedArrows[1]=False
            elif event.key == game.K_UP:
                pressedArrows[2]=False
            elif event.key == game.K_DOWN:
                pressedArrows[3]=False

def fill(surface,rgb):
    w,h = surface.get_size()
    r,g,b = rgb
    for i in range(w):
        for j in range(h):
            surface.set_at((i,j),game.Color(r,g,b,surface.get_at((i,j))[3]))

def frame(x:int,y:int,dx:int,dy:int):
    game.draw.rect(screen, DARKGREY, game.Rect(x,y,dx,dy), border_radius=5)
    game.draw.rect(screen, (180,180,180), game.Rect(x+3,y+3,dx-6,dy-6), border_radius=1)

def inputFrame(x:int,y:int,dx:int,dy:int):
    game.draw.rect(screen, DARKGREY, game.Rect(x,y,dx,dy), border_radius=5)
    game.draw.rect(screen, (220,220,220), game.Rect(x+3,y+3,dx-6,dy-6), border_radius=1)

def buttonFrame(x:int,y:int,dx:int,dy:int,hover:bool):
    game.draw.rect(screen, DARKGREY, game.Rect(x,y,dx,dy), border_radius=5)
    if hover:
        game.draw.rect(screen, (150,150,150), game.Rect(x+3,y+3,dx-6,dy-6), border_radius=1)
    else:
        game.draw.rect(screen, (80,80,80), game.Rect(x+3,y+3,dx-6,dy-6), border_radius=1)

def drawDude(x:int,y:int):
    screen.blit(headImg,(x+76,y+1))
    screen.blit(torsoImg,(x+51,y+60))
    screen.blit(larmImg,(x-1,y+69))
    screen.blit(rarmImg,(x+131,y+76))
    screen.blit(llegImg,(x+23,y+215))
    screen.blit(rlegImg,(x+94,y+213))
    
    drawPointer(x+170,y+150)
    drawPointer(x+135,y+327)
    drawPointer(x+31,y+151,True)
    drawPointer(x+55,y+321,True)

def drawPointer(x:int,y:int,flip:bool=False):
    if flip:
        game.draw.line(screen, (0,0,0), (x,y), (x-30,y-30), 2)
        game.draw.line(screen, (0,0,0), (x-30,y-30), (x-100,y-30), 2)
    else:
        game.draw.line(screen, (0,0,0), (x,y), (x+30,y-30), 2)
        game.draw.line(screen, (0,0,0), (x+30,y-30), (x+100,y-30), 2)

headImg=game.image.load('DT/Body/Head.png').convert_alpha()
torsoImg=game.image.load('DT/Body/Torso.png').convert_alpha()
larmImg=game.image.load('DT/Body/Larm.png').convert_alpha()
rarmImg=game.image.load('DT/Body/Rarm.png').convert_alpha()
llegImg=game.image.load('DT/Body/Lleg.png').convert_alpha()
rlegImg=game.image.load('DT/Body/Rleg.png').convert_alpha()

tempX=0
tempY=0
pressedArrows=[False,False,False,False]

loadTextLabel=monospacedLarge.render("Load",True,(0,0,0))
loadInput=pygame_textinput.TextInputVisualizer()
loadInput.font_object=monospaced
loadInput.manager.validator=(lambda x: len(x)<=21 and str(x).isprintable())
loadSelected=False
loadHitbox=game.Rect(550,42,246,36)
def loadBlit():
    screen.blit(loadTextLabel,(473,45))
    inputFrame(550,42,246,36)
    screen.blit(loadInput.surface,(556,50))

damageTextLabel=monospacedLarge.render("DAMAGE",True,(0,0,0))
damageInput=pygame_textinput.TextInputVisualizer()
damageInput.font_object=monospacedLarge
damageInput.manager.validator=(lambda x: x=='' or (len(x)<=6 and (str(x[-1]).isnumeric() or str(x[-1]).lower()=='d') or x[-1]=='+' or x[-1]=='-'))
damageSelected=False
damageHitbox=game.Rect(506,533,116,46)    
def damageBlit():
    screen.blit(damageTextLabel,(508,503))
    inputFrame(506,533,116,46)
    screen.blit(damageInput.surface,(512,542))

multiplierTextLabel=monospacedLarge.render("X",True,(50,50,50))
multiplierEmptyFieldLabel=monospacedLarge.render("1",True,(50,50,50))
multiplierInput=pygame_textinput.TextInputVisualizer()
multiplierInput.font_object=monospacedLarge
multiplierInput.manager.validator=(lambda x: len(x)<=2 and (str(x).isnumeric() or x==''))
multiplierSelected=False
multiplierHitbox=game.Rect(656,533,40,46)
def multiplierBlit():
    inputFrame(656,533,47,46)
    screen.blit(multiplierTextLabel,(631,543))
    screen.blit(multiplierInput.surface,(663,542))
    if multiplierInput.value=='':
        screen.blit(multiplierEmptyFieldLabel,(663,542))

pewTextLabel=monospaced.render("PEW!",True,(0,0,0))
pewPewTextLabel=monospaced.render("PEW PEW!",True,(0,0,0))
pewHitbox=game.Rect(724,538,100,36)
def pewBlit():
    buttonFrame(724,538,110,36,pewHitbox.collidepoint(game.mouse.get_pos()))
    if multiplierInput.value=='' or multiplierInput.value=='1':
        screen.blit(pewTextLabel,(759,547))
    else:
        screen.blit(pewPewTextLabel,(735,547))


woundTrackText=['LIGHT','SERIOUS','CRITICAL']
for i in range(7):
    woundTrackText.append(f"MORTAL_{i}")

woundTrackLabels=[]
for text in woundTrackText:
    woundTrackLabels.append(monospacedSmall.render(text,True,(0,0,0)))

zeroIconImage=game.image.load('DT/ZeroIco.png')
zeroIconImage=game.transform.scale(zeroIconImage,(26,26)).convert_alpha()
def drawWoundTrack(startX:int,startY:int,endX:int,buffer:int,wounds:int,greyWounds:int):
    wounds=max(0,min(50,wounds))
    boxSize=(endX-startX-buffer*10)/50
    screen.blit(zeroIconImage,(startX-boxSize+buffer//2,startY-3))
    
    offsetX=0
    offsetY=0
    for i in range(10):
        offsetX+=boxSize/2
        if i==5:
            offsetX=-24.5*boxSize
            offsetY=50
            
        rect=woundTrackLabels[i].get_rect(center=(startX+(i+0.5)*5*boxSize+offsetX,startY+offsetY-9))
        screen.blit(woundTrackLabels[i],rect)
        drawWoundSet(startX+i*5*boxSize+offsetX,startY+offsetY,boxSize,wounds,greyWounds)
        if wounds<5:
            greyWounds-=(5-wounds)
        wounds=max(0,wounds-5)

def drawWoundSet(startX:int,startY:int,boxSize:float,wounds:int,greyWounds:int):
    game.draw.line(screen,(0,0,0),(startX,startY),(startX+boxSize*5,startY),2)
    game.draw.line(screen,(0,0,0),(startX,startY+boxSize),(startX+boxSize*5,startY+boxSize),2)
    for i in range(6):
        game.draw.line(screen,(0,0,0),(startX+boxSize*i,startY),(startX+boxSize*i,startY+boxSize),2)
    for i in range(5):
        if i<wounds:
            game.draw.line(screen,WOUNDCOLOR,(startX+boxSize*i+6,startY+3),(startX+boxSize*i+int(boxSize)-5,startY+boxSize-2),8)
            game.draw.line(screen,WOUNDCOLOR,(startX+boxSize*i+6,startY+int(boxSize)-2),(startX+boxSize*i+int(boxSize)-5,startY+3),8)
        elif i<wounds+greyWounds:
            game.draw.line(screen,GREYWOUNDCOLOR,(startX+boxSize*i+6,startY+3),(startX+boxSize*i+int(boxSize)-5,startY+boxSize-2),8)
            game.draw.line(screen,GREYWOUNDCOLOR,(startX+boxSize*i+6,startY+int(boxSize)-2),(startX+boxSize*i+int(boxSize)-5,startY+3),8)

def drawWounds(wounds):
    greyWounds=0
    for i in range(51):
        if woundTrackHitBoxes[i].collidepoint(game.mouse.get_pos()):
            if i>wounds:
                greyWounds=i-wounds
            elif i<wounds:
                greyWounds=wounds-i
                wounds-=greyWounds
            break
    frame(30,645,WIDTH//2-15,HEIGHT-675)
    drawWoundTrack(60,670,WIDTH-150,4,wounds,greyWounds)

def generateWoundHitboxes(startX:int,startY:int,endX:int,buffer:int):
    output=[]
    boxSize=(endX-startX-buffer*10)/50
    output.append(game.Rect((startX-boxSize+buffer//2),startY,boxSize+1,boxSize))
    offsetX=0
    offsetY=0
    for i in range(10):
        offsetX+=boxSize/2
        if i==5:
            offsetX=-24.5*boxSize
            offsetY=50
        for j in range(5):
            output.append(game.Rect((startX+i*5*boxSize+offsetX)+boxSize*j,startY+offsetY,boxSize+1,boxSize))

    return output

woundTrackHitBoxes=generateWoundHitboxes(60,670,WIDTH-150,4)

tempDMG=0

while True: 
    events=game.event.get()
    for event in events: 
        if event.type == game.QUIT: 
            print(round(tempX),"|",round(tempY))
            game.quit()
            exit()

        if event.type == game.MOUSEBUTTONUP:
            loadSelected=loadHitbox.collidepoint(game.mouse.get_pos())
            damageSelected=damageHitbox.collidepoint(game.mouse.get_pos())
            multiplierSelected=multiplierHitbox.collidepoint(game.mouse.get_pos())
            for i in range(51):
                if woundTrackHitBoxes[i].collidepoint(game.mouse.get_pos()):
                    tempDMG=i

        if event.type == game.KEYDOWN and event.key == game.K_RETURN:
            tempDMG+=1 #TEMMPPP _------------------------------------------------------------------------------
            if damageSelected or multiplierSelected:
                print(damageInput.value,'x',multiplierInput.value)

        if event.type == game.KEYDOWN and event.key == game.K_TAB:
            if damageSelected:
                damageSelected=False
                multiplierSelected=True
            elif multiplierSelected:
                multiplierSelected=False
                damageSelected=True


    if loadSelected:
        loadInput.update(events)
    else:
        loadInput.cursor_visible=False

    if damageSelected:
        damageInput.update(events)
        if damageInput.value!='' and damageInput.value[-1]=='d':
            damageInput.value=damageInput.value[:-1]+'D'
    else:
        damageInput.cursor_visible=False

    if multiplierSelected:
        multiplierInput.update(events)
    else:
        multiplierInput.cursor_visible=False
    
        
    updateArrows(events)
    if pressedArrows[0]:
        tempX-=0.2
    if pressedArrows[1]:
        tempX+=0.2
    if pressedArrows[2]:
        tempY-=0.2
    if pressedArrows[3]:
        tempY+=0.2
    
    screen.blit(background,(0,0))
    frame(30,30,400,600)
    frame(460,30,WIDTH-490,600)
    drawDude(133,63)

    loadBlit()
    damageBlit()
    multiplierBlit()
    pewBlit()

    drawWounds(tempDMG)

    frame(WIDTH//2+30,645,WIDTH//2-60,HEIGHT-675)

    game.display.update() 
