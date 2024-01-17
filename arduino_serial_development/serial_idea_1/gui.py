# gui.py

from tkinter import font as tkFont
import tkinter as tk
from tkinter import ttk


class ControlPanel:
    def __init__(self, parent, steps):
        self.steps = steps
        self.start_button = tk.Button(parent, text="Start", command=self.start_button_press)
        self.stop_button = tk.Button(parent, text="Stop", command=self.stop_button_press, state=tk.DISABLED)
        self.next_button = tk.Button(parent, text="Next", command=self.next_button_press)
        self.previous_button = tk.Button(parent, text="Previous", command=self.previous_button_press)

        # Layout the buttons
        self.start_button.pack()
        self.stop_button.pack()
        self.next_button.pack()
        self.previous_button.pack()

    def start_button_press(self):
        # Grey out start button, enable stop button
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)

        # Start action logic
        self.steps.call_current_thread()
        self.steps.start_button_pressed = True

    def stop_button_press(self):
        # Cancel the current step
        self.steps.cancel()

        # Update button states
        self.steps.start_button_pressed = False
        self.steps.stop_button_pressed = True
        self.next_button.config(state=tk.NORMAL)
        self.previous_button.config(state=tk.NORMAL)
        self.start_button.config(state=tk.NORMAL)

    def next_button_press(self):
        # Load the next step
        self.steps.load_next_step()

    def previous_button_press(self):
        # Load the previous step
        self.steps.load_previous_step()


class ArduinoInterface:
    def __init__(self, parent, arduino, address, baud_rate, on_close_callback):
        self.root = parent
        self.address = address
        self.baud_rate = baud_rate
        self.arduino = arduino
        self.on_close_callback = on_close_callback
             
        # Show connection popup

        self.popup = tk.Toplevel(self.root)
        self.popup.title("Connecting")
        self.popup_text = tk.Label(self.popup, text="Connecting to Arduino...", pady=20)
        self.popup_text.pack()

        # Initialize Arduino connection here (if applicable)
        self.connect_arduino()

        # Wait for connection attempt to finish and update popup

        self.root.after(2000, self.update_connection_popup)
    
    def update_connection_popup(self):

        print("Arduino connected: ", self.arduino.connection_ready)
        print("Arduino address: ", self.address)
        print("Arduino baud rate: ", self.baud_rate)

        if self.arduino.connection_ready:

            self.popup.destroy()

        else:

            self.popup_text.config(text="Arduino connection failed. Check connection and restart program")

    def connect_arduino(self):
        # Method to handle Arduino connection
        # Example: self.arduino = Arduino(self.address, self.baud_rate)
        self.arduino.connect(self.address, self.baud_rate)

    def disconnect_arduino(self):
        # Method to handle Arduino disconnection
        # Example: self.arduino.disconnect()
        self.arduino.disconnect()

    def on_close(self):
        # Method to handle closing events
        # Perform necessary cleanup
        self.disconnect_arduino()
        if self.on_close_callback:
            self.on_close_callback()


class StepsDisplay:
    def __init__(self, parent, number_of_labels, pady):
        self.text_label_variables = [tk.StringVar() for _ in range(number_of_labels)]
        self.text_labels = []
        self.number_of_labels = number_of_labels
        self.bold_font = tkFont.Font(family="Helvetica", size=12, weight="bold")

        for i, text_var in enumerate(self.text_label_variables):
            label = tk.Label(parent, textvariable=text_var, font=self.bold_font if i == 0 else None)
            label.pack(anchor='nw', pady=pady)
            self.text_labels.append(label)

    def update_steps_display(self, list_of_strings):
        # Update the text of the labels to display the new steps
        for text_var, new_text in zip(self.text_label_variables, list_of_strings):
            text_var.set(new_text)

    def clear_steps_display(self):
        # Clear the text of all labels
        for text_var in self.text_label_variables:
            text_var.set("")


class ApplicationWindow:
    def __init__(self, root, steps, steps_display, arduino_address, baud_rate):
        self.root = root
        self.root.title("Application Title")  # Set your application's title

        # Initialize the StepsDisplay
        self.steps_display = steps_display

        # Initialize the ControlPanel
        self.control_panel = ControlPanel(self.root, steps)

        # Initialize the ArduinoInterface
        self.arduino_interface = ArduinoInterface(self.root, steps.arduino, arduino_address, baud_rate, None)

        # Additional setup can be done here (e.g., menu bars, status bars, additional frames/panels)

    def run(self):
        # Start the main loop of the application
        self.root.mainloop()

    def on_close(self):
        # Define actions to perform when closing the application
        # This can include saving state, prompting the user, etc.
        self.arduino_interface.on_close()
        self.root.destroy()


class AlarmPopup:
    def __init__(self, parent, steps, stop_button_handler):
        self.parent = parent
        self.steps = steps
        self.stop_button_handler = stop_button_handler

    def show(self, var_name, index, mode): # Arguments are for tkinter callback functionality
        if self.steps.alarm_on:
            # Call the stop button handler to handle any ongoing process
            self.stop_button_handler()

            # Create a top-level window as a popup
            alarm_popup_window = tk.Toplevel(self.parent)
            alarm_popup_window.title("Alarm")

            # Add a label with the alarm message
            alarm_popup_text = tk.Label(alarm_popup_window, text="Alarm raised. Step ended.", pady=20)
            alarm_popup_text.pack()

            # Add a close button to the popup
            close_button = ttk.Button(alarm_popup_window, text="Close", command=alarm_popup_window.destroy)
            close_button.pack(pady=5)

            # Reset the alarm flag
            self.steps.alarm_on.set(False)
