import requests
from bs4 import BeautifulSoup

from Modules.Base import Gun,Armour,ArmourSet
from copy import deepcopy

def processDamage(rawInput): #helper for scrape
    d6 = rawInput[0]
    more = rawInput.split(' ')[0].split('+')[1] if '+' in rawInput else '0'
    return (d6,more)

def scrapeGuns():
    html = requests.get('https://docs.google.com/spreadsheets/d/1Q5rBjDjx-MNGIl-JAVhtFT33W-T9RpQgg4bTRQuFYPA/gviz/tq?tqx=out:html&tq&gid=1296179088').text
    soup = BeautifulSoup(html, 'lxml') # lxml and bs4 required
    table = soup.find_all('table')[0]
    rows = [[td.text for td in row.find_all("td")] for row in table.find_all('tr')] # html magic

    guns=[]
    for row in rows: # construct guns
        if row[15]!='\xa0' and row[15]!='': # two data cols are used to get ROF & mag, if a line has anything in mag itll try to read it, care
            d6,more=processDamage(row[4])
            guns.append([row[0],row[1],row[3],d6,more,row[14],row[15]])

    with open('D_Guns.csv','w') as f: # save to file, ternary is just to remove last '\n'
        for gun in guns:
            f.write(','.join(gun) + ('\n' if gun!=guns[-1] else ''))

def generateGunList(name='D_Guns.csv'):
    guns=[]
    with open(name,'r') as f:
        for line in f:
            data=line.split(",")
            guns.append(Gun(data[0],int(data[1]),int(data[2]),int(data[3]),int(data[4]),int(data[5]),int(data[6])))
        
    guns.sort(key=lambda gun: gun.cost)
    return guns

def findGun(name):
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
    
################################

def processSP(rawInput:str): #helper for scrape
    if 'all' in rawInput.lower():
        return f'{";".join([rawInput.strip().split(" ")[0]]*6)}'
    
    output=''
    for c in rawInput.strip():
        if c=='[' or c==']':
            continue
        elif c=='|' or c==' ':
            output+=';'
        elif c=='-':
            output+='0'
        else:
            output+=c

    return output

def scrapeArmour():
    html = requests.get('https://docs.google.com/spreadsheets/d/1Q5rBjDjx-MNGIl-JAVhtFT33W-T9RpQgg4bTRQuFYPA/gviz/tq?tqx=out:html&tq&gid=997775131').text
    soup = BeautifulSoup(html, 'lxml') # lxml and bs4 required
    table = soup.find_all('table')[0]
    rows = [[td.text for td in row.find_all("td")] for row in table.find_all('tr')] # html magic

    armour=[]
    for row in rows: # construct armour
        if row[6]!='\xa0' and row[6]!='': # check if hard or soft
            sp=processSP(row[3])
            armour.append([row[0],row[1],sp,str(abs(int(row[4]))),str(abs(int(row[5]))),row[6].lower()])

    with open('D_Armour.csv','w') as f: # save to file, ternary is just to remove last '\n'
        for a in armour:
            f.write(','.join(a) + ('\n' if a!=armour[-1] else ''))

def generateArmourList(name='D_Armour.csv'):
    armour=[]
    with open(name,'r') as f:
        for line in f:
            data=line.split(",")
            armour.append(Armour(data[0],data[1],data[2].split(';'),data[3],data[4],data[5].strip()))

    return armour

def wearable(currentSP,armour):
    for i in range(6):
        if armour.sp[i]!=0 and currentSP[i]!=0:
            return False
    return True

def findArmour(sp):
    assert all(isinstance(value,int) for value in sp), "SP values must be integer"
    prospectArmour=deepcopy(ARMOUR_LIST)
    outputSP=[-1 if value==0 else value for value in sp] #set 0 in input to -1 to prevent false positives
    outputArmour=[]

    for i in range(6): #remove all armour that conflicts with given SP
        prospectArmour=[a for a in prospectArmour if a.sp[i]==outputSP[i] or a.sp[i]==0]

    while prospectArmour != []:
        outputSP=[0]*6
        outputArmour=[]

        for a in prospectArmour:
            if wearable(outputSP,a):
                outputArmour.append(a)
                for i in range(6):
                    if a.sp[i]!=0:
                        outputSP[i]=a.sp[i]

        if outputSP==sp:
            return ArmourSet(outputArmour)
        
        prospectArmour=prospectArmour[1:]

    raise "Invalid or nonstandard set of armour, update equipment list with appropriate armour option or manually construct the armour set"
    #fail condition/approx

GUN_LIST=generateGunList()
ARMOUR_LIST=generateArmourList()

if __name__=='__main__':
    scrapeGuns()
    scrapeArmour()