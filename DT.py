import pygame_textinput
import pygame as game
from sys import exit
from colour import Color
from copy import deepcopy

from Modules.Base import Unit
from Modules.Generator import findGun,findArmour
from Modules.Ammo import *
from random import randint

WIDTH=1429 #actively clean multiples of hexagons native resolution
HEIGHT=789

BLACK=(0,0,0)
DARKGREEN=(10,100,10)

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
impactHuge=game.font.SysFont('impact',70)
monospacedHuge=game.font.SysFont('consolas',40)
monospacedLarge=game.font.SysFont('consolas',30)
monospaced=game.font.SysFont('consolas',20)
monospacedSmall=game.font.SysFont('consolas',15)
impactTiny=game.font.SysFont('impact',13)

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

limbImgs=[]
limbImgs.append(game.image.load('DT/Body/Head.png').convert_alpha())
limbImgs.append(game.image.load('DT/Body/Torso.png').convert_alpha())
limbImgs.append(game.image.load('DT/Body/Larm.png').convert_alpha())
limbImgs.append(game.image.load('DT/Body/Rarm.png').convert_alpha())
limbImgs.append(game.image.load('DT/Body/Lleg.png').convert_alpha())
limbImgs.append(game.image.load('DT/Body/Rleg.png').convert_alpha())


stunImg=game.image.load('DT/HUD/stun.png').convert_alpha()
unconImg=game.image.load('DT/HUD/uncon.png').convert_alpha()
deadImg=game.image.load('DT/HUD/dead.png').convert_alpha()
zeroedImg=game.image.load('DT/HUD/zeroed.png').convert_alpha()

shirtImg=game.image.load('DT/HUD/shirt.png').convert_alpha()
shirt2Img=game.image.load('DT/HUD/shirt2.png').convert_alpha()

def drawHudElements():
    if unit.wounds>=50:
        screen.blit(deadImg,(40,40))
        screen.blit(zeroedImg,(110,40))
    elif unit.dead:
        screen.blit(unconImg,(40,40))
        screen.blit(deadImg,(110,40))
    elif unit.uncon:
        screen.blit(stunImg,(40,40))
        screen.blit(unconImg,(110,40))
    elif unit.stunned:
        screen.blit(stunImg,(40,40))  
    
    #screen.blit(shirtImg,(57,460))

def drawDude(x:int,y:int):
    for injury in unit.critInjuries:
        fill(limbImgs[injury.loc],WOUNDCOLOR)
    screen.blit(limbImgs[0],(x+76,y+1))
    screen.blit(limbImgs[1],(x+51,y+60))
    screen.blit(limbImgs[2],(x-1,y+69))
    screen.blit(limbImgs[3],(x+131,y+76))
    screen.blit(limbImgs[4],(x+23,y+215))
    screen.blit(limbImgs[5],(x+93,y+213))
    
    drawPointer(1,x+105,y+85)
    drawPointer(2,x+31,y+151,True)
    drawPointer(3,x+170,y+150)
    drawPointer(4,x+51,y+334,True)
    drawPointer(5,x+135,y+327)    

def drawPointer(loc:int,x:int,y:int,flip:bool=False):
    verticalOffset=0
    draw=False
    for injury in unit.critInjuries:
        if injury.loc==loc:
            draw=True
    if not draw:
        return
    
    if flip:
        game.draw.line(screen, BLACK, (x,y), (x-30,y-30), 2)
        game.draw.line(screen, BLACK, (x-30,y-30), (x-100,y-30), 2)
        for injury in unit.critInjuries:
            if injury.loc==loc:
                if injury.severity==0:
                    textColor=DARKGREEN
                elif injury.severity==2:
                    textColor=WOUNDCOLOR
                else:
                    textColor=BLACK
                label=impactTiny.render(injury.name,True,textColor) #innefficient to render at runtime
                screen.blit(label,label.get_rect(center=(x-70,y-40+verticalOffset)))
                verticalOffset-=14
    else:
        game.draw.line(screen, BLACK, (x,y), (x+30,y-30), 2)
        game.draw.line(screen, BLACK, (x+30,y-30), (x+100,y-30), 2)
        for injury in unit.critInjuries:
            if injury.loc==loc:
                if injury.severity==0:
                    textColor=DARKGREEN
                elif injury.severity==2:
                    textColor=WOUNDCOLOR
                else:
                    textColor=BLACK
                label=impactTiny.render(injury.name,True,textColor) #innefficient to render at runtime
                screen.blit(label,label.get_rect(center=(x+70,y-40+verticalOffset)))
                verticalOffset-=14

tempX=0
tempY=0
pressedArrows=[False,False,False,False]

