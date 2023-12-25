import tkinter as tk
from tkinter import ttk
from tkinter import font as tkFont

class Gui:

    def __init__(self, frame):
        
        self.bold_font = tkFont.Font(family="Helvetica", size=12, weight="bold")
        
        self.text_label_variables = []

        self.number_of_labels = 14

        for i in range(self.number_of_labels):

            text = tk.StringVar()

            self.text_label_variables.append(text)

        self.text_labels = []

        text_label = tk.Label(frame, textvariable=self.text_label_variables[0], font=self.bold_font)

        text_label.pack(anchor='nw', pady=10)

        self.text_labels.append(text_label)

        for i in range(1, len(self.text_label_variables)):

            text_label = tk.Label(frame, textvariable=self.text_label_variables[i])

            text_label.pack(anchor='nw', pady=10)

            self.text_labels.append(text_label)


    def update_gui(self, list_of_strings):

        print("gui.update_gui called")
    
        for index in range(len(list_of_strings)):

            self.text_label_variables[index].set(list_of_strings[index])
            


            
