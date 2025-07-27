from copy import deepcopy
from random import choice

class CritInjury:
    def __init__(self,loc:int,severity:int=0,name:str="Generic Injury",text:str="-",bleedMultiplier:int=1,allNegative:int=0,attackPenalty:int=0,stunUnconPenalty:int=0):
        self.loc=loc
        self.name=name
        self.text=text
        self.severity=severity

        self.bleedMultiplier=bleedMultiplier
        self.allNegative=allNegative
        self.attackPenalty=attackPenalty
        self.stunUnconPenalty=stunUnconPenalty

    
    def breakIncomplete(self):
        if self.loc==2 or self.loc==3:
            new=deepcopy(armCritInjuries[2])
        elif self.loc==4 or self.loc==5:
            new=deepcopy(legCritInjuries[1])
        else:
            raise "Bad location to break"
        
        self.name=new.name
        self.text=new.text
        self.severity=new.severity

        self.bleedMultiplier=new.bleedMultiplier
        self.allNegative=new.allNegative
        self.attackPenalty=new.attackPenalty
        self.stunUnconPenalty=new.stunUnconPenalty
        

legCritInjuries=[
    CritInjury(-1,2,"Dismembered Leg","Your leg is unrecoverable, Your MA is limited to 2, DV:15 athletics/agility or fall prone immediately, Moving is incredibly painful, Not removed upon a successful surgery check"),
    CritInjury(-1,1,"Broken Leg","Your MA is limited to 2, DV:15 athletics/agility or fall prone immediately, Moving is incredibly painful"),
    CritInjury(-1,1,"Punctured Artery","You begin bleeding out, You bleedout twice as fast",bleedMultiplier=2),
    CritInjury(-1,1,"Torn Tendon","Extreme pain, Treat all stats as 1 less, You cannot succeed athletics/agility checks, You cannot sprint or dash attack",allNegative=1),
    CritInjury(-1,1,"Foreign Object","Immediately after you take an action using this leg, take 2 damage direct to body, (this ignores btm and triggeres a stun check)"),
    CritInjury(-1,0,"Incomplete Fracture","DV:15 athletics/agility or fall prone immediately, If this leg is dealt more damage it becomes a broken leg")
]

armCritInjuries=[
    CritInjury(-1,2,"Dismembered Arm","Your arm is unrecoverable, It cannot be used whatsoever, Moving it is incredibly painful, Not removed upon a successful surgery check",attackPenalty=5),
    CritInjury(-1,2,"Destroyed Hand","Your hand is unrecoverable, It cannot be used whatsoever, Not removed upon a successful surgery check",attackPenalty=5),
    CritInjury(-1,1,"Broken Arm","You drop whatever this hand is holding, -5 to all actions using this arm, Moving it is incredibly painful",attackPenalty=5),
    CritInjury(-1,1,"Punctured Artery","You begin bleeding out, You bleedout twice as fast",bleedMultiplier=2),
    CritInjury(-1,1,"Foreign Object","Immediately after you take an action using this arm, take 2 damage direct to body, (this ignores btm and triggeres a stun check)"),
    CritInjury(-1,1,"Compound Fracture","Extreme pain, Treat all stats as 2 less, Arm cannot support more than a guns worth of weight",allNegative=2),
    CritInjury(-1,0,"Incomplete Fracture","Drop whatever this hand is holding, If this arm is dealt more damage it becomes a broken arm")
]

torsoCritInjuries=[
    CritInjury(-1,2,"Spinal Injury","You immediately fall unconcious, You have -1 body permanently (this cannot be undone)"),
    CritInjury(-1,2,"Pierced Heart","You begin bleeding out, You bleedout four times as fast",bleedMultiplier=4),
    CritInjury(-1,2,"Broken Ribs","Searing pain, Treat all stats as 3 less, You retain -1 body for a week",allNegative=3),
    CritInjury(-1,1,"Foreign Object","Immediately after you take an action, Take 2 damage direct to body, (this ignores btm and triggeres a stun check)"),
    CritInjury(-1,1,"Pierced Liver","Stun and uncon checks are 3 harder, You cannot pass resist drugs/torture or athletics/agility checks, Violently painful",stunUnconPenalty=3),
    CritInjury(-1,1,"Collapsed Lung","Attack checks are 2 harder, After you attempt a strenuous action make a stun check, (such a sprinting, dash attack, or multiaction)",attackPenalty=2)
]

headshotCritInjury=CritInjury(-1,2,"Headshot","you fucking die lmao, skill issue headass fr fr, shoulda bought a better helmet")
bonkCritInjury=CritInjury(-1,2,"Bonk","you dont quite die lmao, good hemlet btw good purchase")


def critInjuryRoll(loc:int):
    if loc==0:
        output=deepcopy(bonkCritInjury)
    elif loc==1:
        output=deepcopy(torsoCritInjuries[choice([0,1,1,2,2,3,3,4,4,5])])
    elif loc==2 or loc==3:
        output=deepcopy(armCritInjuries[choice([0,1,2,2,3,4,4,5,6,6])])
    elif loc==4 or loc==5:
        output=deepcopy(legCritInjuries[choice([0,1,1,2,3,3,4,4,5,5])])
    else:
        raise "Bad location"

    output.loc=loc
    return output

def doubleCritInjuryRoll(loc:int):
    if loc==0:
        output=deepcopy(headshotCritInjury)
    elif loc==1:
        output=deepcopy(torsoCritInjuries[0])
    elif loc==2 or loc==3:
        output=deepcopy(armCritInjuries[0])
    elif loc==4 or loc==5:
        output=deepcopy(legCritInjuries[0])
    else:
        raise "Bad location"

    output.loc=loc
    return output