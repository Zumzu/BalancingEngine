from Modules.Base import Ammo
from Modules.Dice import d3,d6

class HP(Ammo):
    def bonusDamage(self,enemyUnit,loc:int):
        if enemyUnit.armour.sp[loc]==0:
            return 6
        elif enemyUnit.armour.typeAt(loc)=='soft':
            return 2
        return 0
    
class AP(Ammo):
    def bonusDamage(self,enemyUnit,loc:int):
        if enemyUnit.armour.typeAt(loc)=='hard':
            return 4
        return 0
    
class Incin(Ammo):
    def onDamage(self,enemyUnit,loc:int):
        enemyUnit.directToBody(d6())

class Explosive(Ammo):
    def postEffect(self,enemyUnit,loc:int):
        enemyUnit.armour.sp[loc]=max(0,enemyUnit.armour.sp[loc]-d3())

class Firecracker(Ammo):
    def postEffect(self,enemyUnit,loc:int):
        enemyUnit.armour.sp[loc]=max(0,enemyUnit.armour.sp[loc]-(d6()+1))
    
class HEI(Ammo):
    def onDamage(self,enemyUnit,loc:int):
        enemyUnit.directToBody(d6())

    def postEffect(self,enemyUnit,loc:int):
        enemyUnit.armour.sp[loc]=max(0,enemyUnit.armour.sp[loc]-d3())

class API(Ammo):
    def onDamage(self,enemyUnit,loc:int):
        enemyUnit.directToBody(d6())

    def bonusDamage(self,enemyUnit,loc:int):
        if enemyUnit.armour.typeAt(loc)=='hard':
            return 4
        return 0
    
class FragFlechette(Ammo):
    def preferred(self,enemyUnit,loc:int):
        return True
    
class Slug(Ammo):
    def preferred(self,enemyUnit,loc:int):
        return enemyUnit.armour.typeAt(loc)=='hard'
    
class Arrow(Ammo):
    def preferred(self,enemyUnit,loc:int):
        return enemyUnit.armour.typeAt(loc)=='soft'
    
class Caseless(Ammo):
    def bonusDamage(self,enemyUnit,loc:int):
        return 2