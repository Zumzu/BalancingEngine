import requests
from bs4 import BeautifulSoup
import firebase_admin
from firebase_admin import credentials,firestore

def scrapeItemsSection():
    cred = credentials.Certificate("C:/Users/zaneg/Documents/Junk Drawer/dt-tracker-d5d20-firebase-adminsdk-5sitn-0e6ea61dcc.json")
    firebase_admin.initialize_app(cred)
    ref = firestore.client().collection("items")

    html = requests.get('https://docs.google.com/spreadsheets/d/1Q5rBjDjx-MNGIl-JAVhtFT33W-T9RpQgg4bTRQuFYPA/gviz/tq?tqx=out:html&tq&gid=1740571340').text
    soup = BeautifulSoup(html, 'lxml') # lxml and bs4 required
    table = soup.find_all('table')[0]
    rows = [[td.text for td in row.find_all("td")] for row in table.find_all('tr')] # html magic

    for row in rows: # construct guns
        if str(row[1]).isnumeric(): # if cell 2 is a number itll try to read the full line, care
            newItem=dict()
            newItem['cost']=int(row[1])
            newItem['rarity']=str(row[2])
            newItem['desc']=str(row[3])
            newItem['version']='1.3'

            ref.document(row[0]).set(newItem)

scrapeItemsSection()