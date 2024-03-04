import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from tkinter import font as tkFont
import tkinter as tk
from tkinter import ttk
from collections import deque

# Set matplotlib to Tkinter mode

matplotlib.use('TkAgg')


class ControlPanel: 
    '''Displays and manages buttons on the main GUI screen'''
    def __init__(self, parent, steps, timer_display):
        self.parent = parent
        self.steps = steps
        self.timer_display = timer_display
        #self.sensor_display = sensor_display

        self.start_button = tk.Button(parent, text="Start", command=self.start_button_press)
        self.stop_button = tk.Button(parent, text="Stop", command=self.stop_button_press, state=tk.DISABLED)
        self.next_button = tk.Button(parent, text="Next", command=self.next_button_press)
        self.previous_button = tk.Button(parent, text="Previous", command=self.previous_button_press)
        
        self.sensor_display_popup_button = tk.Button(parent, text="Raw Input Data")
        self.manual_control_popup_button = tk.Button(parent, text="Manual Control")

        # Layout the buttons
        self.start_button.pack(side=tk.LEFT, padx=20, pady=20)
        self.stop_button.pack(side=tk.LEFT, padx=20, pady=20)
        self.next_button.pack(side=tk.LEFT, padx=20, pady=20)
        self.previous_button.pack(side=tk.LEFT, padx=20, pady=20)
        self.sensor_display_popup_button.pack(side=tk.LEFT, padx=20, pady=20)
        self.manual_control_popup_button.pack(side=tk.LEFT, padx=20, pady=20)

    def start_button_press(self):
        # Grey out start button, enable stop button
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.next_button.config(state=tk.DISABLED)
        self.previous_button.config(state=tk.DISABLED)
        # Start action logic
        self.timer_display.start_step_timer()
        self.timer_display.start_total_timer()
        self.steps.call_current_thread()
        self.steps.start_button_pressed = True

    def stop_button_press(self):
        # Cancel the current step
        self.timer_display.stop_step_timer() 
        self.timer_display.stop_total_timer()
        self.steps.cancel()

        # Update button states
        self.steps.start_button_pressed = False
        self.steps.stop_button_pressed = True
        self.next_button.config(state=tk.NORMAL)
        self.previous_button.config(state=tk.NORMAL)
        self.start_button.config(state=tk.NORMAL)

    def next_button_press(self):
        # Load the next step
        self.timer_display.reset_step_timer()
        self.steps.load_next_step()

    def previous_button_press(self):
        # Load the previous step
        self.timer_display.reset_step_timer()
        self.steps.load_previous_step()

class ArduinoInterface:
    '''Arduino connection, connection popup'''
    def __init__(self, parent, arduino, address, baud_rate, on_close_callback):
        self.root = parent
        self.address = address
        self.baud_rate = baud_rate
        self.arduino = arduino
        self.on_close_callback = on_close_callback
             
        # Show connection popup

        self.popup = tk.Toplevel(self.root)
        self.popup.geometry('600x50')
        self.popup.title("Connection Status")
        self.popup_text = tk.Label(self.popup, text="Connecting to Arduino...", pady=20)
        self.popup_text.pack()

        # Initialize Arduino connection
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

            self.popup_text.config(text="Arduino connection failed. Check connection and restart program.")

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

class StepsDisplay:
    '''Steps display, tkinter is not thread-safe, so step threads update the UI through this class'''
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


