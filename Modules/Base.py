from math import ceil,floor,inf
from copy import deepcopy
from abc import ABC,abstractmethod

from Modules.Dice import d10E,d10EDown,d6,locationDie
from Modules.Injury import critInjuryRoll

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
    
    def bonusDamage(self,enemyUnit,loc:int):
        return 0
    
    def preferred(self,enemyUnit,loc:int):
        return False
    
    def onDamage(self,enemyUnit,loc:int):
        pass

    def postEffect(self,enemyUnit,loc:int):
        pass

    def pierceSP(self):
        return 0
    
    def cybercontrol(self):
        return False

    def getDamage(self):
        total=self.more
        for _ in range(self.d6):
            total+=d6()
        return total
    
    @abstractmethod
    def attack(self,attacker,enemy):
        pass

class Melee(Weapon):
    def __init__(self,name:str,cost:int,wa:int,d6:int,more:int,rof:int,sdp:int,pref:str):
        self.name=name
        self.cost=cost
        self.wa=wa
        self.d6=d6
        self.more=more
        self.rof=rof
        self.sdp=sdp
        self.pref=pref.lower()
        self.broken=False

    def __str__(self) -> str:
        return f"{self.wa}wa, {self.d6}D6+{self.more}, {self.rof}, {self.pref.capitalize()}"

    def attack(self,attacker,enemy):
        if self.broken:
            return
        
        if self.rof==3:
            self._burstAttack(attacker,enemy)
        else:
            self._normalAttack(attacker,enemy)
    
    def _normalAttack(self,attacker,target): # Just single fires as many times as it can up to 2
        for _ in range(min(self.rof,2)):
            if target.dodge==-1:
                disparity=attacker.attackRoll()-target.blockRoll()
                if disparity>=5:
                    target.damage(self) #roll full damage through
                elif disparity>=0:
                    target.damage(dmg=target.weapon.damage(self.getDamage())) #roll damage against their weapon and excess goes through
            else:
                if attacker.attackRoll()>target.dodgeRoll():
                    target.damage(self) #roll full damage through
                 
    def _burstAttack(self,attacker,target): # Burst
        loc=locationDie()
        if target.dodge==-1:
            disparity=attacker.attackRoll()+BURST_BONUS-target.blockRoll()
            if disparity>=5:
                for _ in range(3):
                    target.damage(self,loc)
            elif disparity>=0:
                for _ in range(3):
                    target.damage(dmg=target.weapon.damage(self.getDamage()))
        else:
            if attacker.attackRoll()+BURST_BONUS>target.dodgeRoll():
                for _ in range(3):
                    target.damage(self,loc)
            

    def damage(self,dmg): # returns excess damage
        if self.broken:
            return dmg

        output=max(dmg-self.sdp,0)
        self.sdp=max(self.sdp-dmg,0)
        if self.sdp<=0:
            self.broken=True

        return output

    def preferred(self,enemyUnit,loc:int):
        if self.pref=='none':
            return False
        elif self.pref=='both' or self.pref=='mono': # temp mono
            return True
        
        return enemyUnit.armour.typeAt(loc)==self.pref



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
            self._calledShotHead(attacker,enemy)
        elif(self.rof>=10):
            self._fullAuto(attacker,enemy)
        elif(self.rof==3):
            self._burstAttack(attacker,enemy)
        else:
            self._normalAttack(attacker,enemy)

    def _calledShotHead(self,attacker,target): # Called shot head
        self.currentAmmo-=1
        if(attacker.attackRoll()-CALLED_HEAD_PENALTY>=CLOSE_RANGE):
            target.damage(self,0)

    def _normalAttack(self,attacker,target): # Just single fires as many times as it can up to 2
        for _ in range(min(self.rof,2)):
            self.currentAmmo-=1
            if(attacker.attackRoll()>=CLOSE_RANGE):
                target.damage(self)
    
    def _burstAttack(self,attacker,target): # Burst
        self.currentAmmo-=3
        if(attacker.attackRoll()+BURST_BONUS>=CLOSE_RANGE):
            loc=locationDie()
            for _ in range(3):
                target.damage(self,loc)

    def _fullAuto(self,attacker,target): # Full auto
        rof=min(self.currentAmmo,self.rof)
        self.currentAmmo-=rof
        bulletsHit=attacker.autoAttackRoll(rof)-(CLOSE_RANGE-1)
        
        bulletsHit=min(bulletsHit,rof)
        for _ in range(bulletsHit):
            target.damage(self)

    def bonusDamage(self,enemyUnit,loc:int):
        return self.ammotype.bonusDamage(enemyUnit,loc)
    
    def preferred(self,enemyUnit,loc:int):
        return self.ammotype.preferred(enemyUnit,loc)
    
    def onDamage(self,enemyUnit,loc:int):
        self.ammotype.onDamage(enemyUnit,loc)

    def postEffect(self,enemyUnit,loc:int):
        self.ammotype.postEffect(enemyUnit,loc)

    def pierceSP(self):
        return self.ammotype.pierceSP
    
    def cybercontrol(self):
        return self.ammotype.cybercontrol


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
    def __init__(self,weapon:Weapon,armour:ArmourSet,ws:int,body:int,cool:int=-1,dodge:int=-1,cyber:list[int]=[0,0,0,0,0,0]):
        self.weapon=deepcopy(weapon)
        self.armour=deepcopy(armour)
        self.ws=ws
        self.body=body
        if cool==-1:
            self.cool=body
        else:
            self.cool=cool
        self.dodge=dodge

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
        self.dead=False

        self.critInjuries=[]

    def __str__(self):
        i=0
        output=f"{self.weapon.name}  -  {str(self.weapon)}  ({self.multiPenalty})\n{self.armour}{'  -STUN-' if self.stunned else ''}{'  ##UNCON##' if self.uncon else ''}\nCyber: ("
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
        if type(self.weapon) is Gun:
            self.weapon.reload()
        self.armour.reset()
        self.wounds=0
        self.multiPenalty=0
        self.aim=False
        self.stunned=False
        self.uncon=False
        self.dead=False
        for c in self.cyber:
            if c is not None:
                c.reset()
        self.critInjuries=[]

    def attack(self,enemy):
        if self.uncon:
            return False
        
        self.multiPenalty=0

        if self.unstun():
            self.multiAction()

        if self.stunned:
            return False
        if type(self.weapon) is Gun:
            if self.weapon.currentAmmo<min(abs(self.weapon.rof),10): # if ammo is less than ROF, or 10 if ROF is greater than 10, then reload and apply multiaction
                self.weapon.reload()
                self.multiAction()

        self.weapon.attack(self,enemy)
        return enemy.uncon
        
    def damage(self,weapon=None,loc:int=-1,dmg:int=-1): # returns true if unit died or went uncon, false otherwise
        if loc==-1:
            loc=locationDie()

        if dmg==-1:
            if weapon is None:
                raise 'No source of damage, both dmg and weapon are null'
            dmg=weapon.getDamage()
        if weapon is not None:
            dmg+=weapon.bonusDamage(self,loc)
            dmg=self.armour.apply(loc,dmg, weapon.preferred(self,loc), weapon.pierceSP())
        else:
            dmg=self.armour.apply(loc,dmg,False,0)

        if(dmg<=0): # return early if no damage
            if weapon is not None:
                weapon.postEffect(self,loc)
            return False

        if self.cyber[loc] is None: # if not a cyberlimb
            if(loc==0): # double if head
                dmg*=2

            dmg=max(1,floor(dmg)-self.btm) # apply btm
            self.wounds+=dmg # apply wounds
            
            if loc==0 and dmg>=8:
                self.uncon=True
                self.dead=True
            elif loc!=1 and dmg>=8:
                self.critInjuries.append(critInjuryRoll(loc))
            elif loc==1 and dmg>=15:
                self.critInjuries.append(critInjuryRoll(loc))
            
            if self.wounds>=WOUND_CAP:
                self.uncon=True
                self.dead=True

            if weapon is not None:
                weapon.onDamage(self,loc)

            self.rollStun()

        else: #limb is cyberlimb
            if weapon is not None:
                if weapon.cybercontrol():
                    dmg*=2
                    self.rollStun()
            self.cyber[loc].damage(dmg)
            if self.cyber[loc].broken:
                self.uncon=True #current assumption is that loss of limb is death

        if weapon is not None:
            weapon.postEffect(self,loc)

        return self.uncon or self.critInjuries!=[]# otherwise as a last effort apply stun and return wether or not they die from it or gain a crit injury
    
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
        output+= self.ws + self.weapon.wa
        output-= self.armour.ev + self.multiPenalty + self.allNegative()
        for injury in self.critInjuries:
            output-=injury.attackPenalty
        return output
    
    def autoAttackRoll(self,rof):
        output = d10EDown()
        output+= self.ws + self.weapon.wa + rof//10
        output-= self.armour.ev + self.multiPenalty + self.allNegative()
        for injury in self.critInjuries:
            output-=injury.attackPenalty
        return output
    
    def dodgeRoll(self):
        if self.dodge==-1:
            raise "Dodge not set"
        output = d10E()
        output+= self.dodge
        output-= self.armour.ev + self.allNegative()
        return output
    
    def blockRoll(self): ## NOTE: DOES NOT FACTOR WEAPON SKILL
        output = d10E()
        output+= self.ws
        output-= self.armour.ev + self.allNegative()
        return output

    def stunMod(self):
        output=floor((self.wounds-1)/5)
        for injury in self.critInjuries:
            output+=injury.allNegative+injury.stunUnconPenalty
        return output
    
    def unconMod(self):
        output=self.allNegative()
        for injury in self.critInjuries:
            output+=injury.stunUnconPenalty
        return output
    
    def allNegative(self):
        output=max(floor((self.wounds-1)/5)-3,0)
        for injury in self.critInjuries:
            output+=injury.allNegative
        return output

    def rollStun(self):
        if(not self.stunned):
            if(d10E()>max(self.body,self.cool)-self.stunMod()):
                self.stunned=True

        if(self.stunned and self.wounds>15):
            if(d10E()>self.body-self.unconMod()):
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
        return self.weapon.cost+self.armour.cost


def bodyToBTM(body):
    if(body>14):
        return 7
    elif(body>10):
        return 5
    elif(body<6):
        return ceil(body/2-1)
    else:
        return floor(body/2-1)