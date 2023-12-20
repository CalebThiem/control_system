# import time
import threading
# from arduino import Arduino
# from SPV_control import SpvControl
# from pin_handler import PinHandler
from gui import Gui

class Steps:

    def __init__(self, gui):
        '''
        self.pin_handler = pin_handler_instance

        self.arduino = arduino_instance

        self.spv_control = spv_control_instance
        '''
        self.gui = gui

        self.text_variable_strings = []

        for i in range(gui.number_of_labels):

            self.text_variable_strings.append('')
        
        self.queued_thread = None

        self.current_thread = self.dummy

    def dummy(self):

        print("dummy called")

    def load_step_1(self):

        print("load_step_1 called")

        self.current_thread = self.step_1

    def call_current_thread(self):

        self.current_thread()

        self.gui.update_gui(self.text_variable_strings)

    def start_queued_thread(self):

        self.queued_thread.start()

        self.gui.update_gui(self.text_variable_strings)

    def cancel(self):

        print("cancel called")

        if (self.queued_thread is not None):

            self.queued_thread.cancel()

    def step_1(self):

        print("Step 1 executed")    

        step_duration = 2

        for i in range(self.gui.number_of_labels):

            self.text_variable_strings[i] = "Step 1"

        next_step_option_1 = self.step_2

        self.current_thread = self.step_1

        self.queued_thread = threading.Timer(function=next_step_option_1, interval=step_duration)

        self.start_queued_thread()

    def step_2(self):

        print("Step 2 executed")

        step_duration = 2

        for i in range(self.gui.number_of_labels):

            self.text_variable_strings[i] = "Step 2"

        next_step_option_1 = self.step_1

        self.current_thread = self.step_2

        self.queued_thread = threading.Timer(function=next_step_option_1, interval=step_duration)

        self.start_queued_thread()
