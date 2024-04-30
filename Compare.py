import matplotlib.pyplot as plt
import copy
from math import ceil, floor
from random import choice,random

import numpy as np

CLOSE_RANGE=15
CALLED_HEAD_PENALTY=8
BURST_BONUS=2
WOUND_CAP=50

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

def Instakill(gun,iterations,ws,sp,body):
    successes=0
    protoAttacker=User(gun,ws,sp,body)
    protoDummy=User(gun,ws,sp,body)
    for _ in range(iterations):
        attacker=copy.deepcopy(protoAttacker)
        dummy=copy.deepcopy(protoDummy)
        if(attacker.attack(dummy)):
            successes+=1

    return successes/iterations


TTK_TURN_LIMIT=50
def fightLength(attacker,dummy):
    turns=0
    for _ in range(TTK_TURN_LIMIT):
        turns+=1
        if(attacker.attack(dummy)):
            return turns
    return TTK_TURN_LIMIT


WEAPON_SKILLS=[8,9,10,11,12,13,14,15,16,17,18]
WS_LABELS=[8,9,10,11,12,13,14,15,16,17,18]
SP=[[0]*6,[6]*6,[8]*6,[10]*6,[12]*6,[14]*6,[16]*6,[18]*6,[20]*6,[22]*6,[25]*6]
SP_LABELS=[0,6,8,10,12,14,16,18,20,22,25,28,32]

BODY=7

def plotCompareOnArmour(baseline,guns):
    results=[]
    for gun in guns:
        result=[]
        for i in range(len(SP)):
            result.append(compare(gun,baseline,3000,WEAPON_SKILLS[4],SP[i],BODY))

        results.append(result)

    plt.gca().set_xticks(range(len(SP_LABELS)))
    plt.gca().set_xticklabels(SP_LABELS)
    plt.ylabel(f"% winrate baseline ({baseline.name})")
    plt.xlabel("SP All")
    for i in range(len(results)):
        plt.plot(results[i],label=guns[i].name)
    plt.axhline(y=0.5, color='r', linestyle='dotted')
    plt.legend()


def plotTTKonArmour(guns):
    results=[]
    for gun in guns:
        result=[]
        for i in range(len(SP)):
            result.append(TTK(gun,3000,WEAPON_SKILLS[4],SP[i],BODY))

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


def plotTTKonCost(guns,mark=None):
    cost=[]
    ttk=[]
    for gun in guns:
        if(gun.rof==1):
            color="tab:blue"
        elif(gun.rof==2):
            color="tab:green"
        elif(gun.rof==3):
            color="tab:orange"
        else:#auto
            color="tab:red"

        if(mark is not None and mark.lower() in gun.name.lower()):
            color="black"
        
        newCost=gun.cost
        newTTK=TTK(gun,3000,TTK_WS,TTK_SP,BODY)
        plt.scatter(newCost,newTTK,color=color,alpha=0.7,edgecolors='none')
        cost.append(newCost)
        ttk.append(newTTK)

    plt.axhline(y=1, color='r', linestyle='dotted')
    plt.axhline(y=3.5, color='b', linestyle='dotted')
    #plt.axvline(x=450, color='b', linestyle='dotted')
    plt.ylabel("TTK in turns")
    plt.xlabel("Cost of weapon")
    plt.title(f"TTK vs Cost for skill [{TTK_WS}] armour {TTK_SP}")
    
    #cost,ttk = zip(*sorted(zip(cost,ttk))) 
    #x=np.array(cost)
    #y=np.array(ttk)
    #a,b=np.polyfit(np.log10(x),y,1)
    #plt.plot(x,a*np.log10(x)+b,color='steelblue',linestyle='--')

def plotInstakillOnCost(guns,mark=None):
    for gun in guns:
        if(gun.rof==1):
            color="tab:blue"
        elif(gun.rof==2):
            color="tab:green"
        elif(gun.rof==3):
            color="tab:orange"
        else:#auto
            color="tab:red"

        if(mark is not None and mark.lower() in gun.name.lower()):
            color="black"
        
        plt.scatter(gun.cost,Instakill(gun,3000,TTK_WS,TTK_SP,BODY),color=color,alpha=0.7,edgecolors='none')

    plt.ylabel("Percentile chance to instantly kill")
    plt.xlabel("Cost of weapon")
    plt.title(f"Instakill vs Cost for skill [{TTK_WS}] armour {TTK_SP}")

def generateGunList(name):
    guns=[]
    with open(name,'r') as f:
        for line in f:
            data=line.split(",")
            guns.append(Gun(data[0],int(data[1]),int(data[2]),int(data[3]),int(data[4]),int(data[5]),int(data[6])))
    return guns

TTK_WS=12
#TTK_SP=[10,10,10,10,10,10]
TTK_SP=[14,14,14,14,10,10]
#TTK_SP=[18]*6

if __name__=="__main__":

    guns=generateGunList("Proposed.csv")
    #guns=generateGunList("OG.csv")
    #plotTTKonCost(guns,"LMG")
    plotInstakillOnCost(guns,"LMG")