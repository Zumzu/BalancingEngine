from random import choice
from copy import deepcopy

from BaseModule import Gun,User,generateGunList
from GunScraper import scrape

FIGHT_TURN_LIMIT=30
FAVOUR_ITERATIONS=3000

def searchGunList(name):
    gunList=generateGunList()

    prospectGun=None
    for gun in gunList:
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
    bottleneck=8

    # the bottleneck is a simulation hard cap to the number of units that can act against the enemy at a time (default 8)
    # Its designed such that the units at the list start fight first, and the backfill replaces them when they die
    # If you intend to use this feature, place units in order of contact

    def __init__(self,units,bottleneck=8):
        self.units=units
        self.bottleneck=bottleneck

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



def teamFight(teamA,teamB): # Fight until conclusion, True for team A, False for team B
    for _ in range(FIGHT_TURN_LIMIT):
        if(teamA.attack(teamB)):
            return True
        if(teamB.attack(teamA)):
            return False
    raise Exception('TURN LIMIT REACHED')


def favour(protoTeamA,protoTeamB): # returns percentile victory odds for team A
    total=0
    for _ in range(FAVOUR_ITERATIONS):
        teamA=deepcopy(protoTeamA)
        teamB=deepcopy(protoTeamB)
        if teamFight(teamA,teamB):
            total+=1

    return total/FAVOUR_ITERATIONS


if __name__=='__main__':
    # scrape when main list changes!!
    #scrape()

    unitsA,unitsB=[],[]

    for _ in range(4):
        unitsA.append(User(searchGunList('darra'),15,[14]*6,7))
    
    for _ in range(12):
        unitsB.append(User(searchGunList('police'),12,[12]*6,7))

    teamA=Team(unitsA)
    teamB=Team(unitsB,6)

    print(f'{round(favour(teamA,teamB)*100,1)}%')


    