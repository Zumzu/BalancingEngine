import requests
from bs4 import BeautifulSoup

def processDamage(rawInput):
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

    with open('Scraped.csv','w') as f: # save to file, ternary is just to remove last '\n'
        for gun in guns:
            f.write(','.join(gun) + ('\n' if gun!=guns[-1] else ''))

if __name__=='__main__':
    scrapeGuns()