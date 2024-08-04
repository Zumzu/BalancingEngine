from math import ceil,floor,inf
from copy import deepcopy
from abc import ABC,abstractmethod

from Modules.Dice import d10E,d10EDown,d6,locationDie

CLOSE_RANGE=15
CALLED_HEAD_PENALTY=8
BURST_BONUS=2
WOUND_CAP=50

class Ammo:
    def __init__(self):
        self.pierceSP=0
        self.cybercontrol=False
    
    def bonusDamage(self,enemyUnit,loc:int):
        return 0
    
    def preferred(self,enemyUnit,loc:int):
        return False
    
    def onDamage(self,enemyUnit,loc:int):
        pass

    def postEffect(self,enemyUnit,loc:int):
        pass

class Weapon(ABC):
    def __init__(self) -> None:
        super().__init__()
        self.name=None
        self.cost=None
        self.wa=None
        self.d6=None
        self.more=None
        self.rof=None
    
    def getDamage(self):
        total=self.more
        for _ in range(self.d6):
            total+=d6()
        return total
    
    @abstractmethod
    def attack(self,attacker,enemy):
        pass

class Melee(Weapon):
    def __init__(self,name:str,cost:int,wa:int,d6:int,more:int,rof:int,sdp:int,preferred:str):
        self.name=name
        self.cost=cost
        self.wa=wa
        self.d6=d6
        self.more=more
        self.rof=rof
        self.sdp=sdp
        self.preferred=preferred

    def __str__(self) -> str:
        return f"{self.wa}wa, {self.d6}D6+{self.more}, {self.rof}, {self.preferred}"

    def attack(self,attacker,enemy):
        if self.rof==3:
            self.burstAttack(attacker,enemy)
        else:
            self.normalAttack(attacker,enemy)
    
    def normalAttack(self,attacker,target): # Just single fires as many times as it can up to 2, returns true if target dies, false otherwise
        #for _ in range(min(self.rof,2)):
        #    if(attacker.attackRoll()>=CLOSE_RANGE): #DEFENDER?
        #        if(target.damage(attacker)):
        #            return True
        return False

    def burstAttack(self,attacker,target): # Burst, returns true if target dies, false otherwise
        #if(attacker.attackRoll()+BURST_BONUS>=CLOSE_RANGE):
        #    loc=locationDie()
        #    for _ in range(3):
        target.damage(attacker)



class Gun(Weapon):
    def __init__(self,name:str,cost:int,wa:int,d6:int,more:int,rof:int,mag:int,ammotype:Ammo):
        self.name=name
        self.cost=cost
        self.wa=wa
        self.d6=d6
        self.more=more
        self.rof=rof
        if mag==-1:
            self.mag=inf
        else:
            self.mag=mag

        self.currentAmmo=mag
        self.ammotype=ammotype
    
    def __str__(self) -> str:
        return f"{self.wa}wa, {self.d6}D6+{self.more}, {self.rof}{('|'+str(self.mag)) if self.mag!=inf else ''}"
    
    def reload(self):
        self.currentAmmo=self.mag

    def attack(self,attacker,enemy):
        if(self.rof==-1):
            self.calledShotHead(attacker,enemy)
        elif(self.rof>=10):
            self.fullAuto(attacker,enemy)
        elif(self.rof==3):
            self.burstAttack(attacker,enemy)
        else:
            self.normalAttack(attacker,enemy)

    def calledShotHead(self,attacker,target): # Called shot head, returns true if target dies, false otherwise
        self.currentAmmo-=1
        if(attacker.attackRoll()-CALLED_HEAD_PENALTY>=CLOSE_RANGE):
            target.damage(attacker,0)

    def normalAttack(self,attacker,target): # Just single fires as many times as it can up to 2, returns true if target dies, false otherwise
        for _ in range(min(self.rof,2)):
            self.currentAmmo-=1
            if(attacker.attackRoll()>=CLOSE_RANGE):
                target.damage(attacker)
    
    def burstAttack(self,attacker,target): # Burst, returns true if target dies, false otherwise
        self.currentAmmo-=3
        if(attacker.attackRoll()+BURST_BONUS>=CLOSE_RANGE):
            loc=locationDie()
            for _ in range(3):
                target.damage(attacker,loc)

    def fullAuto(self,attacker,target): # Full auto, returns true if target dies, false otherwise
        rof=min(self.currentAmmo,self.rof)
        self.currentAmmo-=rof
        bulletsHit=attacker.autoAttackRoll(rof)-(CLOSE_RANGE-1)
        
        bulletsHit=min(bulletsHit,rof)
        for _ in range(bulletsHit):
            target.damage(attacker)

