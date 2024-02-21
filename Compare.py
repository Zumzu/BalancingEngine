import copy
from math import ceil, floor
from random import choice
import random

CLOSE_RANGE=15
CALLED_HEAD_PENALTY=8
BURST_BONUS=2
WOUND_CAP=50

class Gun:
    def __init__(self,wa,d6,more,rof,mag,rel):
        self.wa=wa
        self.d6=d6
        self.more=more
        self.rof=rof
        self.mag=mag
        self.currentAmmo=mag
        self.rel=rel
    
    def __str__(self) -> str:
        return f"{self.wa}wa, {self.d6}D6+{self.more}, {self.rof} | {self.mag}, {self.rel}"
    
    def getDamage(self):
        total=self.more
        for _ in range(self.d6):
            total+=self.rollD6()
        return total

    def rollD6(self):
        d6=[1,2,3,4,5,6]
        return choice(d6)
    

class User:
    def __init__(self,gun,ws,sp,body):
        self.gun=gun
        self.ws=ws
        self.sp=sp
        self.body=body

        self.btm=self.bodyToBTM()
        self.wounds=0
        self.stunned=False
        self.multiPenalty=0
    
    def attack(self,enemy): #handle reload and stun and shit
        self.multiPenalty=0

        if(self.unstun()):
            self.multiPenalty+=3

        if(self.stunned):
            return False

        if(self.gun.currentAmmo<min(self.gun.rof,10)): # if ammo is less than ROF, or 10 if ROF is greater than 10, then reload and apply multiaction
            self.gun.currentAmmo=self.gun.mag
            self.multiPenalty+=3

        if(self.gun.rof>=10):
            return self.fullAuto(enemy)
        
        elif(self.gun.rof==3):
            return self.burstAttack(enemy)
        
        else:
            return self.calledShotHead(enemy)
    
    def calledShotHead(self,enemy): # Called shot head, returns true if target dies, false otherwise
        self.gun.Currentammo-=1
        if(self.attackRoll()-CALLED_HEAD_PENALTY>=CLOSE_RANGE):
            if(enemy.damage(self.gun.getDamage(),0)):
                return True
        return False

    def normalAttack(self,enemy): # Just single fires as many times as it can up to 2, returns true if target dies, false otherwise
        for _ in range(max(self.gun.rof,2)):
            self.gun.Currentammo-=1
            if(self.attackRoll()>=CLOSE_RANGE):
                if(enemy.damage(self.gun.getDamage())):
                    return True
        return False
    
    def burstAttack(self,enemy): # Burst, returns true if target dies, false otherwise
        self.gun.Currentammo-=3
        if(self.attackRoll()+BURST_BONUS>=CLOSE_RANGE):
            loc=self.rollLocation()
            for _ in range(3):
                if(enemy.damage(self.gun.getDamage(),loc)):
                    return True
        return False

    def fullAuto(self,enemy): # Full auto, returns true if target dies, false otherwise
        rof=min(self.gun.currentAmmo,self.gun.rof)
        self.gun.currentAmmo-=rof
        bulletsHit=self.attackRoll()+rof//10-(CLOSE_RANGE-1) # since 15 should be one hit, so 15-(15-1)=1
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

        if(dmg>=8 and loc==0): # check if dies due to headshot
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
        
def compare(gun1,gun2,iterations,ws,sp,body):
    score1=0
    score2=0
    prototypeUser1=User(gun1,ws,sp,body)
    prototypeUser2=User(gun2,ws,sp,body)

    for _ in range(iterations):
        user1=copy.deepcopy(prototypeUser1)
        user2=copy.deepcopy(prototypeUser2)
        if(random.random() < .5):
            if(fight(user1,user2)):
                score1+=1
            else:
                score2+=1

        else:
            if(fight(user2,user1)):
                score2+=1
            else:
                score1+=1

    print(score1)
    print(score1/iterations)

    print(score2)
    print(score2/iterations)

def fight(user1,user2): # returns true if the first user wins, false if the second user wins
    for _ in range(30):
        if(user1.attack(user2)):
            return True
        if(user2.attack(user1)):
            return False

WEAPON_SKILL=14
SP=[12,12,12,12,10,10]
BODY=7

if __name__=="__main__":
    gun1=Gun(0,2,3,30,60,"vr") #viper
    gun2=Gun(0,4,2,10,20,"st") #darra
    compare(gun1,gun2,1000,WEAPON_SKILL,SP,BODY)
