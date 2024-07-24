from random import choice,random
from copy import deepcopy

from C_BaseModule import Gun,User,generateGunList
from C_Scraper import scrapeGuns

FIGHT_TURN_LIMIT=30
FAVOUR_ITERATIONS=3000
GUN_LIST=generateGunList()

def searchGunList(name):
    prospectGun=None
    for gun in GUN_LIST:
        if name.lower() in gun.name.lower():
            if prospectGun is not None:
                print(f'Warning: Multiple guns found by search "{name}", likely incorrect')
                break
            prospectGun=gun

    if prospectGun is None:
        raise Exception(f'Error: Gun not found by search "{name}"')
    else:
        return prospectGun

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


def teamFight(teamA,teamB): # Fight until conclusion, True for team A, False for team B. Randomizes engaging team
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

    raise Exception('TURN LIMIT REACHED')


def favour(protoTeamA,protoTeamB): # returns ([0-1 % win for A],[Avg combat length in turns])
    totalWins=0
    totalTurns=0
    for _ in range(FAVOUR_ITERATIONS):
        teamA=deepcopy(protoTeamA)
        teamB=deepcopy(protoTeamB)
        result=teamFight(teamA,teamB)

        totalWins+=1 if result[0] else 0
        totalTurns+=result[1]

    return (totalWins/FAVOUR_ITERATIONS,totalTurns/FAVOUR_ITERATIONS)

def compareTeam(teamA,teamB):
    print(f'[Team A] cost: ~{teamA.cost()}',f'bottleneck: {teamA.bottleneck}' if teamA.bottleneck<len(teamA.units) else '')
    print(f'[Team B] cost: ~{teamB.cost()}',f'bottleneck: {teamB.bottleneck}' if teamB.bottleneck<len(teamB.units) else '')
    results=favour(teamA,teamB)
    print(f'\n[Team A] will win {round(results[0]*100,1)}% of the time, in an average of {round(results[1],1)} turns')

def generateTeam(maxUnitCost=2000,uniqueUnits=4,style='any'):
    pass

if __name__=='__main__':
    # scrape when main list changes!!
    #scrape()

    unitsA,unitsB=[],[]

    unitsA.append(User(searchGunList('akr'),armour,15,9,9)) # full metal AKR
    unitsA.append(User(searchGunList('pump'),armour,15,8,8)) # 14 all pump
    unitsA.append(User(searchGunList('scorpion'),armour,14,7,7)) # 14 all pump
    unitsA.append(User(searchGunList('desert'),armour,15,8,8)) # 14 all pump
    
    for _ in range(7):
        unitsB.append(User(searchGunList('police'),armour,12,7,7))

    unitsB.append(User(searchGunList('ares'),armour,13,8,8))

    teamA=Team(unitsA)
    teamB=Team(unitsB)

    #teamFight(teamA,teamB)
    #print('[Team A]:\n'+str(teamA))
    #print('[Team B]:\n'+str(teamB))

    compareTeam(teamA,teamB)