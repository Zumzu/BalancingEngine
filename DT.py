import pygame_textinput
import pygame as game
from sys import exit

from Modules.Base import Unit
from Modules.Generator import findGun,findArmour

WIDTH=1429
HEIGHT=789

game.init() 

background=game.image.load('DT/Hexagons.png')
background=game.transform.scale(background,(WIDTH,HEIGHT))
screen = game.display.set_mode((WIDTH,HEIGHT)) 
background=background.convert_alpha()
game.display.set_caption("Damage Tracker Mk2")
game.display.set_icon(game.image.load('DT/EngineIco.png'))
monospacedLarge=game.font.SysFont('consolas',30)
monospaced=game.font.SysFont('consolas',20)
  
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
    game.draw.rect(screen, (30,30,30), game.Rect(x,y,dx,dy), border_radius=5)
    game.draw.rect(screen, (180,180,180), game.Rect(x+3,y+3,dx-6,dy-6), border_radius=1)

def buttonFrame(x:int,y:int,dx:int,dy:int):
    game.draw.rect(screen, (30,30,30), game.Rect(x,y,dx,dy), border_radius=5)
    game.draw.rect(screen, (220,220,220), game.Rect(x+3,y+3,dx-6,dy-6), border_radius=1)

def drawDude(x:int,y:int):
    screen.blit(headImg,(x+76,y+1))
    screen.blit(torsoImg,(x+51,y+60))
    screen.blit(larmImg,(x-1,y+69))
    screen.blit(rarmImg,(x+131,y+76))
    screen.blit(llegImg,(x+23,y+215))
    screen.blit(rlegImg,(x+94,y+213))
    
    #drawPointer(x+170,y+150)
    #drawPointer(x+135,y+327)
    #drawPointer(x+31,y+151,True)
    #drawPointer(x+55,y+321,True)

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

tempX=WIDTH//4
tempY=HEIGHT//4
pressedArrows=[False,False,False,False]

damageTrack1=monospaced.render("[#####][#####][###..][.....][.....]",True,(0,0,0))
damageTrack2=monospaced.render("[.....][.....][.....][.....][.....]",True,(0,0,0))

loadTextLabel=monospacedLarge.render("Load",True,(0,0,0))
loadInput=pygame_textinput.TextInputVisualizer()
loadInput.font_object=monospaced
loadSelected=False
loadHitbox=game.Rect(550,42,250,36)

while True: 
    events=game.event.get()
    for event in events: 
        if event.type == game.QUIT: 
            print(round(tempX),"|",round(tempY))
            game.quit()
            exit()

        if event.type == game.MOUSEBUTTONUP:
            loadSelected=loadHitbox.collidepoint(game.mouse.get_pos())

    if loadSelected:
        loadInput.update(events)
    else:
        loadInput.cursor_visible=False
    
        
    updateArrows(events)
    if pressedArrows[0]:
        tempX-=0.1
    if pressedArrows[1]:
        tempX+=0.1
    if pressedArrows[2]:
        tempY-=0.1
    if pressedArrows[3]:
        tempY+=0.1
    
    screen.blit(background,(0,0))
    frame(30,30,400,600)
    frame(460,30,WIDTH-490,600)
    drawDude(133,63)

    screen.blit(damageTrack1,(38,575))
    screen.blit(damageTrack2,(38,600))
    screen.blit(loadTextLabel,(473,45))
    buttonFrame(550,42,250,36)
    screen.blit(loadInput.surface,(556,50))

    game.display.update() 
