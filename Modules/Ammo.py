from Modules.Base import Ammo,Unit
from Modules.Dice import d3,d6

class HP(Ammo):
    def __init__(self):
        super().__init__()
        self.name="Hollow Point"
        self.desc="Deals +2 damage against soft armour, Deals +6 damage against unarmoured locations"

    def bonusDamage(self,enemyUnit:Unit,loc:int):
        if enemyUnit.armour.sp[loc]==0:
            return 6
        elif enemyUnit.armour.typeAt(loc)=='soft':
            return 2
        return 0
    
class AP(Ammo):
    def __init__(self):
        super().__init__()
        self.name="Armour Piercing"
        self.desc="Deals +4 damage against hard armour"

    def bonusDamage(self,enemyUnit:Unit,loc:int):
        if enemyUnit.armour.typeAt(loc)=='hard':
            return 4
        return 0
    
class TMJ(Ammo):
    def __init__(self):
        super().__init__()
        self.name="Total Metal Jacket"
        self.desc="Pierces 16sp of barriers"
        self.pierceBar=16

class Incin(Ammo):
    def __init__(self):
        super().__init__()
        self.name="Incendiary Rounds"
        self.desc="When dealing damage through:, 1D6 damage direct to body, (triggers an additional stun check)"
    
    def onDamage(self,enemyUnit:Unit,loc:int):
        enemyUnit.directToBody(d6())

class Explosive(Ammo):
    def __init__(self):
        super().__init__()
        self.name="Explosive"
        self.desc="Deals an additional 1D3 SP damage"

    def postContact(self,enemyUnit:Unit,loc:int):
        enemyUnit.armour.sp[loc]=max(0,enemyUnit.armour.sp[loc]-d3())

class Firecracker(Ammo):
    def __init__(self):
        super().__init__()
        self.name="Firecracker"
        self.desc="Deals an additional 1D6+1 SP damage"

    def postContact(self,enemyUnit:Unit,loc:int):
        enemyUnit.armour.sp[loc]=max(0,enemyUnit.armour.sp[loc]-(d6()+1))

class Hellfire(Ammo):
    def __init__(self):
        super().__init__()
        self.name="Hellfire Rounds"
        self.desc="When dealing damage through:, 2D6 damage direct to body, (triggers an additional stun check)"
    
    def onDamage(self,enemyUnit:Unit,loc:int):
        enemyUnit.directToBody(d6()+d6())
    
class HEI(Ammo):
    def __init__(self):
        super().__init__()
        self.name="HEI"
        self.desc="Explosive with additional incendiary effect"

    def onDamage(self,enemyUnit:Unit,loc:int):
        enemyUnit.directToBody(d6())

    def postContact(self,enemyUnit:Unit,loc:int):
        enemyUnit.armour.sp[loc]=max(0,enemyUnit.armour.sp[loc]-d3())

class API(Ammo):
    def __init__(self):
        super().__init__()
        self.name="API"
        self.desc="AP with additional incendiary effect"

    def onDamage(self,enemyUnit:Unit,loc:int):
        enemyUnit.directToBody(d6())

    def bonusDamage(self,enemyUnit:Unit,loc:int):
        if enemyUnit.armour.typeAt(loc)=='hard':
            return 4
        return 0
    
class FragFlechette(Ammo):
    def __init__(self):
        super().__init__()
        self.name="Pref. Both"
        self.desc="Preferred both (0.5x SP) "

    def spMultiplier(self,enemyUnit:Unit,loc:int):
        return 0.5
    
class Cybercontrol(Ammo):
    def __init__(self):
        super().__init__()
        self.name="Cybercontrol Round"
        self.desc="Deals 2x SDP damage to cyber limbs, Triggers a stun check"
        self.cybercontrol=True

class CybercontrolSlug(Ammo):
    def __init__(self):
        super().__init__()
        self.name="Cybercontrol Slug"
        self.desc="Slug that additionally, deals 2x SDP damage to cyber limbs, Triggers a stun check"
        self.cybercontrol=True
    
    def spMultiplier(self,enemyUnit:Unit,loc:int):
        return 0.5 if enemyUnit.armour.typeAt(loc)=='hard' and enemyUnit.injuryThreshold[0]<12 else 1
    
class Slug(Ammo):
    def __init__(self):
        super().__init__()
        self.name="Pref. Hard"
        self.desc="Preferred hard (0.5x SP if hard)"

    def spMultiplier(self,enemyUnit:Unit,loc:int):
        return 0.5 if enemyUnit.armour.typeAt(loc)=='hard' and enemyUnit.injuryThreshold[0]<12 else 1
    
class Arrow(Ammo):
    def __init__(self):
        super().__init__()
        self.name="Pref. Soft"
        self.desc="Preferred soft (0.5x SP if soft)"

    def spMultiplier(self,enemyUnit:Unit,loc:int):
        return 0.5 if enemyUnit.armour.typeAt(loc)=='soft' else 1

class Mono(Ammo):
    def __init__(self):
        super().__init__()
        self.name="Pref. Mono"
        self.desc="Preferred mono (0.25x SP if soft else 0.5x SP)"

    def spMultiplier(self,enemyUnit:Unit,loc:int):
        return 0.25 if enemyUnit.armour.typeAt(loc)=='soft' else 0.5

class DoublePreferred(Ammo):
    def __init__(self):
        super().__init__()
        self.name="Double Preferred"
        self.desc="Preferred + Weakpoint (0.25x SP)"

    def spMultiplier(self,enemyUnit:Unit,loc:int):
        return 0.25

class BuckshotInCQB(Ammo):
    def bonusDamage(self,enemyUnit,loc: int):
        return d6()+d6()
    
class FlechetteInCQB(Ammo):
    def bonusDamage(self,enemyUnit,loc: int):
        return d6()+d6()
    
    def spMultiplier(self,enemyUnit:Unit,loc:int):
        return 0.5
    
class Caseless(Ammo):
    def bonusDamage(self,enemyUnit:Unit,loc:int):
        return 2