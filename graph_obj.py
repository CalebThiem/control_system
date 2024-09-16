import tkinter

from matplotlib.animation import FuncAnimation

import random

import numpy as np

from matplotlib.figure import Figure

from collections import deque

from matplotlib.backend_bases import key_press_handler

from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)


class Graph:

    def __init__(self, parent_window):

        self.data_points = deque([], 50)

        for i in range(50):

            self.data_points.append(0)

        self.root = parent_window

        self.fig = Figure(figsize=(3, 1), dpi=100, frameon=True, layout='tight')
        self.ax = self.fig.add_subplot()
        self.ax.set_ylim(0, 10)

        self.add_data_point()

        self.line, = self.ax.plot(self.data_points)
        self.ax.set_xlabel("Data Point")
        self.ax.set_ylabel("value")

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)

        self.canvas.draw()

        self.ani = FuncAnimation(self.fig, self.animate, frames=100, interval=60, blit=True)

        self.canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, pady=10, expand=True)


    def add_data_point(self):

        self.data_points.appendleft(random.randint(4, 8))    


    def update_line(self, frame):

        for i in range(1):

            self.add_data_point()

        self.line.set_ydata(self.data_points)

        return self.line,

    def animate(self, frame):

        return(self.update_line(frame))


