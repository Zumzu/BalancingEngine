import pygame_textinput
import pygame as game
from sys import exit
from colour import Color
from copy import deepcopy
from os import system

from Modules.Base import Unit,bodyToBTM
from Modules.Generator import findGun,findArmour
from Modules.Ammo import *
from Modules.Dice import locationDie
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

#Cyberware
#Barrier
#Log

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
monospacedMediumLarge=game.font.SysFont('consolas',23)
monospacedMedium=game.font.SysFont('consolas',20)
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

limbImgs=dudeImgs()

#Cached versions of the limbs with the appropriate coloring
limbImgsWounded=dudeImgs()
limbImgsCalled=dudeImgs()
limbImgsHighlight=dudeImgs()
for i in range(6):
    fill(limbImgsWounded[i],WOUNDCOLOR)
    fill(limbImgsCalled[i],(10,50,200))
    fill(limbImgsHighlight[i],(200,200,200))

limbOffsets=[]
limbOffsets.append((76,1))
limbOffsets.append((51,60))
limbOffsets.append((-1,69))
limbOffsets.append((131,76))
limbOffsets.append((23,215))
limbOffsets.append((93,213))

stunImg=game.image.load('DT/HUD/stun.png').convert_alpha()
unconImg=game.image.load('DT/HUD/uncon.png').convert_alpha()
deadImg=game.image.load('DT/HUD/dead.png').convert_alpha()
zeroedImg=game.image.load('DT/HUD/zeroed.png').convert_alpha()

shirtImg=game.image.load('DT/HUD/shirt.png').convert_alpha()
shirt2Img=game.image.load('DT/HUD/shirt2.png').convert_alpha()

stunHudHitbox=game.Rect(40,40,64,64)
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
    
    totalSp=0
    totalSpMax=0
    for i in range(6):
        totalSp+=unit.armour.sp[i]
        totalSpMax+=unit.armour.spMax[i]

    if totalSp/totalSpMax<0.75:
        screen.blit(shirt2Img,(57,460))
    elif totalSp/totalSpMax<0.9:
        screen.blit(shirtImg,(57,460))

def limbCollision(i:int):
    x=133
    y=63
    width,height=limbImgs[i].get_size()
    mouseX,mouseY=game.mouse.get_pos()
    pixel=(mouseX-limbOffsets[i][0]-x, mouseY-limbOffsets[i][1]-y)
    if pixel[0]<0 or pixel[0]>=width or pixel[1]<0 or pixel[1]>=height:
        return False

    return not limbImgs[i].get_at(pixel)[3]==0

def drawDude():
    x=133
    y=63

    injured=[False]*6
    for injury in unit.critInjuries:
        injured[injury.loc]=True

    for i in range(6):
        if calledShotLoc==i:
            screen.blit(limbImgsCalled[i],(x+limbOffsets[i][0],y+limbOffsets[i][1]))
        elif injured[i]:
            screen.blit(limbImgsWounded[i],(x+limbOffsets[i][0],y+limbOffsets[i][1]))
        else:
            screen.blit(limbImgs[i],(x+limbOffsets[i][0],y+limbOffsets[i][1]))
        
        if limbCollision(i):
            screen.blit(limbImgsHighlight[i],(x+limbOffsets[i][0],y+limbOffsets[i][1]))

    drawPointer(1,x+105,y+85)
    drawPointer(2,x+31,y+151,True)
    drawPointer(3,x+170,y+150)
    drawPointer(4,x+51,y+334,True)
    drawPointer(5,x+135,y+327)    

injuryTextCache={}
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
                if injury.name not in injuryTextCache:
                    if injury.severity==0:
                        textColor=DARKGREEN
                    elif injury.severity==2:
                        textColor=WOUNDCOLOR
                    else:
                        textColor=BLACK
                    injuryTextCache[injury.name]=impactTiny.render(injury.name,True,textColor)
                screen.blit(injuryTextCache[injury.name],injuryTextCache[injury.name].get_rect(center=(x-70,y-40+verticalOffset)))
                verticalOffset-=14
    else:
        game.draw.line(screen, BLACK, (x,y), (x+30,y-30), 2)
        game.draw.line(screen, BLACK, (x+30,y-30), (x+100,y-30), 2)
        for injury in unit.critInjuries:
            if injury.loc==loc:
                if injury.name not in injuryTextCache:
                    if injury.severity==0:
                        textColor=DARKGREEN
                    elif injury.severity==2:
                        textColor=WOUNDCOLOR
                    else:
                        textColor=BLACK
                    injuryTextCache[injury.name]=impactTiny.render(injury.name,True,textColor)
                screen.blit(injuryTextCache[injury.name],injuryTextCache[injury.name].get_rect(center=(x+70,y-40+verticalOffset)))
                verticalOffset-=14



tempX=WIDTH//2
tempY=HEIGHT//2
pressedArrows=[False]*4

loadTextLabel=monospacedLarge.render("Load",True,BLACK)
loadInput=pygame_textinput.TextInputVisualizer()
loadInput.font_object=monospacedMedium
loadInput.manager.validator=(lambda x: len(x)<=21 and str(x).isprintable())
loadSelected=False
loadHitbox=game.Rect(550,42,246,36)
def loadBlit():
    screen.blit(loadTextLabel,(473,45))
    frame(550,42,246,36,LIGHTGREY)
    screen.blit(loadInput.surface,(556,50))


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
    screen.blit(damageTextLabel,(DAMAGEX+8,DAMAGEY+3))
    frame(DAMAGEX+6,DAMAGEY+33,116,46,LIGHTGREY)
    screen.blit(damageInput.surface,(DAMAGEX+12,DAMAGEY+42))

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

