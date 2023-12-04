from random import choice
from math import floor,ceil

class Gun:
    def __init__(self,stats:list,ammo=None):
        self.name=stats[0]
        self.cost=stats[1]
        self.rarity=stats[2]
        self.wa=stats[3]
        self.d6=stats[4]
        self.more=stats[5]
        self.rof=stats[6]
        self.mag=stats[7]
        self.gunRange=stats[8]
        self.rel=stats[9]
        self.tooHandy=stats[10]
        self.ammo=ammo
        for stat in stats:
            if stat is None:
                raise ValueError(f"Value in gun is None!")
    
    def __str__(self) -> str:
        return f"{self.name}, {self.cost}, {self.rarity}, {self.wa}, {self.d6}D6+{self.more}, {self.rof} | {self.mag}, {self.gunRange}m, {self.rel}{'T' if self.rel=='S' else 'R'}, {2 if self.tooHandy==1 else 1}h"
        
def strToStat(input:str,delimiter=', '):
    input=str(input).split(delimiter)
    out=[]
    out.append(input[0])
    out.append(int(input[1]))
    out.append(input[2][0])
    out.append(int(input[3]))
    dmg=input[4].split("D6")
    out.append(int(dmg[0]))
    if(dmg[1]!=''):
        out.append(int(dmg[1][1:]))
    else:
        out.append(0)
    rofMag=input[5].split(" | ")
    out.append(int(rofMag[0]))
    out.append(int(rofMag[1]))
    out.append(int(input[6].split('m')[0]))
    out.append(input[7][0])
    out.append(True if input[8 if delimiter==', ' else 9][0]=='2' else False)
    return out

def generateGunList(name:str):
    with open(name,'r') as f:
        for line in f:
            guns.append(Gun(strToStat(line,',')))

def d10():
    d10=[1,2,3,4,5,6,7,8,9,10]
    roll=choice(d10)
    total=roll

    if(roll==1):
        while(True):
            roll=choice(d10)
            total-=roll
            if(roll!=10):
                break

    elif(roll==10):
        while(True):
            roll=choice(d10)
            total+=roll
            if(roll!=10):
                break

    return total

def d6(count):
    d6=[1,2,3,4,5,6]
    total=0
    for _ in range(count):
        total+=choice(d6)
    return total

def d6F():
    d6F=[1,1,1,2,2,3]
    return choice(d6F)

def bodyToBTM(body):
    if(body>10):
        return 5
    elif(body<6):
        return ceil(body/2-1)
    else:
        return floor(body/2-1)
    
def stunMod(damageTaken):
    return floor((damageTaken-1)/5)


def HS(gun,ws,armour,rangeDC=15,body=7):
    damageTaken=0
    stunned=False
    ammo=gun.mag

    turns=0
    while(True):
        turns+=1
        if turns>=100:
            return 100
        if ammo==0:
            ammo=gun.mag
            continue
        
        ammo-=1
        if ws+gun.wa+d10()<rangeDC:
            continue

        dmg=d6(gun.d6)+gun.more
        if dmg>=armour//2:
            dmg-=armour
            if armour>0:
                armour-=1
            if dmg<=0:
                continue
        else:
            continue
            
        btm=bodyToBTM(body)
        dmg*=2
        if dmg-btm>=8:
            return turns
        damageTaken+=max(1,dmg-btm)
        if damageTaken>=50:
            return turns
        
        if(not stunned):
            if(d10()>body-stunMod(damageTaken)):
                stunned=True

        if(stunned and damageTaken>15):
            if(d10()>body+3-stunMod(damageTaken)):
                return turns

def avgHS(iterations,gun,ws,armour,rangeDC=15,body=7):
    total=0
    for _ in range(iterations):
        total+=HS(gun,ws,armour,rangeDC,body)
    return total/iterations 

