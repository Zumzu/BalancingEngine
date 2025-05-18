from random import randint

def processDamage(input):
    dmg=0
    rolled=[]
    more=0
    try:
        if '-' in input:
            input=input.upper().strip().split("-")
            input[-1]=str(-int(input[-1]))
        else:
            input=input.upper().strip().split("+")

        for item in input:
            if(item.__contains__("D")):
                multiple,dieType=item.split("D")
                if(multiple==""):
                    multiple=1
                for _ in range(int(multiple)):
                    result=randint(1,int(dieType))
                    rolled.append(result)
                    dmg+=result
            else:#its just a number
                more+=int(item)
                dmg+=int(item)
      
    except:
        print("@@FAILED DMG EVAL@@")

    return (dmg,rolled,more)