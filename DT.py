import pygame as game
from sys import exit

#ZUMZU.DEV DOWN



game.init() 

background=game.image.load('DT/Hexagons.png')
WIDTH,HEIGHT=background.get_rect().size
screen = game.display.set_mode((WIDTH,HEIGHT)) 
background=background.convert_alpha()

game.display.set_caption("Damage Tracker Mk2")
game.display.set_icon(game.image.load('DT/EngineIco.png'))
font=game.font.Font(None,50)
  
def updateArrows(event):
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

headImg=game.image.load('DT/Body/Head.png').convert_alpha()
torsoImg=game.image.load('DT/Body/Torso.png').convert_alpha()
larmImg=game.image.load('DT/Body/Larm.png').convert_alpha()
rarmImg=game.image.load('DT/Body/Rarm.png').convert_alpha()
llegImg=game.image.load('DT/Body/Lleg.png').convert_alpha()
rlegImg=game.image.load('DT/Body/Rleg.png').convert_alpha()

tempX=WIDTH//2
tempY=HEIGHT//2
pressedArrows=[False,False,False,False]

tempText=font.render("Hello",True,(255,255,255))

def frame(x:int,y:int,dx:int,dy:int):
    game.draw.rect(screen, (30,30,30), game.Rect(x,y,dx,dy), border_radius=5)
    game.draw.rect(screen, (60,60,60), game.Rect(x+3,y+3,dx-6,dy-6), border_radius=1)

def drawDude(x:int,y:int):
    screen.blit(headImg,(x+76,y+1))
    screen.blit(torsoImg,(x+51,y+60))
    screen.blit(larmImg,(x-1,y+69))
    screen.blit(rarmImg,(x+131,y+76))
    screen.blit(llegImg,(x+23,y+215))
    screen.blit(rlegImg,(x+94,y+213))

while True: 
    for event in game.event.get(): 
        if event.type == game.QUIT: 
            print(round(tempX),"|",round(tempY))
            game.quit()
            exit()
        
        updateArrows(event)
    
    if pressedArrows[0]:
        tempX-=0.1
    if pressedArrows[1]:
        tempX+=0.1
    if pressedArrows[2]:
        tempY-=0.1
    if pressedArrows[3]:
        tempY+=0.1
    
    screen.blit(background,(0,0))
    frame(30,30,WIDTH-60,500)
    drawDude(52,43)
    
    #screen.blit(tempText,(tempX,tempY))

    game.display.update() 
