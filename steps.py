import threading
import time
from arduino import Arduino
from SPV_control import SpvControl
from pin_handler import PinHandler
import tkinter as tk
from sensor_input import SensorInput

class Steps:

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
 
        self.write_steps_display_text(text_as_list)

        self.current_thread = self.step_0

    def step_1(self, mode):

        print("Step 1 executed")    

        self.current_thread = self.step_1

        self.current_step_number = 1

        text_as_list = [
            "Step 1",
            "Name: Fill PV with Used Water",
            "Action: Fill PV to Level 2 with used water. Start FB rotation and BB.",
            "Outputs: 6, 11, 16, BB, BO",
            "Inputs: PVL2, timer",
            "Alarm Condition: t=7 min & PVL2=0",
            "Alarm Action: Stop step and find problem",
            "Step End: PVL2=1",
            "Action: Advance to next step"
        ]

        self.write_steps_display_text(text_as_list)


        if (mode == "run_logic"):

            self.step_running = True

            start_time = time.time()

            self.setLeachRelays([6, 11, 16, 40, 41])

            while self.step_running:

                # Check alarm conditions

                if (time.time() - start_time >= 5) and (self.check_sensor('PVL2') == 0):

                    self.cancel() # Cancel sheduled step progression
                    
                    self.raise_alarm()

                    print(time.time() - start_time)

                    break

                # Check step progression conditions

                if self.check_sensor('PVL2') == 1 and time.time() - start_time >=5:
                    
                    self.step_running = False

                    self.load_next_step()

                    self.call_current_thread()

                    break

                time.sleep(0.2)
    
    def step_2(self, mode):
        
        print("step 2 executed")

        self.current_thread = self.step_2

        self.current_step_number = 2

        text_as_list = [
                "Step 2",
                "Name: Circulate and Neutralize PV Water",
                "Action: PV water circulation and H2SO4 slowly added. pH monitored.",
                "Outputs: 3, 9, 11, 14, 16, 19, BB, BO",
                "Inputs: timer",
                "Alarm condition: PVFM = 0",
                "Alarm action: stop step, find problem",
                "Step end: t=5min",
                "Step end action: advance to next step"
                ]

        self.write_steps_display_text(text_as_list)

        if (mode == "run_logic"):
            
            self.step_running = True

            start_time = time.time()

            self.setLeachRelays([3, 9, 11, 14, 19, 16, 44, 45])

            self.spv_control.start_rotation()

            self.spv_control.start_inflation_cycle()

            while self.step_running:

                # Check alarm conditions

                if self.check_sensor('PVFM') == 0:
                    
                    self.cancel()

                    self.raise_alarm()
                    
                    break

                # Check advancement conditions

                if time.time() - start_time >= 5:

                    self.cancel()

                    self.spv_control.wait_for_rest_state()

                    self.load_step('step_1', 'run_logic')

                    self.call_current_thread()

                    break

                time.sleep(0.2)

    def __init__(self, steps_display, timer_display, arduino, pin_handler):
        
        self.arduino = arduino

        self.sensor_input = SensorInput(arduino)

        self.pin_handler = pin_handler

        self.spv_control = SpvControl(self.pin_handler, self.arduino)
        
        self.steps_display = steps_display

        self.timer_display = timer_display  

        self.text_variable_strings = []

        for i in range(steps_display.number_of_labels):

            self.text_variable_strings.append('')
        
        self.queued_thread = None

        self.current_thread = self.dummy

        self.current_step_number = -1

        self.step_running = False

        self.number_of_steps = 2

        self.load_next_step()

        self.start_button_pressed = False

        self.stop_button_pressed = False

        self.alarm_on = tk.BooleanVar()
 
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

        self.timer_display.reset_step_timer()

        self.steps_display.update_steps_display(self.text_variable_strings)

    def load_previous_step(self):

        if (self.step_running):

            return

        print("load_next_step called")

        if (self.current_step_number > 0):
    
            self.current_step_number -= 1

        method_to_call = f"step_{self.current_step_number}"

        self.current_thread = getattr(self, method_to_call)

        self.current_thread(mode="display_only")

        self.timer_display.reset_step_timer()

        self.steps_display.update_steps_display(self.text_variable_strings)

    def call_current_thread(self):

        mode = "run_logic"

        threading.Thread(target=self.current_thread, args=(mode,)).start()

        self.steps_display.update_steps_display(self.text_variable_strings)

    def load_step(self, step, mode):

        self.timer_display.reset_step_timer()

        self.current_thread = getattr(self, step)

    def start_queued_thread(self):

        self.queued_thread.start()

        self.steps_display.update_steps_display(self.text_variable_strings)

    def cancel(self):

        print("cancel called")

        self.step_running = False
        
        with self.pin_handler.lock:

            self.pin_handler.resetAll()

        with self.arduino.lock:

            self.arduino.serial_communicate(self.pin_handler.pin_array_string())

        if self.spv_control.rotate_SPV:

            self.spv_control.rotate_SPV = False

        if self.spv_control.inflation_cycle_running:

            self.spv_control.inflation_cycle_running = False

        if self.spv_control.evacuation_sequence_running:

            self.spv_control.evacuation_sequence_running = False

        if (type(self.queued_thread) == threading.Timer):

            self.queued_thread.cancel()

    def raise_alarm(self):

        print("alarm raised")

        self.alarm_on.set(True)

    def check_sensor(self, sensor_name):

        return self.sensor_input.get_sensor_value(sensor_name)
        #return self.dummy_sensor_input.get_dummy_state(sensor_name)

    def write_steps_display_text(self, text_as_list):

        provided_text_elements = len(text_as_list)

        for i in range(provided_text_elements):

            self.text_variable_strings[i] = text_as_list[i]

        for i in range(provided_text_elements, len(self.text_variable_strings)):

            self.text_variable_strings[i] = ''
        
        self.steps_display.update_steps_display(self.text_variable_strings)
        

    def setLeachRelays(self, relay_numbers_list):

        if (type(relay_numbers_list) is not list):

            raise Exception("relay_numbers_list passed as argument is not a list")

        if (max(relay_numbers_list) > 48):

            raise Exception("Relay number greater than 48 passed to setLeachRelays. Leach relays are 1 through 48.")

        # --- Relay handling code
        with self.pin_handler.lock:

            self.pin_handler.setLeachRelays(relay_numbers_list)

        with self.arduino.lock:

            print(self.arduino.serial_communicate(self.pin_handler.pin_array_string()))

        # --- End 

