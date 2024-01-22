import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from matplotlib.figure import Figure # Old implementation
import time
import gc
from collections import deque
class SensorDisplay:

    def __init__(self, parent, arduino):
        self.root = parent
        self.arduino = arduino
        self.update_id = None
        self.data_labels = {}
        self.graphs = {}
        self.data_points = {}  # Store data points for each analog input
        print("With blit")

    def read_arduino(self):
        # Efficiently read data from Arduino
        # Placeholder for actual Arduino data reading logic
        return {'A0': 123, 'A1': 456, 'D0': '1', 'D1': '0'}  # Example data structure

    def show_popup(self):
        self.popup = tk.Toplevel(self.root)
        self.popup.title("Sensor Data Display")
        self.popup.geometry("800x500")

        # Create a Frame for scrolling capability
        self.canvas = tk.Canvas(self.popup)
        scrollbar = tk.Scrollbar(self.popup, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)

        # Configure the canvas for scrolling
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        # Pack the scrollbar and canvas into the popup window
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.popup.protocol("WM_DELETE_WINDOW", self.on_window_close)

        self.initialize_widgets()
        self.start_displaying()

    def initialize_widgets(self):
        data = self.read_arduino()
        for key, value in data.items():
            var = tk.StringVar(value=str(value))
            label = tk.Label(self.scrollable_frame, textvariable=var)
            label.pack(anchor='nw', pady=2, padx=5)
            self.data_labels[key] = var

            if key.startswith("A"):  # Analog inputs
                self.setup_graph(key)

    def setup_graph(self, key):
        self.data_points[key] = []  # Initialize data points list
        fig, ax = plt.subplots(figsize=(5, 2), dpi=100)
        line, = ax.plot([], [], 'r-')
        ax.set_xlim(0, 50)  # Adjust as needed
        ax.set_ylim(0, 1023)  # Adjust as needed

        canvas = FigureCanvasTkAgg(fig, master=self.scrollable_frame)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(anchor='nw', pady=2, padx=5)

        self.graphs[key] = {'fig': fig, 'ax': ax, 'line': line, 'canvas': canvas}

    def start_displaying(self):
        self.update_data()

    def update_data(self):
        data = self.read_arduino()
        for key, value in data.items():
            if key in self.data_labels:
                self.data_labels[key].set(f"{key}: {value}")
            if key in self.graphs:
                self.update_graph(key, value)

        self.update_id = self.root.after(1000, self.update_data)  # Adjust interval as needed

    def update_graph(self, key, value):
        if key in self.graphs:
            self.data_points[key].append(value)
            # Keep only the last 50 data points
            if len(self.data_points[key]) > 50:
                self.data_points[key] = self.data_points[key][-50:]

            graph = self.graphs[key]
            line = graph['line']
            line.set_data(range(len(self.data_points[key])), self.data_points[key])
            graph['canvas'].draw()

    def stop_displaying(self):
        if self.update_id is not None:
            self.root.after_cancel(self.update_id)

    def on_window_close(self):
        self.stop_displaying()
        for key, graph in self.graphs.items():
            canvas = graph['canvas']
            canvas.get_tk_widget().destroy()
        self.popup.destroy()

