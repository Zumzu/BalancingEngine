import pygame_textinput
import pygame as game
from sys import exit
from colour import Color
from copy import deepcopy
from os import system
from math import cos,sin,pi

from Modules.Base import Unit,bodyToBTM,CyberLimb
from Modules.Generator import findGun,findArmour,generateUnitList
from Modules.Ammo import *
from Modules.Dice import locationDie
from random import randint,uniform,random


#  PREFACE
#OKAY if anyone is reading this code at this point in development, Im aware this is an absolutely awful way of doing front end
#This is the definition of code debt, and the only reason I can get away with this is because this god document is strictly UI, all functionality is handled in a WAY more elegant way
#But in the short term, this is actually highly malleable for a solo dev, and I do plan on going back and refactoring this if I dont move on to better architectures than literal pygame
#The choice of pygame was largely with the intention of making a portable, relatively lightweight UI that supports things like particles and animation so long as I write them myself
#(An older iteration of this was in unity and the overhead was UNREAL)

#  TODO
#Tabss - Rename reorder
#Graveyard
#Explosion and fire symbols in log
#Ignore wound levels
#Skull Cusioning
#Luck
#More Hud Symbols - All negative, Stun negative
#Push melee/gun/armour list to firestore eventually
#SO much refactoring to a real code format


WIDTH=1429 #actively clean multiple of hexagon backgrounds native resolution
HEIGHT=789

BLACK=(0,0,0)
WHITE=(255,255,255)

LUCKGREEN=(0,158,0)
DARKGREEN=(10,100,10)
TRACEBLUE=(0,200,255)
TRACEYELLOW=(244,249,51)
TRACERED=(255,0,0)
CYBERCOLOR=(144,176,185)
CYBERWOUNDCOLOR=(0,145,185)

STUNYELLOW=(255,244,55)
DARKYELLOW=(198,187,0)

WOUNDCOLOR=(169,18,1)
DARKWOUNDCOLOR=(130,13,0)
GREYWOUNDCOLOR=(200,150,150)

DARKERGREY=(30,30,30)
DARKGREY=(100,100,100)
BASEGREY=(180,180,180)
LIGHTGREY=(220,220,220)

SHOTDELAY=0.8 #measured in seconds
TRACEDELAY=0.2 #measured in seconds

game.init() 

background=game.image.load('DT/Hexagons.png')
background=game.transform.scale(background,(WIDTH,HEIGHT))
screen = game.display.set_mode((WIDTH,HEIGHT)) 
background=background.convert_alpha()
game.display.set_caption("Damage Tracker Mk2")
game.display.set_icon(game.image.load('DT/EngineIco.png'))
monospacedHuge=game.font.SysFont('consolas',40)
monospacedLarge=game.font.SysFont('consolas',30)
monospacedMediumLarge=game.font.SysFont('consolas',23)
monospacedMedium=game.font.SysFont('consolas',20)
monospacedSmall=game.font.SysFont('consolas',15)
monospacedTiny=game.font.SysFont('consolas',12)


impactHuge=game.font.SysFont('impact',70)
impactLarge=game.font.SysFont('impact',30)
impactMedium=game.font.SysFont('impact',22)
impactTiny=game.font.SysFont('impact',13)

allNegativeFont=game.font.SysFont('impact',33)

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

def fill255(surface,rgb): #alpha from 0-1
    w,h = surface.get_size()
    r,g,b = rgb
    for i in range(w):
        for j in range(h):
            a=surface.get_at((i,j))[3]
            if a==255:
                surface.set_at((i,j),game.Color(r,g,b,150))
            else:
                surface.set_at((i,j),game.Color(r,g,b,0))

def fill100(surface,rgb): #alpha from 0-1
    w,h = surface.get_size()
    r,g,b = rgb
    for i in range(w):
        for j in range(h):
            a=surface.get_at((i,j))[3]
            if a==100:
                surface.set_at((i,j),game.Color(r,g,b,100))
            else:
                surface.set_at((i,j),game.Color(r,g,b,0))

def tint(surface,rgb):
    w,h = surface.get_size()
    for i in range(w):
        for j in range(h):
            rgba=surface.get_at((i,j))
            surface.set_at((i,j),game.Color(min(255,rgba[0]+rgb[0]),min(255,rgba[1]+rgb[1]),min(255,rgba[2]+rgb[2]),rgba[3]))

def charFrame(x:int,y:int,dx:int,dy:int):
    game.draw.rect(screen, DARKERGREY, game.Rect(x,y,dx,dy), 4, border_radius=5)

    s=game.Surface((dx-6,dy-6),game.SRCALPHA)
    s.fill((180,180,180,230))
    screen.blit(s,(x+3,y+3))

def frame(x:int,y:int,dx:int,dy:int,rgb:tuple):
    game.draw.rect(screen, DARKERGREY, game.Rect(x,y,dx,dy), border_radius=5)
    game.draw.rect(screen, rgb, game.Rect(x+3,y+3,dx-6,dy-6), border_radius=1)

def frameSelect(x:int,y:int,dx:int,dy:int,rgb:tuple):
    game.draw.rect(screen, BLACK, game.Rect(x,y,dx,dy), border_radius=5)
    game.draw.rect(screen, rgb, game.Rect(x+3,y+3,dx-6,dy-6), border_radius=1)

def buttonFrame(x:int,y:int,dx:int,dy:int,hover:bool):
    game.draw.rect(screen, DARKERGREY, game.Rect(x,y,dx,dy), border_radius=5)
    if hover:
        game.draw.rect(screen, (150,150,150), game.Rect(x+3,y+3,dx-6,dy-6), border_radius=1)
    else:
        game.draw.rect(screen, (80,80,80), game.Rect(x+3,y+3,dx-6,dy-6), border_radius=1)

def dudeImgs():
    output=[]
    output.append(game.image.load('DT/Body/Head.png').convert_alpha())
    output.append(game.image.load('DT/Body/Torso.png').convert_alpha())
    output.append(game.image.load('DT/Body/Larm.png').convert_alpha())
    output.append(game.image.load('DT/Body/Rarm.png').convert_alpha())
    output.append(game.image.load('DT/Body/Lleg.png').convert_alpha())
    output.append(game.image.load('DT/Body/Rleg.png').convert_alpha())
    return output

def smallDudeImgs():
    output=[]
    output.append(game.image.load('DT/SmallBody/Head.png').convert_alpha())
    output.append(game.image.load('DT/SmallBody/Torso.png').convert_alpha())
    output.append(game.image.load('DT/SmallBody/Larm.png').convert_alpha())
    output.append(game.image.load('DT/SmallBody/Rarm.png').convert_alpha())
    output.append(game.image.load('DT/SmallBody/Lleg.png').convert_alpha())
    output.append(game.image.load('DT/SmallBody/Rleg.png').convert_alpha())
    return output

def shieldImgs():
    output=[]
    output.append(game.image.load('DT/Shield/shieldLarm.png').convert_alpha())
    output.append(game.image.load('DT/Shield/shieldRarm.png').convert_alpha())
    output.append(game.image.load('DT/Shield/shieldLleg.png').convert_alpha())
    output.append(game.image.load('DT/Shield/shieldRleg.png').convert_alpha())
    return output

shieldWiggle=0
barrierActive=False

shieldBorder=game.image.load('DT/Shield/shieldBorder.png').convert_alpha()
shieldBorderDark=game.image.load('DT/Shield/shieldBorder.png').convert_alpha()
fill255(shieldBorderDark,DARKGREY)

shieldParts=shieldImgs()
shieldPartsDark=shieldImgs()
shieldPartsHighlight=shieldImgs()
for i in range(4):
    fill255(shieldParts[i],TRACEBLUE)
    fill255(shieldPartsDark[i],DARKGREY)
    fill255(shieldPartsHighlight[i],LIGHTGREY)

smallLimbImgs=smallDudeImgs()
smallLimbImgsWounded=smallDudeImgs()
smallLimbImgsCyber=smallDudeImgs()
smallLimbImgsCyberDamaged=smallDudeImgs()
for i in range(6):
    fill(smallLimbImgs[i],DARKERGREY)
    fill(smallLimbImgsWounded[i],WOUNDCOLOR)
    fill(smallLimbImgsCyber[i],TRACEBLUE)
    fill(smallLimbImgsCyberDamaged[i],TRACEYELLOW)

