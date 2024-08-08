from random import choice,random
from copy import deepcopy

from Modules.Base import Unit
from Modules.Generator import findGun,findArmour
from Modules.Ammo import *
from Modules.Dice import d6

FIGHT_TURN_LIMIT=30

class Team:
    units=[]

    def __init__(self,units):
        self.units=units

    def __str__(self):
        output=''
        for unit in self.units:
            output+=str(unit)+'\n\n'
        return output

    def attack(self,targetTeam):
        for attacker in self.units:
            target=choice(targetTeam.units)

            if attacker.attack(target):
                targetTeam.kill(target)

            if len(targetTeam.units)==0:
                return True
        
        return False

    def kill(self,unit):
        self.units.remove(unit)

    def cost(self):
        total=0
        for unit in self.units:
            total+=unit.cost()
        return total
    
def fight(unitA:Unit,unitB:Unit): # Fight until conclusion, True for unit A, False for unit B. Randomizes engaging unit
    unitA.reset()
    unitB.reset()
    if random() < .5:
        for _ in range(1,FIGHT_TURN_LIMIT):
            if(unitA.attack(unitB)):
                return True
            if(unitB.attack(unitA)):
                return False
    else:
        for _ in range(1,FIGHT_TURN_LIMIT):
            if(unitB.attack(unitA)):
                return False
            if(unitA.attack(unitB)):
                return True

    print(unitA) #err
    print("--")
    print(unitB)
    raise Exception('TURN LIMIT REACHED')

def favour(unitA,unitB): # returns ([0-1 % win for A],[Avg combat length in turns])
    totalWins=0
    for _ in range(FAVOUR_ITERATIONS):
        totalWins+=1 if fight(unitA,unitB) else 0

    return totalWins/FAVOUR_ITERATIONS

def teamFight(teamA,teamB): # Fight until conclusion, True for team A, False for team B. Randomizes engaging team
    teamA=deepcopy(teamA)
    teamB=deepcopy(teamB)
    if random() < .5:
        for i in range(1,FIGHT_TURN_LIMIT):
            if(teamA.attack(teamB)):
                return (True,i)
            if(teamB.attack(teamA)):
                return (False,i)
    else:
        for i in range(1,FIGHT_TURN_LIMIT):
            if(teamB.attack(teamA)):
                return (False,i)
            if(teamA.attack(teamB)):
                return (True,i)

    print(teamA) #err
    print("--")
    print(teamB)
    raise Exception('TURN LIMIT REACHED')


def teamFavor(teamA,teamB): # returns ([0-1 % win for A],[Avg combat length in turns])
    totalWins=0
    totalTurns=0
    for _ in range(FAVOUR_ITERATIONS):
        result=teamFight(teamA,teamB)

        totalWins+=1 if result[0] else 0
        totalTurns+=result[1]

    return (totalWins/FAVOUR_ITERATIONS,totalTurns/FAVOUR_ITERATIONS)

def compareTeam(teamA,teamB):
    print(f'[Team A] cost: {teamA.cost()}')
    print(f'[Team B] cost: {teamB.cost()}')
    results=teamFavor(teamA,teamB)
    print(f'\n[Team A] will win {round(results[0]*100,1)}% of the time, in an average of {round(results[1],1)} turns')


FAVOUR_ITERATIONS=10000

if __name__=='__main__':
    unitsA,unitsB=[],[]
    
    s1=Unit(findGun('viper'),findArmour([14,14,14,14,10,10]),15,8)
    s2=Unit(findGun('viper'),findArmour([14,14,14,14,10,10]),15,8)

    for _ in range(1):
        unitsA.append(deepcopy(s1))

    for _ in range(1):
        unitsB.append(deepcopy(s2))

    teamA=Team(unitsA)
    teamB=Team(unitsB)

    compareTeam(teamA,teamB)