import pygame as game

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

def rot_center(image, angle, x, y):
    rotated_image = game.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center = image.get_rect(center = (x, y)).center)

    return rotated_image, new_rect

# Batch generators below

def dudeImgs():
    output=[]
    output.append(game.image.load('DT_Images/Body/Head.png').convert_alpha())
    output.append(game.image.load('DT_Images/Body/Torso.png').convert_alpha())
    output.append(game.image.load('DT_Images/Body/Larm.png').convert_alpha())
    output.append(game.image.load('DT_Images/Body/Rarm.png').convert_alpha())
    output.append(game.image.load('DT_Images/Body/Lleg.png').convert_alpha())
    output.append(game.image.load('DT_Images/Body/Rleg.png').convert_alpha())
    return output

def smallDudeImgs():
    output=[]
    output.append(game.image.load('DT_Images/Body/SmallBody/Head.png').convert_alpha())
    output.append(game.image.load('DT_Images/Body/SmallBody/Torso.png').convert_alpha())
    output.append(game.image.load('DT_Images/Body/SmallBody/Larm.png').convert_alpha())
    output.append(game.image.load('DT_Images/Body/SmallBody/Rarm.png').convert_alpha())
    output.append(game.image.load('DT_Images/Body/SmallBody/Lleg.png').convert_alpha())
    output.append(game.image.load('DT_Images/Body/SmallBody/Rleg.png').convert_alpha())
    return output

def shieldImgs():
    output=[]
    output.append(game.image.load('DT_Images/HUD/Shield/shieldLarm.png').convert_alpha())
    output.append(game.image.load('DT_Images/HUD/Shield/shieldRarm.png').convert_alpha())
    output.append(game.image.load('DT_Images/HUD/Shield/shieldLleg.png').convert_alpha())
    output.append(game.image.load('DT_Images/HUD/Shield/shieldRleg.png').convert_alpha())
    return output