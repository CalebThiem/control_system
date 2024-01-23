import matplotlib
matplotlib.use('TkAgg')
print(matplotlib.get_backend())
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from tkinter import font as tkFont
import tkinter as tk
from tkinter import ttk
from collections import deque
from testClass import SensorDisplayNew
from testClass import SensorDisplayFast

# Buttons
class ControlPanel: 
    def __init__(self, parent, steps, sensor_display):
        self.parent = parent
        self.steps = steps
        self.sensor_display = sensor_display

        self.start_button = tk.Button(parent, text="Start", command=self.start_button_press)
        self.stop_button = tk.Button(parent, text="Stop", command=self.stop_button_press, state=tk.DISABLED)
        self.next_button = tk.Button(parent, text="Next", command=self.next_button_press)
        self.previous_button = tk.Button(parent, text="Previous", command=self.previous_button_press)
        
        self.sensor_display_popup_button = tk.Button(parent, text="Raw Input Data", command=self.sensor_display.show_popup)

        # Layout the buttons
        self.start_button.pack(side=tk.LEFT, padx=20, pady=20)
        self.stop_button.pack(side=tk.LEFT, padx=20, pady=20)
        self.next_button.pack(side=tk.LEFT, padx=20, pady=20)
        self.previous_button.pack(side=tk.LEFT, padx=20, pady=20)
        self.sensor_display_popup_button.pack(side=tk.LEFT, padx=20, pady=20)

    def start_button_press(self):
        # Grey out start button, enable stop button
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.next_button.config(state=tk.DISABLED)
        self.previous_button.config(state=tk.DISABLED)
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

# Arduino connection, connection popup
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
        with self.arduino.lock:

            self.arduino.disconnect()

    def on_close(self):
        # Method to handle closing events
        # Perform necessary cleanup
        self.disconnect_arduino()
        if self.on_close_callback:
            self.on_close_callback()

# Steps display, tkinter is not thread-safe, so step threads update the UI through this class
class StepsDisplay:
    def __init__(self, parent, number_of_labels, pady):
        self.parent = parent
        self.parent.update() # First call preceeds mainloop start, resulting in a width of 1, if update() is not called
        parent.pack_propagate(False) # Prevents the frame from resizing
        self.text_label_variables = [tk.StringVar() for _ in range(number_of_labels)] # Step threads update this list with text to be displayed
        self.text_labels = [] 
        self.number_of_labels = number_of_labels
        self.bold_font = tkFont.Font(family="Helvetica", size=12, weight="bold")

        for i, text_var in enumerate(self.text_label_variables):
            label = tk.Label(parent, textvariable=text_var, font=self.bold_font if i == 0 else None, justify=tk.LEFT)
            label.pack(anchor='nw', pady=pady)
            self.text_labels.append(label)

    def update_steps_display(self, list_of_strings):
         
        frame_width = self.parent.winfo_width()

        for label in self.text_labels:

            label.config(wraplength=frame_width)
        
        # Update the text of the labels to display the new steps
        for text_var, new_text in zip(self.text_label_variables, list_of_strings):
            text_var.set(new_text)

    def clear_steps_display(self):
        # Clear the text of all labels
        for text_var in self.text_label_variables:
            text_var.set("")

# Generates the UI, creates instances of necessary classes to make everything work
class ApplicationWindow:
    def __init__(self, root, layout, steps, steps_display, arduino, arduino_address, baud_rate):
        self.root = root
        self.steps = steps
        
        self.layout = layout

        # Initialize the StepsDisplay
        self.steps_display = steps_display

        #self.sensor_display = SensorDisplayNew(self.root, arduino)
        self.sensor_display = SensorDisplay(self.root, arduino)

        # Initialize the ControlPanel
        self.control_panel = ControlPanel(self.layout['frame_bottom'], steps, self.sensor_display)


        # Initialize the ArduinoInterface
        self.arduino_interface = ArduinoInterface(self.root, arduino, arduino_address, baud_rate, None)

        # Additional setup can be done here (e.g., menu bars, status bars, additional frames/panels)

    def run(self):
        # Start the main loop of the application
        self.root.mainloop()

    def on_close(self):
        # Define actions to perform when closing the application
        # This can include saving state, prompting the user, etc.
        self.steps.step_running = False # End while loop of any running threads
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

