import matplotlib.pyplot as plt
import copy
from math import ceil, floor
from random import choice,random

CLOSE_RANGE=15
CALLED_HEAD_PENALTY=8
BURST_BONUS=2
WOUND_CAP=50

class Gun:
    def __init__(self,name,wa,d6,more,rof,mag):
        self.name=name
        self.wa=wa
        self.d6=d6
        self.more=more
        self.rof=rof
        self.mag=mag
        self.currentAmmo=mag
    
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
        bulletsHit=self.attackRoll()+rof//10-(CLOSE_RANGE-1) # since 15 should be one hit, so 15-(15-1)=1
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
        
        
def compare(gun1,gun2,iterations,ws,sp,body):
    score1=0
    prototypeUser1=User(gun1,ws,sp,body)
    prototypeUser2=User(gun2,ws,sp,body)

    for _ in range(iterations):
        user1=copy.deepcopy(prototypeUser1)
        user2=copy.deepcopy(prototypeUser2)
        if(random() < .5):
            if(fightWinner(user1,user2)):
                score1+=1

        else:
            if(not fightWinner(user2,user1)):
                score1+=1

    return score1/iterations

def fightWinner(user1,user2): # returns true if the first user wins, false if the second user wins
    for _ in range(50):
        if(user1.attack(user2)):
            return True
        if(user2.attack(user1)):
            return False
        

def TTK(gun,iterations,ws,sp,body):
    totalTurns=0
    protoAttacker=User(gun,ws,sp,body)
    protoDummy=User(gun,ws,sp,body)
    for _ in range(iterations):
        attacker=copy.deepcopy(protoAttacker)
        dummy=copy.deepcopy(protoDummy)
        totalTurns+=fightLength(attacker,dummy)

    return totalTurns/iterations


TTK_TURN_LIMIT=12
def fightLength(attacker,dummy):
    turns=0
    for _ in range(TTK_TURN_LIMIT):
        turns+=1
        if(attacker.attack(dummy)):
            return turns
    return TTK_TURN_LIMIT


WEAPON_SKILL=15
SP=[[0]*6,[6]*6,[8]*6,[10]*6,[12]*6,[14]*6,[16]*6,[18]*6,[20]*6,[22]*6,[25]*6]
SP_LABELS=[0,6,8,10,12,14,16,18,20,22,25,28,32]
BODY=7

def plotAgainst(baseline,guns):
    results=[]
    for gun in guns:
        result=[]
        for i in range(len(SP)):
            result.append(compare(gun,baseline,3000,WEAPON_SKILL,SP[i],BODY))

        results.append(result)

    plt.gca().set_xticks(range(len(SP_LABELS)))
    plt.gca().set_xticklabels(SP_LABELS)
    plt.ylabel(f"% winrate baseline ({baseline.name})")
    plt.xlabel("SP All")
    for i in range(len(results)):
        plt.plot(results[i],label=guns[i].name)
    plt.axhline(y=0.5, color='r', linestyle='dotted')
    plt.legend()


def plotTTK(guns):
    results=[]
    for gun in guns:
        result=[]
        for i in range(len(SP)):
            result.append(TTK(gun,3000,WEAPON_SKILL,SP[i],BODY))

        results.append(result)

    plt.gca().set_xticks(range(len(SP_LABELS)))
    plt.gca().set_xticklabels(SP_LABELS)
    plt.ylabel(f"TTK in turns")
    plt.xlabel("SP All")
    for i in range(len(results)):
        plt.plot(results[i],label=guns[i].name)
    plt.axhline(y=1, color='r', linestyle='dotted')
    plt.axhline(y=4, color='b', linestyle='dotted')
    plt.legend()

if __name__=="__main__":
    guns=[]
    #guns.append(Gun("Darra",0,4,2,10,20))
    #guns.append(Gun("Viper",0,2,3,30,60))
    
    #guns.append(Gun("Evo Auto",2,3,3,20,35))
    #guns.append(Gun("Evo Burst",2,3,3,3,35))
    #guns.append(Gun("Super Chief",2,4,3,1,5))
    #guns.append(Gun("AKR",-2,5,1,10,25))
    #guns.append(Gun("AKR Burst",-2,5,1,3,25))

    #guns.append(Gun("RPK Setup",-1,4,1,40,120))
    #guns.append(Gun("RPK NOT Setup",-3,4,1,10,120))

    #guns.append(Gun("M1911",0,3,1,2,7))
    
    #guns.append(Gun("SKS AIM+HS",1,4,3,-2,12))
    #guns.append(Gun("SKS HS",1,4,3,-1,12))
    #guns.append(Gun("SKS BURST",1,4,3,3,12))

    #guns.append(Gun("L96",0,5,3,1,4))
    #guns.append(Gun("L96 HS",0,5,3,-1,4))
    #guns.append(Gun("L96 AIM+HS",0,5,3,-2,4))

    #guns.append(Gun("Pumpy",4,5,3,1,6))
    #guns.append(Gun("Pumpy PB",1,7,3,1,6))
    #guns.append(Gun("Saiga",1,4,3,2,6))
    #guns.append(Gun("Saiga PB",-2,6,3,2,6))
    #guns.append(Gun("Slamfire",1,5,3,2,6))

    #guns.append(Gun("TripleTake",1,5,1,3,12))

    #guns.append(Gun("RPK",-1,4,1,40,120))
    #guns.append(Gun("Ares",-4,5,1,50,100))
    #guns.append(Gun("Odin",-3,6,1,50,200))
    #guns.append(Gun("MA70",-3,5,3,80,240))
    #guns.append(Gun("DP27",-1,6,1,47,47))
    guns.append(Gun("M249",-2,6,3,50,100))

    guns.append(Gun("Vandal",-1,6,1,10,25))
    guns.append(Gun("RAL",0,6,2,15,30))
    guns.append(Gun("MOX",2,5,1,10,20))

    #baseline=Gun("Slamfire",1,5,3,2,6)
    #baseline=Gun("SKS",1,4,3,2,12)
    #baseline=Gun("Viper",0,2,3,30,60)
    #baseline=Gun("Darra",0,4,2,10,20)
    baseline=Gun("RPK",-1,4,1,40,120)
    plotAgainst(baseline,guns)

    #plotTTK(guns)