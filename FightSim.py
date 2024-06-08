from BaseModule import User,generateGunList

class Team:
    def __init__(self,units,bias=0): # bias represents number of units deemed to be 'occupied' per round average in an encounter (not fighting)
        self.units=units

gunlist=[]

def searchGunList(name):
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


if __name__=='__main__':
    gunList=generateGunList('Proposed.csv')
    print(searchGunList('six'))