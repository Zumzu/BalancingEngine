from random import choice


def d10(): # d10 result
    d10=[1,2,3,4,5,6,7,8,9,10]
    return choice(d10)

def d10EDown(): # d10 result factoring explosions DOWNWARD ONLY for full auto weapons
    roll=d10()
    total=roll

    if(roll==1):
        while(True):
            roll=d10()
            total-=roll
            if(roll!=10):
                break

    return total

def d10E(): # d10 result factoring explosions
    roll=d10()
    total=roll

    if(roll==1):
        while(True):
            roll=d10()
            total-=roll
            if(roll!=10):
                break

    elif(roll==10):
        while(True):
            roll=d10()
            total+=roll
            if(roll!=10):
                break

    return total

def d6():
    d6=[1,2,3,4,5,6]
    return choice(d6)

def locationDie():
    locations=[0,1,1,1,1,1,2,3,4,5]
    return choice(locations)