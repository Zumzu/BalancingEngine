from math import ceil, floor
from copy import deepcopy
from Modules.Dice import d10E,d10EDown,d6,locationDie

CLOSE_RANGE=15
CALLED_HEAD_PENALTY=8
BURST_BONUS=2
WOUND_CAP=50

class Ammo:
    def __init__(self):
        self.pierceSP=0
    
    def bonusDamage(self,enemyUnit,loc:int):
        return 0
    
    def preferred(self,enemyUnit,loc:int):
        return False
    
    def onDamage(self,enemyUnit,loc:int):
        pass

    def postEffect(self,enemyUnit,loc:int):
        pass

class Gun:
    def __init__(self,name:str,cost:int,wa:int,d6:int,more:int,rof:int,mag:int,ammotype:Ammo):
        self.name=name
        self.cost=cost
        self.wa=wa
        self.d6=d6
        self.more=more
        self.rof=rof
        self.mag=mag
        self.currentAmmo=mag
        self.ammotype=ammotype
    
    def __str__(self) -> str:
        return f"{self.wa}wa, {self.d6}D6+{self.more}, {self.rof}|{self.mag}"

    def getDamage(self):
        total=self.more
        for _ in range(self.d6):
            total+=d6()
        return total
    
    def reload(self):
        self.currentAmmo=self.mag

    def expend(self,bullets=1):
        self.currentAmmo-=bullets

class Armour:
    def __init__(self,name,cost:int,sp,mv:int,ev:int,type='soft'):
        self.name=name
        self.cost=int(cost)
        sp=list(map(int,sp))
        self.sp=sp
        self.mv=abs(int(mv))
        self.ev=abs(int(ev))
        self.type=type
    
    def __str__(self) -> str:
        return f"{self.sp}, {self.mv} MV, {self.ev} EV"
    