class TimerDisplay:

    '''Displays step time and total elapsed time on main GUI window'''

    def __init__(self, root, parent_frame):

        self.root = root

        self.step_time = 0

        self.total_time = 0

        self.step_timer_tick_after_id = None

        self.total_timer_tick_after_id = None

        self.timer_frame = tk.Frame(parent_frame, width=100, height=200, bd=2, relief="raised")



        self.step_time_display = tk.Label(self.timer_frame)

        self.step_time_display.pack(anchor='w')

        self.total_time_display = tk.Label(self.timer_frame)

        self.total_time_display.pack(anchor='w')

        self.timer_frame.place(x=5, y=5)

    def step_timer_tick(self):

        self.step_time += 1

        self.step_time_display.configure(text=f"Step elapsed time: {self.step_time}")

        self.step_timer_tick_after_id = self.root.after(1000, self.step_timer_tick)

    def total_timer_tick(self):

        self.total_time += 1

        self.total_time_display.configure(text=f"Total elapsed time: {self.total_time}")

        self.total_timer_tick_after_id = self.root.after(1000, self.total_timer_tick)

    def start_step_timer(self):

        self.step_timer_tick()

    def start_total_timer(self):

        self.total_timer_tick()

    def stop_step_timer(self):

        self.root.after_cancel(self.step_timer_tick_after_id)

    def stop_total_timer(self):

        self.root.after_cancel(self.total_timer_tick_after_id)

    def reset_step_timer(self):

        self.step_time = 0

        self.step_time_display.configure(text=f"Step elapsed time: {self.step_time}")

    def reset_total_timer(self):

        self.total_time = 0


class ApplicationWindow:
    '''Generates the UI, creates instances of necessary classes to make everything work'''
    def __init__(self, root, layout, steps, steps_display, timer_display, pin_handler, arduino, arduino_address, baud_rate):
        self.root = root
        self.steps = steps
        self.layout = layout
        self.steps_display = steps_display
        self.timer_display = timer_display

        # Initialize the ControlPanel
        self.control_panel = ControlPanel(self.layout['frame_bottom'], steps, timer_display) # self.sensor_display

        self.sensor_display = SensorDisplay(self.root, arduino, self.control_panel)

        self.button_grid = ButtonGrid(self.root, pin_handler, arduino, self.control_panel)

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
        if self.sensor_display.window_open:
            self.sensor_display.on_window_close()
        self.root.destroy()


