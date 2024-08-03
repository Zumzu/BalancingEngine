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
    s1=Unit(findGun("chief"),findArmour([12,18,18,18,15,15]),14,7)
    s2=Unit(findGun("chief",HP()),findArmour([12,18,18,18,15,15]),14,7)
    while True:
        slowFight(s1,s2)
        s1.reset()
        s2.reset()
