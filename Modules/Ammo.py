from Base import Ammo

class FragFlechette(Ammo):
    def preferred(self,enemyUnit,loc:int):
        return True