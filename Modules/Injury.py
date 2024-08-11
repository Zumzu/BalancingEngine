from copy import deepcopy
from random import choice

class CritInjury:
    def __init__(self,loc:int,name:str="Generic Injury",text:str="-",bleedMultiplier:int=1,allNegative:int=0,attackPenalty:int=0,stunUnconPenalty:int=0):
        self.loc=loc
        self.name=name
        self.text=text

        self.bleedMultiplier=bleedMultiplier
        self.allNegative=allNegative
        self.attackPenalty=attackPenalty
        self.stunUnconPenalty=stunUnconPenalty

legCritInjuries=[
    CritInjury(-1,"Dismembered Leg","Your leg is unrecoverable, treat as broken leg, and is not removed upon a successful surgery check"),
    CritInjury(-1,"Broken Leg","Your MA is limited to 2, DV:15 athletics or fall prone immediately, moving is incredibly painful"),
    CritInjury(-1,"Punctured Artery","You begin bleeding out, you bleedout twice as fast",bleedMultiplier=2),
    CritInjury(-1,"Torn Tendon","Extreme pain, treat all stats as 1 less, you cannot succeed athletics checks or take the sprint action",allNegative=1),
    CritInjury(-1,"Foreign Object","Whenever you take an action using this leg, take 2 damage direct to body (this ignores btm and triggeres a stun check)"),
    CritInjury(-1,"Incomplete Fracture","DV:15 athletics or fall prone immediately. Until treated, if this leg is dealt any more damage, it becomes a broken leg")
]

armCritInjuries=[
    CritInjury(-1,"Dismembered Arm","Your arm is unrecoverable, treat as broken arm, and is not removed upon a successful surgery check",attackPenalty=5),
    CritInjury(-1,"Dismembered Hand","Your hand is unrecoverable, it cannot be used whatsoever, this effect is not removed upon a successful surgery check",attackPenalty=5),
    CritInjury(-1,"Broken Arm","You drop whatever this hand is holding, -5 to all actions using this arm, moving it is incredibly painful",attackPenalty=5),
    CritInjury(-1,"Punctured Artery","You begin bleeding out, you bleedout twice as fast",bleedMultiplier=2),
    CritInjury(-1,"Foreign Object","Whenever you take an action using this arm, take 2 damage direct to body (this ignores btm and triggeres a stun check)"),
    CritInjury(-1,"Compound Fracture","Extreme pain, treat all stats as 2 less, arm cannot support more than a guns worth of weight",allNegative=2),
    CritInjury(-1,"Incomplete Fracture","Drop whatever this hand is holding. Until treated, if this arm is dealt any more damage, it becomes a broken arm")
]

torsoCritInjuries=[
    CritInjury(-1,"Spinal Injury","You immediately fall unconcious until a successful surgery check is performed on you, you have -1 body permanently (this cannot be undone)"),
    CritInjury(-1,"Pierced Heart","You begin bleeding out, you bleedout four times as fast",bleedMultiplier=4),
    CritInjury(-1,"Broken Ribs","Searing pain, treat all stats as 3 less, after this is removed, you retain -1 body for a week",allNegative=3),
    CritInjury(-1,"Foreign Object","Whenever you take an action, take 2 damage direct to body (this ignores btm and triggeres a stun check)"),
    CritInjury(-1,"Pierced Liver","Stun and uncon checks are 3 harder, you cannot pass resist drugs/torture or endurance checks, violently painful",stunUnconPenalty=3),
    CritInjury(-1,"Collapsed Lung","Attack checks are 2 harder, after you attempt a strenuous action (such a sprinting, multiaction), make a stun check",attackPenalty=2)
]


def critInjuryRoll(loc:int):
    if loc==1:
        output=deepcopy(torsoCritInjuries[choice([0,1,1,2,2,3,3,4,4,5])])
    elif loc==2 or loc==3:
        output=deepcopy(armCritInjuries[choice([0,1,2,2,3,3,4,4,5,6])])
    elif loc==4 or loc==5:
        output=deepcopy(legCritInjuries[choice([0,1,2,2,3,3,4,4,5,5])])
    else:
        raise "Bad location, doesnt support head"

    output.loc=loc
    return output