import pygame_textinput
import pygame as game
from sys import exit
from colour import Color

from Modules.Base import Unit
from Modules.Generator import findGun,findArmour
from random import randint

WIDTH=1429 #actively clean multiples of hexagons native resolution
HEIGHT=789

WOUNDCOLOR=(169,18,1)
GREYWOUNDCOLOR=(200,150,150)

DARKERGREY=(30,30,30)
DARKGREY=(100,100,100)
BASEGREY=(180,180,180)
LIGHTGREY=(220,220,220)




game.init() 

background=game.image.load('DT/Hexagons.png')
background=game.transform.scale(background,(WIDTH,HEIGHT))
screen = game.display.set_mode((WIDTH,HEIGHT)) 
background=background.convert_alpha()
game.display.set_caption("Damage Tracker Mk2")
game.display.set_icon(game.image.load('DT/EngineIco.png'))
monospacedHuge=game.font.SysFont('consolas',40)
monospacedLarge=game.font.SysFont('consolas',30)
monospaced=game.font.SysFont('consolas',20)
monospacedSmall=game.font.SysFont('consolas',15)

clock = game.time.Clock()

  
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

def charFrame(x:int,y:int,dx:int,dy:int):
    game.draw.rect(screen, DARKERGREY, game.Rect(x,y,dx,dy), 4, border_radius=5)

    s=game.Surface((dx-6,dy-6),game.SRCALPHA)
    s.fill((180,180,180,230))
    screen.blit(s,(x+3,y+3))

def frame(x:int,y:int,dx:int,dy:int,rgb:tuple):
    game.draw.rect(screen, DARKERGREY, game.Rect(x,y,dx,dy), border_radius=5)
    game.draw.rect(screen, rgb, game.Rect(x+3,y+3,dx-6,dy-6), border_radius=1)

def buttonFrame(x:int,y:int,dx:int,dy:int,hover:bool):
    game.draw.rect(screen, DARKERGREY, game.Rect(x,y,dx,dy), border_radius=5)
    if hover:
        game.draw.rect(screen, (150,150,150), game.Rect(x+3,y+3,dx-6,dy-6), border_radius=1)
    else:
        game.draw.rect(screen, (80,80,80), game.Rect(x+3,y+3,dx-6,dy-6), border_radius=1)

def drawDude(x:int,y:int):
    screen.blit(limbImgs[0],(x+76,y+1))
    screen.blit(limbImgs[1],(x+51,y+60))
    screen.blit(limbImgs[2],(x-1,y+69))
    screen.blit(limbImgs[3],(x+131,y+76))
    screen.blit(limbImgs[4],(x+23,y+215))
    screen.blit(limbImgs[5],(x+93,y+213))
    
    drawPointer(1,x+105,y+85)
    drawPointer(2,x+31,y+151,True)
    drawPointer(3,x+170,y+150)
    drawPointer(4,x+55,y+321,True)
    drawPointer(5,x+135,y+327)    

def drawPointer(loc:int,x:int,y:int,flip:bool=False):
    if flip:
        game.draw.line(screen, (0,0,0), (x,y), (x-30,y-30), 2)
        game.draw.line(screen, (0,0,0), (x-30,y-30), (x-100,y-30), 2)
        for injury in unit.critInjuries:
            if injury.loc==loc:
                label=monospacedHuge.render(injury.name,True,WOUNDCOLOR)
                screen.blit(label,label.get_rect(center=(x-70,y-30)))
                
    else:
        game.draw.line(screen, (0,0,0), (x,y), (x+30,y-30), 2)
        game.draw.line(screen, (0,0,0), (x+30,y-30), (x+100,y-30), 2)
        for injury in unit.critInjuries:
            if injury.loc==loc:
                label=monospacedHuge.render(injury.name,True,WOUNDCOLOR)
                screen.blit(label,label.get_rect(center=(x+70,y-30)))

limbImgs=[]
limbImgs.append(game.image.load('DT/Body/Head.png').convert_alpha())
limbImgs.append(game.image.load('DT/Body/Torso.png').convert_alpha())
limbImgs.append(game.image.load('DT/Body/Larm.png').convert_alpha())
limbImgs.append(game.image.load('DT/Body/Rarm.png').convert_alpha())
limbImgs.append(game.image.load('DT/Body/Lleg.png').convert_alpha())
limbImgs.append(game.image.load('DT/Body/Rleg.png').convert_alpha())

stunImg=game.image.load('DT/HUD/stun.png').convert_alpha()

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
    frame(550,42,246,36,LIGHTGREY)
    screen.blit(loadInput.surface,(556,50))

damageTextLabel=monospacedLarge.render("DAMAGE",True,(0,0,0))
damageInput=pygame_textinput.TextInputVisualizer()
damageInput.font_object=monospacedLarge
damageInput.manager.validator=(lambda x: x=='' or (len(x)<=6 and (str(x[-1]).isnumeric() or str(x[-1]).lower()=='d') or x[-1]=='+' or x[-1]=='-'))
damageSelected=False
damageHitbox=game.Rect(506,533,116,46)    
def damageBlit():
    screen.blit(damageTextLabel,(508,503))
    frame(506,533,116,46,LIGHTGREY)
    screen.blit(damageInput.surface,(512,542))