loadTextLabel=monospacedLarge.render("Load",True,BLACK)
loadInput=pygame_textinput.TextInputVisualizer()
loadInput.font_object=monospaced
loadInput.manager.validator=(lambda x: len(x)<=21 and str(x).isprintable())
loadSelected=False
loadHitbox=game.Rect(550,42,246,36)
def loadBlit():
    screen.blit(loadTextLabel,(473,45))
    frame(550,42,246,36,LIGHTGREY)
    screen.blit(loadInput.surface,(556,50))

damageTextLabel=monospacedLarge.render("DAMAGE",True,BLACK)
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

pewTextLabel=monospaced.render("PEW!",True,BLACK)
pewPewTextLabel=monospaced.render("PEW PEW!",True,BLACK)
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
    woundTrackLabels.append(monospacedSmall.render(text,True,BLACK))

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
    game.draw.line(screen,BLACK,(startX,startY),(startX+boxSize*5,startY),2)
    game.draw.line(screen,BLACK,(startX,startY+boxSize),(startX+boxSize*5,startY+boxSize),2)
    for i in range(6):
        game.draw.line(screen,BLACK,(startX+boxSize*i,startY),(startX+boxSize*i,startY+boxSize),2)
    for i in range(5):
        if i<wounds:
            game.draw.line(screen,WOUNDCOLOR,(startX+boxSize*i+6,startY+3),(startX+boxSize*i+int(boxSize)-5,startY+boxSize-2),8)
            game.draw.line(screen,WOUNDCOLOR,(startX+boxSize*i+6,startY+int(boxSize)-2),(startX+boxSize*i+int(boxSize)-5,startY+3),8)
        elif i<wounds+greyWounds:
            game.draw.line(screen,GREYWOUNDCOLOR,(startX+boxSize*i+6,startY+3),(startX+boxSize*i+int(boxSize)-5,startY+boxSize-2),8)
            game.draw.line(screen,GREYWOUNDCOLOR,(startX+boxSize*i+6,startY+int(boxSize)-2),(startX+boxSize*i+int(boxSize)-5,startY+3),8)

woundsHitbox=game.Rect(30,645,WIDTH//2-15,HEIGHT-675)
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
    if wounds>=50 and not woundsHitbox.collidepoint(game.mouse.get_pos()):
        s=game.Surface((WIDTH//2-15,HEIGHT-675),game.SRCALPHA)
        s.fill((30,30,30,200))
        screen.blit(s,(30,645))

        zeroedText=impactHuge.render("Z E R O E D",True,WOUNDCOLOR)
        screen.blit(zeroedText,zeroedText.get_rect(center=(394,699)))


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

spInputsSelected=[False]*6
spInputs=[]
def populateSPInputs():
    for i in range(6):
        spInput=pygame_textinput.TextInputVisualizer()
        spInput.font_object=monospacedHuge
        spInput.manager.validator=deepcopy(lambda x: len(x)<=2 and (str(x).isnumeric() or x==''))
        spInput.cursor_color=(255,255,255)
        spInput.value=str(unit.armour.sp[i])
        spInputs.append(spInput)


def drawSP(startX,startY,sp,maxSP):
    for i in range(6):
        x=startX+i*63
        y=startY

        frame(x,y,63,63,DARKGREY)
        textColor=spGradient[max(min(maxSP[i]-sp[i],spGradient.__len__()-1),0)]
        textColor=(textColor.get_red()*255,textColor.get_green()*255,textColor.get_blue()*255)
        spInputs[i].font_color=textColor

        screen.blit(spInputs[i].surface,(x+10,y+13))
    

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

populateSPInputs()

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

            for i in range(6):
                spInputsSelected[i]=spHitboxes[i].collidepoint(game.mouse.get_pos())


        if event.type == game.MOUSEWHEEL:
            for i in range(6):
                if spHitboxes[i].collidepoint(game.mouse.get_pos()):
                    unit.armour.sp[i]=max(min(unit.armour.spMax[i],unit.armour.sp[i]+event.y),0)

        if event.type == game.KEYDOWN and event.key == game.K_RETURN:
            if damageSelected or multiplierSelected:
                pew()
            for i in range(6):
                spInputsSelected[i]=False

        if event.type == game.KEYDOWN and event.key == game.K_TAB:
            if damageSelected:
                damageSelected=False
                multiplierSelected=True
            elif multiplierSelected:
                multiplierSelected=False
                damageSelected=True
            for i in range(6):
                if spInputsSelected[i]:
                    spInputsSelected[i]=False
                    spInputsSelected[(i+1)%6]=True
                    break


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

    for i in range(6):
        if spInputsSelected[i]:
            spInputs[i].manager.cursor_pos=2
            spInputs[i].update(events)
            unit.armour.sp[i]=int(spInputs[i].value if spInputs[i].value.isnumeric() else 1)
            unit.armour.spMax[i]=int(spInputs[i].value if spInputs[i].value.isnumeric() else 1)
        else:
            spInputs[i].value=str(unit.armour.sp[i])
            spInputs[i].cursor_visible=False
    
        
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
    drawHudElements()
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