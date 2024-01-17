import tkinter as tk
from steps import Steps
from gui import ApplicationWindow
from gui import StepsDisplay
from gui import AlarmPopup
import time

arduino_address = '/dev/ttyACM0'
baud_rate = 460800

root = tk.Tk()

steps_display = StepsDisplay(root, number_of_labels=14, pady=10)

steps = Steps(steps_display)

application_window = ApplicationWindow(root, steps, steps_display, arduino_address, baud_rate)

alarm_popup = AlarmPopup(root, steps, stop_button_handler=application_window.control_panel.stop_button_press)

steps.alarm_on.trace_add('write', alarm_popup.show) # tkinter callback monitors flag

root.protocol("WM_DELETE_WINDOW", application_window.on_close)

application_window.run()
