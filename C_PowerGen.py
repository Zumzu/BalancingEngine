from random import random,sample,choice
from copy import deepcopy
from os import system

from Modules.Base import Unit
from Modules.Generator import findGun,findArmour
from C_FightSim import Team,teamFight

class Player:
    def __init__(self,unit,elo=None,fixed=False):
        self.unit=unit
        if elo is None:
            self.elo=unit.cost()
        else:
            self.elo=elo
        self.fixed=fixed

    def win(self,opponent):
        disparity=1
        if not self.fixed:
            self.elo+=disparity
        if not opponent.fixed:
            opponent.elo-=disparity
    
    def cost(self):
        return self.unit.cost()

def battle(playerA,playerB):
    teamA,teamB=matchMake(playerA,playerB)
    if teamFight(teamA,teamB)[0]:
        playerA.win(playerB)
    else:
        playerB.win(playerA)
    
def matchMake(playerA,playerB):
    if playerA.elo>=playerB.elo:
        teamAunits = [deepcopy(playerA.unit),deepcopy(playerA.unit)]
        teamBunits = [deepcopy(playerB.unit) for _ in range(max(1, round(playerA.elo*2 / playerB.elo)))]
    else:
        teamAunits = [deepcopy(playerA.unit) for _ in range(max(1, round(playerB.elo*2 / playerA.elo)))]
        teamBunits = [deepcopy(playerB.unit),deepcopy(playerB.unit)]

    if teamAunits.__len__()%2==0 and teamBunits.__len__()%2==0:
        teamAunits=teamAunits[:int(teamAunits.__len__()/2)]
        teamBunits=teamBunits[:int(teamBunits.__len__()/2)]

    return (Team(teamAunits),Team(teamBunits))

def simlulate(players,iterations):
    for i in range(iterations):
        if i%(iterations//200)==0:
            system('cls')
            for _ in range(i//(iterations//200)):
                print("#",end='')
            for _ in range(200-i//(iterations//200)):
                print(".",end='')
            print()

        p1,p2=sample(players,2)
        battle(p1,p2)
    system('cls')

def simlulateNew(newPlayer,players,iterations):
    for i in range(iterations):
        if i%(iterations//200)==0:
            system('cls')
            for _ in range(i//(iterations//200)):
                print("#",end='')
            for _ in range(200-i//(iterations//200)):
                print(".",end='')
            print()

        p2=choice(players)
        battle(newPlayer,p2)
    system('cls')

if __name__=='__main__':
    players=[]
    players.append(Player(Unit(findGun("darra"),findArmour([20,20,20,20,20,20]),16,10),3882,True)) 
    players.append(Player(Unit(findGun("viper"),findArmour([12,12,12,12,8,8]),13,7,8),1000,True)) 
    players.append(Player(Unit(findGun("police"),findArmour([10,10,10,10,8,8]),12,6),778,True))
    players.append(Player(Unit(findGun("l96"),findArmour([14,16,16,16,15,15]),15,8,10),2066,True)) 
    players.append(Player(Unit(findGun("scorpion"),findArmour([14,16,16,16,15,15]),15,9),2575,True))
    players.append(Player(Unit(findGun("sks"),findArmour([14,14,14,14,10,10]),15,7,9),1627,True)) 
    players.append(Player(Unit(findGun("vonya"),findArmour([12,14,14,14,10,10]),16,5,9),1382,True)) 
    players.append(Player(Unit(findGun("scout"),findArmour([12,12,12,12,10,10]),15,7),1006,True)) 
    players.append(Player(Unit(findGun("chief"),findArmour([12,14,14,14,8,8]),14,7),1166,True)) 
    players.append(Player(Unit(findGun("uzi"),findArmour([14,10,10,10,8,8]),13,6,8),693,True))
  
    #simlulate(players,100000)
    #for p in players:
    #    print(p.unit.cost(),'|',p.elo,'|',p.unit.gun.name)

    
    newbie=Player(Unit(findGun("scorpion"),findArmour([12,10,10,10,10,10]),16,5,5))
    simlulateNew(newbie,players,10000)
    print(newbie.unit.cost(),'|',newbie.elo)