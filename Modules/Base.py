from math import ceil,floor,inf
from copy import deepcopy
from abc import ABC,abstractmethod

from Modules.Dice import d10E,d10EDown,d6,locationDie
from Modules.Injury import critInjuryRoll,doubleCritInjuryRoll

CLOSE_RANGE=15
CALLED_HEAD_PENALTY=8
BURST_BONUS=2
WOUND_CAP=50

class Ammo:
    def __init__(self):
        self.name='Normal'
        self.desc='~'
        self.pierceSP=0
        self.pierceBar=0
        self.cybercontrol=False

    def bonusDamage(self,enemyUnit,loc:int):
        return 0
    
    def spMultiplier(self,enemyUnit,loc:int):
        return 1
    
    def onDamage(self,enemyUnit,loc:int):
        pass

    def postContact(self,enemyUnit,loc:int):
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
    
    def spMultiplier(self,enemyUnit,loc:int):
        return 1
    
    def onDamage(self,enemyUnit,loc:int):
        pass

    def postContact(self,enemyUnit,loc:int):
        pass

    def pierceSP(self):
        return 0
    
    def pierceBar(self):
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

    def spMultiplier(self,enemyUnit,loc:int):
        if self.pref=='none':
            return 1
        elif self.pref=='both':
            return 0.5
        elif self.pref=='mono':
            return 0.25 if enemyUnit.armour.typeAt(loc)=='soft' else 0.5
        elif self.pref=='soft':
            return 0.5 if enemyUnit.armour.typeAt(loc)=='soft' else 1
        elif self.pref=='hard' and enemyUnit.injuryThreshold[0]<12: #for inner skull
            return 0.5 if enemyUnit.armour.typeAt(loc)=='hard' else 1

        return 1
            

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
        bulletsHit=attacker.autoAttackRoll(rof)-CLOSE_RANGE
        
        bulletsHit=min(bulletsHit,rof)
        for _ in range(bulletsHit):
            target.damage(self)

    def bonusDamage(self,enemyUnit,loc:int):
        return self.ammotype.bonusDamage(enemyUnit,loc)
    
    def spMultiplier(self,enemyUnit,loc:int):
        return self.ammotype.spMultiplier(enemyUnit,loc)
    
    def onDamage(self,enemyUnit,loc:int):
        self.ammotype.onDamage(enemyUnit,loc)

    def postContact(self,enemyUnit,loc:int):
        self.ammotype.postContact(enemyUnit,loc)

    def pierceSP(self):
        return self.ammotype.pierceSP
    
    def pierceBar(self):
        return self.ammotype.pierceBar
    
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

    def apply(self,loc:int,damage:int,spMultiplier:int,pierce:int):
        output=max(0, damage-max(0,floor(self.sp[loc]*spMultiplier)-pierce))

        if damage>=self.sp[loc]//2 and self.sp[loc]>0: #POTENTIAL ISSUE? MONO CAN FAIL TO DEGRADE WHILE DAMAGING
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

    def setSDP(self,sdp:int):
        self.sdp=sdp
        self.damaged=self.sdp<=self.maxSdp//2
        self.broken=self.sdp==0

    def reset(self):
        self.sdp=self.maxSdp
        self.damaged=False
        self.broken=False

class Barrier:
    def __init__(self,sp:int,covers:list[bool]):
        self.sp=sp
        self.covers=covers

    def apply(self,loc:int,dmg:int,ignore:int):
        if not self.covers[loc]:
            return dmg

        output=max(dmg-max(self.sp-ignore,0),0)
        if self.sp>0 and dmg>=self.sp//2:
            self.sp-=1
        return output
    
class FragileBarrier(Barrier):
    def apply(self,loc:int,dmg:int,ignore:int):
        if not self.covers[loc]:
            return dmg
        
        if self.sp>=dmg:
            self.sp-=dmg
            return 0
        else:
            dmg-=self.sp
            self.sp=0
            return dmg
    

