from tkinter import *
from tkinter.ttk import Entry
from tkinterdnd2 import DND_FILES, TkinterDnD
from ttkwidgets.autocomplete import AutocompleteCombobox
from PIL import ImageTk, Image

from Modules.Character import Character

char=Character('jame')

window = TkinterDnD.Tk()
window.title("The Cyberpunk Mk2 Codex")

window.rowconfigure([0,1,2,3,4], minsize=150, weight=1)
window.columnconfigure([0,1,2,3], minsize=200, weight=1)
window.columnconfigure(4, minsize=300, weight=2)

imageFrame = Frame(window, relief=RAISED, bd=2)
imageFrame.grid(row=0, column=0, rowspan=2, sticky="nsew")
imagePanel=Label(imageFrame)
imagePanel.pack()

armorFrame = Frame(window, relief=RAISED, bd=2)
armorFrame.grid(row=0, column=1, rowspan=2, columnspan=3, sticky="nsew")

itemsFrame = Frame(window, relief=RAISED, bd=2)
itemsFrame.grid(row=0, column=4, rowspan=5, columnspan=1, sticky="nsew")

statsFrame = Frame(window, relief=RAISED, bd=2)
statsFrame.grid(row=2, column=0, rowspan=3, sticky="nsew")

skillsFrame = Frame(window, relief=RAISED, bd=2)
skillsFrame.grid(row=2, column=1, rowspan=3, sticky="nswe")

gunFrame = Frame(window, relief=RAISED, bd=2)
gunFrame.grid(row=2, column=2, rowspan=3, columnspan=2, sticky="nsew")

consolas = ("Consolas", 24)
consolasSmall = ("Consolas", 16)

def addSkillPrompt():
    suggestions = [skillName for stat in char.skillSet.skillList for skillName, skillValue in stat.get('skills', {}).items() if skillValue == 0]
    suggestions.extend(['surgery','solo','fixer','tactician','tech','ronin','netrunner','medtech'])

    newSkillWindow = Toplevel()
    newSkillWindow.title("Add New Skill")
    Label(newSkillWindow, text="Skill Name:", font=consolasSmall).grid(row=0, column=0, sticky="w", padx=5, pady=5)
    
    skillEntry = AutocompleteCombobox(newSkillWindow, completevalues=suggestions, font=consolasSmall, width=30)
    skillEntry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
    skillEntry.set("")
    skillEntry.after(100, skillEntry.focus_set())

    def addSkill():
        skillName = skillEntry.get().strip()
        if skillName:
            char.skillSet.setSkill(skillName, 3)
            refreshSkills()
            newSkillWindow.destroy()

    skillEntry.bind('<Return>',lambda _: addSkill())
    addButton = Button(newSkillWindow, text="Add Skill", command=addSkill, font=consolasSmall)
    addButton.grid(row=2, columnspan=2, pady=10)

addSkillButton = Button(skillsFrame, text="+", command=addSkillPrompt, font=consolasSmall)
addSkillButton.grid(row=0,column=1, padx=5, sticky="ew")
def refreshSkills():
    updateSkillSum()
    for widget in skillsFrame.winfo_children()[2:]:
        widget.destroy()

    row = 1
    for stat in char.skillSet.skillList:
        for skillName, skillValue in stat.get('skills', {}).items():
            netSkillValue = char.skillSet.getSkill(skillName)
            if skillValue is not None and skillValue > 0:
                skillLabel = Label(skillsFrame, text=skillName.capitalize(), anchor="w", font=consolasSmall)
                skillLabel.grid(row=row, column=0, sticky="w")

                skillEntry = Entry(skillsFrame, font=consolasSmall, width=3, justify="center")
                skillEntry.insert(0, str(netSkillValue))
                skillEntry.grid(row=row, column=1, sticky="ew", padx=3)

                warningLabel = Label(skillsFrame, text="⚠️", font=consolasSmall, fg="red")
                warningLabel.grid(row=row, column=2, sticky="w", padx=3)
                warningLabel.grid_remove()

                def showTooltip(event):
                    tooltip = Toplevel()
                    tooltip.wm_overrideredirect(True)
                    tooltip.geometry(f"+{event.x_root + 10}+{event.y_root + 10}")
                    label = Label(tooltip, text="Value not be saved. Must be numeric and in range [0,20].", background="yellow", relief="solid", borderwidth=1)
                    label.pack()
                    warningLabel.tooltip = tooltip

                def hideTooltip(_):
                    if hasattr(warningLabel, 'tooltip'):
                        warningLabel.tooltip.destroy()
                        del warningLabel.tooltip
                
                skillEntry.bind("<KeyRelease>", lambda _, skillName=skillName, entry=skillEntry, warning=warningLabel: skillChanged(skillName, entry, warning))
                skillEntry.bind("<MouseWheel>", lambda event, skillName=skillName, entry=skillEntry, warning=warningLabel: skillScrolled(event, skillName, entry, warning))
                warningLabel.bind("<Enter>", showTooltip)
                warningLabel.bind("<Leave>", hideTooltip)
                row += 1