class ArmourSet:
    def __init__(self,armour):
        self.armour=armour
        self.sp=[0]*6
        self.type=['soft']*6
        for a in armour:
            for i in range(6):
                if a.sp[i]!=0:
                    self.type[i]=a.type
                    self.sp[i]=a.sp[i]

        self.spMax=list(self.sp)

        self.ev=0
        for a in self.armour:
            self.ev+=a.ev

        self.mv=0
        for a in self.armour:
            self.mv+=a.mv

        self.cost=0
        for a in self.armour:
            self.cost+=a.cost

    def __str__(self) -> str:
        return f"[{self.sp[0]}] [{self.sp[1]}] [{self.sp[2]}|{self.sp[3]}] [{self.sp[4]}|{self.sp[5]}]"
    
    def reset(self):
        self.sp=list(self.spMax)

    def apply(self,loc:int,damage:int,preferred:bool,pierce:int):
        if preferred:
            output=max(0, damage-(self.sp[loc]//2-pierce))
        else:
            output=max(0, damage-(self.sp[loc]-pierce))

        if damage>=self.sp[loc]//2 and self.sp[loc]>0:
            self.sp[loc]-=1
            
        return output
    
    def typeAt(self,location):
        return self.type[location]
    
class CyberLimb:
    def __init__(self):
        pass

class Barrier:
    def __init__(self,sp:int,covers:tuple):
        self.sp=sp
        self.covers=covers

    def apply(self,loc:int,dmg:int):
        if loc not in self.covers:
            return dmg

        output=dmg-self.sp
        if self.sp>0:
            self.sp-=1
        return output
        

class Unit:
    def __init__(self,gun:Gun,armour:ArmourSet,ws:int,body:int,cool:int=-1):
        self.gun=deepcopy(gun)
        self.armour=deepcopy(armour)
        self.ws=ws
        self.body=body
        if cool==-1:
            self.cool=body
        else:
            self.cool=cool

        self.btm=bodyToBTM(body)
        self.wounds=0
        self.multiPenalty=0

        self.stunned=False
        self.aim=False
        self.uncon=False

    def __str__(self):
        i=0
        output=f"{self.gun.name}\n{self.armour}{'  -STUN-' if self.stunned else ''}{'  ##UNCON##' if self.uncon else ''}\n["
        for _ in range(self.wounds):
            i+=1
            output+="#"
            if(i%10==0):
                output+="]["
            elif(i%5==0):
                output+="|"
            if(i==50):
                break
        for _ in range(50-self.wounds):
            i+=1
            output+="."
            if(i%10==0):
                output+="]["
            elif(i%5==0):
                output+="|"
        return output[:-1]

    def reset(self):
        self.gun.reload()
        self.armour.reset()
        self.wounds=0
        self.multiPenalty=0
        self.aim=False
        self.stunned=False
        self.uncon=False

    
    def attack(self,enemy):
        self.multiPenalty=0

        if(self.unstun()):
            self.multiAction()

        if(self.stunned):
            return False

        if(self.gun.currentAmmo<min(abs(self.gun.rof),10)): # if ammo is less than ROF, or 10 if ROF is greater than 10, then reload and apply multiaction
            self.gun.reload()
            self.multiAction()

        elif(self.gun.rof==-1):
            return self.calledShotHead(enemy)

        elif(self.gun.rof>=10):
            return self.fullAuto(enemy)
        
        elif(self.gun.rof==3):
            return self.burstAttack(enemy)
        
        else:
            return self.normalAttack(enemy)
        
    def damage(self,attacker,loc=-1,dmg=-1): # returns true if unit died or went uncon, false otherwise
        if(loc==-1):
            loc=locationDie()

        if(dmg==-1):
            dmg=attacker.gun.getDamage()

        dmg+=attacker.gun.ammotype.bonusDamage(self,loc)

        dmg=self.armour.apply(loc,dmg, attacker.gun.ammotype.preferred(self,loc), attacker.gun.ammotype.pierceSP)

        if(dmg<=0): # return early if no damage
            return False

        if(loc==0): # double if head
            dmg*=2

        dmg=max(1,floor(dmg)-self.btm) # apply btm
        self.wounds+=dmg
        attacker.gun.ammotype.onDamage(self,loc)
        
        if (dmg>=8 and loc!=1) or dmg>=15 or self.wounds>=WOUND_CAP: # check if dies due to headshot or wound cap
            self.uncon=True
        
        attacker.gun.ammotype.postEffect(self,loc)

        if self.uncon:
            return True
        return self.rollStun() # otherwise as a last effort apply stun and return wether or not they die from it
    
    def directToBody(self,dmg):
        if dmg<=0: #return early if no damage
            return False
        
        self.wounds+=dmg
        if(self.wounds>=WOUND_CAP):
            self.uncon=True

        if self.uncon:
            return True
        return self.rollStun()
    
    def calledShotHead(self,enemy): # Called shot head, returns true if target dies, false otherwise
        self.gun.currentAmmo-=1
        if(self.attackRoll()-CALLED_HEAD_PENALTY>=CLOSE_RANGE):
            if(enemy.damage(self,0)):
                return True
        return False

    def normalAttack(self,enemy): # Just single fires as many times as it can up to 2, returns true if target dies, false otherwise
        for _ in range(min(self.gun.rof,2)):
            self.gun.expend()
            if(self.attackRoll()>=CLOSE_RANGE):
                if(enemy.damage(self)):
                    return True
        return False
    
    def burstAttack(self,enemy): # Burst, returns true if target dies, false otherwise
        self.gun.expend(3)
        if(self.attackRoll()+BURST_BONUS>=CLOSE_RANGE):
            loc=locationDie()
            for _ in range(3):
                if(enemy.damage(self,loc)):
                    return True
        return False

    def fullAuto(self,enemy): # Full auto, returns true if target dies, false otherwise
        rof=min(self.gun.currentAmmo,self.gun.rof)
        self.gun.expend(rof)
        bulletsHit=self.autoAttackRoll(rof)-(CLOSE_RANGE-1)
        
        bulletsHit=min(bulletsHit,rof)
        for _ in range(bulletsHit):
            if(enemy.damage(self)):
                return True
        return False
        
    def multiAction(self):
        self.multiPenalty += 2+self.armour.mv

    def attackRoll(self):
        output = d10E()
        output+= self.ws + self.gun.wa
        output-= self.armour.ev + self.multiPenalty + self.allNegative()
        return output
    
    def autoAttackRoll(self,rof):
        output = d10EDown()
        output+= self.ws + self.gun.wa + rof//10
        output-= self.armour.ev + self.multiPenalty + self.allNegative()
        return output

    def stunMod(self):
        return floor((self.wounds-1)/5)
    
    def allNegative(self):
        return max(floor((self.wounds-1)/5)-3,0)

    def rollStun(self):
        if(not self.stunned):
            if(d10E()>max(self.body,self.cool)-self.stunMod()):
                self.stunned=True

        if(self.stunned and self.wounds>15):
            if(d10E()>self.body-self.allNegative()):
                self.uncon=True
                return True

        return False

    def unstun(self): # unit attempts unstun, if they succeed stunned is set to false and this function returns true if they went from stunned to unstunned
        if(self.stunned):
            if(d10E()<=self.body-self.stunMod()):
                self.stunned=False
                return True
        return False 
    
    def cost(self):
        return self.gun.cost+self.armour.cost


def bodyToBTM(body):
    if(body>14):
        return 7
    elif(body>10):
        return 5
    elif(body<6):
        return ceil(body/2-1)
    else:
        return floor(body/2-1)