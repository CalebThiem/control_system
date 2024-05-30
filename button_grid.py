import tkinter as tk
from arduino import Arduino
from pin_handler import PinHandler

pin_handler = PinHandler()

arduino = Arduino()

arduino.connect('/dev/ttyACM1', 480600)


class ButtonGrid:
    def __init__(self, pin_handler, arduino):
        self.root = tk.Tk()
        self.buttons = {}
        self.defaultbg = self.root.cget('bg')
        self.pin_handler = pin_handler
        self.arduino = arduino
        

    def create_window(self):
        self.root.title("Button Grid")
        self.populate_buttons()
        self.root.mainloop()

    def populate_buttons(self):
        for i in range(1, 97):
            button = tk.Button(self.root, text=str(i), command=lambda i=i: self.button_press(i), highlightbackground = self.defaultbg, highlightthickness = "2")
            button.grid(row=(i-1)//12, column=(i-1)%12, sticky="nsew")

            # Configure row and column weights so buttons expand
            self.root.grid_rowconfigure((i-1)//12, weight=1)
            self.root.grid_columnconfigure((i-1)%12, weight=1)
            self.buttons[i] = button

    def button_press(self, number):
        button = self.buttons[number]
        print(f"Button {number} pressed")

        # Toggle red outline
        if button.cget("highlightbackground") == self.defaultbg:
            button.config(highlightbackground="red")

            # --- Relay handling code

            pin_handler.setRelaysOn([number])

            with arduino.lock:

                print(arduino.serial_communicate(pin_handler.pin_array_string()))

            # --- End 

        else:
            button.config(highlightbackground=self.defaultbg)

            pin_handler.setRelaysOff([number])
            
            with arduino.lock:

                print(arduino.serial_communicate(pin_handler.pin_array_string()))


# Usage
app = ButtonGrid(pin_handler, arduino)
app.create_window()