def TTK(gun,ws,armour,rangeDC=15,body=7):
    locations=[0,1,1,1,1,1,2,3,4,5]
    currentArmour=[armour]*6
    damageTaken=0
    stunned=False
    ammo=gun.mag

    turns=0
    while(True):
        turns+=1
        if turns>=100:
            return 100
        bulletsHit=0
        if ammo<gun.rof and ammo<10:
            ammo=gun.mag
            continue
        
        if gun.rof<3:
            for _ in range(gun.rof):
                ammo-=1
                if ws+gun.wa+d10()>=rangeDC:
                    bulletsHit+=1
        elif gun.rof==3:
            ammo-=3
            if ws+gun.wa+d10()+3>=rangeDC:
                bulletsHit=d6F()
        else: #full auto
            rof=min(ammo,gun.rof)
            ammo-=rof
            if rangeDC==15:
                bulletsHit=ws+gun.wa+d10()+rof//10-14
            else:
                bulletsHit=ws+gun.wa+d10()+1-rof//10-rangeDC

            if bulletsHit<=0:
                continue
            elif bulletsHit>rof:
                bulletsHit=rof
        

        for _ in range(bulletsHit):
            loc=choice(locations)
            dmg=d6(gun.d6)+gun.more
            if dmg>=currentArmour[loc]//2:
                dmg-=currentArmour[loc]
                if currentArmour[loc]>0:
                    currentArmour[loc]-=1
                if dmg<=0:
                    continue
            else:
                continue
            
            btm=bodyToBTM(body)
            if loc==0:
                dmg*=2
                if dmg-btm>=8:
                    return turns
            damageTaken+=max(1,dmg-btm)

            if damageTaken>=50:
                return turns

            if(not stunned):
                if(d10()>body-stunMod(damageTaken)):
                    stunned=True
    
            if(stunned and damageTaken>15):
                if(d10()>body+3-stunMod(damageTaken)):
                    return turns
    
def avgTTK(iterations,gun,ws,armour,rangeDC=15,body=7):
    total=0
    for _ in range(iterations):
        total+=TTK(gun,ws,armour,rangeDC,body)
    return total/iterations 


def avgDMG(iterations,gun,ws,armour,rangeDC=15,body=7):
    locations=[0,1,1,1,1,1,2,3,4,5]
    ammo=gun.mag
    dmgTotal=0

    for _ in range(iterations):
        currentArmour=[armour]*6
        bulletsHit=0
        if ammo<gun.rof and ammo<10:
            ammo=gun.mag
            continue
        
        if gun.rof<3:
            for _ in range(gun.rof):
                ammo-=1
                if ws+gun.wa+d10()>=rangeDC:
                    bulletsHit+=1
        elif gun.rof==3:
            ammo-=3
            if ws+gun.wa+d10()+3>=rangeDC:
                bulletsHit=d6F()
        else: #full auto
            rof=min(ammo,gun.rof)
            ammo-=rof
            if rangeDC==15:
                bulletsHit=ws+gun.wa+d10()+rof//10-14
            else:
                bulletsHit=ws+gun.wa+d10()+1-rof//10-rangeDC

            if bulletsHit<=0:
                continue
            elif bulletsHit>rof:
                bulletsHit=rof
        

        for _ in range(bulletsHit):
            loc=choice(locations)
            dmg=d6(gun.d6)+gun.more
            if dmg>=currentArmour[loc]//2:
                dmg-=currentArmour[loc]
                if currentArmour[loc]>0:
                    currentArmour[loc]-=1
                if dmg<=0:
                    continue
            else:
                continue

            if loc==0:
                dmg*=2
                
            dmgTotal+=max(1,dmg-bodyToBTM(body))
    
    return dmgTotal/iterations


# Mook - Capable - Edgerunner - God
weaponSkills=[9,12,15,17,20]
armourSets=[6,12,14,16,18,20]

guns=[]
generateGunList('WeaponsRAW.txt')


for a in armourSets:
    with open(f'Armour_{a}.txt','w') as f:
        f.write(f"{"NAME":35} - ")
        for ws in weaponSkills:
            f.write(f"{f"Skill: {ws}":12}")
        f.write("\n")
        for gun in guns:
            f.write(f"{gun.name:35} - ")
            for ws in weaponSkills:
                f.write(f"{round(avgDMG(2000,gun,ws,a),1):12}")
            f.write(f"\n")
                
