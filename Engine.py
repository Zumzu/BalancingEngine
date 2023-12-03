class Gun:
    def __init__(self,name,cost,rarity,wa,d6,more,rof,mag,range,rel,tooHandy,ammo=None):
        self.name=name
        self.cost=cost
        self.rarity=rarity
        self.wa=wa
        self.d6=d6
        self.more=more
        self.rof=rof
        self.mag=mag
        self.range=range
        self.rel=rel
        self.tooHandy=tooHandy
        self.ammo=ammo
        if name is None or cost is None or rarity is None is wa is None or d6 is None or more is None or rof is None or mag is None or range is None or rel is None or tooHandy is None:
            raise ValueError("Invalid gun :(")
    
    def __str__(self) -> str:
        return f"{self.name}, {self.cost}, {self.rarity}, {self.wa}, {self.d6}d6+{self.more}, {self.rof} | {self.mag}, {self.range}m, {self.rel}{'T' if self.rel=='S' else 'R'}, {2 if self.tooHandy==1 else 1}h"
        
def strToStat(input,delimeter=', '):
    input=str(input).split(delimeter)
    out=[]
    out.append(input[0])
    out.append(int(input[1]))
    out.append(input[2][0])
    out.append(int(input[3]))
    dmg=input[4].split("d6")
    out.append(int(dmg[0]))
    if(dmg is not None):
        out.append(int(dmg[1][1:]))
    else:
        out.append(0)
    rofMag=input[5].split(" | ")
    out.append(int(rofMag[0]))
    out.append(int(rofMag[1]))
    out.append(int(input[6].split('m')[0]))
    out.append(input[7][0])
    out.append(True if input[8][0]=='2' else False)
    return out

guns=[]
guns.append(Gun('Dai Lung Streetmaster',150,'E',0,2,1,2,12,12,'S',False))
guns.append(Gun('Millitech Viper SMG',600,'C',0,2,3,30,60,12,'S',True))

for gun in guns:
    print(gun)
    print(strToStat(gun))
