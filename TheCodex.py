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

consolas = ("Consolas", 24)

def populateStatsFrame():
    for index, stat in enumerate(char.skillSet.skillList[:-1]):
        for i in range(len(char.skillSet.skillList) - 1):
            statsFrame.rowconfigure(i, weight=1)

        label = tk.Label(statsFrame, text=str(stat['name']).capitalize(), anchor="w", font=consolas)
        label.grid(row=index, column=0, sticky="w")

        valueEntry = tk.Entry(statsFrame, font=consolas, width=3, justify="center")
        valueEntry.insert(0, str(stat['value']))
        valueEntry.grid(row=index, column=1, sticky="ew", padx=3)

        warningLabel = tk.Label(statsFrame, text="⚠️", font=consolas, fg="red")
        warningLabel.grid(row=index, column=2, sticky="w", padx=3)
        warningLabel.grid_remove()

        valueEntry.bind("<FocusOut>", lambda _, statName=stat['name'], entry=valueEntry, warning=warningLabel: statChanged(statName, entry, warning))
        valueEntry.bind("<MouseWheel>", lambda event, statName=stat['name'], entry=valueEntry, warning=warningLabel: scrollValue(event, statName, entry, warning))

        def showTooltip(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.geometry(f"+{event.x_root + 10}+{event.y_root + 10}")
            label = tk.Label(tooltip, text="Value not be saved. Must be numeric and in range [0,20].", background="yellow", relief="solid", borderwidth=1)
            label.pack()
            warningLabel.tooltip = tooltip

        def hideTooltip(_):
            if hasattr(warningLabel, 'tooltip'):
                warningLabel.tooltip.destroy()
                del warningLabel.tooltip

        warningLabel.bind("<Enter>", showTooltip)
        warningLabel.bind("<Leave>", hideTooltip)

def statChanged(statName: str, entry:tk.Entry, warningLabel: tk.Label):
    newValue=str(entry.get())
    if newValue.isnumeric() and 0 <= int(newValue) <= 20:
        char.skillSet.setStat(statName, newValue)
        warningLabel.grid_remove()
    else:
        warningLabel.grid()

def scrollValue(event, statName:str, entry:tk.Entry, warningLabel: tk.Label):
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
window.protocol("WM_DELETE_WINDOW",onClose)
window.drop_target_register(DND_FILES)
window.dnd_bind('<<Drop>>', dropImage)
window.mainloop()