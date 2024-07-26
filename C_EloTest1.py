from random import random,sample,choice

from C_BaseModule import User
from C_Scraper import findGun,findArmour
from C_FightSim import fight

FIGHT_TURN_LIMIT=30

class Player:
    def __init__(self,unit,elo=0,fixed=False):
        self.unit=unit
        if elo==0:
            self.elo=unit.cost()
        else:
            self.elo=elo
        self.fixed=fixed

    def win(self,opponent):
        disparity=32*(1-self.estimation(opponent))
        if not self.fixed:
            self.elo+=disparity
        if not opponent.fixed:
            opponent.elo-=disparity
        
    def estimation(self,opponent):
        return 1/(1+10**((opponent.elo-self.elo)/1000))

def battle(playerA,playerB):
    if fight(playerA.unit,playerB.unit):
        playerA.win(playerB)
    else:
        playerB.win(playerA)

def simlulate(players,iterations):
    for _ in range(iterations):
        p1,p2=sample(players,2)
        battle(p1,p2)

def simlulateNew(newPlayer,players,iterations):
    for _ in range(iterations):
        p2=choice(players)
        battle(newPlayer,p2)

if __name__=='__main__':
    players=[]
    players.append(Player(User(findGun("darra"),findArmour([20,20,20,20,20,20]),16,10),3700,True)) 
    players.append(Player(User(findGun("l96"),findArmour([14,16,16,16,15,15]),15,8,10),2400,True)) 
    players.append(Player(User(findGun("scorpion"),findArmour([14,16,16,16,15,15]),15,9),2800,True))
    players.append(Player(User(findGun("sks"),findArmour([14,14,14,14,10,10]),15,7,9),1925,True)) 
    players.append(Player(User(findGun("pump"),findArmour([14,14,14,14,10,10]),15,9),2000,True)) 
    players.append(Player(User(findGun("vonya"),findArmour([12,14,14,14,10,10]),16,5,9),1300,True)) 
    players.append(Player(User(findGun("viper"),findArmour([12,12,12,12,8,8]),12,8),900,True)) 
    players.append(Player(User(findGun("scout"),findArmour([12,12,12,12,10,10]),15,7),950,True)) 
    players.append(Player(User(findGun("chief"),findArmour([12,14,14,14,8,8]),14,7),1150,True)) 
    players.append(Player(User(findGun("uzi"),findArmour([14,10,10,10,8,8]),13,6,8),-300,True))
    players.append(Player(User(findGun("police"),findArmour([10,10,10,10,8,8]),12,6),200,True))

    #simlulate(players,5000000)

    newbie=Player(User(findGun("mp5"),findArmour([12,14,14,14,10,10]),16,6,9))
    simlulateNew(newbie,players,500000)

    print(newbie.unit.cost(),'|',newbie.elo)
    #for p in players:
    #    print(p.unit.cost(),'|',p.elo,'|',p.unit.gun.name)