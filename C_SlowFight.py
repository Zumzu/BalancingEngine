from os import system

from Modules.Base import Unit
from Modules.Generator import findGun,findArmour
from Modules.Ammo import *


#Largely a debugging tool for engine itself to make sure all components are working as they should

def explosive(unit:Unit,dice:int,multiple:int):
    for _ in range(multiple):
        dmg=0
        for _ in range(dice):
            dmg+=d6()
        unit.damage(dmg=dmg)


def slowFight(unitA,unitB):
    clear()
    #explosive(unitA,6,3) ##TEMP

    printState(unitA,unitB,0)
    for i in range(30):
        if(unitA.attack(unitB)):
            print("######## FIRST UNIT WINS!! ########")
            printState(unitA,unitB,i+1)
            break
        printState(unitA,unitB,i+1)

        if(unitB.attack(unitA)):
            print("######## SECOND UNIT WINS!! ########")
            printState(unitA,unitB,i+1)
            break
        printState(unitA,unitB,i+1)


def printState(unitA,unitB,turn):
    print(f"---- Turn {turn} ----")
    print(unitA)
    print('--')
    print(unitB)
    input()
    clear()
        
def clear():
    system('cls')

if __name__=='__main__':
    s1=Unit(findGun('darra'),findArmour([14,14,14,14,10,10]),15,8)
    s2=Unit(findGun('enforcer',HEI()),findArmour([10,10,10,10,8,8]),15,8)
    
    while True:
        slowFight(s1,s2)
        s1.reset()
        s2.reset()
