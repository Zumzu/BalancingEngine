from random import choice,random
from copy import deepcopy

from Modules.Base import Unit
from Modules.Generator import findGun,findArmour
from Modules.Ammo import *

FIGHT_TURN_LIMIT=30
FAVOUR_ITERATIONS=30000

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
    
def fight(unitA,unitB): # Fight until conclusion, True for unit A, False for unit B. Randomizes engaging unit
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
    for _ in range(10000):
        totalWins+=1 if fight(unitA,unitB) else 0

    return totalWins/10000

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

if __name__=='__main__':
    unitsA,unitsB=[],[]

    u1=Unit(findGun("darra"),findArmour([20,20,20,20,20,20]),16,10)
    u2=Unit(findGun("viper"),findArmour([12,12,12,12,8,8]),15,7,8)
    u3=Unit(findGun("police"),findArmour([10,10,10,10,8,8]),12,6)
    u4=Unit(findGun("l96"),findArmour([14,16,16,16,15,15]),15,8,10)
    u5=Unit(findGun("scorpion"),findArmour([14,16,16,16,15,15]),15,9)
    u6=Unit(findGun("sks"),findArmour([14,14,14,14,10,10]),15,7,9)
    u7=Unit(findGun("pump"),findArmour([14,14,14,14,10,10]),15,9)
    u8=Unit(findGun("vonya"),findArmour([12,14,14,14,10,10]),16,5,9)
    u9=Unit(findGun("scout"),findArmour([12,12,12,12,10,10]),15,7)
    u10=Unit(findGun("chief"),findArmour([12,14,14,14,8,8]),14,7)
    u11=Unit(findGun("uzi"),findArmour([14,10,10,10,8,8]),13,6,8)


    s1=Unit(findGun("police"),findArmour([10,10,10,10,8,8]),12,6)
    s2=Unit(findGun("police"),findArmour([10,10,10,10,8,8]),12,6)

    for _ in range(1):
        unitsA.append(deepcopy(s1))

    for _ in range(1):
        unitsB.append(deepcopy(s2))

    teamA=Team(unitsA)
    teamB=Team(unitsB)

    compareTeam(teamA,teamB)