class SensorDisplay:

    def __init__(self, root, arduino):
        self.refresh_rate_millis = 2000
        self.y_axis_resolution = 3000
        self.root = root
        self.arduino = arduino
        self.update_id = None
        self.data_labels = {}
        self.graphs = {}
        self.data_points = {}  # Dynamically populated based on analog inputs
        self.graph_mode = tk.IntVar(value=1)
    def change_display_settings(self, new_y_axis_resolution, new_refresh_rate):
        # Update y-axis resolution
        self.y_axis_resolution = new_y_axis_resolution
        for key in self.graphs:
            graph = self.graphs[key]
            ax = graph['ax']

            # Reset y-axis limits and clear data points
            ax.set_xlim(0, self.y_axis_resolution)
            self.data_points[key] = deque(maxlen=self.y_axis_resolution)  # Reset data points
            self.clear_graph_data(key)

        # Update refresh rate
        self.refresh_rate_millis = new_refresh_rate
        self.restart_display_loop()

    def clear_graph_data(self, key):
        if key in self.graphs:
            graph = self.graphs[key]
            line = graph['line']
            canvas = graph['canvas']

            # Clear the line data
            line.set_data([], [])
            canvas.draw()

    def update_graph_layout(self, key):
        if key in self.graphs:
            graph = self.graphs[key]
            canvas = graph['canvas']
            ax = graph['ax']
            canvas.draw()
            graph['bg'] = canvas.copy_from_bbox(ax.bbox)

    def restart_display_loop(self):
        self.stop_displaying()
        self.start_displaying()

    def on_radio_button_change(self):
        # Check the value of 'selected_function' and call the appropriate function
        if self.graph_mode.get() == 1:
            self.change_display_settings(new_y_axis_resolution=2000, new_refresh_rate=3000)
        elif self.graph_mode.get() == 2:
            self.change_display_settings(300, 20)

    def read_arduino(self):
        if self.arduino.connection_ready:
            with self.arduino.lock:
                self.arduino_input_data = self.arduino.read_inputs()

        data = dict()
        digital_input_counter = 30
        analog_input_counter = 0

        for i in self.arduino_input_data:
            if len(i) == 1:
                # Digital input
                data[str(digital_input_counter)] = i
                digital_input_counter += 1
            elif len(i) == 4:
                # Analog input
                key = f"A{analog_input_counter}"
                data[key] = int(i)  # Convert to integer
                analog_input_counter += 1

        return data

    def initialize_widgets(self, parent_frame, bottom_frame):
        # Initialize main widgets in the parent_frame

        data = self.read_arduino()
        for key in data.keys():
            var = tk.StringVar()
            label = tk.Label(parent_frame, textvariable=var)
            label.pack(anchor='nw', pady=2, padx=5)
            self.data_labels[key] = var

            if key.startswith("A"):  # For analog inputs, create graphs
                self.data_points[key] = deque(maxlen=self.y_axis_resolution)
                
                fig, ax = plt.subplots(figsize=(10, 5), dpi=100)
                line, = ax.plot([], [], linewidth=0.5, color=('teal'))
                ax.set_xlim(0, self.y_axis_resolution)
                ax.set_ylim(0, 1023)

                canvas = FigureCanvasTkAgg(fig, master=parent_frame)
                canvas_widget = canvas.get_tk_widget()
                canvas_widget.pack(anchor='nw', pady=2, padx=5)

                canvas.draw()
                self.graphs[key] = {'fig': fig, 'ax': ax, 'line': line, 'canvas': canvas, 'bg': canvas.copy_from_bbox(ax.bbox)}

        # Initialize radio buttons in the bottom_frame
        radio_button1 = tk.Radiobutton(bottom_frame, text="Slow refresh, long logging time", variable=self.graph_mode, value=1, command=self.on_radio_button_change)
        radio_button2 = tk.Radiobutton(bottom_frame, text="Fast refresh, short logging time", variable=self.graph_mode, value=2, command=self.on_radio_button_change)
        radio_button1.pack(side='left')
        radio_button2.pack(side='left')

    def show_popup(self):
        # self.control_panel_frame.sensor_display_popup_button.config(state=tk.DISABLED) move to new class passed to control panel and sensor display
        self.popup = tk.Toplevel(self.root)
        self.popup.title("Raw Sensor Data")
        self.popup.geometry("800x500")

        popup_content_frame = tk.Frame(self.popup)
        popup_content_frame.pack(side="top", fill="both", expand=True)

        popup_bottom_frame = tk.Frame(self.popup)
        popup_bottom_frame.pack(side="bottom", fill="x")

        self.canvas = tk.Canvas(popup_content_frame)
        scrollbar = tk.Scrollbar(popup_content_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.initialize_widgets(self.scrollable_frame, popup_bottom_frame)

        self.popup.protocol("WM_DELETE_WINDOW", self.on_window_close)
        self.start_displaying()

    def update_graph(self, key, value):
        if key in self.graphs:
            self.data_points[key].append(value)
            graph = self.graphs[key]
            line = graph['line']
            canvas = graph['canvas']
            ax = graph['ax']
            bg = graph['bg']

            # Update the line data
            line.set_data(range(len(self.data_points[key])), self.data_points[key])

            # Restore the background and draw the updated line
            canvas.restore_region(bg)
            ax.draw_artist(line)
            canvas.blit(ax.bbox)

    def start_displaying(self):
        self.update_data()

    def update_data(self):
        data = self.read_arduino()
        for key, value in data.items():
            if key in self.data_labels:
                self.data_labels[key].set(f"{key}: {value}")
            self.update_graph(key, value)

        self.update_id = self.root.after(self.refresh_rate_millis, self.update_data)

    def stop_displaying(self):
        if self.update_id is not None:
            self.root.after_cancel(self.update_id)
            print("Stopped loop")

    def on_window_close(self):
        self.stop_displaying()
  
        self.release_graph_resources()

        # Destroy the popup window
        self.popup.destroy()

        # self.control_panel_frame.sensor_display_popup_button.config(state=tk.NORMAL)


    def release_graph_resources(self):
        for key, graph in self.graphs.items():
            # Close the Matplotlib figure
            plt.close(graph['fig'])

            # Destroy the Tkinter canvas widget
            canvas_widget = graph['canvas'].get_tk_widget()
            canvas_widget.destroy()

        # Clear the dictionary
        self.graphs.clear()


