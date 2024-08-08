import pygame as pg

#ZUMZU.DEV DOWN

pg.init() 
  
# CREATING CANVAS 
canvas = pg.display.set_mode((1200, 800)) 
  
# TITLE OF CANVAS 
pg.display.set_caption("My Board") 
exit = False
  
while not exit: 
    for event in pg.event.get(): 
        if event.type == pg.QUIT: 
            exit = True
    pg.display.update() 