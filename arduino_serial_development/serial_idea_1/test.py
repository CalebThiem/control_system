import tkinter as tk
from tkinter import ttk
from steps import Steps
from gui import Gui

def on_close():

    steps.cancel()

    root.destroy()


root = tk.Tk()
root.title("test GUI")
root.geometry("1200x650")
root.resizable(False, False)

frame_left = tk.Frame(root, width=600, height=600)
frame_right = tk.Frame(root, width=600, height=600)
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



bottom_button_0 = ttk.Button(frame_bottom, text="Next", command=steps.load_next_step)
bottom_button_1 = ttk.Button(frame_bottom, text="Previous", command=steps.load_previous_step)
bottom_button_2 = ttk.Button(frame_bottom, text="Start", command=steps.call_current_thread)
bottom_button_3 = ttk.Button(frame_bottom, text="Stop", command=steps.cancel)
bottom_button_4 = ttk.Button(frame_bottom, text="Pause")


bottom_button_0.pack(side=tk.LEFT, padx=20, pady=20)
bottom_button_1.pack(side=tk.LEFT, padx=20, pady=20)
bottom_button_2.pack(side=tk.LEFT, padx=20, pady=20)
bottom_button_3.pack(side=tk.LEFT, padx=20, pady=20)
bottom_button_4.pack(side=tk.LEFT, padx=20, pady=20)

root.protocol("WM_DELETE_WINDOW", on_close)

root.mainloop()
