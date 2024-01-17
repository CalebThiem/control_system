import tkinter as tk
from tkinter import ttk
from steps import Steps
from gui import StepsDisplay
from arduino import Arduino
import time

shutdown = False

arduino_address = '/dev/ttyACM0'

baud_rate = 460800

refresh_arduino_input_data_sheduled = None

input_data_display = None

arduino_input_data = []

def on_close():

    global arduino
    global shutdown 
    global root
    
    if arduino.connection_ready:

        with arduino.lock:    
    
            arduino.disconnect()

        root.after_cancel(refresh_arduino_input_data_sheduled)

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


def refresh_arduino_input_data():
    
    global root
    global arduino
    global arduino_input_data
    global input_data_display
    global shutdown
    global refresh_arduino_input_data_sheduled

    if (arduino.connection_ready):
        
        with arduino.lock:

            arduino_input_data = arduino.read_inputs()

    else:

        arduino_input_data = ['no_connection']

    input_data_display.update_steps_display(arduino_input_data)

    refresh_arduino_input_data_sheduled = root.after(200, refresh_arduino_input_data)

def count_input_data_elements():

    global arduino

    global arduino_input_data

    if (arduino.connection_ready):
        
        with arduino.lock:

            arduino_input_data = arduino.read_inputs()

        element_count = len(arduino_input_data)

        return element_count

def connection_popup_close():

    global arduino
    global popup
    global popup_text

    if arduino.connection_ready:

        popup.destroy()

    else:

        popup_text.config(text="Arduino connection failed. Check connection and restart program")

def alarm_popup(var_name, index, mode):
    
    global root
    
    if steps.alarm_on:

        stop_button_press()

        alarm_popup = tk.Toplevel(root)
        alarm_popup.title("Alarm")
        alarm_popup_text = tk.Label(alarm_popup, text="Alarm raised. Step ended.", pady=20)
        alarm_popup_text.pack()
        
        close_button = ttk.Button(alarm_popup, text="Close", command=alarm_popup.destroy)
        close_button.pack(pady=5)
        steps.alarm_on.set(False)



def arduino_tasks():

    global arduino
    global input_data_display

    if arduino.connection_ready:
        
        input_data_display = StepsDisplay(frame_right, number_of_labels=count_input_data_elements(), pady=0)

        refresh_arduino_input_data()

root = tk.Tk()
root.title("test GUI")
root.geometry("1000x1000")
root.resizable(False, False)

frame_left = tk.Frame(root, width=900, height=600)
frame_right = tk.Frame(root, width=300, height=600)
frame_bottom = tk.Frame(root, width=1200, height=50)

frame_left.grid(row=0, column=0, sticky="nw", padx="10")
frame_right.grid(row=0, column= 1, sticky="ne", padx="10")
frame_bottom.grid(row=1, column=0, columnspan=2)

# Configure grid weights
root.grid_rowconfigure(0, weight=1)
root.grid_rowconfigure(1, weight=0)
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)

frame_left.grid_propagate(False)
frame_right.grid_propagate(False)
frame_bottom.grid_propagate(False)

popup = tk.Toplevel(root)
popup.title("Connecting")
popup_text = tk.Label(popup, text="Connecting to Arduino...", pady=20)
popup_text.pack()


steps_display = StepsDisplay(frame_left, number_of_labels=14, pady=10)
steps = Steps(steps_display)
steps.alarm_on.trace_add('write', alarm_popup)

arduino = steps.arduino
arduino.connect(arduino_address, baud_rate)

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

root.after(2000, connection_popup_close)

# Start refresh_arduino_input_data loop (arduino_tasks schedules itself to be called with root.after)

root.after(2000, arduino_tasks)

root.mainloop()

