import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

class SensorDisplay:

    def __init__(self, parent, arduino):
        self.root = parent
        self.arduino = arduino
        self.update_id = None
        self.data_labels = {}
        self.graphs = {}
        self.data_points = {}  # Store data points for each analog input

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
            graph['ax'].relim()
            graph['ax'].autoscale_view()
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
