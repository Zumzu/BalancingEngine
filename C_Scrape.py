from Modules.Generator import scrapeGuns,scrapeArmour,scrapeMelee
import firebase_admin
from firebase_admin import credentials,firestore

def pushGunList(): # pushing to DB deligated to codex project, scraping for engine should be purely local
    cred = credentials.Certificate("C:/Users/zaneg/Documents/Junk Drawer/dt-tracker-d5d20-firebase-adminsdk-5sitn-0e6ea61dcc.json")
    firebase_admin.initialize_app(cred)

    db = firebase_admin.firestore.client()

    guns_ref = db.collection("guns")

    with open('D_Guns.csv') as f:
        for line in f.read().split('\n'):
            gunDict={}
            name,cost,wa,d6,more,rof,mag=line.split(',')
            gunDict['cost']=int(cost)
            gunDict['wa']=int(wa)
            gunDict['d6']=int(d6)
            gunDict['more']=int(more)
            gunDict['rof']=int(rof)
            gunDict['mag']=int(mag)
            gunDict['version']='1.2'

            guns_ref.document(name).set(gunDict)

scrapeGuns()
#scrapeArmour()
#scrapeMelee()