from random import random,sample,choice
from copy import deepcopy
from os import system

from C_BaseModule import User
from C_Scraper import findGun,findArmour
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
        teamBunits = [deepcopy(playerB.unit) for _ in range(max(1, round(playerA.elo / playerB.elo)))]
        return (Team([deepcopy(playerA.unit)]),Team(teamBunits))
    else:
        teamAunits = [deepcopy(playerA.unit) for _ in range(max(1, round(playerB.elo / playerA.elo)))]
        return (Team(teamAunits),Team([deepcopy(playerB.unit)]))

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
    for _ in range(iterations):
        p2=choice(players)
        battle(newPlayer,p2)

if __name__=='__main__':
    players=[]
    players.append(Player(User(findGun("darra"),findArmour([20,20,20,20,20,20]),16,10))) 
    players.append(Player(User(findGun("viper"),findArmour([12,12,12,12,8,8]),13,7,8))) 
    players.append(Player(User(findGun("police"),findArmour([10,10,10,10,8,8]),12,6)))
    #players.append(Player(User(findGun("l96"),findArmour([14,16,16,16,15,15]),15,8,10))) 
    #players.append(Player(User(findGun("scorpion"),findArmour([14,16,16,16,15,15]),15,9)))
    #players.append(Player(User(findGun("sks"),findArmour([14,14,14,14,10,10]),15,7,9))) 
    #players.append(Player(User(findGun("pump"),findArmour([14,14,14,14,10,10]),15,9))) 
    #players.append(Player(User(findGun("vonya"),findArmour([12,14,14,14,10,10]),16,5,9))) 
    #players.append(Player(User(findGun("scout"),findArmour([12,12,12,12,10,10]),15,7))) 
    #players.append(Player(User(findGun("chief"),findArmour([12,14,14,14,8,8]),14,7))) 
    #players.append(Player(User(findGun("uzi"),findArmour([14,10,10,10,8,8]),13,6,8)))
  
    simlulate(players,10000)

    for p in players:
        print(p.unit.cost(),'|',p.elo,'|',p.unit.gun.name)

    
    #newbie=Player(User(findGun("mp5"),findArmour([12,14,14,14,10,10]),16,6,9))
    #simlulateNew(newbie,players,500000)
    #print(newbie.unit.cost(),'|',newbie.elo)