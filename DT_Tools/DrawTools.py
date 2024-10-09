import pygame as game

BLACK=(0,0,0)
DARKERGREY=(30,30,30)

def charFrame(screen,x:int,y:int,dx:int,dy:int):
    game.draw.rect(screen, DARKERGREY, game.Rect(x,y,dx,dy), 4, border_radius=5)

    s=game.Surface((dx-6,dy-6),game.SRCALPHA)
    s.fill((180,180,180,230))
    screen.blit(s,(x+3,y+3))

def frame(screen,x:int,y:int,dx:int,dy:int,rgb:tuple):
    game.draw.rect(screen, DARKERGREY, game.Rect(x,y,dx,dy), border_radius=5)
    game.draw.rect(screen, rgb, game.Rect(x+3,y+3,dx-6,dy-6), border_radius=1)

def frameSelect(screen,x:int,y:int,dx:int,dy:int,rgb:tuple):
    game.draw.rect(screen, BLACK, game.Rect(x,y,dx,dy), border_radius=5)
    game.draw.rect(screen, rgb, game.Rect(x+3,y+3,dx-6,dy-6), border_radius=1)

def buttonFrame(screen,x:int,y:int,dx:int,dy:int,hover:bool):
    game.draw.rect(screen, DARKERGREY, game.Rect(x,y,dx,dy), border_radius=5)
    if hover:
        game.draw.rect(screen, (150,150,150), game.Rect(x+3,y+3,dx-6,dy-6), border_radius=1)
    else:
        game.draw.rect(screen, (80,80,80), game.Rect(x+3,y+3,dx-6,dy-6), border_radius=1)