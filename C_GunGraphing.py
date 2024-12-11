import matplotlib.pyplot as plt
import copy
import numpy as np

from Modules.Base import Unit,Gun
from Modules.Generator import generateGunList,findArmour
from Modules.Ammo import *
        
TTK_TURN_LIMIT=50
def fightLength(attacker,dummy):
    turns=0
    for _ in range(TTK_TURN_LIMIT):
        turns+=1
        if(attacker.attack(dummy)):
            return turns
    return TTK_TURN_LIMIT

def TTK(gun,iterations,armour,ws,body,cool):
    totalTurns=0
    protoAttacker=Unit(gun,armour,ws,body,cool)
    protoDummy=Unit(gun,armour,ws,body,cool)
    for _ in range(iterations):
        attacker=copy.deepcopy(protoAttacker)
        dummy=copy.deepcopy(protoDummy)
        totalTurns+=fightLength(attacker,dummy)

    return totalTurns/iterations

def Instakill(gun,iterations,armour,ws,body,cool):
    successes=0
    protoAttacker=Unit(gun,armour,ws,body,cool)
    protoDummy=Unit(gun,armour,ws,body,cool)
    for _ in range(iterations):
        attacker=copy.deepcopy(protoAttacker)
        dummy=copy.deepcopy(protoDummy)
        if(attacker.attack(dummy)):
            successes+=1

    return successes/iterations

def plotTTKonCost(guns,mark:str):
    cost=[]
    ttk=[]
    for gun in guns:
        m='o'
        if(gun.rof==1):
            color="tab:blue"
        elif(gun.rof==2):
            color="tab:green"
        elif(gun.rof==3):
            color="tab:orange"
        else:#auto
            color="tab:red"

        if(mark.lower() in gun.name.lower()):
            color="magenta"
            m='s'
        
        newCost=gun.cost
        newTTK=TTK(gun,ITERATIONS,ARMOUR,WS,BODY,COOL)
        plt.scatter(newCost,newTTK,color=color,alpha=0.7,edgecolors='none',marker=m)
        cost.append(newCost)
        ttk.append(newTTK)

    plt.axhline(y=1, color='r', linestyle='dotted')
    plt.axhline(y=3.5, color='b', linestyle='dotted')
    #plt.axvline(x=450, color='b', linestyle='dotted')
    plt.ylabel("TTK in turns")
    plt.xlabel("Cost of weapon")
    plt.title(f"TTK vs Cost for skill [{WS}] armour {ARMOUR.sp[1]}")
    
    #cost,ttk = zip(*sorted(zip(cost,ttk))) 
    #x=np.array(cost)
    #y=np.array(ttk)
    #a,b=np.polyfit(np.log10(x),y,1)
    #plt.plot(x,a*np.log10(x)+b,color='steelblue',linestyle='--')

def plotInstakillOnCost(guns,mark:str):
    for gun in guns:
        m='o'
        if(gun.rof==1):
            color="tab:blue"
        elif(gun.rof==2):
            color="tab:green"
        elif(gun.rof==3):
            color="tab:orange"
        else:#auto
            color="tab:red"

        if(mark.lower() in gun.name.lower()):
            color="magenta"
            m='s'
        
        plt.scatter(gun.cost,Instakill(gun,ITERATIONS,ARMOUR,WS,BODY,COOL),color=color,marker=m,alpha=0.5,edgecolors='none')

    plt.ylabel("Percentile chance to instantly kill")
    plt.xlabel("Cost of weapon")
    plt.title(f"Instakill vs Cost for skill [{WS}] armour [{ARMOUR.sp[0]}][{ARMOUR.sp[1]}][{ARMOUR.sp[2]}|{ARMOUR.sp[3]}][{ARMOUR.sp[4]}|{ARMOUR.sp[5]}]")

#The body, WS, and SP to be used for individual applications such as TTK or instakill on cost
ITERATIONS=3000
BODY=7
COOL=7
WS=15
ARMOUR=findArmour([14,14,14,14,10,10])

if __name__=="__main__":
    guns=generateGunList()
    guns.append(Gun("Hellfire",950,2,4,3,1,6,Hellfire()))
    guns.append(Gun("Hellfire Dual",1900,0,4,3,2,12,Hellfire()))

    guns.append(Gun("Super Hellfire",750,2,5,1,1,5,Incin()))
    guns.append(Gun("Super Hellfire Dual",1400,0,5,1,2,10,Incin()))
    plotTTKonCost(guns,"Hellfire")
    #plotInstakillOnCost(guns,"LMG")