from PIL import ImageTk, Image
import tkinter as tk
from tkinterdnd2 import DND_FILES, TkinterDnD

from Modules.Character import Character

char=Character('jame')

window = TkinterDnD.Tk()
window.title("The Cyberpunk Mk2 Codex")

window.rowconfigure([0,1,2,3,4], minsize=150, weight=1)
window.columnconfigure([0,1,2,3], minsize=200, weight=1)
window.columnconfigure(4, minsize=300, weight=2)

imageFrame = tk.Frame(window, relief=tk.RAISED, bd=2)
imageFrame.grid(row=0, column=0, rowspan=2, sticky="nsew")
imagePanel=tk.Label(imageFrame)
imagePanel.pack()

armorFrame = tk.Frame(window, relief=tk.RAISED, bd=2)
armorFrame.grid(row=0, column=1, rowspan=2, columnspan=3, sticky="nsew")

itemsFrame = tk.Frame(window, relief=tk.RAISED, bd=2)
itemsFrame.grid(row=0, column=4, rowspan=5, columnspan=1, sticky="nsew")

statsFrame = tk.Frame(window, relief=tk.RAISED, bd=2)
statsFrame.grid(row=2, column=0, rowspan=3, columnspan=2, sticky="nsew")

gunFrame = tk.Frame(window, relief=tk.RAISED, bd=2)
gunFrame.grid(row=2, column=2, rowspan=3, columnspan=2, sticky="nsew")

def statChanged(statName:str, newValue:str):
    if newValue.isnumeric() and int(newValue)>0 and int(newValue)<=20:
        char.skillSet.setStat(statName,newValue)

consolas = ("Consolas", 24)

for index,stat in enumerate(char.skillSet.skillList[:-1]):
    for i in range(len(char.skillSet.skillList)-1):
        statsFrame.rowconfigure(i,weight=1)

    label = tk.Label(statsFrame, text=str(stat['name']).capitalize(), anchor="w", font=consolas)
    label.grid(row=index, column=0, sticky="w")

    valueEntry = tk.Entry(statsFrame, font=consolas, width=3,justify="center")
    valueEntry.insert(0, str(stat['value']))
    valueEntry.grid(row=index, column=1, sticky="ew", padx=3)

    valueEntry.bind(    
        "<FocusOut>",
        lambda _, statName=stat['name'], entry=valueEntry: statChanged(statName, entry.get())
    )

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

window.protocol("WM_DELETE_WINDOW",onClose)
window.drop_target_register(DND_FILES)
window.dnd_bind('<<Drop>>', dropImage)
window.mainloop()