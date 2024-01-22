import tkinter as tk
from testClass import SensorDisplay  # Assuming your class is in sensor_display.py
from testClass import SensorDisplayNoBlit
from testClass import SensorDisplayOld
from testClass import SensorDisplayNew
import threading

class SensorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sensor Display Application")

        # Mock Arduino object (replace this with your actual Arduino interface)
        self.arduino = MockArduino()

        # Create a button to open the sensor display
        self.open_button = tk.Button(self.root, text="Open Sensor Display", command=self.open_sensor_display)
        self.open_button.pack(pady=20)

    def open_sensor_display(self):
        # Create an instance of SensorDisplay
        self.sensor_display = SensorDisplayNew(self.root, self.arduino)

        # Open the sensor display popup
        self.sensor_display.show_popup()


class MockArduino:
    # Mock Arduino class for testing
    # Replace this with your actual Arduino interfacing code
    def __init__(self):
        self.connection_ready = True
        self.lock = threading.Lock()  # Replace with an appropriate lock if needed

    def read_inputs(self):
        # Mock input data, replace with actual data reading logic
        return ['1', '1', '0143', '0061', '0000', '0000']


if __name__ == "__main__":
    root = tk.Tk()
    app = SensorApp(root)
    root.mainloop()