class SensorDisplayNoBlit:
    
    def __init__(self, parent, arduino):
        self.root = parent
        self.arduino = arduino
        self.update_id = None
        self.data_labels = {}
        self.graphs = {}
        self.data_points = {}  # Store data points for each analog input
        print("Without blit")
        self.update_id = None
    def read_arduino(self):
        # Efficiently read data from Arduino
        # Placeholder for actual Arduino data reading logic
        return {'A0': 123, 'A1': 456, 'D0': '1', 'D1': '0'}  # Example data structure

    def show_popup(self):
        self.popup = tk.Toplevel(self.root)
        self.popup.title("Sensor Data Display")
        self.popup.geometry("800x500")

        self.canvas = tk.Canvas(self.popup)
        scrollbar = tk.Scrollbar(self.popup, orient="vertical", command=self.canvas.yview)
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

        self.popup.protocol("WM_DELETE_WINDOW", self.on_window_close)
        
        self.initialize_widgets()
        '''
        self.start_displaying()
        ''' 
    def initialize_widgets(self):
        data = self.read_arduino()
        for key, value in data.items():
            var = tk.StringVar(value=str(value))
            label = tk.Label(self.scrollable_frame, textvariable=var)
            label.pack(anchor='nw', pady=2, padx=5)
            self.data_labels[key] = var
            
            if key.startswith("A"):  # Analog inputs
                self.setup_graph(key)
            
    def setup_graph(self, key):
        self.data_points[key] = []  # Initialize data points list
        
        fig, ax = plt.subplots(figsize=(5, 2), dpi=100) # This line seems to cause the closing problem
        '''        
        line, = ax.plot([], [], 'r-')
         
        ax.set_xlim(0, 50)  # Adjust as needed
        ax.set_ylim(0, 1023)  # Adjust as needed
        
        canvas = FigureCanvasTkAgg(fig, master=self.scrollable_frame)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(anchor='nw', pady=2, padx=5)
        
        self.graphs[key] = {'fig': fig, 'ax': ax, 'line': line, 'canvas': canvas}
        '''
    def start_displaying(self):
        self.update_data()

    def update_data(self):
        data = self.read_arduino()
        for key, value in data.items():
            if key in self.data_labels:
                self.data_labels[key].set(f"{key}: {value}")
            if key in self.graphs:
                self.update_graph(key, value)

        self.update_id = self.root.after(1000, self.update_data)  # Adjust interval as needed

    def update_graph(self, key, value):
        if key in self.graphs:
            self.data_points[key].append(value)
            # Keep only the last 50 data points
            if len(self.data_points[key]) > 50:
                self.data_points[key].pop(0)

            graph = self.graphs[key]
            line = graph['line']
            line.set_data(range(len(self.data_points[key])), self.data_points[key])
            graph['ax'].relim()
           # graph['ax'].autoscale_view()
            graph['canvas'].draw()

    def stop_displaying(self):
        if self.update_id is not None:
            self.root.after_cancel(self.update_id)

    def on_window_close(self):
        for key, graph in self.graphs.items():
            # Close the figure explicitly
            plt.close(graph['fig'])

        gc.collect()
        self.stop_displaying()
        self.popup.destroy()


class SensorDisplayOld:

    def __init__(self, parent, arduino):
        self.root = parent
        self.arduino = arduino
        self.update_id = None
        self.data_labels = {}
        self.graphs = {}
        self.data_points = {}  # Dynamically populated based on analog inputs

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

    def show_popup(self):
        self.popup = tk.Toplevel(self.root)
        self.popup.title("Raw Sensor Data")
        self.popup.geometry("800x500")

        self.canvas = tk.Canvas(self.popup)
        scrollbar = tk.Scrollbar(self.popup, orient="vertical", command=self.canvas.yview)
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

        self.popup.protocol("WM_DELETE_WINDOW", self.on_window_close)

        self.initialize_widgets()
        self.start_displaying()

    def initialize_widgets(self):
        data = self.read_arduino()
        for key in data.keys():
            var = tk.StringVar()
            label = tk.Label(self.scrollable_frame, textvariable=var)
            label.pack(anchor='nw', pady=2, padx=5)
            self.data_labels[key] = var

            if key.startswith("A"):  # For analog inputs, create graphs
                self.data_points[key] = []  # Initialize data points list
                fig = Figure(figsize=(5, 2), dpi=100)
                fig.add_subplot(111).plot([], [])
                canvas = FigureCanvasTkAgg(fig, master=self.scrollable_frame)
                canvas_widget = canvas.get_tk_widget()
                canvas_widget.pack(anchor='nw', pady=2, padx=5)
                self.graphs[key] = (fig, canvas)

    def update_graph(self, key, value):
        if key in self.graphs:
            fig, canvas = self.graphs[key]
            ax = fig.get_axes()[0]
            ax.clear()
            self.data_points[key].append(value)
            ax.plot(self.data_points[key], 'r-')
            ax.set_title(f"Graph for {key}")
            canvas.draw()

    def start_displaying(self):
        self.update_data()

    def update_data(self):
        data = self.read_arduino()
        for key, value in data.items():
            if key in self.data_labels:
                self.data_labels[key].set(f"{key}: {value}")
            self.update_graph(key, value)

        self.update_id = self.root.after(1000, self.update_data)

    def stop_displaying(self):
        if self.update_id is not None:
            self.root.after_cancel(self.update_id)

    def on_window_close(self):
        self.stop_displaying()
        self.popup.destroy()