pewTextLabel=monospacedMedium.render("PEW!",True,BLACK)
pewPewTextLabel=monospacedMedium.render("PEW PEW!",True,BLACK)
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
    drawWoundTrack(60,670,WIDTH-150,4,wounds,greyWounds)
    if wounds>=50 and not woundsHitbox.collidepoint(game.mouse.get_pos()):
        s=game.Surface((WIDTH//2-15,HEIGHT-675),game.SRCALPHA)
        s.fill((30,30,30,200))
        screen.blit(s,(30,645))

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
        
        self.unit=deepcopy(newUnit)

        self.lines=[]
        diceString=""
        for dice in dmgRolled:
            diceString+=f"{dice} "
        if diceString=="":
            self.lines.append(monospacedMedium.render(f"{self.dmgTotal} to {locationTextNames[self.loc]}",True,BLACK))
        else:
            self.lines.append(monospacedMedium.render(f"{diceString}+{self.more} = {self.dmgTotal} to {locationTextNames[self.loc]}",True,BLACK))
        
        if not self.degraded:
            self.lines.append(monospacedMedium.render(f"Did not degrade",True,DARKGREY))
        elif self.through==0:
            self.lines.append(monospacedMedium.render(f"Dealt 0 wounds, degraded",True,DARKGREY))
        else:
            self.lines.append(monospacedMedium.render(f"Dealt {self.through} wounds",True,BLACK))

        self.lines.append(monospacedMedium.render(f"-",True,DARKGREY))

    def draw(self,x:int,y:int):
        lineSpace=0
        for line in self.lines:
            screen.blit(line,(x,y+lineSpace))
            lineSpace+=18

logs:list[Log]=[]

logTextLabel=monospacedHuge.render("History",True,BLACK)
def drawLog():
    screen.blit(logTextLabel,logTextLabel.get_rect(center=(930+450//2,80)))
    frame(930,100,450,510,LIGHTGREY)
    for i in range(len(logs)):
        game.draw.line(screen,DARKGREY,(940,540-i*65),(1360,540-i*65),2)
        logs[i].draw(950,545-i*65)

############### MECHANICAL BELOW

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


def pew():
    weapon.ammotype=ammoTypes[ammoIndex]
    if damageInput.value=='':
        return
    multi=int(multiplierInput.value) if multiplierInput.value.isnumeric() else 1
    for _ in range(multi):
        if logs==[]:
            oldUnit=deepcopy(unit)
        else:
            oldUnit=logs[-1].unit

        if calledShotLoc==-1:
            loc=locationDie()
        else:
            loc=calledShotLoc

        dmg,rolls,more=processDamage()

        unit.damage(weapon=weapon,dmg=dmg,loc=loc)
        logs.append(Log(loc,dmg,rolls,more,oldUnit,unit))

calledShotLoc=-1

ammoIndex=0
ammoTypes=[Ammo(),
           HP(),
           AP(),
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

weapon=findGun("streetmaster")
unit=Unit(None,findArmour([14,16,16,16,10,10]),0,8,9,cyber=[0,0,0,0,0,0])

populateBody()
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
            bodySelected=bodyHitbox.collidepoint(game.mouse.get_pos())
            coolSelected=coolHitbox.collidepoint(game.mouse.get_pos())
            for i in range(51):
                if woundTrackHitBoxes[i].collidepoint(game.mouse.get_pos()):
                    unit.wounds=i
            if pewHitbox.collidepoint(game.mouse.get_pos()):
                pew()

            for i in range(6):
                spInputsSelected[i]=spHitboxes[i].collidepoint(game.mouse.get_pos())

            if stunHudHitbox.collidepoint(game.mouse.get_pos()):
                unit.stunned=False

            for i in range(6):
                if limbCollision(i):
                    if calledShotLoc==i:
                        calledShotLoc=-1
                    else:
                        calledShotLoc=i

        if event.type == game.MOUSEBUTTONDOWN and game.mouse.get_pressed()[2]:
            for i in range(6):
                if spHitboxes[i].collidepoint(game.mouse.get_pos()):
                    unit.armour.type[i]='hard' if unit.armour.typeAt(i)=='soft' else 'soft'

        if event.type == game.MOUSEWHEEL:
            if coolHitbox.collidepoint(game.mouse.get_pos()):
                unit.cool=max(min(10,unit.cool+event.y),3)

            if bodyHitbox.collidepoint(game.mouse.get_pos()):
                unit.body=max(min(10,unit.body+event.y),3)
                unit.btm=bodyToBTM(unit.body)

            for i in range(6):
                if spHitboxes[i].collidepoint(game.mouse.get_pos()):
                    unit.armour.sp[i]=max(min(unit.armour.spMax[i],unit.armour.sp[i]+event.y),0)

            if ammoHitbox.collidepoint(game.mouse.get_pos()):
                ammoIndex=max(min(len(ammoTypes)-1,ammoIndex-event.y),0)

        if event.type == game.KEYDOWN and event.key == game.K_RETURN:
            if damageSelected or multiplierSelected:
                pew()
            for i in range(6):
                spInputsSelected[i]=False
            bodySelected=False
            coolSelected=False

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
    drawDude()
    drawSP(41,557,unit.armour.sp,unit.armour.spMax)

    loadBlit()
    bodyBlit()
    coolBlit()
    drawLog()

    drawWounds(unit.wounds)

    frame(WIDTH//2+45,645,WIDTH//2-75,HEIGHT-675,BASEGREY)
    damageBlit()
    multiplierBlit()
    pewBlit()
    ammoSpinner()

    game.display.update() 
    clock.tick(30)

    system('cls')
    print(round(clock.get_fps(),1))