def populateStatsFrame():
    updateStatSum()
    for index, stat in enumerate(char.skillSet.skillList[:-1]):
        for i in range(len(char.skillSet.skillList)):
            statsFrame.rowconfigure(i, weight=1)

        label = Label(statsFrame, text=str(stat['name']).capitalize(), anchor="w", font=consolas)
        label.grid(row=index+1, column=0, sticky="w")

        valueEntry = Entry(statsFrame, font=consolas, width=3, justify="center")
        valueEntry.insert(0, str(stat['value']))
        valueEntry.grid(row=index+1, column=1, sticky="ew", padx=3)

        warningLabel = Label(statsFrame, text="⚠️", font=consolas, fg="red")
        warningLabel.grid(row=index+1, column=2, sticky="w", padx=3)
        warningLabel.grid_remove()

        valueEntry.bind("<KeyRelease>", lambda _, statName=stat['name'], entry=valueEntry, warning=warningLabel: statChanged(statName, entry, warning))
        valueEntry.bind("<MouseWheel>", lambda event, statName=stat['name'], entry=valueEntry, warning=warningLabel: statScrolled(event, statName, entry, warning))

        def showTooltip(event):
            tooltip = Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.geometry(f"+{event.x_root + 10}+{event.y_root + 10}")
            label = Label(tooltip, text="Value not be saved. Must be numeric and in range [0,20].", background="yellow", relief="solid", borderwidth=1)
            label.pack()
            warningLabel.tooltip = tooltip

        def hideTooltip(_):
            if hasattr(warningLabel, 'tooltip'):
                warningLabel.tooltip.destroy()
                del warningLabel.tooltip

        warningLabel.bind("<Enter>", showTooltip)
        warningLabel.bind("<Leave>", hideTooltip)

statSumLabel=Label(statsFrame, text='?/60', anchor="w", font=consolasSmall)
statSumLabel.grid(row=0, column=0, columnspan=3, sticky="ew")
def updateStatSum():
    statSum=0
    questionMark=False
    for stat in char.skillSet.skillList[:-1]:
        value=int(stat['value'])
        if value<3 or value>10:
            questionMark=True
        statSum+=value+max(0,value-8)

    statSumLabel.config(text=f'{statSum}{"?" if questionMark else ""}/60')

skillSumLabel=Label(skillsFrame, text='?/? | ?/?', anchor="w", font=consolasSmall)
skillSumLabel.grid(row=0, column=0, sticky="ew")
def updateSkillSum():
    littleSkillSum=0
    bigSkillSum=0
    
    for stat in char.skillSet.skillList:
        for _,skillValue in stat.get('skills', {}).items():
            if skillValue <= 3:
                littleSkillSum += skillValue
                if littleSkillSum > 24:
                    bigSkillSum += littleSkillSum-24
                    littleSkillSum = 24
            else:
                bigSkillSum += skillValue

    skillSumLabel.config(text=f'{bigSkillSum}/{50+char.skillSet.getStat("int")*2} | {littleSkillSum}/24')

def statChanged(statName: str, entry:Entry, warningLabel: Label):
    newValue=str(entry.get())
    if newValue.isnumeric() and 0 <= int(newValue) <= 20:
        char.skillSet.setStat(statName, int(newValue))
        refreshSkills()
        updateStatSum()
        warningLabel.grid_remove()
    else:
        warningLabel.grid()

def statScrolled(event, statName:str, entry:Entry, warningLabel: Label):
    try:
        currentVal = int(entry.get())
        if event.delta > 0 and currentVal < 10:
            entry.delete(0,"end")
            entry.insert(0, str(currentVal + 1))
            statChanged(statName,entry,warningLabel)
        elif event.delta < 0 and currentVal > 3:
            entry.delete(0,"end")
            entry.insert(0, str(currentVal - 1))
            statChanged(statName,entry,warningLabel)
    except ValueError:
        pass

def skillChanged(skillName: str, entry:Entry, warningLabel: Label):
    newValue=str(entry.get())
    if newValue.isnumeric() and 0 <= int(newValue) <= 20:
        char.skillSet.setSkill(skillName, int(newValue))
        updateSkillSum()
        warningLabel.grid_remove()
        if int(newValue)==0:
            refreshSkills()
    else:
        warningLabel.grid()

def skillScrolled(event, skillName:str, entry:Entry, warningLabel: Label):
    try:
        currentVal = int(entry.get())
        if event.delta > 0 and currentVal < 10:
            entry.delete(0,"end")
            entry.insert(0, str(currentVal + 1))
            skillChanged(skillName,entry,warningLabel)
        elif event.delta < 0 and currentVal > 1:
            entry.delete(0,"end")
            entry.insert(0, str(currentVal - 1))
            skillChanged(skillName,entry,warningLabel)
    except ValueError:
        pass

def dropImage(event):
    file_path = event.data
    if file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
        img = Image.open(file_path)
        img = img.resize((200,280),Image.Resampling.LANCZOS)
        img = ImageTk.PhotoImage(img)
        imagePanel.config(image=img)
        imagePanel.image = img

def onClose():
    char.saveCharacter()    
    window.destroy()

populateStatsFrame()
refreshSkills()
window.protocol("WM_DELETE_WINDOW",onClose)
window.drop_target_register(DND_FILES)
window.dnd_bind('<<Drop>>', dropImage)
window.iconphoto(False,PhotoImage(file='./DT_Images/Misc/EngineIco.png'))
window.mainloop()