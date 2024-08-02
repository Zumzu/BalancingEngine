from os import system

from Modules.Base import Unit
from Modules.Generator import findGun,findArmour


#Largely a debugging tool for engine itself to make sure all components are working as they should

def slowFight(unitA,unitB): # Fight until conclusion, True for unit A, False for unit B. Randomizes engaging unit
    for i in range(30):
        clear()
        printState(unitA,unitB,i+1)
        if(unitA.attack(unitB)):
            clear()
            print("######## UNIT A WINS!! ########")
            printState(unitA,unitB,i+1)
            break

        clear()
        printState(unitA,unitB,i+1)
        if(unitB.attack(unitA)):
            clear()
            print("######## UNIT B WINS!! ########")
            printState(unitA,unitB,i+1)
            break


def printState(unitA,unitB,turn):
    print(f"---- Turn {turn} ----")
    print(unitA)
    print('--')
    print(unitB)
    input()
        
def clear():
    system('cls')

if __name__=='__main__':
    u1=Unit(findGun("chief"),findArmour([12,14,14,14,8,8]),14,7)
    u2=Unit(findGun("viper"),findArmour([12,12,12,12,8,8]),15,7,8)

    slowFight(u1,u2)