class AlarmPopup:
    '''Popup displayed when alarm conditions are met, alerts operator'''
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
    '''Graphs displayed when Raw Sensor Data button is pressed'''
    def __init__(self, root, arduino, control_panel):
        # Window properties
        self.window_open = False
        self.root = root
        self.arduino = arduino
        self.control_panel = control_panel

        # Graph settings
        self.slow_refresh_rate_millis = 1000
        self.slow_y_axis_resolution = 2000
        self.fast_refresh_rate_millis = 20
        self.fast_y_axis_resolution = 150
        self.refresh_rate_millis = self.slow_refresh_rate_millis
        self.y_axis_resolution = self.slow_y_axis_resolution

        # Graph mode selection
        self.graph_mode = tk.IntVar(value=1)

        # Data structures for storing sensor data and graph objects
        self.data_labels = {}
        self.graphs = {}
        self.data_points = {}  # Dynamically populated based on analog inputs

        # Configure control panel button to show sensor display popup
        control_panel.sensor_display_popup_button.config(command=self.show_popup)

        # Initialize update ID for data refreshing
        self.update_id = None

    # Public methods
    def start_displaying(self):
        """Begin the data update loop."""
        self.update_data()

    def show_popup(self):
        """Create and show a popup window with sensor data and graphs."""
        # Popup window setup
        self.window_open = True
        self.control_panel.sensor_display_popup_button.config(state=tk.DISABLED)
        self.popup = tk.Toplevel(self.root)
        self.popup.title("Raw Sensor Data")
        self.popup.geometry("800x500")
        self.setup_popup_contents()
        self.popup.protocol("WM_DELETE_WINDOW", self.on_window_close)
        self.start_displaying()

    # Private helper methods
    def setup_popup_contents(self):
        """Setup the contents of the popup window."""
        # Create frames for content and controls
        popup_content_frame = tk.Frame(self.popup)
        popup_content_frame.pack(side="top", fill="both", expand=True)
        popup_bottom_frame = tk.Frame(self.popup)
        popup_bottom_frame.pack(side="bottom", fill="x")

        # Setup scrollable canvas
        self.canvas = tk.Canvas(popup_content_frame)
        scrollbar = tk.Scrollbar(popup_content_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)
        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Initialize widgets for data display and controls
        self.initialize_widgets(self.scrollable_frame, popup_bottom_frame)

    def initialize_widgets(self, parent_frame, bottom_frame):
        """Initialize widgets for displaying data and controls."""
        data = self.read_arduino()

        # Setup data labels and graphs for each sensor
        for key in data.keys():
            self.setup_data_label(parent_frame, key)
            if key.startswith("A"):  # For analog inputs, create graphs
                self.setup_graph(parent_frame, key)

        # Setup control widgets
        self.setup_control_widgets(bottom_frame)

    def setup_data_label(self, parent_frame, key):
        """Setup data label for a sensor."""
        var = tk.StringVar()
        label = tk.Label(parent_frame, textvariable=var)
        label.pack(anchor='nw', pady=2, padx=5)
        self.data_labels[key] = var

    def setup_graph(self, parent_frame, key):
        """Setup graph for a sensor."""
        self.data_points[key] = deque(maxlen=self.y_axis_resolution)
        fig, ax = plt.subplots(figsize=(10, 5), dpi=100)
        line, = ax.plot([], [], linewidth=0.5, color=('teal'))
        ax.set_xlim(0, self.y_axis_resolution)
        ax.set_ylim(0, 1023)
        ax.set_xlabel('Data Points')
        ax.set_ylabel('ADC Value (0=0V, 1023=5V)')
        canvas = FigureCanvasTkAgg(fig, master=parent_frame)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(anchor='nw', pady=2, padx=5)
        canvas.draw()
        self.graphs[key] = {'fig': fig, 'ax': ax, 'line': line, 'canvas': canvas, 'bg': canvas.copy_from_bbox(ax.bbox)}

    def setup_control_widgets(self, bottom_frame):
        """Setup control widgets in the bottom frame."""
        radio_button1 = tk.Radiobutton(bottom_frame, text="Slow refresh, long logging time", variable=self.graph_mode, value=1, command=self.on_radio_button_change)
        radio_button2 = tk.Radiobutton(bottom_frame, text="Fast refresh, short logging time", variable=self.graph_mode, value=2, command=self.on_radio_button_change)
        radio_button1.pack(side='left')
        radio_button2.pack(side='left')

    def on_window_close(self):
        """Handle the closing of the popup window."""
        self.stop_displaying()
        self.release_graph_resources()
        self.popup.destroy()
        self.control_panel.sensor_display_popup_button.config(state=tk.NORMAL)
        self.window_open = False

    def release_graph_resources(self):
        """Release resources used by graphs."""
        for key, graph in self.graphs.items():
            plt.close(graph['fig'])  # Close the Matplotlib figure
            canvas_widget = graph['canvas'].get_tk_widget()
            canvas_widget.destroy()  # Destroy the Tkinter canvas widget
        self.graphs.clear()

    def on_radio_button_change(self):
        """Handle changes in the radio button selection."""
        if self.graph_mode.get() == 1:
            self.change_display_settings(new_y_axis_resolution=self.slow_y_axis_resolution, new_refresh_rate=self.slow_refresh_rate_millis)
        elif self.graph_mode.get() == 2:
            self.change_display_settings(new_y_axis_resolution=self.fast_y_axis_resolution, new_refresh_rate=self.fast_refresh_rate_millis)

    def change_display_settings(self, new_y_axis_resolution, new_refresh_rate):
        """Change the display settings for graphs."""
        self.y_axis_resolution = new_y_axis_resolution
        for key in self.graphs:
            self.update_graph_limits(key, new_y_axis_resolution)
        self.refresh_rate_millis = new_refresh_rate
        self.restart_display_loop()

    def update_graph_limits(self, key, new_y_axis_resolution):
        """Update the limits and data points for a specific graph."""
        if key in self.graphs:
            graph = self.graphs[key]
            ax = graph['ax']
            ax.set_xlim(0, new_y_axis_resolution)
            self.data_points[key] = deque(maxlen=new_y_axis_resolution)  # Reset data points
            self.clear_graph_data(key)

    def restart_display_loop(self):
        """Restart the display loop after settings change."""
        self.stop_displaying()
        self.start_displaying()

    def stop_displaying(self):
        """Stop the data update loop."""
        if self.update_id is not None:
            self.root.after_cancel(self.update_id)
            print("Stopped loop")

    def clear_graph_data(self, key):
        """Clear the data from a specific graph."""
        if key in self.graphs:
            graph = self.graphs[key]
            line = graph['line']
            line.set_data([], [])
            graph['canvas'].draw()

    def update_data(self):
        """Update data for all sensors and graphs."""
        data = self.read_arduino()
        for key, value in data.items():
            if key in self.data_labels:
                self.data_labels[key].set(f"{key}: {value}")
            self.update_graph(key, value)
        self.update_id = self.root.after(self.refresh_rate_millis, self.update_data)

    def update_graph(self, key, value):
        """Update a specific graph with new data."""
        if key in self.graphs:
            self.data_points[key].append(value)
            graph = self.graphs[key]
            line = graph['line']
            line.set_data(range(len(self.data_points[key])), self.data_points[key])
            canvas = graph['canvas']
            canvas.restore_region(graph['bg'])
            graph['ax'].draw_artist(line)
            canvas.blit(graph['ax'].bbox)

    def read_arduino(self):
        """Read data from Arduino and format it."""
        if self.arduino.connection_ready:
            with self.arduino.lock:
                self.arduino_input_data = self.arduino.read_inputs()

        data = {}
        digital_input_counter = 30  # First digital input used is 30 on Arduino Mega
        analog_input_counter = 6   # First analog input used is A6 

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


