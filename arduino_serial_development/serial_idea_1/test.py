import tkinter as tk
from tkinter import ttk
from steps import Steps
from gui import Gui

def on_close():

    steps.cancel()

    root.destroy()

def previous_button_press():

    steps.load_previous_step()

def next_button_press():

    steps.load_next_step()

def start_button_press():

    # Grey out buttons

    next_button.config(state=tk.DISABLED)

    previous_button.config(state=tk.DISABLED)

    start_button.config(state=tk.DISABLED)

    steps.call_current_thread()

    steps.start_button_pressed = True
    
    steps.stop_button_pressed = False

def stop_button_press():

    steps.cancel()

    steps.start_button_pressed = False

    steps.stop_button_pressed = True

    next_button.config(state=tk.NORMAL)

    previous_button.config(state=tk.NORMAL)

    start_button.config(state=tk.NORMAL)

   

root = tk.Tk()
root.title("test GUI")
root.geometry("1220x650")
root.resizable(False, False)

frame_left = tk.Frame(root, width=900, height=600)
frame_right = tk.Frame(root, width=300, height=600)
frame_bottom = tk.Frame(root, width=1200, height=50)

frame_left.grid(row=0, column=0, sticky="nw", padx="10")
frame_right.grid(row=0, column= 1, sticky="nw", padx="10")
frame_bottom.grid(row=1, column=0, columnspan=2)

# Configure grid weights
root.grid_rowconfigure(0, weight=1)
root.grid_rowconfigure(1, weight=0)
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)

frame_left.grid_propagate(False)
frame_right.grid_propagate(False)
frame_bottom.grid_propagate(False)


gui = Gui(frame_left)

steps = Steps(gui)

bottom_button_0 = ttk.Button(frame_bottom, text="Previous", command=previous_button_press)
bottom_button_1 = ttk.Button(frame_bottom, text="Next", command=next_button_press)
bottom_button_2 = ttk.Button(frame_bottom, text="Start", command=start_button_press)
bottom_button_3 = ttk.Button(frame_bottom, text="Stop", command=stop_button_press)
bottom_button_4 = ttk.Button(frame_bottom, text="Pause")

previous_button = bottom_button_0
next_button = bottom_button_1
start_button = bottom_button_2
stop_button = bottom_button_3

bottom_button_0.pack(side=tk.LEFT, padx=20, pady=20)
bottom_button_1.pack(side=tk.LEFT, padx=20, pady=20)
bottom_button_2.pack(side=tk.LEFT, padx=20, pady=20)
bottom_button_3.pack(side=tk.LEFT, padx=20, pady=20)
bottom_button_4.pack(side=tk.LEFT, padx=20, pady=20)

root.protocol("WM_DELETE_WINDOW", on_close)

root.mainloop()
