import tkinter

from matplotlib.animation import FuncAnimation

import random

import numpy as np

from matplotlib.figure import Figure

from collections import deque

from matplotlib.backend_bases import key_press_handler

from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)

data_points = deque([], 50)

def add_data_point(data_points):

    data_points.appendleft(random.randint(4, 8))    

for i in range(50):

    data_points.append(0)


root = tkinter.Tk()
root.wm_title("Sine graph")
root.attributes('-fullscreen', True)


fig = Figure(figsize=(5, 4), dpi=100)
ax =fig.add_subplot()
ax.set_ylim(0, 10)

add_data_point(data_points)

line, = ax.plot(data_points)
ax.set_xlabel("Data Point")
ax.set_ylabel("value")

def update_line(data_points, frame):

    for i in range(1):

        add_data_point(data_points)

    line.set_ydata(data_points)

    return line,

def animate(frame):

    return(update_line(data_points, frame))

canvas = FigureCanvasTkAgg(fig, master=root)

canvas.draw()

ani = FuncAnimation(fig, animate, frames=100, interval=50, blit=True)

canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=True)

tkinter.mainloop()

