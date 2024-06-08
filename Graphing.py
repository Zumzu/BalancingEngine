import matplotlib.pyplot as plt
import copy
import numpy as np
from random import choice,random

from GunScraper import scrape
from BaseModule import User,generateGunList

def compare(gun1,gun2,iterations,ws,sp,body):
    score1=0
    prototypeUser1=User(gun1,ws,sp,body)
    prototypeUser2=User(gun2,ws,sp,body)

    for _ in range(iterations):
        user1=copy.deepcopy(prototypeUser1)
        user2=copy.deepcopy(prototypeUser2)
        if(random() < .5):
            if(fightWinner(user1,user2)):
                score1+=1
        else:
            if(not fightWinner(user2,user1)):
                score1+=1

    return score1/iterations

def fightWinner(user1,user2): # returns true if the first user wins, false if the second user wins
    for _ in range(50):
        if(user1.attack(user2)):
            return True
        if(user2.attack(user1)):
            return False

def TTK(gun,iterations,ws,sp,body):
    totalTurns=0
    protoAttacker=User(gun,ws,sp,body)
    protoDummy=User(gun,ws,sp,body)
    for _ in range(iterations):
        attacker=copy.deepcopy(protoAttacker)
        dummy=copy.deepcopy(protoDummy)
        totalTurns+=fightLength(attacker,dummy)

    return totalTurns/iterations

def Instakill(gun,iterations,ws,sp,body):
    successes=0
    protoAttacker=User(gun,ws,sp,body)
    protoDummy=User(gun,ws,sp,body)
    for _ in range(iterations):
        attacker=copy.deepcopy(protoAttacker)
        dummy=copy.deepcopy(protoDummy)
        if(attacker.attack(dummy)):
            successes+=1

    return successes/iterations


TTK_TURN_LIMIT=50
def fightLength(attacker,dummy):
    turns=0
    for _ in range(TTK_TURN_LIMIT):
        turns+=1
        if(attacker.attack(dummy)):
            return turns
    return TTK_TURN_LIMIT

def plotCompareOnArmour(baseline,guns):
    results=[]
    for gun in guns:
        result=[]
        for i in range(len(SPS)):
            result.append(compare(gun,baseline,3000,WS,SPS[i],BODY))

        results.append(result)

    plt.gca().set_xticks(range(len(SP_LABELS)))
    plt.gca().set_xticklabels(SP_LABELS)
    plt.ylabel(f"% winrate baseline ({baseline.name})")
    plt.xlabel("SP All")
    for i in range(len(results)):
        plt.plot(results[i],label=guns[i].name)
    plt.axhline(y=0.5, color='r', linestyle='dotted')
    plt.legend()


def plotTTKonArmour(guns):
    results=[]
    for gun in guns:
        result=[]
        for i in range(len(SPS)):
            result.append(TTK(gun,3000,WS,SPS[i],BODY))

        results.append(result)

    plt.gca().set_xticks(range(len(SP_LABELS)))
    plt.gca().set_xticklabels(SP_LABELS)
    plt.ylabel(f"TTK in turns")
    plt.xlabel("SP All")
    for i in range(len(results)):
        plt.plot(results[i],label=guns[i].name)
    plt.axhline(y=1, color='r', linestyle='dotted')
    plt.axhline(y=4, color='b', linestyle='dotted')
    plt.legend()


def plotTTKonCost(guns,mark=None):
    cost=[]
    ttk=[]
    for gun in guns:
        if(gun.rof==1):
            color="tab:blue"
        elif(gun.rof==2):
            color="tab:green"
        elif(gun.rof==3):
            color="tab:orange"
        else:#auto
            color="tab:red"

        if(mark is not None and mark.lower() in gun.name.lower()):
            color="black"
        
        newCost=gun.cost
        newTTK=TTK(gun,3000,WS,SP,BODY)
        plt.scatter(newCost,newTTK,color=color,alpha=0.7,edgecolors='none')
        cost.append(newCost)
        ttk.append(newTTK)

    plt.axhline(y=1, color='r', linestyle='dotted')
    plt.axhline(y=3.5, color='b', linestyle='dotted')
    #plt.axvline(x=450, color='b', linestyle='dotted')
    plt.ylabel("TTK in turns")
    plt.xlabel("Cost of weapon")
    plt.title(f"TTK vs Cost for skill [{WS}] armour {SP}")
    
    #cost,ttk = zip(*sorted(zip(cost,ttk))) 
    #x=np.array(cost)
    #y=np.array(ttk)
    #a,b=np.polyfit(np.log10(x),y,1)
    #plt.plot(x,a*np.log10(x)+b,color='steelblue',linestyle='--')

def plotInstakillOnCost(guns,mark=None):
    for gun in guns:
        if(gun.rof==1):
            color="tab:blue"
        elif(gun.rof==2):
            color="tab:green"
        elif(gun.rof==3):
            color="tab:orange"
        else:#auto
            color="tab:red"

        if(mark is not None and mark.lower() in gun.name.lower()):
            color="black"
        
        plt.scatter(gun.cost,Instakill(gun,3000,WS,SP,BODY),color=color,alpha=0.7,edgecolors='none')

    plt.ylabel("Percentile chance to instantly kill")
    plt.xlabel("Cost of weapon")
    plt.title(f"Instakill vs Cost for skill [{WS}] armour {SP}")

#Input data for graphing a weapons effectiveness across differing weapon skills and SP sets
WEAPON_SKILLS=[8,9,10,11,12,13,14,15,16,17,18]
WS_LABELS=[8,9,10,11,12,13,14,15,16,17,18]
SPS=[[0]*6,[6]*6,[8]*6,[10]*6,[12]*6,[14]*6,[16]*6,[18]*6,[20]*6,[22]*6,[25]*6]
SP_LABELS=[0,6,8,10,12,14,16,18,20,22,25]

#The body, WS, and SP to be used for individual applications such as TTK or instakill on cost
BODY=7
WS=12
SP=[14,14,14,14,10,10]

if __name__=="__main__":
    # scrape when main list changes!!
    #scrape()
    
    guns=generateGunList()
    plotTTKonCost(guns,"LMG")
    #plotInstakillOnCost(guns,"LMG")