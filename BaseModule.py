from math import ceil, floor
from random import choice,random

CLOSE_RANGE=15
CALLED_HEAD_PENALTY=8
BURST_BONUS=2
WOUND_CAP=50

def generateGunList(name='Scraped.csv'):
    guns=[]
    with open(name,'r') as f:
        for line in f:
            data=line.split(",")
            guns.append(Gun(data[0],int(data[1]),int(data[2]),int(data[3]),int(data[4]),int(data[5]),int(data[6])))
    return guns

class Gun:
    def __init__(self,name:str,cost:int,wa:int,d6:int,more:int,rof:int,mag:int):
        self.name=name
        self.cost=cost
        self.wa=wa
        self.d6=d6
        self.more=more
        self.rof=rof
        self.mag=mag
        self.currentAmmo=mag
    
    def __str__(self) -> str:
        return f"{self.wa}wa, {self.d6}D6+{self.more}, {self.rof}|{self.mag}"
    
    def getDamage(self):
        total=self.more
        for _ in range(self.d6):
            total+=self.rollD6()
        return total

    def rollD6(self):
        d6=[1,2,3,4,5,6]
        return choice(d6)
    

class User:
    def __init__(self,gun:Gun,ws:int,sp,body:int):
        self.gun=gun
        self.ws=ws
        self.sp=sp
        self.body=body

        self.btm=self.bodyToBTM()
        self.wounds=0
        self.stunned=False
        self.multiPenalty=0
        self.aim=False
    
    def attack(self,enemy): #handle reload and stun and shit
        self.multiPenalty=0

        if(self.unstun()):
            self.multiPenalty+=3

        if(self.stunned):
            return False

        if(self.gun.currentAmmo<min(self.gun.rof,10)): # if ammo is less than ROF, or 10 if ROF is greater than 10, then reload and apply multiaction
            self.gun.currentAmmo=self.gun.mag
            self.multiPenalty+=3

        if(self.gun.rof==-2):#stun doesnt cancel aim rn is fine, also unstun aim is possible etc
            if(self.aim):
                self.aim=False
                self.multiPenalty-=5
                return self.calledShotHead(enemy)
            else:
                self.aim=True
                return False

        elif(self.gun.rof==-1):
            return self.calledShotHead(enemy)

        elif(self.gun.rof>=10):
            return self.fullAuto(enemy)
        
        elif(self.gun.rof==3):
            return self.burstAttack(enemy)
        
        else:
            return self.normalAttack(enemy)
    
    def calledShotHead(self,enemy): # Called shot head, returns true if target dies, false otherwise
        self.gun.currentAmmo-=1
        if(self.attackRoll()-CALLED_HEAD_PENALTY>=CLOSE_RANGE):
            if(enemy.damage(self.gun.getDamage(),0)):
                return True
        return False

    def normalAttack(self,enemy): # Just single fires as many times as it can up to 2, returns true if target dies, false otherwise
        for _ in range(min(self.gun.rof,2)):
            self.gun.currentAmmo-=1
            if(self.attackRoll()>=CLOSE_RANGE):
                if(enemy.damage(self.gun.getDamage())):
                    return True
        return False
    
    def burstAttack(self,enemy): # Burst, returns true if target dies, false otherwise
        self.gun.currentAmmo-=3
        if(self.attackRoll()+BURST_BONUS>=CLOSE_RANGE):
            loc=self.rollLocation()
            for _ in range(3):
                if(enemy.damage(self.gun.getDamage(),loc)):
                    return True
        return False

    def fullAuto(self,enemy): # Full auto, returns true if target dies, false otherwise
        rof=min(self.gun.currentAmmo,self.gun.rof)
        self.gun.currentAmmo-=rof
        bulletsHit=self.attackRoll()+rof//10-(CLOSE_RANGE-1)
        
        bulletsHit=min(bulletsHit,rof)
        for _ in range(bulletsHit):
            if(enemy.damage(self.gun.getDamage())):
                return True
        return False


    def damage(self,dmg,loc=-1): # returns true if unit died or went uncon, false otherwise
        if(loc==-1):
            loc=self.rollLocation()

        dmg-=self.sp[loc] # factor SP
        if(dmg+self.sp[loc]>=self.sp[loc]/2 and self.sp[loc]>0):
            self.sp[loc]-=1 # degrade SP if applicable

        if(dmg<=0): # return early if no damage
            return False

        if(loc==0): # double if head
            dmg*=2

        dmg=max(1,floor(dmg)-self.btm) # apply btm

        if(dmg>=8 and loc!=1): # check if dies due to headshot
            #CURRENTLY TUNED FOR CRITICAL INJURY TREATED AS KILL
            return True
        
        self.wounds+=dmg
        if(self.wounds>=WOUND_CAP): # apply wounds and check if unit goes off the wound track
            return True
        
        return self.rollStun() # otherwise as a last effort apply stun and return wether or not they die from it

    def bodyToBTM(self):
        if(self.body>14):
            return 7
        elif(self.body>10):
            return 5
        elif(self.body<6):
            return ceil(self.body/2-1)
        else:
            return floor(self.body/2-1)
        
    def d10(self): # d10 result factoring explosions
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

    def rollLocation(self):
        locations=[0,1,1,1,1,1,2,3,4,5]
        return choice(locations)
    
    def attackRoll(self):
        return self.ws+self.d10()+self.gun.wa-self.allNegative()-self.multiPenalty

    def stunMod(self):
        return floor((self.wounds-1)/5)
    
    def allNegative(self):
        return max(floor((self.wounds-1)/5)-3,0)

    def rollStun(self):
        if(not self.stunned):
            if(self.d10()>self.body-self.stunMod()):
                self.stunned=True

        if(self.stunned and self.wounds>15):
            if(self.d10()>self.body-self.allNegative()):
                return True

        return False

    def unstun(self): # unit attempts unstun, if they succeed stunned is set to false and this function returns true if they went from stunned to unstunned
        if(self.stunned):
            if(self.d10()<=self.body-self.stunMod()):
                self.stunned=False
                return True
        return False 