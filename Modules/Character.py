import firebase_admin
from firebase_admin import credentials,firestore
import json

from Modules.Base import Unit,Weapon,ArmourSet,Armour

firebase_admin.initialize_app(credentials.Certificate("C:/Users/zaneg/Documents/Junk Drawer/dt-tracker-d5d20-firebase-adminsdk-5sitn-0e6ea61dcc.json"))
DB = firebase_admin.firestore.client()


class Skillset:
    def __init__(self,skillList:list[dict]=None):
        if skillList is not None:
            self.skillList=skillList
        else:
            with open('Modules/skillset.json','r') as f:
                self.skillList=json.load(f)['BASESKILLSET']

    def getStat(self,input:str):
        for stat in self.skillList:
            if input in stat['name']:
                return stat['value']
        raise
    
    def setStat(self,input:str,newValue:int):
        for stat in self.skillList:
            if input in stat['name']:
                stat['value']=newValue
                return
        raise

    def getSkill(self,input:str):
        for stat in self.skillList:
            value=stat['skills'].get(input)
            if value is not None:
                return value
                
    def setSkill(self,input:str,newValue:int):
        for stat in self.skillList[:-1]:
            if stat['skills'].get(input) is not None:
                stat['skills'][input]=newValue
                return
        self.skillList[-1]['skills'][input]=newValue

    def getNetSkill(self,input:str):
        for stat in self.skillList:
            value=stat['skills'].get(input)
            if value is not None:
                return value+stat['value']

    def updateUnit(self,unit:Unit):
        unit.cool=self.skillList[4]['value']
        unit.body=self.skillList[7]['value']
        unit.ws=max(self.getNetSkill('handgun'),self.getNetSkill('rifle'))
        unit.dodge=self.getNetSkill('dodge')    #TODO



class Character:
    def __init__(self,name):
        self.name=name
        if not self._loadCharacter(name):
            self.skillSet=Skillset()
            self.weapons:list[Weapon]=[]
            #self.items:list[Item]=[]

    def _loadCharacter(self,name):
        users_ref = DB.collection("characters")

        doc = users_ref.document(name).get()
        if doc.exists:
            data=doc.to_dict()
            self.skillSet=Skillset(data['skillset'])
            self.weapons:list[Weapon]=[]    #TODO
            return True
        
        return False

    def saveCharacter(self):
        charRef=DB.collection("characters")

        charDict={'skillset': [skill for skill in self.skillSet.skillList]}
        charRef.document(self.name).set(charDict)

    def getStat(self,input:str) -> int:
        return self.skillSet.getStat(input)
    
    def setStat(self,input:str,newValue:int):
        self.skillSet.setStat(input,newValue)

    def getSkill(self,input:str) -> int:
        return self.skillSet.getSkill(input)
                
    def setSkill(self,input:str,newValue:int):
        self.skillSet.setSkill(input,newValue)

    def getNetSkill(self,input:str) -> int:
        return self.skillSet.getNetSkill(input)
    
    def genUnit(self) -> Unit:
        return Unit(self.weapons[0], ArmourSet([]), max(self.getNetSkill('handgun'), self.getNetSkill('rifle')), self.skillSet.getStat('body'), self.skillSet.getStat('cool'), self.skillSet.getSkill('dodge'))


"""
Unit :)

Hierarchy:
    Weapons - external, primary on unit
    Armour - link to unit
    Items
    Cyberware (Items)
    Special Rules (Items)

Extra Stats: {dict}
    Luck
    Int
    Tech
    Emp
    Dex
    Ref
    MA

Skills: {dict}
    Handgun/SMG
    Rifle/Shotgun
    Melee
    Brawl
    Dodge
    Stealth
    Willpower
    Awareness
    First Aid
    Throwing


"""