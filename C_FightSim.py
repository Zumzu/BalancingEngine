from random import choice,random
from copy import deepcopy

from C_BaseModule import Gun,User
from C_Scraper import findGun,findArmour

FIGHT_TURN_LIMIT=30
FAVOUR_ITERATIONS=10000

class Team:
    units=[]

    # the bottleneck is a simulation hard cap to the number of units that can act against the enemy at a time (default 8)
    # Its designed such that the units at the list start fight first, and the backfill replaces them when they die
    # If you intend to use this feature, place units in order of contact

    def __init__(self,units,bottleneck=8):
        self.units=units
        self.bottleneck=bottleneck

    def __str__(self):
        output=''
        for unit in self.units:
            output+=str(unit)+'\n\n'
        return output

    def attack(self,targetTeam):
        for attacker in self.units[:self.bottleneck]:
            target=choice(targetTeam.units[:targetTeam.bottleneck])

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
    print(f'[Team A] cost: {teamA.cost()}',f'bottleneck: {teamA.bottleneck}' if teamA.bottleneck<len(teamA.units) else '')
    print(f'[Team B] cost: {teamB.cost()}',f'bottleneck: {teamB.bottleneck}' if teamB.bottleneck<len(teamB.units) else '')
    results=teamFavor(teamA,teamB)
    print(f'\n[Team A] will win {round(results[0]*100,1)}% of the time, in an average of {round(results[1],1)} turns')

if __name__=='__main__':
    unitsA,unitsB=[],[]

    u1=User(findGun("darra"),findArmour([20,20,20,20,20,20]),17,10)
    u2=User(findGun("police"),findArmour([10,10,10,10,8,8]),14,6,8)

    unitsA.append(u1)

    for _ in range(6):
        unitsB.append(u2)

    teamA=Team(unitsA)
    teamB=Team(unitsB,20)
    compareTeam(teamA,teamB)