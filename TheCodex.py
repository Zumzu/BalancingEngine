from PIL import ImageTk, Image
import tkinter as tk
from tkinterdnd2 import DND_FILES, TkinterDnD

from Modules.Character import Skillset,Character


testChar=Character('james')
print(testChar.getSkill("agility"))
print(testChar.getNetSkill("agility"))

print()
raise

window = TkinterDnD.Tk()
window.title("The Cyberpunk Mk2 Codex")

window.rowconfigure([0,1,2,3,4], minsize=150, weight=1)
window.columnconfigure([0,2], minsize=300, weight=1)
window.columnconfigure(1, minsize=600, weight=2)

imageFrame = tk.Frame(window, relief=tk.RAISED, bd=2)
imageFrame.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=5, pady=5)
imagePanel=tk.Label(imageFrame)
imagePanel.pack()

armorFrame = tk.Frame(window, relief=tk.RAISED, bd=2)
armorFrame.grid(row=0, column=1, rowspan=2, sticky="nsew", padx=5, pady=5)

statsFrame = tk.Frame(window, relief=tk.RAISED, bd=2)
statsFrame.grid(row=2, column=0, rowspan=3, sticky="nsew", padx=5, pady=5)

gunFrame = tk.Frame(window, relief=tk.RAISED, bd=2)
gunFrame.grid(row=2, column=1, rowspan=3, sticky="nsew", padx=5, pady=5)

itemsFrame = tk.Frame(window, relief=tk.RAISED, bd=2)
itemsFrame.grid(row=0, column=2, rowspan=5, sticky="nsew", padx=5, pady=5)

def dropImage(event):
    file_path = event.data
    if file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
        img = Image.open(file_path)
        img = img.resize((250,300),Image.Resampling.LANCZOS)
        img = ImageTk.PhotoImage(img)
        imagePanel.config(image=img)
        imagePanel.image = img


window.drop_target_register(DND_FILES)
window.dnd_bind('<<Drop>>', dropImage)
window.mainloop()