multiplierTextLabel=monospacedLarge.render("X",True,(50,50,50))
multiplierEmptyFieldLabel=monospacedLarge.render("1",True,(50,50,50))
multiplierInput=pygame_textinput.TextInputVisualizer()
multiplierInput.font_object=monospacedLarge
multiplierInput.manager.validator=(lambda x: len(x)<=2 and (str(x).isnumeric() or x==''))
multiplierSelected=False
multiplierHitbox=game.Rect(656,533,40,46)
def multiplierBlit():
    frame(656,533,47,46,LIGHTGREY)
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
            
        rect=woundTrackLabels[i].get_rect(center=(startX+(i+0.5)*5*boxSize+offsetX,startY+offsetY-7))
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
    frame(30,645,WIDTH//2-15,HEIGHT-675,BASEGREY)
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

spGradient=[Color("white")]
spGradient+=list(Color("#FBE795").range_to(Color("red"),8))

def drawSP(startX,startY,sp,maxSP):
    for i in range(6):
        drawSPBox(startX+i*63,startY,sp[i],maxSP[i])

def drawSPBox(x,y,spValue,maxSPValue):
    frame(x,y,63,63,DARKGREY)
    textColor=spGradient[max(min(maxSPValue-spValue,spGradient.__len__()-1),0)]
    textColor=(textColor.get_red()*255,textColor.get_green()*255,textColor.get_blue()*255)
    label=monospacedHuge.render(str(spValue),True,textColor)
    rect=label.get_rect(center=(x+32,y+33))
    screen.blit(label,rect)

def generateSPHitboxes(startX,startY):
    output=[]
    for i in range(6):
        output.append(game.Rect(startX+i*63,startY,63,63))
    return output

spHitboxes=generateSPHitboxes(41,557)

############### MECHANICAL BELOW

def processDamage():
    output=0
    try:
        input=damageInput.value
        
        if '-' in input:
            input=input.upper().strip().split("-")
            input[-1]=str(-int(input[-1]))
        else:
            input=input.upper().strip().split("+")

        for item in input:
            if(item.__contains__("D")):
                multiple,dieType=item.split("D")
                if(multiple==""):
                    multiple=1
                for _ in range(int(multiple)):
                    output+=randint(1,int(dieType))
            else:#its just a number
                output+=int(item)
      
    except:
        raise "@@FAILED DMG EVAL@@"

    return output


def pew(loc:int=-1):
    multi=int(multiplierInput.value) if multiplierInput.value.isnumeric() else 1
    for _ in range(multi):
        unit.damage(dmg=processDamage(),loc=loc)

weapon=findGun("streetmaster")
unit=Unit(None,findArmour([14,16,16,16,10,10]),0,8,9,cyber=[0,0,0,0,0,0])

##TEMP
unit.damage(dmg=30,loc=2)
unit.damage(dmg=30,loc=5)
unit.damage(dmg=30,loc=5)

while True: 
    events=game.event.get()
    for event in events: 
        if event.type == game.QUIT: 
            print(round(tempX),"|",round(tempY))
            game.quit()
            exit()

        if event.type == game.MOUSEBUTTONDOWN and game.mouse.get_pressed()[0]:
            loadSelected=loadHitbox.collidepoint(game.mouse.get_pos())
            damageSelected=damageHitbox.collidepoint(game.mouse.get_pos())
            multiplierSelected=multiplierHitbox.collidepoint(game.mouse.get_pos())
            for i in range(51):
                if woundTrackHitBoxes[i].collidepoint(game.mouse.get_pos()):
                    unit.wounds=i
            if pewHitbox.collidepoint(game.mouse.get_pos()):
                pew()

        if event.type == game.MOUSEWHEEL:
            for i in range(6):
                if spHitboxes[i].collidepoint(game.mouse.get_pos()):
                    unit.armour.sp[i]=max(min(unit.armour.spMax[i],unit.armour.sp[i]+event.y),0)

        if event.type == game.KEYDOWN and event.key == game.K_RETURN:
            if damageSelected or multiplierSelected:
                pew()

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
    
        
    updateArrows(events) ##TEMPP
    if pressedArrows[0]:
        tempX-=1.5
    if pressedArrows[1]:
        tempX+=1.5
    if pressedArrows[2]:
        tempY-=1.5
    if pressedArrows[3]:
        tempY+=1.5
    
    screen.blit(background,(0,0))
    charFrame(30,30,400,600) # char frame
    frame(460,30,WIDTH-490,600,BASEGREY) # main frame
    drawDude(133,63)
    drawSP(41,557,unit.armour.sp,unit.armour.spMax)

    loadBlit()
    damageBlit()
    multiplierBlit()
    pewBlit()

    drawWounds(unit.wounds)

    frame(WIDTH//2+45,645,WIDTH//2-75,HEIGHT-675,BASEGREY)

    game.display.update() 
    clock.tick(30)