from os import system

from Modules.Base import Unit
from Modules.Generator import findGun,findArmour
from Modules.Ammo import *


#Largely a debugging tool for engine itself to make sure all components are working as they should

def slowFight(unitA,unitB):
    clear()
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
    u1=Unit(findGun("chief"),findArmour([12,14,14,14,8,8]),14,7)
    u2=Unit(findGun("viper",Incin()),findArmour([12,12,12,12,8,8]),15,7,8)
    while True:
        slowFight(u1,u2)
        u1.reset()
        u2.reset()