class Unit:
    def __init__(self,weapon:Weapon,armour:ArmourSet,ws:int,body:int,cool:int=-1,cyber:list[int]=[0,0,0,0,0,0],threshold:list[int]=[10,20,10,10,10,10],block:int=-1,breach:int=-1):
        self.weapon=deepcopy(weapon)
        self.armour=deepcopy(armour)
        self.ws=ws
        self.body=body
        if cool==-1:
            self.cool=body
        else:
            self.cool=cool

        self.block=block
        self.breach=breach

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
        self.barrier=Barrier(0,[True]*6)
        self.faceShield=Barrier(0,[True,False,False,False,False,False])
        self.injuryThreshold=threshold

        self.deflection=False
        self.decentralized=False
        self.ignoreWounds=0

        self.stunCallback=None
        self.unconCallback=None

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
        self.barrier=Barrier(0,[True]*6)

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
        
    def damage(self,weapon=None,loc:int=-1,dmg:int=-1,lethality=False): # returns true if unit died or went uncon, false otherwise
        if loc==-1:
            loc=locationDie()

        if dmg==-1:
            if weapon is None:
                raise 'No source of damage, both dmg and weapon are null'
            dmg=weapon.getDamage()
        
        contact=False

        if weapon is not None:
            dmg+=weapon.bonusDamage(self,loc)
            dmg=self.barrier.apply(loc,dmg,weapon.pierceBar())
            dmg=self.faceShield.apply(loc,dmg,weapon.pierceBar())
            if dmg>0:
                contact=True
            dmg=self.armour.apply(loc,dmg,weapon.spMultiplier(self,loc),weapon.pierceSP())
        else:
            dmg=self.barrier.apply(loc,dmg,0)
            dmg=self.faceShield.apply(loc,dmg,0)
            if dmg>0:
                contact=True
            dmg=self.armour.apply(loc,dmg,False,0)

        if dmg<=0 or self.injuryThreshold[loc]==0: # return early if no damage
            if weapon is not None and contact:
                weapon.postContact(self,loc)
            return False

        if self.cyber[loc] is None: # if not a cyberlimb
            if(loc==0): # double if head
                dmg*=2

            dmg=max(1,floor(dmg)-self.btm) # apply btm
            if self.deflection:
                dmg-=1
                if dmg<=0:
                    if weapon is not None and contact:
                        weapon.postContact(self,loc)
                    return False
            self.wounds+=dmg # apply wounds
            
            self._checkCritInjury(dmg,loc,lethality)
            
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
            weapon.postContact(self,loc)

        return self.uncon or self.critInjuries!=[]# otherwise as a last effort apply stun and return wether or not they die from it or gain a crit injury
    
    def _checkCritInjury(self,dmg,loc,lethality):
        for injury in self.critInjuries:
            if 'incomplete' in injury.name.lower() and injury.loc==loc:
                injury.breakIncomplete()

        target=self.injuryThreshold[loc]-2 if lethality and loc>0 else self.injuryThreshold[loc]
        if dmg>=target and not (self.decentralized and loc==1):
            if dmg>=target*2:
                self.critInjuries.append(doubleCritInjuryRoll(loc))
            else:
                self.critInjuries.append(critInjuryRoll(loc))
            if loc>1 and self.injuryThreshold[loc]>1:
                self.injuryThreshold[loc]-=1

        for injury in self.critInjuries:
            if 'spinal' in injury.name.lower() or 'bonk' in injury.name.lower():
                self.stun=True
                self.uncon=True
            elif 'headshot' in injury.name.lower():
                self.stun=True
                self.uncon=True
                self.dead=True
            elif 'dismember' in injury.name.lower():
                self.injuryThreshold[injury.loc]=0

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

    def stunMod(self):
        output=max(floor((self.wounds-self.ignoreWounds-1)/5),0)
        for injury in self.critInjuries:
            output+=injury.allNegative+injury.stunUnconPenalty
        return output
    
    def unconMod(self):
        output=self.allNegative()
        for injury in self.critInjuries:
            output+=injury.stunUnconPenalty

        if self.decentralized:
            output-=3

        return output
    
    def allNegative(self):
        output=max(floor((self.wounds-self.ignoreWounds-1)/5)-3,0)
        for injury in self.critInjuries:
            output+=injury.allNegative
        return output

    def rollStun(self):
        if not self.stunned:
            if self.stunCallback is not None:
                self.stunCallback(self.stunDV(),self.unconDV())
            elif d10E() < self.stunDV():
                self.stunned=True

        if not self.uncon and self.stunned and self.wounds-self.ignoreWounds>15:
            if self.unconCallback is not None:
                self.unconCallback(self.unconDV())
                if self.uncon:
                    return True
            elif d10E() < self.unconDV():
                self.uncon=True
                return True

        return False
    
    def stunDV(self):
        return 11+self.stunMod()-max(self.body,self.cool)
    
    def unconDV(self):
        return 11+self.unconMod()-self.body
    
    def blockDV(self):
        injuryAllNegative=0
        for injury in self.critInjuries:
            injuryAllNegative+=injury.allNegative
        return self.block-injuryAllNegative

    def breachDV(self):
        injuryAllNegative=0
        for injury in self.critInjuries:
            injuryAllNegative+=injury.allNegative
        return self.breach-injuryAllNegative*2

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
    
def bodyToBonusMeleeDamage(body):
    if body<=2:
        return -2
    elif body<=4:
        return -1
    elif body<=7:
        return 0
    elif body<=9:
        return +1
    elif body<=10:
        return +2
    elif body<=14:
        return +3
    else:
        return +5
    