limbImgs=dudeImgs()
limbImgsWounded=dudeImgs()
limbImgsCalled=dudeImgs()
limbImgsHighlight=dudeImgs()
limbImgCyber=dudeImgs()
for i in range(6):
    fill(limbImgsWounded[i],WOUNDCOLOR)
    fill(limbImgsCalled[i],TRACEBLUE)
    fill(limbImgsHighlight[i],(200,200,200))
    fill100(limbImgCyber[i],CYBERCOLOR)

limbWiggle=[0]*6

limbOffsets=[]
limbOffsets.append((76,1))
limbOffsets.append((51,60))
limbOffsets.append((-1,69))
limbOffsets.append((131,76))
limbOffsets.append((23,215))
limbOffsets.append((93,213))

woundPoints=[]
woundPoints.append((99,32))
woundPoints.append((105,130))
woundPoints.append((31,151))
woundPoints.append((170,150))
woundPoints.append((51,334))
woundPoints.append((135,327))

stunImg=game.image.load('DT/HUD/stun.png').convert_alpha()
stunSmolImg=game.image.load('DT/HUD/stunSmol.png').convert_alpha()
stunTinyImg=game.image.load('DT/HUD/stunTiny.png').convert_alpha()
unconImg=game.image.load('DT/HUD/uncon.png').convert_alpha()
unconSmolImg=game.image.load('DT/HUD/unconSmol.png').convert_alpha()
unconTinyImg=game.image.load('DT/HUD/unconTiny.png').convert_alpha()
deadImg=game.image.load('DT/HUD/dead.png').convert_alpha()
deadSmolImg=game.image.load('DT/HUD/deadSmol.png').convert_alpha()
deadTinyImg=game.image.load('DT/HUD/deadTiny.png').convert_alpha()
zeroedImg=game.image.load('DT/HUD/zeroed.png').convert_alpha()

allNegativeImg=game.image.load('DT/HUD/allNegative.png').convert_alpha()
stunNegativeImg=game.image.load('DT/HUD/stunNegative.png').convert_alpha()
stunNegativeSmolImg=game.image.load('DT/HUD/stunNegativeSmol.png').convert_alpha()

shirtImg=game.image.load('DT/HUD/shirtSmall.png').convert_alpha()
shirt2Img=game.image.load('DT/HUD/shirt2Small.png').convert_alpha()

undoImg=game.image.load('DT/undo.png').convert_alpha()
bulletImg=game.image.load('DT/bullet.png').convert_alpha()

warningRedImg=game.image.load('DT/HUD/warning.png').convert_alpha()
warningYellowImg=game.image.load('DT/HUD/warning.png').convert_alpha()
fill(warningYellowImg,STUNYELLOW)
warningBlinkTimer=40

bleedImg=game.image.load('DT/HUD/bleed.png').convert_alpha()

