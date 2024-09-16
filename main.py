#!/usr/bin/python3

import tkinter as tk
from arduino import Arduino
from steps import Steps
from gui import ApplicationWindow
from gui import StepsDisplay
from gui import AlarmPopup
from gui import TimerDisplay
from pin_handler import PinHandler
import time
import os.path

arduino_address = ""

for address in os.listdir("/dev/serial/by-id"):

    if "Arduino" in address:

        arduino_address = '/dev/serial/by-id/' + address

       
baud_rate = 460800

root = tk.Tk()
root.title("test GUI")
# Adjust the root geometry to fit the frames
#root.geometry("1200x650")
#root.resizable(False, False)

#root.attributes('-fullscreen', True)

layout = dict()

# Adjust the width of the frames to fit within the root window
layout['frame_left'] = tk.Frame(root, width=900, height=600, bd=2, relief="raised")
layout['frame_right'] = tk.Frame(root, width=300, height=600, bd=2, relief="raised")
layout['frame_bottom'] = tk.Frame(root, width=1200, height=50, bd=2, relief="raised")

# Use grid to place the frames
layout['frame_left'].grid(row=0, column=0, sticky="nsew", padx=10)
layout['frame_right'].grid(row=0, column=1, sticky="ne", padx=10)
layout['frame_bottom'].grid(row=1, column=0, columnspan=2, sticky="ew")

# Configure grid weights
root.grid_rowconfigure(0, weight=1)
root.grid_rowconfigure(1, weight=0)
root.grid_columnconfigure(0, weight=3)  # Adjusted weight for frame_left
root.grid_columnconfigure(1, weight=1)  # Adjusted weight for frame_right

# Prevent the frames from resizing based on their content
layout['frame_left'].grid_propagate(False)
layout['frame_right'].grid_propagate(False)
layout['frame_bottom'].grid_propagate(False)

arduino = Arduino()

pin_handler = PinHandler()

steps_display = StepsDisplay(layout['frame_left'], number_of_labels=14, pady=10)

timer_display = TimerDisplay(root, layout['frame_right'])

steps = Steps(steps_display, timer_display, arduino, pin_handler)

application_window = ApplicationWindow(root, layout, steps, steps_display, timer_display, pin_handler, arduino, arduino_address, baud_rate)

alarm_popup = AlarmPopup(root, steps, stop_button_handler=application_window.control_panel.stop_button_press)

steps.alarm_on.trace_add('write', alarm_popup.show) # tkinter callback monitors flag

root.protocol("WM_DELETE_WINDOW", application_window.on_close)

application_window.run()
