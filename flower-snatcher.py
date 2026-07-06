import tkinter as tk
from tkinter import simpledialog as sd
from tkinter import messagebox as mb
import random

window = tk.Tk()
window.title("Snatch the Flower")

snatching = tk.Canvas(window, height=1000, width=5000, bg="Light Green")
snatching.pack()
window.focus_set()

flower = snatching.create_oval(650, 350, 750, 450, outline="black", fill="yellow")

colours = ["yellow", "blue", "red", "green", "purple", "orange", "pink"]

def prepare(event=None):
    a=sd.askstring('Player Names', 'Name (nickname) of Player 1')
    b=sd.askstring('Player Names', 'Name (nickname) of Player 2')

prepare()

def catch(event=None):
    global flower
    snatching.delete(flower)
    window.after(1000, restart_flower)

def restart_flower():
    global flower
    random_colour = random.choice(colours)
    flower = snatching.create_oval(650, 350, 750, 450, outline="black", fill=random_colour)

snatching.bind("<KeyPress-space>", catch)
snatching.focus_set()

window.mainloop()