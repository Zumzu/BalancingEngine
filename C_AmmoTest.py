from Modules.Base import Unit
from Modules.Generator import findGun,findArmour
from Modules.Ammo import *

from C_FightSim import favour



U1=Unit(findGun("viper"),findArmour([12,12,10,10,8,8]),15,9,cyber=[0,0,0,0,20,20])
U2=Unit(findGun("sks"),findArmour([14,16,16,16,10,10]),15,9)
U3=Unit(findGun("akr"),findArmour([14,14,14,14,10,10]),15,8,cyber=[0,0,0,20,0,20])
U4=Unit(findGun("pump"),findArmour([20,20,20,20,20,20]),15,9,cyber=[0,0,30,30,0,0])

def winrates(unit:Unit):
    return [round(favour(unit,U1),2),round(favour(unit,U2),2),round(favour(unit,U3),2),round(favour(unit,U4),2)]

def difference(unit:Unit):
    print("--")
    output=list(map(float.__sub__,winrates(unit),base))
    output=[round(n,2) for n in output]
    print(output)

GUN1='mp5'
a1=Unit(findGun(GUN1),findArmour([14,14,14,14,10,10]),15,8)
base=winrates(a1)
print(base)

a2=Unit(findGun(GUN1,HP()),findArmour([14,14,14,14,10,10]),15,8)
difference(a2)

a3=Unit(findGun(GUN1,AP()),findArmour([14,14,14,14,10,10]),15,8)
difference(a3)