stunHudHitbox=game.Rect(40,40,64,64)
unconHudHitbox=game.Rect(110,40,64,64)
def drawHudElements():
    global shieldWiggle, warningBlinkTimer

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
    
    if not (unit.uncon or unit.dead or unit.wounds>=50) and unit.stunMod()>0:
        if unit.stunned:
            stunNegativeText=monospacedMediumLarge.render(f'-{unit.stunMod()}',True,DARKERGREY)
            screen.blit(stunNegativeSmolImg,(110,36)) 
            screen.blit(stunNegativeText,stunNegativeText.get_rect(center=(142,51)))
        else:
            stunNegativeText=monospacedMediumLarge.render(f'STUN -{unit.stunMod()}',True,DARKERGREY)
            screen.blit(stunNegativeImg,(43,36)) 
            screen.blit(stunNegativeText,stunNegativeText.get_rect(center=(107,51)))

    if unit.wounds>20:
        if unit.wounds>=50 or unit.dead:
            allNegativeText=allNegativeFont.render('DEAD',True,DARKWOUNDCOLOR)
        else:
            allNegativeText=allNegativeFont.render(f'ALL -{unit.allNegative()}',True,DARKWOUNDCOLOR)
            
        screen.blit(allNegativeImg,(270,40)) 
        screen.blit(allNegativeText,allNegativeText.get_rect(center=(346,64)))

    totalSp=0
    totalSpMax=0
    for i in range(6):
        totalSp+=unit.armour.sp[i]
        totalSpMax+=unit.armour.spMax[i]

    if totalSpMax!=0:
        disparity=totalSpMax-totalSp
        if totalSp/totalSpMax<0.8:
            screen.blit(shirt2Img,(41,475))
            if disparity<10:
                shirtText=impactLarge.render(f'-{disparity}',True,DARKWOUNDCOLOR)
            else:
                shirtText=impactMedium.render(f'-{disparity}',True,DARKWOUNDCOLOR)
            screen.blit(shirtText,shirtText.get_rect(center=(123,516)))

        elif totalSp/totalSpMax<0.9:
            if disparity<10:
                shirtText=impactLarge.render(f'-{disparity}',True,DARKGREY)
            else:
                shirtText=impactMedium.render(f'-{disparity}',True,DARKGREY)
            screen.blit(shirtImg,(41,475))
            screen.blit(shirtText,shirtText.get_rect(center=(123,516)))
    
    if barrierActive:
        x=321+randint(-shieldWiggle//8,shieldWiggle//8)
        y=374+randint(-shieldWiggle//8,shieldWiggle//8)
        if shieldWiggle>0:
            shieldWiggle-=1
        if unit.barrier.sp==0:
            screen.blit(shieldBorderDark,(x,y))
        else:
            screen.blit(shieldBorder,(x,y))

        for i in range(4):
            if unit.barrier.covers[i+2]:
                if unit.barrier.sp==0:
                    screen.blit(shieldPartsDark[i],(x,y))
                else:
                    screen.blit(shieldParts[i],(x,y))
            if shieldCollision(i,game.mouse.get_pos()):
                screen.blit(shieldPartsHighlight[i],(x,y))

        barText=monospacedHuge.render(str(unit.barrier.sp),True,BLACK)
        screen.blit(barText,barText.get_rect(center=(x+40,y+47)))
    else:
        if unit.barrier.sp!=0:
            unit.barrier.sp=0
            unit.barrier.covers=[True]*6

    if unit.wounds>=15:
        warningBlinkTimer-=1
        if unit.dead:
            screen.blit(warningRedImg,(51,194))
        elif warningBlinkTimer>=0:
            if unit.wounds<=30:
                screen.blit(warningYellowImg,(51,194))
            else:
                screen.blit(warningRedImg,(51,194))

        dangerValue=max(3,50-unit.wounds*1.3)
        if warningBlinkTimer<=-dangerValue:
            warningBlinkTimer=dangerValue

    bleeding=unit.uncon and unit.wounds>15
    for injury in unit.critInjuries:
        if 'bleeding' in injury.text:
            bleeding=True
            break

    if bleeding:
        screen.blit(bleedImg,(306,478))
        if unit.wounds>=50:
            minutesText=impactLarge.render('~',False,DARKWOUNDCOLOR)
        else:
            minutes=50-unit.wounds
            for injury in unit.critInjuries:
                minutes/=injury.bleedMultiplier
            minutesText=impactLarge.render(str(round(minutes))+'m',False,DARKWOUNDCOLOR)

        screen.blit(minutesText,minutesText.get_rect(center=(380,516)))

    if bleeding and not unit.dead:
        screen.blit(monospacedMediumLarge.render(f'DC-{10+2*((unit.wounds-1)//5)}',True,DARKGREY),(42,410))
        screen.blit(monospacedSmall.render(f'{5 if unit.wounds<=25 else 10}m / {5+5*((unit.wounds-1)//10)}m',True,DARKGREY),(42,430))


barValueHitbox=game.Rect(330,390,63,83)

def shieldCollision(i:int,pos):
    width,height=shieldParts[i].get_size()
    posX,posY=pos
    pixel=(posX-321,posY-384)
    if pixel[0]<0 or pixel[0]>=width or pixel[1]<0 or pixel[1]>=height:
        return False

    return not shieldParts[i].get_at(pixel)[3]==0

def limbCollision(i:int,pos):
    x=133
    y=63
    width,height=limbImgs[i].get_size()
    posX,posY=pos
    pixel=(posX-limbOffsets[i][0]-x, posY-limbOffsets[i][1]-y)
    if pixel[0]<0 or pixel[0]>=width or pixel[1]<0 or pixel[1]>=height:
        return False

    return not limbImgs[i].get_at(pixel)[3]==0

def limbInnerCollision(i:int,pos):
    x=133
    y=63
    width,height=limbImgs[i].get_size()
    posX,posY=pos
    pixel=(posX-limbOffsets[i][0]-x, posY-limbOffsets[i][1]-y)
    if pixel[0]<0 or pixel[0]>=width or pixel[1]<0 or pixel[1]>=height:
        return False
    
    return limbImgs[i].get_at(pixel)[3]==100

def drawDude():
    injured=[False]*6
    for injury in unit.critInjuries:
        injured[injury.loc]=True

    for i in range(6):
        x=133
        y=63
        if limbWiggle[i]!=0:
            if i==1:
                wiggleMod=8
            else:
                wiggleMod=4

            x+=randint(-limbWiggle[i]//wiggleMod,limbWiggle[i]//wiggleMod)
            y+=randint(-limbWiggle[i]//wiggleMod,limbWiggle[i]//wiggleMod)
            limbWiggle[i]-=1

        
        if calledShotLoc==i:
            screen.blit(limbImgsCalled[i],(x+limbOffsets[i][0],y+limbOffsets[i][1]))
        elif injured[i]:
            screen.blit(limbImgsWounded[i],(x+limbOffsets[i][0],y+limbOffsets[i][1]))
        else:
            screen.blit(limbImgs[i],(x+limbOffsets[i][0],y+limbOffsets[i][1]))
        
        if unit.cyber[i] is not None:
            screen.blit(limbImgCyber[i],(x+limbOffsets[i][0],y+limbOffsets[i][1]))
        if limbCollision(i,game.mouse.get_pos()):
            screen.blit(limbImgsHighlight[i],(x+limbOffsets[i][0],y+limbOffsets[i][1]))

    x=133
    y=63

    drawPointer(1,x+105,y+85)
    drawPointer(2,x+31,y+151,True)
    drawPointer(3,x+170,y+150)
    drawPointer(4,x+51,y+334,True)
    drawPointer(5,x+135,y+327)
    
    drawSDP(0,x+110,y+30)
    drawSDP(1,x+105,y+85)
    drawSDP(2,x+31,y+151,True)
    drawSDP(3,x+170,y+150)
    drawSDP(4,x+51,y+334,True)
    drawSDP(5,x+135,y+327)

    global pointerAngle
    pointerAngle+=0.03

pointerAngle=0
def drawPointer(loc:int,x:int,y:int,flip:bool=False):
    global infoText
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
                injuryText=impactTiny.render(injury.name,True,textColor)
                injuryRect=injuryText.get_rect(center=(x-70,y-40+verticalOffset))
                screen.blit(injuryText,injuryRect)
                verticalOffset-=14
                if injuryRect.collidepoint(game.mouse.get_pos()):
                    infoText=injury.text

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
                injuryText=impactTiny.render(injury.name,True,textColor)
                injuryRect=injuryText.get_rect(center=(x+70,y-40+verticalOffset))
                screen.blit(injuryText,injuryRect)
                verticalOffset-=14
                if injuryRect.collidepoint(game.mouse.get_pos()):
                    infoText=injury.text

    count=3
    for i in range(count):
        newParticle=Particle((8*cos(pointerAngle+pi*2*(i/count))+x,8*sin(pointerAngle+pi*2*(i/count))+y),'tracewound')
        newParticle.lifetime/=2
        particles.append(newParticle)

infoText=""
def drawInfoBox():
    global infoText
    if infoText=='':
        return
    x,y=game.mouse.get_pos()
    maxWidth=0
    maxHeight=20
    lines=infoText.split(', ')
    renderedText=[]
    for line in lines:
        if line[0]=='@':
            renderedText.append(monospacedMediumLarge.render(line[1:],True,BLACK))
        else:
            renderedText.append(monospacedMedium.render(line,True,BLACK))
        rect=renderedText[-1].get_rect()
        maxWidth=max(maxWidth,rect.width+20)
        maxHeight+=rect.height
    
    if maxWidth==0 or maxHeight==0:
        raise "@@ INFO BOX BAD TEXT @@"
    
    if x+maxWidth>WIDTH:
        x-=maxWidth
    
    if y-maxHeight>=0:
        y-=maxHeight

    offset=0
    frame(x,y,maxWidth,maxHeight,LIGHTGREY)
    for i in range(len(renderedText)):
        screen.blit(renderedText[i],(x+10,y+10+offset))
        offset+=renderedText[i].get_rect().height

    infoText=''


sdpHitboxes=[]
sdpHitboxes.append(game.Rect(260,44,32,20))
sdpHitboxes.append(game.Rect(259,101,32,20))
sdpHitboxes.append(game.Rect(117,166,32,20))
sdpHitboxes.append(game.Rect(324,165,32,20))
sdpHitboxes.append(game.Rect(136,350,32,20))
sdpHitboxes.append(game.Rect(288,342,32,20))

def drawSDP(loc:int,x:int,y:int,flip:bool=False):
    if unit.cyber[loc] is None:
        return
    if unit.cyber[loc].broken:
        sdpText=monospacedMediumLarge.render(str(unit.cyber[loc].sdp),True,WOUNDCOLOR)
    else:
        sdpText=monospacedMediumLarge.render(str(unit.cyber[loc].sdp),True,BLACK)

    if flip:
        game.draw.line(screen, BLACK, (x,y), (x-28,y-28), 2)
        game.draw.line(screen, BLACK, (x-28,y-28), (x-40,y-28), 2)
        screen.blit(sdpText,sdpText.get_rect(center=(x-34,y-38)))
    else:
        game.draw.line(screen, BLACK, (x,y), (x+28,y-28), 2)
        game.draw.line(screen, BLACK, (x+28,y-28), (x+40,y-28), 2)
        screen.blit(sdpText,sdpText.get_rect(center=(x+34,y-38)))

tempX=0
tempY=0
pressedArrows=[False]*4

loadTextLabel=monospacedLarge.render("Load",True,BLACK)
loadInput=pygame_textinput.TextInputVisualizer()
loadInput.font_object=monospacedMedium
loadInput.manager.validator=(lambda x: len(x)<=21 and str(x).isprintable())
loadSelected=False
loadHitbox=game.Rect(550,42,246,36)
loadDict=None
def loadBlit():
    global loadDict
    loadDict=None

    index=0
    if loadSelected:
        if unitDicts==[]:
            frame(550,78,246,40,LIGHTGREY)
            screen.blit(monospacedLarge.render('Firestore Err.',True,WOUNDCOLOR),(554,84))
        else:
            for unitDict in unitDicts:
                if loadInput.value.lower() in unitDict['name'].lower():
                    drawUnitPreview(550,78+index*40,unitDict)
                    index+=1
                    if index>=3:
                        break

    screen.blit(loadTextLabel,(473,45))
    frame(550,42,246,36,LIGHTGREY)
    screen.blit(loadInput.surface,(556,50))

def drawUnitPreview(x:int,y:int,unitDict:dict):
    global loadDict
    frameRect=game.Rect(x,y,246,40)
    if frameRect.collidepoint(game.mouse.get_pos()):
        frame(x,y,246,40,TRACEBLUE)
        loadDict=unitDict
    else:
        frame(x,y,246,40,LIGHTGREY)
        
    screen.blit(monospacedMedium.render(unitDict['name'].title(),True,BLACK),(x+4,y+6))
    sp=unitDict['sp']
    screen.blit(monospacedTiny.render(f"[{sp[0]},{sp[1]},{sp[2]},{sp[3]},{sp[4]},{sp[5]}] Body:{unitDict['body']} Cool:{unitDict['cool']}",True,BLACK),(x+3,y+25))

bodyTextLabel=monospacedLarge.render("Body",True,BLACK)
btmTextLabel=monospacedMedium.render("BTM:",True,BLACK)
bodyInput=pygame_textinput.TextInputVisualizer()
bodyInput.font_object=monospacedHuge
bodyInput.manager.validator=(lambda x: len(x)<=2 and ((str(x).isnumeric() and int(x)<=20 and int(x)>0)or x==''))
bodySelected=False
bodyHitbox=game.Rect(471,557,63,63)
def bodyBlit():
    screen.blit(bodyTextLabel,(539,563))
    screen.blit(btmTextLabel,(540,596))
    btmValue=monospacedMedium.render(f"-{str(unit.btm)}",True,BLACK)
    screen.blit(btmValue,(591,596))
    frame(471,557,63,63,BASEGREY)
    if len(bodyInput.value)==2:
        screen.blit(bodyInput.surface,(479,570))
    else:
        screen.blit(bodyInput.surface,(492,570))
    


coolTextLabel=monospacedLarge.render("Cool",True,BLACK)
coolInput=pygame_textinput.TextInputVisualizer()
coolInput.font_object=monospacedHuge
coolInput.manager.validator=(lambda x: len(x)<=2 and ((str(x).isnumeric() and int(x)<=20 and int(x)>0)or x==''))
coolSelected=False
coolHitbox=game.Rect(471,488,63,63)
def coolBlit():
    screen.blit(coolTextLabel,(539,505))
    frame(471,488,63,63,BASEGREY)
    coolInput.font_color=BLACK if unit.cool>unit.body else DARKGREY
    if len(coolInput.value)==2:
        screen.blit(coolInput.surface,(479,501))
    else:
        screen.blit(coolInput.surface,(492,501))

def populateBody():
    bodyInput.value=str(unit.body)
    coolInput.value=str(unit.cool)


DAMAGEX=780
DAMAGEY=660

damageTextLabel=monospacedLarge.render("DAMAGE",True,BLACK)
damageInput=pygame_textinput.TextInputVisualizer()
damageInput.font_object=monospacedLarge
damageInput.manager.validator=(lambda x: x=='' or (len(x)<=6 and (str(x[-1]).isnumeric() or str(x[-1]).lower()=='d') or x[-1]=='+' or x[-1]=='-'))
damageSelected=False
damageHitbox=game.Rect(DAMAGEX+6,DAMAGEY+33,116,46)    
def damageBlit():
    drawBullets(DAMAGEX+117,DAMAGEY+3)
    screen.blit(damageTextLabel,(DAMAGEX+8,DAMAGEY+3))
    frame(DAMAGEX+6,DAMAGEY+33,116,46,LIGHTGREY)
    screen.blit(damageInput.surface,(DAMAGEX+12,DAMAGEY+42))

def drawBullets(x,y):
    for i in range(len(shotQueue)):
        screen.blit(bulletImg,(x+i*8,y))

multiplierTextLabel=monospacedLarge.render("X",True,(50,50,50))
multiplierEmptyFieldLabel=monospacedLarge.render("1",True,(50,50,50))
multiplierInput=pygame_textinput.TextInputVisualizer()
multiplierInput.font_object=monospacedLarge
multiplierInput.manager.validator=(lambda x: len(x)<=2 and (str(x).isnumeric() or x==''))
multiplierSelected=False
multiplierHitbox=game.Rect(DAMAGEX+150,DAMAGEY+33,40,46)
def multiplierBlit():
    screen.blit(multiplierTextLabel,(DAMAGEX+128,DAMAGEY+43))
    frame(DAMAGEX+150,DAMAGEY+33,47,46,LIGHTGREY)
    screen.blit(multiplierInput.surface,(DAMAGEX+157,DAMAGEY+42))
    if multiplierInput.value=='':
        screen.blit(multiplierEmptyFieldLabel,(DAMAGEX+157,DAMAGEY+42))

pewTextLabel=monospacedMedium.render("PEW!",True,(255,255,255))
pewPewTextLabel=monospacedMedium.render("PEW PEW!",True,(255,255,255))
pewHitbox=game.Rect(DAMAGEX+214,DAMAGEY+38,100,36)
def pewBlit():
    buttonFrame(DAMAGEX+214,DAMAGEY+38,110,36,pewHitbox.collidepoint(game.mouse.get_pos()))
    if multiplierInput.value=='' or multiplierInput.value=='1':
        screen.blit(pewTextLabel,(DAMAGEX+249,DAMAGEY+47))
    else:
        screen.blit(pewPewTextLabel,(DAMAGEX+225,DAMAGEY+47))

ammoBoldTextCache={}
ammoFaintTextCache={}

ammoHitbox=game.Rect(1135,647,252,100)
ammoInnerHitbox=game.Rect(1135,683,252,40)
def ammoSpinner():
    frame(1135,683,252,40,LIGHTGREY)
    if ammoIndex>0:
        if str(ammoIndex-1) not in ammoFaintTextCache:
            ammoFaintTextCache[ammoIndex]=monospacedMedium.render(ammoTypes[ammoIndex-1].name,True,DARKGREY)
        screen.blit(ammoFaintTextCache[ammoIndex],(1143,659))

    if str(ammoIndex) not in ammoBoldTextCache:
        ammoBoldTextCache[ammoIndex]=monospacedMediumLarge.render(ammoTypes[ammoIndex].name,True,BLACK)
    screen.blit(ammoBoldTextCache[ammoIndex],(1143,691))

    if ammoIndex<len(ammoTypes)-1:
        if str(ammoIndex+1) not in ammoFaintTextCache:
            ammoFaintTextCache[ammoIndex]=monospacedMedium.render(ammoTypes[ammoIndex+1].name,True,DARKGREY)
        screen.blit(ammoFaintTextCache[ammoIndex],(1143,729))

    if ammoInnerHitbox.collidepoint(game.mouse.get_pos()):
        global infoText
        infoText=f"@{ammoTypes[ammoIndex].name}, {ammoTypes[ammoIndex].desc}"

woundTrackText=['LIGHT','SERIOUS','CRITICAL']
for i in range(7):
    woundTrackText.append(f"MORTAL {i}")

woundTrackLabels=[]
for text in woundTrackText:
    woundTrackLabels.append(monospacedSmall.render(text,True,BLACK))

medicalIconImage=game.image.load('DT/medical.png').convert_alpha()
zeroIconImage=game.image.load('DT/ZeroIco.png')
zeroIconImage=game.transform.scale(zeroIconImage,(26,26)).convert_alpha()
def drawWoundTrack(startX:int,startY:int,endX:int,buffer:int,wounds:int,greyWounds:int):
    wounds=max(0,min(50,wounds))
    boxSize=(endX-startX-buffer*10)/50
    screen.blit(zeroIconImage,(startX-boxSize+buffer//3,startY-3))
    screen.blit(medicalIconImage,(startX-boxSize+buffer//3,startY+49))
    
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
deadText=impactHuge.render("D  E  A  D",True,WOUNDCOLOR)
zeroedText=impactHuge.render("Z E R O E D",True,WOUNDCOLOR)
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
    drawWoundTrack(64,670,WIDTH-150,4,wounds,greyWounds)
    if wounds>=50 and not woundsHitbox.collidepoint(game.mouse.get_pos()):
        s=game.Surface((WIDTH//2-15,HEIGHT-675),game.SRCALPHA)
        s.fill((30,30,30,200))
        screen.blit(s,(30,645))
        screen.blit(zeroedText,zeroedText.get_rect(center=(394,699)))

    elif unit.dead and not woundsHitbox.collidepoint(game.mouse.get_pos()):
        s=game.Surface((WIDTH//2-15,HEIGHT-675),game.SRCALPHA)
        s.fill((30,30,30,200))
        screen.blit(s,(30,645))
        screen.blit(deadText,deadText.get_rect(center=(394,699)))

    
    if medicalHitbox.collidepoint(game.mouse.get_pos()):
        global infoText
        if unit.wounds==0:
            infoText='This unit is perfectly healthy! :)'
        elif unit.wounds>=50 or unit.dead:
            infoText='This unit is super not alive'
        else:
            infoText=f'@DC-{10+2*((unit.wounds-1)//5)}, First Aid Time: {5 if unit.wounds<=25 else 10}m, Surgery Time: {5+5*((unit.wounds-1)//10)}m'


def generateWoundHitboxes(startX:int,startY:int,endX:int,buffer:int):
    output=[]
    boxSize=(endX-startX-buffer*10)/50
    output.append(game.Rect((startX-boxSize+buffer//3),startY-3,boxSize+5,boxSize+5))
    medicalHitbox=game.Rect((startX-boxSize+buffer//3),startY+49,boxSize+5,boxSize+5)
    offsetX=0
    offsetY=0
    for i in range(10):
        offsetX+=boxSize/2
        if i==5:
            offsetX=-24.5*boxSize
            offsetY=50
        for j in range(5):
            output.append(game.Rect((startX+i*5*boxSize+offsetX)+boxSize*j,startY+offsetY,boxSize+1,boxSize))

    return (medicalHitbox,output)

medicalHitbox,woundTrackHitBoxes=generateWoundHitboxes(60,670,WIDTH-150,4)

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
        frameColor=DARKGREY
        if i==1:
            frameColor=(60,60,60)
        elif i==4 or i==5:
            frameColor=(80,80,80)

        frame(x,y,63,63,frameColor)
        textColor=spGradient[max(min(maxSP[i]-sp[i],spGradient.__len__()-1),0)]
        textColor=(textColor.get_red()*255,textColor.get_green()*255,textColor.get_blue()*255)
        spInputs[i].font_color=textColor
        
        if len(spInputs[i].value)==2:
            screen.blit(spInputs[i].surface,(x+10,y+13))
        else:
            screen.blit(spInputs[i].surface,(x+21,y+13))

        if unit.armour.typeAt(i)=='soft':
            game.draw.polygon(screen,(255,182,0),((x+3,y+3),(x+12,y+3),(x+3,y+12)))
        else:
            game.draw.polygon(screen,(230,60,13),((x+3,y+3),(x+12,y+3),(x+3,y+12)))

def generateSPHitboxes(startX,startY):
    spHitboxes=[]
    for i in range(6):
        spHitboxes.append(game.Rect(startX+i*63,startY,63,63))
    return spHitboxes

spHitboxes=generateSPHitboxes(41,557)

barrierIconOn=game.image.load('DT/shieldIconOn.png').convert_alpha()
barrierIconOff=game.image.load('DT/shieldIconOff.png').convert_alpha()

barToggleHitbox=game.Rect(471,419,63,63)
def drawBar():
    frame(471,419,63,63,BASEGREY)
    if barrierActive:
        screen.blit(barrierIconOn,(481,427))
    else:
        screen.blit(barrierIconOff,(481,427))

luckActive=False
luckIconOn=game.image.load('DT/luckIconOn.png').convert_alpha()
luckIconOff=game.image.load('DT/luckIconOff.png').convert_alpha()

luckToggleHitbox=game.Rect(471,350,63,63)
def drawLuck():
    frame(471,350,63,63,BASEGREY)
    if luckActive:
        screen.blit(luckIconOn,(481,358))
    else:
        screen.blit(luckIconOff,(481,358))

luckRerollHitbox=game.Rect(290,77,65,30)
luckDontHitbox=game.Rect(360,77,55,30)
def drawReroll():
    if shotTimer>5000:
        frame(285,72,135,40,LUCKGREEN)
        frame(290,77,65,30,WHITE if luckRerollHitbox.collidepoint(game.mouse.get_pos()) else LIGHTGREY)
        frame(360,77,55,30,WHITE if luckDontHitbox.collidepoint(game.mouse.get_pos()) else LIGHTGREY)

        screen.blit(impactMedium.render('Reroll',True,BLACK),(295,77))
        screen.blit(impactMedium.render('Dont',True,BLACK),(365,77))

deflectionIconOn=game.image.load('DT/deflectionIconOn.png').convert_alpha()
deflectionIconOff=game.image.load('DT/deflectionIconOff.png').convert_alpha()

deflectionHitbox=game.Rect(471,236,63,63)
def drawDeflection():
    frame(471,236,63,63,BASEGREY)
    if unit.deflection:
        screen.blit(deflectionIconOn,(481,244))
    else:
        screen.blit(deflectionIconOff,(481,244))
    

locationTextNames=["Head","Torso","L.Arm","R.Arm","L.Leg","R.Leg"]
class Log:
    def __init__(self,loc:int,dmgTotal:int,dmgRolled:list[int],more:int,oldUnit:Unit,newUnit:Unit) -> None:
        self.loc=loc
        self.dmgTotal=dmgTotal
        self.dmgRolled=dmgRolled
        self.more=more

        self.through=newUnit.wounds-oldUnit.wounds
        for i in range(6):
            if newUnit.cyber[i] is not None:
                self.through+=newUnit.cyber[i].sdp-oldUnit.cyber[i].sdp
        self.critInjuries=newUnit.critInjuries[len(oldUnit.critInjuries):]
        self.degraded=not oldUnit.armour.sp==newUnit.armour.sp
        self.stunned=not oldUnit.stunned==newUnit.stunned
        self.unconned=not oldUnit.uncon==newUnit.uncon
        self.killed=not oldUnit.dead==newUnit.dead
        self.greyed=oldUnit.uncon or oldUnit.dead
        
        self.height=60 if self.critInjuries!=[] else 40
        self.hitbox=None

        self.unit=deepcopy(newUnit)

    def draw(self,x:int,y:int):
        black=BLACK
        woundColor=WOUNDCOLOR
        cyberColor=CYBERWOUNDCOLOR
        if self.greyed:
            black=DARKGREY
            woundColor=DARKGREY
            cyberColor=DARKGREY
        

        offset=0
        if self.dmgRolled!=[]:
            for roll in self.dmgRolled:
                if roll>5:
                    rollColor=woundColor
                else:
                    rollColor=black
                screen.blit(monospacedMedium.render(str(roll),True,rollColor),(x+5+offset,y+2))
                game.draw.rect(screen,BLACK,game.Rect(x+offset,y,20,20),1)
                offset+=24
            
            if self.more!=0:
                line=monospacedMediumLarge.render(f"+{self.more} = {self.dmgTotal} to {locationTextNames[self.loc]}",True,black)
            else:
                line=monospacedMediumLarge.render(f"= {self.dmgTotal} to {locationTextNames[self.loc]}",True,black)
        else:
            line=monospacedMediumLarge.render(f"{self.dmgTotal} to {locationTextNames[self.loc]}",True,black)

        screen.blit(line,(x+offset,y))
        offset=0
        if not self.degraded and self.through==0:
            if self.unit.barrier.sp>0 and self.unit.barrier.covers[self.loc]:
                screen.blit(monospacedMedium.render(f"Absorbed by barrier",True,DARKGREY),(x,y+23))
            else:
                screen.blit(monospacedMedium.render(f"Did not degrade",True,DARKGREY),(x,y+23))
        elif self.through==0:
            screen.blit(monospacedMedium.render(f"Degraded",True,DARKGREY),(x,y+23))
        else:
            screen.blit(monospacedMedium.render("Dealt",True,black),(x,y+23))
            offset+=60
            
            if self.through>0:
                screen.blit(monospacedMediumLarge.render(f"{abs(self.through)}",True,woundColor),(x+offset,y+21))
                offset+=len(str(abs(self.through)))*14+4
                screen.blit(monospacedMedium.render(f"wound{'s' if self.through>1 else ''}",True,black),(x+offset,y+23))
                offset+=72
            else:
                screen.blit(monospacedMediumLarge.render(f"{abs(self.through)}",True,cyberColor),(x+offset,y+21))
                offset+=len(str(abs(self.through)))*14+4
                screen.blit(monospacedMedium.render(f"SDP damage",True,black),(x+offset,y+23))
                offset+=125

            if self.stunned:
                screen.blit(stunSmolImg,(x+offset,y+20))
                offset+=72
            if self.unconned:
                screen.blit(unconSmolImg,(x+offset,y+20))
                offset+=72
            if self.killed:
                screen.blit(deadSmolImg,(x+offset,y+20))
                offset+=72

        if self.critInjuries!=[]:
            text=""
            for injury in self.critInjuries:
                text+=f"+{injury.name}  "
            screen.blit(monospacedMedium.render(text,True,woundColor),(x,y+43))

        self.hitbox=undoImg.get_rect(center=(x+400,y+self.height//2))
        screen.blit(undoImg,self.hitbox)

class LoadLog:
    def __init__(self,unit:Unit,desc:str) -> None:
        self.hitbox=undoImg.get_rect(center=(1350,127))
        self.unit=deepcopy(unit)
        self.desc=desc

    def draw(self):
        screen.blit(monospacedMediumLarge.render(f"{self.desc.title()}",True,BLACK),(950,107))
        screen.blit(monospacedSmall.render(f"[{self.unit.armour.sp[0]}] [{self.unit.armour.sp[1]}] [{self.unit.armour.sp[2]}|{self.unit.armour.sp[3]}] [{self.unit.armour.sp[4]}|{self.unit.armour.sp[5]}], BODY-{self.unit.body}, COOL-{self.unit.cool}",True,BLACK),(950,134))
        screen.blit(undoImg,self.hitbox)

logHitbox=game.Rect(930,100,450,510)
logTextLabel=monospacedHuge.render("History",True,BLACK)
def drawLog():
    screen.blit(logTextLabel,logTextLabel.get_rect(center=(930+450//2,80)))
    drawTabs()
    frame(930,100,450,510,LIGHTGREY)
    offset=0
    for i in range(logIndex,len(logs)):
        offset+=logs[i].height+15
        if offset<=490:
            game.draw.line(screen,DARKGREY,(940,595-offset),(1360,595-offset),2)
            logs[i].draw(950,605-offset)
        else:
            logs[i].hitbox=None
    
    frame(930,100,450,56,LIGHTGREY)
    loadLog.draw()

    if logIndex>0:
        game.draw.polygon(screen,BLACK,((1100,580),(1155,600),(1210,580)))


class Tab:
    def __init__(self,loadLog:LoadLog,logs:list[Log]) -> None:
        self.loadLog=loadLog
        self.logs=logs
        self.mainHitbox=game.Rect(0,0,1,1)
        self.outerHitbox=game.Rect(0,0,1,1)
        self.duplicateHitbox=game.Rect(0,0,1,1)
        self.deleteHitbox=game.Rect(0,0,1,1)
        if self.logs==[]:
            self.currentUnit=deepcopy(loadLog.unit)
        else:
            self.currentUnit=deepcopy(logs[0].unit)

    def saveState(self):
        self.loadLog=loadLog
        self.logs=logs
        self.currentUnit=deepcopy(unit)

    def loadState(self):
        global loadLog,logs,unit
        loadLog=self.loadLog
        logs=self.logs 
        unit=deepcopy(self.currentUnit)

deleteImg=game.image.load('DT/delete.png').convert_alpha()
deleteImgHighlight=game.image.load('DT/delete.png').convert_alpha()
fill(deleteImgHighlight,WOUNDCOLOR)

duplicateImg=game.image.load('DT/duplicate.png').convert_alpha()
duplicateImgHighlight=game.image.load('DT/duplicate.png').convert_alpha()
fill(duplicateImgHighlight,DARKGREEN)

def drawTabs():
    for i in range(min(len(tabs),8)):
        x=760
        y=553-i*56
        tabs[i].mainHitbox=game.Rect(x,y,175,52)
        tabs[i].outerHitbox=game.Rect(x-80,y,255,52)
        tabs[i].duplicateHitbox=duplicateImg.get_rect(topleft=(x-32,y+12))
        tabs[i].deleteHitbox=deleteImg.get_rect(topleft=(x-64,y+12))
        
        if tabIndex==i:
            frameSelect(x,y,175,52,WHITE if game.Rect(x,y,175,52).collidepoint(game.mouse.get_pos()) else LIGHTGREY)
        else:
            frame(x,y,175,52,WHITE if game.Rect(x,y,175,52).collidepoint(game.mouse.get_pos()) else BASEGREY)  

        name=tabs[i].loadLog.desc.title()
        if len(name)>15:
            name=name[:12]+'...'
        screen.blit(monospacedSmall.render(name,True,BLACK),(x+6,y+6))

        critWounded=[False]*6
        for injury in tabs[i].currentUnit.critInjuries:
            critWounded[injury.loc]=True

        for j in range(6):
            if critWounded[j]:
                screen.blit(smallLimbImgsWounded[j],(x+138,y+4))
            elif tabs[i].currentUnit.cyber[j] is not None:
                if tabs[i].currentUnit.cyber[j].damaged:
                    screen.blit(smallLimbImgsCyberDamaged[j],(x+138,y+4))
                else:
                    screen.blit(smallLimbImgsCyber[j],(x+138,y+4))
            else:
                screen.blit(smallLimbImgs[j],(x+138,y+4))

        if tabs[i].currentUnit.dead:
            screen.blit(deadTinyImg,(x+6,y+22))
        elif tabs[i].currentUnit.uncon:
            screen.blit(unconTinyImg,(x+6,y+22))
        elif tabs[i].currentUnit.stunned:
            screen.blit(stunTinyImg,(x+6,y+22))
        
        if tabs[i].outerHitbox.collidepoint(game.mouse.get_pos()):
            if tabs[i].duplicateHitbox.collidepoint(game.mouse.get_pos()):
                screen.blit(duplicateImgHighlight,(x-32,y+12))
            else:
                screen.blit(duplicateImg,(x-32,y+12))

            if tabs[i].deleteHitbox.collidepoint(game.mouse.get_pos()):
                screen.blit(deleteImgHighlight,(x-64,y+12))
            else:
                screen.blit(deleteImg,(x-64,y+12))

        wounds=tabs[i].currentUnit.wounds
        if wounds>0:
            game.draw.line(screen,WOUNDCOLOR,(x+3,y+46),(x+3+min(50,max(0,wounds))/50*169,y+46),4)

debugImg=game.image.load('DT/smolParticle.png').convert_alpha()
fill(debugImg,(255,0,255))

crossImg=game.image.load('DT/cross.png').convert_alpha()
fill(crossImg,(255,0,0))

traceBlueImg=game.image.load('DT/tinyParticle.png').convert_alpha()
traceYellowImg=game.image.load('DT/tinyParticle.png').convert_alpha()
traceRedImg=game.image.load('DT/tinyParticle.png').convert_alpha()
traceWoundImg=game.image.load('DT/tinyParticle.png').convert_alpha()
fill(traceBlueImg,TRACEBLUE)
fill(traceYellowImg,TRACEYELLOW)
fill(traceRedImg,TRACERED)
fill(traceWoundImg,WOUNDCOLOR)

luckParticleImg=game.image.load('DT/particle.png').convert_alpha()
fill255(luckParticleImg,LUCKGREEN)

particleImg=game.image.load('DT/smolParticle.png').convert_alpha()
bloodImg=game.image.load('DT/smolParticle.png').convert_alpha()
bloodImg.fill(WOUNDCOLOR)

sparkImg=game.image.load('DT/spark.png').convert_alpha()
sparkImg.fill(TRACEYELLOW)

class Particle:
    def __init__(self,loc:tuple[int],type:str):
        self.x,self.y=loc
        self.r=0
        self.type=type.lower()
        self.dx=0
        self.dy=0
        self.ry=0
        self.damp=1
        if self.type=='blood':
            self.surface=bloodImg
            self.lifetime=int(0.5*30)
            self.dx=uniform(-6,6)
            self.dy=uniform(-10,2)

        elif self.type=='tink':
            self.surface=particleImg
            self.lifetime=int(0.25*30)
            self.dx=uniform(-10,10)
            self.dy=uniform(-10,10)

        elif self.type=='cross':
            self.surface=crossImg
            self.lifetime=int(1.2*30)
            self.ry=20

        elif self.type=='spark':
            self.surface=sparkImg
            self.lifetime=int(0.9*30)
            self.dx=uniform(-6,6)
            self.dy=uniform(-6,6)
            self.damp=1.15

        elif self.type=='luck':
            self.surface=luckParticleImg
            self.lifetime=int(0.9*30)
            self.dx=uniform(-6,6)
            self.dy=uniform(-6,6)
            self.damp=1.15
        
        elif 'trace' in self.type:
            if 'yellow' in self.type:
                self.surface=traceYellowImg
            elif 'red' in self.type:
                self.surface=traceRedImg
            elif 'blue' in self.type:
                self.surface=traceBlueImg
            elif 'wound' in self.type:
                self.surface=traceWoundImg
            else:
                raise '@@ TRACE ERROR @@'
            self.lifetime=int(2.5*30)
        
        else:
            raise "@@ BAD PARTICLE TYPE @@"

    def update(self):
        if self.lifetime<=0:
            particles.remove(self)
        self.lifetime-=1

        self.rect=self.surface.get_rect(center=(self.x,self.y))
        if 'trace' in self.type:
            self.surface.set_alpha(int(min(200,self.lifetime*15)))
        else:
            self.surface.set_alpha(int(min(255,self.lifetime*52)))
        if self.type=='cross' or self.type=='spark':
            blitSurface,self.rect=rot_center(self.surface,self.r,self.rect[0],self.rect[1])
        else:
            blitSurface=self.surface
        screen.blit(blitSurface,self.rect)
        self.x+=self.dx
        self.y+=self.dy
        self.r+=self.ry
        self.dx/=self.damp
        self.dy/=self.damp

        if self.type=='blood':
            self.dy+=1
        elif self.type=='cross':
            self.ry=max(self.ry/1.09,0.5)
        elif self.type=='spark':
            self.r=(self.r+randint(-50,50))%360


class Trace:
    def __init__(self,loc:tuple[int],minY):
        self.minY=minY
        self.x,self.y=loc
        self.dx=0
        self.dy=-3
        self.decisionTimer=0

    def update(self):
        if self.y<self.minY:
            traces.remove(self)

        if self.decisionTimer<=0:
            if self.dy==0:
                self.dy=-2
                self.dx=0
            elif random()<.2:
                self.dy=0
                self.dx=-2 if random()<.5 else 2

            self.decisionTimer=randint(3,25)
        else:
            self.decisionTimer-=1


        for i in range(6):
            if unit.cyber[i] is not None and limbInnerCollision(i,(self.x,self.y)):
                if unit.cyber[i].broken:
                    particles.append(Particle((self.x,self.y),'tracered'))
                elif unit.cyber[i].damaged:
                    particles.append(Particle((self.x,self.y),'traceyellow'))
                else:
                    particles.append(Particle((self.x,self.y),'traceblue'))
        self.x+=self.dx
        self.y+=self.dy

def rot_center(image, angle, x, y):
    rotated_image = game.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center = image.get_rect(center = (x, y)).center)

    return rotated_image, new_rect

def drawTraces(x,y,dx,dy):
    global traceTimer
    for trace in traces:
        trace.update()

    if traceTimer<=0:
        traceTimer=int(TRACEDELAY*30)
        traces.append(Trace((randint(x,x+dx),y+dy),y))
    else:
        traceTimer-=1

############### MECHANICAL BELOW

def loadFromDict():
    newUnit=Unit(weapon,findArmour([10,10,10,10,8,8]),0,loadDict['body'],loadDict['cool'],cyber=loadDict['cyber'])
    newUnit.armour.sp=deepcopy(loadDict['sp'])
    newUnit.armour.spMax=deepcopy(loadDict['sp'])
    
    hardness=[]
    for isHard in loadDict['hard']:
        hardness.append('hard' if isHard else 'soft')
    newUnit.armour.type=hardness

    newLoadLog=LoadLog(newUnit,loadDict['name'])
    
    tabs.append(Tab(newLoadLog,[]))
    global tabIndex
    tabIndex=len(tabs)-1
    tabs[tabIndex].loadState()

def duplicateTabAt(index:int):
    tabs.insert(index+1,deepcopy(tabs[tabIndex]))

def deleteTabAt(index:int):
    global tabIndex
    tabs.remove(tabs[index])
    if tabIndex==index:
        tabIndex=0
        if tabs==[]:
            tabs.append(Tab(LoadLog(Unit(None,findArmour([14,14,14,14,10,10]),0,7,7,cyber=[0,0,0,0,0,0]),'Default'),[]))
        tabs[tabIndex].loadState()
    elif tabIndex>index:
        tabIndex-=1

def processDamage():
    dmg=0
    rolled=[]
    more=0
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
                    result=randint(1,int(dieType))
                    rolled.append(result)
                    dmg+=result
            else:#its just a number
                more+=int(item)
                dmg+=int(item)
      
    except:
        raise "@@FAILED DMG EVAL@@"

    return (dmg,rolled,more)

def shoot():
    global shotTimer
    if shotTimer>5000:
        return

    shotTimer=0
    if damageInput.value=='':
        return
    multi=int(multiplierInput.value) if multiplierInput.value.isnumeric() else 1
    for _ in range(multi):
        if calledShotLoc==-1:
            loc=locationDie()
            if loc==0:
                loc=-2
        else:
            loc=calledShotLoc

        dmg,rolls,more=processDamage()

        shotQueue.insert(0,(loc,dmg,rolls,more,ammoIndex))

def runShot():
    global shotQueue,logIndex,shotTimer,shieldWiggle
    shotLoc,shotDmg,shotRolls,shotMore,shotAmmoIndex=shotQueue[-1]
    shotQueue=shotQueue[:-1]

    if shotLoc==-2:
        particles.append(Particle((133+148,63+76),'cross'))
        shotQueue.append((0,shotDmg,shotRolls,shotMore,shotAmmoIndex))
        if luckActive:
            particles[-1].lifetime=9999999
            shotTimer=9999999
        else:
            shotTimer=int(1.15*30)
    else:
        weapon.ammotype=ammoTypes[shotAmmoIndex]
        oldUnit=deepcopy(unit)
        unit.damage(weapon=weapon,dmg=shotDmg,loc=shotLoc)
        if oldUnit.wounds==unit.wounds and not oldUnit.uncon and unit.uncon:
            unit.uncon=False
        logs.insert(0,Log(shotLoc,shotDmg,shotRolls,shotMore,oldUnit,unit))

        if oldUnit.barrier.sp>0 and unit.barrier.covers[shotLoc]:
            shieldWiggle=10

        if unit.armour.sp[shotLoc]==0 or oldUnit.armour.sp[shotLoc]!=unit.armour.sp[shotLoc] or oldUnit.barrier.sp==0:
            limbWiggle[shotLoc]=10

        if oldUnit.barrier.sp>0 and oldUnit.armour.sp[shotLoc]==unit.armour.sp[shotLoc]:
            for _ in range(20):
                particles.append(Particle((361+randint(-20,20),429+randint(-20,20)),'tink'))
        elif logs[0].through!=0:
            for _ in range(logs[0].through*2):
                particles.append(Particle((133+woundPoints[shotLoc][0],63+woundPoints[shotLoc][1]),'blood'))
            for _ in range(logs[0].through*-2):
                particles.append(Particle((133+woundPoints[shotLoc][0],63+woundPoints[shotLoc][1]),'spark'))
        else:
            for _ in range(10):
                particles.append(Particle((133+woundPoints[shotLoc][0],63+woundPoints[shotLoc][1]),'tink'))
        logIndex=0
        shotTimer=int(SHOTDELAY*30)

shotTimer=0
traceTimer=0
ammoIndex=0
ammoTypes=[Ammo(),
           HP(),
           AP(),
           TMJ(),
           Explosive(),
           Incin(),
           API(),
           HEI(),
           FragFlechette(),
           Firecracker(),
           Cybercontrol(),
           CybercontrolSlug(),
           Slug(),
           Arrow()]

logIndex=0
calledShotLoc=-1
tabIndex=0

shotQueue:list[tuple]=[]
particles:list[Particle]=[]
traces:list[Trace]=[]
unitDicts:list[dict]=[]
try:
    unitDicts=generateUnitList()
except:
    print('@@@ FAILED TO INITIALIZE FIRESTORE @@@')



weapon=findGun("streetmaster")
unit=Unit(None,findArmour([14,14,14,14,10,10]),0,7,7,cyber=[0,0,0,0,0,0]) # manual load

logs:list[Log]=[]
loadLog:LoadLog=LoadLog(unit,"Default")
tabs:list[Tab]=[Tab(loadLog,logs)]

populateBody()
populateSPInputs()


while True: 
    if shotTimer==0 and shotQueue!=[]:
        runShot()
    elif shotTimer>0:
        shotTimer-=1

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
            bodySelected=bodyHitbox.collidepoint(game.mouse.get_pos())
            coolSelected=coolHitbox.collidepoint(game.mouse.get_pos())
            for i in range(51):
                if woundTrackHitBoxes[i].collidepoint(game.mouse.get_pos()):
                    unit.wounds=i
            if pewHitbox.collidepoint(game.mouse.get_pos()):
                shoot()

            for i in range(6):
                spInputsSelected[i]=spHitboxes[i].collidepoint(game.mouse.get_pos())

            if stunHudHitbox.collidepoint(game.mouse.get_pos()):
                unit.stunned=not unit.stunned
            elif unconHudHitbox.collidepoint(game.mouse.get_pos()):
                if unit.wounds<50:
                    if unit.dead:
                        unit.dead=False
                    elif unit.uncon:
                        unit.uncon=False

            for i in range(6):
                if limbCollision(i,game.mouse.get_pos()):
                    if calledShotLoc==i:
                        calledShotLoc=-1
                    else:
                        calledShotLoc=i

            for i in range(len(logs)):
                if logs[i].hitbox is not None and logs[i].hitbox.collidepoint(game.mouse.get_pos()):
                    unit=deepcopy(logs[i].unit)
                    logs=logs[i:]
                    logIndex=0
                    break
            
            if loadLog.hitbox.collidepoint(game.mouse.get_pos()):
                unit=deepcopy(loadLog.unit)
                logs=[]
                logIndex=0

            for i in range(4):
                if shieldCollision(i,game.mouse.get_pos()):
                    unit.barrier.covers[i+2]=not unit.barrier.covers[i+2]
                    unit.barrier.covers[0]=unit.barrier.covers[2] and unit.barrier.covers[3]
                    unit.barrier.covers[1]=unit.barrier.covers[2] and unit.barrier.covers[3]

            if barToggleHitbox.collidepoint(game.mouse.get_pos()):
                barrierActive=not barrierActive
                unit.barrier.covers=[True]*6

            if luckToggleHitbox.collidepoint(game.mouse.get_pos()):
                luckActive=not luckActive

            if shotTimer>5000:
                if luckRerollHitbox.collidepoint(game.mouse.get_pos()):
                    particles=[]
                    luckActive=False
                    loc=locationDie()
                    if loc==0:
                        loc=-2
                    _,shotDmg,shotRolls,shotMore,shotAmmoIndex=shotQueue[-1]
                    shotQueue=shotQueue[:-1]
                    shotQueue.append((loc,shotDmg,shotRolls,shotMore,shotAmmoIndex))
                    shotTimer=15
                    for _ in range(30):
                        particles.append(Particle((133+woundPoints[0][0]+randint(-10,10),63+woundPoints[0][1]+randint(-10,10)),'luck'))
                elif luckDontHitbox.collidepoint(game.mouse.get_pos()):
                    shotTimer=15
                    for particle in particles:
                        particle.lifetime=18

            if deflectionHitbox.collidepoint(game.mouse.get_pos()):
                unit.deflection=not unit.deflection

            if loadDict is not None:
                loadFromDict()
                loadInput.value=''

            for i in range(min(len(tabs),8)):
                if tabs[i].mainHitbox.collidepoint(game.mouse.get_pos()):
                    tabs[i].loadState()
                    tabIndex=i

            for i in range(len(tabs)):
                if tabs[i].duplicateHitbox.collidepoint(game.mouse.get_pos()):
                    duplicateTabAt(i)
                    break
                elif tabs[i].deleteHitbox.collidepoint(game.mouse.get_pos()):
                    deleteTabAt(i)
                    break

        if event.type == game.MOUSEBUTTONDOWN and game.mouse.get_pressed()[2]:
            for i in range(6):
                if spHitboxes[i].collidepoint(game.mouse.get_pos()):
                    unit.armour.type[i]='hard' if unit.armour.typeAt(i)=='soft' else 'soft'

            for i in range(6):
                if limbCollision(i,game.mouse.get_pos()):
                    if unit.cyber[i] is None:
                        unit.cyber[i]=CyberLimb(20)
                    elif unit.cyber[i].sdp==20:
                        unit.cyber[i]=CyberLimb(30)
                    else:
                        unit.cyber[i]=None
                
            if barValueHitbox.collidepoint(game.mouse.get_pos()) and barrierActive:
                unit.barrier.sp=0


        if event.type == game.MOUSEWHEEL:
            if coolHitbox.collidepoint(game.mouse.get_pos()):
                unit.cool=max(min(10,unit.cool+event.y),3)

            if barValueHitbox.collidepoint(game.mouse.get_pos()) and barrierActive:
                unit.barrier.sp=max(min(99,unit.barrier.sp+event.y),0)

            if bodyHitbox.collidepoint(game.mouse.get_pos()):
                unit.body=max(min(10,unit.body+event.y),3)
                unit.btm=bodyToBTM(unit.body)

            for i in range(6):
                if spHitboxes[i].collidepoint(game.mouse.get_pos()):
                    unit.armour.sp[i]=max(min(unit.armour.spMax[i],unit.armour.sp[i]+event.y),0)

            if ammoHitbox.collidepoint(game.mouse.get_pos()):
                ammoIndex=max(min(len(ammoTypes)-1,ammoIndex-event.y),0)

            if logHitbox.collidepoint(game.mouse.get_pos()):
                logIndex=max(logIndex+event.y,0)
            
            for i in range(6):
                if sdpHitboxes[i].collidepoint(game.mouse.get_pos()):
                    unit.cyber[i].setSDP(max(min(unit.cyber[i].maxSdp,unit.cyber[i].sdp+event.y),0))

        if event.type == game.KEYDOWN and event.key == game.K_RETURN:
            if damageSelected or multiplierSelected:
                shoot()
            for i in range(6):
                spInputsSelected[i]=False
            bodySelected=False
            coolSelected=False

            if loadSelected:
                for unitDict in unitDicts:
                    if loadInput.value.lower() in unitDict['name'].lower():
                        loadDict=unitDict
                        loadFromDict()
                        loadSelected=False
                        loadInput.value=''
                        break

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
                    spInputs[(i+1)%6].value=''
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

    if bodySelected:
        bodyInput.manager.cursor_pos=2
        bodyInput.update(events)
        unit.body=int(bodyInput.value if bodyInput.value.isnumeric() else 1)
        unit.btm=bodyToBTM(unit.body)
    else:
        bodyInput.cursor_visible=False
        bodyInput.value=str(unit.body)

    if coolSelected:
        coolInput.manager.cursor_pos=2
        coolInput.update(events)
        unit.cool=int(coolInput.value if coolInput.value.isnumeric() else 1)
    else:
        coolInput.cursor_visible=False
        coolInput.value=str(unit.cool)

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
    drawTraces(120,68,207,469)
    drawDude()
    drawSP(41,557,unit.armour.sp,unit.armour.spMax)

    bodyBlit()
    coolBlit()
    drawBar()
    drawLuck()
    drawDeflection()
    drawLog()
    loadBlit()

    drawWounds(unit.wounds)

    frame(WIDTH//2+45,645,WIDTH//2-75,HEIGHT-675,BASEGREY)
    damageBlit()
    multiplierBlit()
    pewBlit()
    ammoSpinner()

    for particle in particles:
        particle.update()

    drawReroll()

    drawInfoBox()

    #DEBUG
    screen.blit(debugImg,debugImg.get_rect(center=(tempX,tempY)))

    game.display.update() 
    clock.tick(30)

    if logs==[]:
        loadLog=LoadLog(unit,loadLog.desc)
    
    tabs[tabIndex].saveState()

    #system('cls')
    #print(round(clock.get_fps(),1))