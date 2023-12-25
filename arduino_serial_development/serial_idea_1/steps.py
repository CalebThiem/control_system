# import time
import threading
# from arduino import Arduino
# from SPV_control import SpvControl
# from pin_handler import PinHandler
# from gui import Gui

class Steps:

    def __init__(self, gui):
        
        # self.pin_handler = pin_handler_instance

        # self.arduino = arduino_instance

        # self.spv_control = spv_control_instance
        
        self.gui = gui

        self.text_variable_strings = []

        for i in range(gui.number_of_labels):

            self.text_variable_strings.append('')
        
        self.queued_thread = None

        self.current_thread = self.dummy

        self.current_step_number = -1

        self.step_running = False

        self.number_of_steps = 2

        self.load_next_step()

        self.start_button_pressed = False

        self.stop_button_pressed = False

    def write_gui_text(self, text_as_list):

        provided_text_elements = len(text_as_list)

        for i in range(provided_text_elements):

            self.text_variable_strings[i] = text_as_list[i]

        for i in range(provided_text_elements, len(self.text_variable_strings)):

            self.text_variable_strings[i] = ''
        
        self.gui.update_gui(self.text_variable_strings)
        
    def step_0(self, mode):

        text_as_list = [
            "Initial Actions",
            "1. Check that LT1L3=1, LT2L3=1, Temp control active",
            "2. Take filter basket loaded with 10kg EFD in horizontal position and using lift place over PV",
            "3. Connect bladder air line",
            "4. Check that basket is oriented so magnet will lock",
            "5. Lower basket into PV until seated and magnet halves lock",
            "When done, click Next."
        ]
 
        self.write_gui_text(text_as_list)

        self.current_thread = self.step_0

    def step_1(self, mode):

        print("Step 1 executed")    

        step_duration = 2

        text_as_list = [
            "Step 1",
            "Prog No. 1",
            "Name: Fill PV with Used Water",
            "Action: Fill PV to Level 2 with used water. Start FB rotation and BB.",
            "Outputs: 6, 11, 16, BB, BO",
            "Inputs: PVL2",
            "Step End: PVL2=1"

        ]

        self.write_gui_text(text_as_list)

        next_step_option_1 = self.step_2

        self.current_thread = self.step_1

        if (mode == "run_logic"):

            self.step_running = True

            self.queued_thread = threading.Timer(interval=step_duration, function=next_step_option_1, args=("run_logic",))

            self.start_queued_thread()

    def step_2(self, mode):

        print("Step 2 executed")

        step_duration = 2

        for i in range(self.gui.number_of_labels):

            self.text_variable_strings[i] = "Step 2"

        next_step_option_1 = self.step_1

        self.current_thread = self.step_2

        if (mode == "run_logic"):

            self.step_running = True

            self.queued_thread = threading.Timer(interval=step_duration, function=next_step_option_1, args=("run_logic",))

            self.start_queued_thread()

    def dummy(self):

        print("dummy called")

    def load_next_step(self):

        if (self.step_running):

            return

        print("load_next_step called")

        if (self.current_step_number < self.number_of_steps):
    
            self.current_step_number += 1

        method_to_call = f"step_{self.current_step_number}"

        self.current_thread = getattr(self, method_to_call)

        self.current_thread(mode="display_only")

        self.gui.update_gui(self.text_variable_strings)

    def load_previous_step(self):

        if (self.step_running):

            return

        print("load_next_step called")

        if (self.current_step_number > 0):
    
            self.current_step_number -= 1

        method_to_call = f"step_{self.current_step_number}"

        self.current_thread = getattr(self, method_to_call)

        self.current_thread(mode="display_only")

        self.gui.update_gui(self.text_variable_strings)

    def call_current_thread(self):

        self.current_thread(mode="run_logic")

        self.gui.update_gui(self.text_variable_strings)

    def start_queued_thread(self):

        self.queued_thread.start()

        self.gui.update_gui(self.text_variable_strings)

    def cancel(self):

        print("cancel called")

        self.step_running = False

        if (self.queued_thread is not None):

            self.queued_thread.cancel()