class SensorDisplayNew:

    def __init__(self, parent, arduino):
        self.root = parent
        self.arduino = arduino
        self.update_id = None
        self.data_labels = {}
        self.graphs = {}
        self.data_points = {}  # Store data points for each analog input
    '''
    def read_arduino(self):
        # Efficiently read data from Arduino
        # Placeholder for actual Arduino data reading logic
        return {'A0': 123, 'A1': 456, 'D0': '1', 'D1': '0'}  # Example data structure
    '''

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
    
    def show_popup(self):
        self.popup = tk.Toplevel(self.root)
        self.popup.title("Sensor Data Display")
        self.popup.geometry("800x500")

        self.canvas = tk.Canvas(self.popup)
        scrollbar = tk.Scrollbar(self.popup, orient="vertical", command=self.canvas.yview)
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

        self.popup.protocol("WM_DELETE_WINDOW", self.on_window_close)

        self.initialize_widgets()
        self.start_displaying()

    def initialize_widgets(self):
        data = self.read_arduino()
        for key, value in data.items():
            var = tk.StringVar(value=str(value))
            label = tk.Label(self.scrollable_frame, textvariable=var)
            label.pack(anchor='nw', pady=2, padx=5)
            self.data_labels[key] = var

            if key.startswith("A"):  # Analog inputs
                self.setup_graph(key)

    def setup_graph(self, key):
        self.data_points[key] = []  # Initialize data points list
        fig = Figure(figsize=(10, 4), dpi=100)
        ax = fig.add_subplot(111)

        canvas = FigureCanvasTkAgg(fig, master=self.scrollable_frame)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(anchor='nw', pady=2, padx=5)

        # Initial draw to create the background
        canvas.draw()
        bg = canvas.copy_from_bbox(ax.bbox)

        self.graphs[key] = {'fig': fig, 'ax': ax, 'line': None, 'canvas': canvas, 'bg': bg}

    def start_displaying(self):
        self.update_data()

    def update_data(self):
        data = self.read_arduino()
        for key, value in data.items():
            if key in self.data_labels:
                self.data_labels[key].set(f"{key}: {value}")
            if key in self.graphs:
                self.update_graph(key, value)

        self.update_id = self.root.after(100, self.update_data)  # Adjust interval as needed

    def update_graph(self, key, value):
        graph = self.graphs[key]
        self.data_points[key].append(value)

        # Keep only the last 50 data points
        if len(self.data_points[key]) > 50:
            # self.data_points[key] = self.data_points[key][-50:]
            self.data_points[key].pop(0)

        x_data = range(len(self.data_points[key]))
        y_data = self.data_points[key]

        # Update or create the line
        if graph['line'] is None:
            graph['line'], = graph['ax'].plot(x_data, y_data, 'r-')
        else:
            graph['line'].set_data(x_data, y_data)

        # Adjust the limits and redraw the background if needed
        graph['ax'].relim()
        graph['ax'].autoscale_view()
        graph['canvas'].draw()
        graph['bg'] = graph['canvas'].copy_from_bbox(graph['ax'].bbox)

        # Blit technique
        canvas = graph['canvas']
        ax = graph['ax']
        bg = graph['bg']

        canvas.restore_region(bg)
        ax.draw_artist(graph['line'])
        canvas.blit(ax.bbox)
    def stop_displaying(self):
        if self.update_id is not None:
            self.root.after_cancel(self.update_id)

    def on_window_close(self):
        self.stop_displaying()
        for key, graph in self.graphs.items():
            canvas = graph['canvas']
            canvas.get_tk_widget().destroy()
        self.popup.destroy()