class ButtonGrid:
    '''Button matrix displayed when Manual Control button is pressed'''
    def __init__(self, parent, pin_handler, arduino, control_panel):
        self.root = parent
        self.buttons = {}
        self.defaultbg = self.root.cget('bg')
        self.pin_handler = pin_handler
        self.arduino = arduino
        self.control_panel = control_panel

        self.control_panel.manual_control_popup_button.config(command=self.create_window)
        

    def create_window(self):
        self.popup = tk.Toplevel(self.root)

        self.control_panel.manual_control_popup_button.config(state=tk.DISABLED)
        self.popup.protocol("WM_DELETE_WINDOW", self.on_window_close)
        self.popup.title("Manual Control")
        self.populate_buttons()

    def populate_buttons(self):
        for i in range(1, 97):
            button = tk.Button(self.popup, text=str(i), command=lambda i=i: self.button_press(i), highlightbackground = self.defaultbg, highlightthickness = "2")
            button.grid(row=(i-1)//12, column=(i-1)%12, sticky="nsew")

            # Configure row and column weights so buttons expand
            self.popup.grid_rowconfigure((i-1)//12, weight=1)
            self.popup.grid_columnconfigure((i-1)%12, weight=1)
            self.buttons[i] = button

    def button_press(self, number):
        button = self.buttons[number]
        print(f"Button {number} pressed")

        # Toggle red outline
        if button.cget("highlightbackground") == self.defaultbg:
            button.config(highlightbackground="red")

            # --- Relay handling code
            with self.pin_handler.lock:

                self.pin_handler.setRelaysOn([number])

            with self.arduino.lock:

                print(self.arduino.serial_communicate(self.pin_handler.pin_array_string()))

            # --- End 

        else:
            button.config(highlightbackground=self.defaultbg)
            
            with self.pin_handler.lock:

                self.pin_handler.setRelaysOff([number])
            
            with self.arduino.lock:

                print(self.arduino.serial_communicate(self.pin_handler.pin_array_string()))

    def on_window_close(self):

        with self.pin_handler.lock:
            
            self.pin_handler.resetAll()

        with self.arduino.lock:

            print("Resetting all pins...", self.arduino.serial_communicate(self.pin_handler.pin_array_string()))


        self.control_panel.manual_control_popup_button.config(state=tk.NORMAL)

        self.popup.destroy()