class Armour:
    def __init__(self,name:str,cost:int,sp,mv:int,ev:int,type:str='soft'):
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
    def __init__(self,armour:list[Armour]):
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
        self.mv=0
        self.cost=0
        for a in self.armour:
            self.ev+=a.ev
        for a in self.armour:
            self.mv+=a.mv
        for a in self.armour:
            self.cost+=a.cost

    def __str__(self) -> str:
        return f"[{self.sp[0]}] [{self.sp[1]}] [{self.sp[2]}|{self.sp[3]}] [{self.sp[4]}|{self.sp[5]}]"
    
    def reset(self):
        self.sp=list(self.spMax)

    def apply(self,loc:int,damage:int,preferred:bool,pierce:int):
        if preferred:
            output=max(0, damage-max(0,self.sp[loc]//2-pierce))
        else:
            output=max(0, damage-max(0,self.sp[loc]-pierce))

        if damage>=self.sp[loc]//2 and self.sp[loc]>0:
            self.sp[loc]-=1
            
        return output
    
    def typeAt(self,loc:int):
        return self.type[loc]
    
class CyberLimb:
    def __init__(self,sdp:int):
        self.sdp=sdp
        self.maxSdp=sdp
        self.damaged=False
        self.broken=False

    def __str__(self):
        return str(self.sdp)

    def damage(self,dmg):
        if dmg<=0:
            return 
        self.sdp=max(0,self.sdp-dmg)
        if self.sdp<=self.maxSdp//2:
            self.damaged=True
        if self.sdp==0:
            self.broken=True

    def reset(self):
        self.sdp=self.maxSdp
        self.damaged=False
        self.broken=False

class Barrier:
    def __init__(self,sp:int,covers:tuple[int]):
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
    def __init__(self,gun:Weapon,armour:ArmourSet,ws:int,body:int,cool:int=-1,cyber:list[int]=[0,0,0,0,0,0]):
        self.gun=deepcopy(gun)
        self.armour=deepcopy(armour)
        self.ws=ws
        self.body=body
        if cool==-1:
            self.cool=body
        else:
            self.cool=cool

        self.cyber=[]
        for c in cyber:
            self.cyber.append(CyberLimb(c) if c!=0 else None)
        assert self.cyber.__len__()==6

        self.btm=bodyToBTM(body)
        self.wounds=0
        self.multiPenalty=0

        self.stunned=False
        self.aim=False
        self.uncon=False

    def __str__(self):
        i=0
        output=f"{self.gun.name}  -  {str(self.gun)}  ({self.multiPenalty})\n{self.armour}{'  -STUN-' if self.stunned else ''}{'  ##UNCON##' if self.uncon else ''}\nCyber: ("
        for c in self.cyber:
            output+=f"{'-' if c is None else str(c)},"
        output+="\b)\n["
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
        for c in self.cyber:
            if c is not None:
                c.reset()

    def attack(self,enemy):
        self.multiPenalty=0

        if(self.unstun()):
            self.multiAction()

        if(self.stunned):
            return False

        if(self.gun.currentAmmo<min(abs(self.gun.rof),10)): # if ammo is less than ROF, or 10 if ROF is greater than 10, then reload and apply multiaction
            self.gun.reload()
            self.multiAction()

        self.gun.attack(self,enemy)
        return enemy.uncon
        
    def damage(self,attacker=None,loc:int=-1,dmg:int=-1): # returns true if unit died or went uncon, false otherwise
        if loc==-1:
            loc=locationDie()

        if dmg==-1:
            if attacker is None:
                raise 'No source of damage, both dmg and attacker are null'
            dmg=attacker.gun.getDamage()
        if attacker is not None:
            dmg+=attacker.gun.ammotype.bonusDamage(self,loc)
            dmg=self.armour.apply(loc,dmg, attacker.gun.ammotype.preferred(self,loc), attacker.gun.ammotype.pierceSP)
        else:
            dmg=self.armour.apply(loc,dmg,False,0)

        if(dmg<=0): # return early if no damage
            if attacker is not None:
                attacker.gun.ammotype.postEffect(self,loc)
            return False

        if self.cyber[loc] is None: # if not a cyberlimb
            if(loc==0): # double if head
                dmg*=2

            dmg=max(1,floor(dmg)-self.btm) # apply btm
            self.wounds+=dmg # apply wounds
            if attacker is not None:
                attacker.gun.ammotype.onDamage(self,loc)

            if (dmg>=8 and loc!=1) or dmg>=15 or self.wounds>=WOUND_CAP: # check if dies due to headshot or wound cap
                self.uncon=True #current assumption is that loss of limb is death
            self.rollStun()

        else: #limb is cyberlimb
            if attacker is not None:
                if attacker.gun.ammotype.cybercontrol:
                    dmg*=2
                    self.rollStun()
            self.cyber[loc].damage(dmg)
            if self.cyber[loc].broken:
                self.uncon=True #current assumption is that loss of limb is death

        if attacker is not None:
            attacker.gun.ammotype.postEffect(self,loc)
        return self.uncon# otherwise as a last effort apply stun and return wether or not they die from it
    
    def directToBody(self,dmg:int):
        if dmg<=0: #return early if no damage
            return False
        
        self.wounds+=dmg
        if(self.wounds>=WOUND_CAP):
            self.uncon=True

        if self.uncon:
            return True
        return self.rollStun()
        
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
            if(d10E()<=max(self.body,self.cool)-self.stunMod()):
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