class SensorDisplayFast:

    def __init__(self, parent, arduino):
        
        self.refresh_rate = 100
        self.y_axis_length = 100

        self.root = parent
        self.arduino = arduino
        self.update_id = None
        self.data_labels = {}
        self.graphs = {}
        self.data_points = {}  # Dynamically populated based on analog inputs
        

    def read_arduino(self):
        if self.arduino.connection_ready:
            with self.arduino.lock:
                self.arduino_input_data = self.arduino.read_inputs()

        data = dict()
        digital_input_counter = 30
        analog_input_counter = 6

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

    def show_popup(self):
        self.popup = tk.Toplevel(self.root)
        self.popup.title("Raw Sensor Data")
        self.popup.geometry("800x500")

        self.canvas = tk.Canvas(self.popup)
        scrollbar = tk.Scrollbar(self.popup, orient="vertical", command=self.canvas.yview)
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

        self.popup.protocol("WM_DELETE_WINDOW", self.on_window_close)

        self.initialize_widgets()
        self.start_displaying()

    def initialize_widgets(self):
        data = self.read_arduino()
        for key in data.keys():
            var = tk.StringVar()
            label = tk.Label(self.scrollable_frame, textvariable=var)
            label.pack(anchor='nw', pady=2, padx=5)
            self.data_labels[key] = var

            if key.startswith("A"):  # For analog inputs, create graphs
                self.setup_graph(key)

    def setup_graph(self, key):
        self.data_points[key] = deque(maxlen=self.y_axis_length)  # Initialize data points list
        fig = Figure(figsize=(10, 5), dpi=100)
        ax = fig.add_subplot(111)

        ax.set_xlabel(f"Data Points (approx. {self.refresh_rate} per second)")
        ax.set_ylabel("ADC Reading (0=0V, 1023=5V)")

        canvas = FigureCanvasTkAgg(fig, master=self.scrollable_frame)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(anchor='nw', pady=2, padx=5)

        # Initial draw to create the background
        canvas.draw()
        bg = canvas.copy_from_bbox(ax.bbox)

        self.graphs[key] = {'fig': fig, 'ax': ax, 'line': None, 'canvas': canvas, 'bg': bg}

    def update_graph(self, key, value):
        graph = self.graphs[key]
        self.data_points[key].append(value)

        x_data = range(len(self.data_points[key]))
        y_data = self.data_points[key]

        if graph['line'] is None:
            graph['line'], = graph['ax'].plot(x_data, y_data, 'r-')
            graph['ax'].set_xlim(0, self.y_axis_length)
            graph['ax'].set_ylim(min(y_data), 1023)
        else:
            graph['line'].set_data(x_data, y_data)

        # Update limits and background only if necessary
        if self.needs_rescale(graph['ax'], y_data):
            graph['ax'].relim()
            graph['ax'].autoscale_view()
            graph['canvas'].draw()
            graph['bg'] = graph['canvas'].copy_from_bbox(graph['ax'].bbox)

        canvas = graph['canvas']
        bg = graph['bg']

        canvas.restore_region(bg)
        graph['ax'].draw_artist(graph['line'])
        canvas.blit(graph['ax'].bbox)

    def needs_rescale(self, ax, y_data):
        ymin, ymax = ax.get_ylim()
        return min(y_data) < ymin or max(y_data) > ymax

    def start_displaying(self):
        self.update_data()

    def update_data(self):
        data = self.read_arduino()
        for key, value in data.items():
            if key in self.data_labels:
                self.data_labels[key].set(f"{key}: {value}")
            if key in self.graphs:
                self.update_graph(key, value)

        self.update_id = self.root.after(self.refresh_rate, self.update_data)

    def stop_displaying(self):
        if self.update_id is not None:
            self.root.after_cancel(self.update_id)

    def on_window_close(self):
        self.stop_displaying()
        for key, graph in self.graphs.items():
            canvas = graph['canvas']
            canvas.get_tk_widget().destroy()
        self.popup.destroy()

