import time
import threading
import itertools

'''
Basket control relay numbers and time parameters are defined here.

Modifies pin_handler relay state record and updates Arduino with that record
in order to contol the basket rotation and bladder inflation/deflation cycle.

Methods:

    start_rotation()

        Starts basket clockwise/anticlockwise rotation cycle

    stop_rotation()

        Continues basket rotation until an even number of clockwise/anticlockwise
        rotations is made, then stops rotation.

    rotate_clockwise()

        Rotates the basket clockwise

    rotate_anticlockwise()

        Rotates the basket anticlockwise

    start_inflation_cycle()

        Starts the inflation cylcle (defined in inflation_cycle())

    disable_inflation_cycle()

        Completes the current inflation run, then disables the cycle.

    start_evacuation_sequence()

        Incrementaly inflates bladder to max pressure, then vents and vacuums

    set_bladder_state(state_to_engage)

        Engages a bladder inflation/deflation state. Available states:

            high_pressure
            medium_pressure
            low_pressure
            vent
            vacuum_pump
            none

Variables:
        
        bool basket_assumed_in_rest_state
        bool bladder_assumed_in_rest_state
        bool inflation_cycle_running
        bool evacuation_sequence_running
'''


class SpvControl:

    def __init__(self, pin_handler_instance, arduino_instance):

        self.pin_handler = pin_handler_instance
        self.arduino = arduino_instance

        self.process_cancelled = False

        self.basket_assumed_in_rest_state = True
        self.bladder_assumed_in_rest_state = True

        # Rotation time in seconds

        self.rotation_time = 2
        self.pause_time = 1

        # Inflation times in seconds

        self.high_pressure_inflation = 2
        self.medium_pressure_inflation = 2
        self.low_pressure_inflation = 2
        self.venting_deflation = 2
        self.vacuum_deflation = 2

        # Set relay control system  numbers

        self.motor_clockwise = [18]
        self.motor_anticlockwise = [17, 18]

        self.high_pressure = [28]
        self.medium_pressure = [27]
        self.low_pressure = [25]
        self.vent = [26]
        self.vacuum_pump = [21, 22]
        self.none = None
        
        self.motor_relays = [

            self.motor_clockwise,
            self.motor_anticlockwise
            
            ]

        self.motor_relays = set(itertools.chain(*self.motor_relays))

        self.bladder_relays = [

            self.high_pressure,
            self.medium_pressure,
            self.low_pressure,
            self.vent,
            self.vacuum_pump
            
            ]

        self.bladder_relays = set(itertools.chain(*self.bladder_relays))

        # Tracking for number of rotations

        self.clockwise_rotations = 0
        self.anticlockwise_rotations = 0

        self.rotate_SPV = False

        self.inflation_cycle_running = False
        self.evacuation_sequence_running = False

    def rotate_clockwise(self):

        with self.pin_handler.lock:

            self.pin_handler.setRelaysOff(self.motor_anticlockwise)
            self.pin_handler.setRelaysOff(self.motor_clockwise)

        with self.arduino.lock:

            self.arduino.serial_communicate(self.pin_handler.pin_array_string())

        time.sleep(self.pause_time)

        with self.pin_handler.lock:

            self.pin_handler.setRelaysOn(self.motor_clockwise)

        with self.arduino.lock:

            self.arduino.serial_communicate(self.pin_handler.pin_array_string())

        self.clockwise_rotations += 1

    def rotate_anticlockwise(self):

        with self.pin_handler.lock:

            self.pin_handler.setRelaysOff(self.motor_anticlockwise)
            self.pin_handler.setRelaysOff(self.motor_clockwise)

        with self.arduino.lock:

            self.arduino.serial_communicate(self.pin_handler.pin_array_string())

        time.sleep(self.pause_time)

        with self.pin_handler.lock:

            self.pin_handler.setRelaysOn(self.motor_anticlockwise)

        with self.arduino.lock:

            self.arduino.serial_communicate(self.pin_handler.pin_array_string())

        self.anticlockwise_rotations += 1

    def rotation_manager(self):

        while (self.rotate_SPV or (self.clockwise_rotations != self.anticlockwise_rotations)):

            self.rotate_clockwise()

            time.sleep(self.rotation_time)

            self.rotate_anticlockwise()

            time.sleep(self.rotation_time)

        with self.pin_handler.lock:

            self.pin_handler.setRelaysOff(self.motor_anticlockwise)
            self.pin_handler.setRelaysOff(self.motor_clockwise)

        with self.arduino.lock:

            self.arduino.serial_communicate(self.pin_handler.pin_array_string())

        self.basket_assumed_in_rest_state = True

    def start_rotation(self):

        self.rotate_SPV = True

        self.basket_assumed_in_rest_state = False
        
        with self.pin_handler.lock:

            self.pin_handler.excludePins([17, 18])

        rotation = threading.Thread(target=self.rotation_manager)
        rotation.start()

    def stop_rotation(self):

        self.rotate_SPV = False
        
        with self.pin_handler.lock:

            self.pin_handler.undoExcludePins(self.motor_relays)

    def set_bladder_state(self, state_to_engage):

        with self.pin_handler.lock:

            self.pin_handler.setRelaysOff(self.high_pressure)
            self.pin_handler.setRelaysOff(self.medium_pressure)
            self.pin_handler.setRelaysOff(self.low_pressure)
            self.pin_handler.setRelaysOff(self.vent)
            self.pin_handler.setRelaysOff(self.vacuum_pump)

            if (state_to_engage is not None):

                self.pin_handler.setRelaysOn(state_to_engage)

        with self.arduino.lock:

            self.arduino.serial_communicate(self.pin_handler.pin_array_string())

    def inflation_cycle(self):

        while self.inflation_cycle_running is True:

            self.set_bladder_state(self.low_pressure)

            time.sleep(self.low_pressure_inflation)

            self.set_bladder_state(self.vent)

            time.sleep(self.venting_deflation)

            self.set_bladder_state(self.vacuum_pump)

            time.sleep(self.vacuum_deflation)

        self.set_bladder_state(None)

        self.bladder_assumed_in_rest_state = True

    def evacuation_sequence(self):

        self.set_bladder_state(self.low_pressure)

        time.sleep(self.low_pressure_inflation)

        self.set_bladder_state(self.medium_pressure)

        time.sleep(self.medium_pressure_inflation)

        self.set_bladder_state(self.high_pressure)

        time.sleep(self.high_pressure_inflation)

        self.set_bladder_state(self.vent)

        time.sleep(self.venting_deflation)

        self.set_bladder_state(self.vacuum_pump)

        time.sleep(self.vacuum_deflation)

        self.set_bladder_state(None)

        self.bladder_assumed_in_rest_state = True

        self.evacuation_cycle_running = False

        with self.pin_handler.lock:

            self.pin_handler.undoExcludePins(self.bladder_relays)

    def start_inflation_cycle(self):

        self.inflation_cycle_running = True

        self.bladder_assumed_in_rest_state = False

        with self.pin_handler.lock:

            self.pin_handler.excludePins(self.bladder_relays)

        inflation_cycle_thread = threading.Thread(target=self.inflation_cycle)
        inflation_cycle_thread.start()

    def disable_inflation_cycle(self):

        self.inflation_cycle_running = False

        with self.pin_handler.lock:

            self.pin_handler.undoExcludePins(self.bladder_relays)

    def start_evacuation_sequence(self):

        self.evacuation_sequence_running = True

        with self.pin_handler.lock:

            self.pin_handler.excludePins(self.bladder_relays)

        evacuation_sequence_thread = threading.Thread(target=self.evacuation_sequence)
        evacuation_sequence_thread.start()

    def wait_for_rest_state(self):

        while (True):
            
            if (self.basket_assumed_in_rest_state and self.bladder_assumed_in_rest_state):

                break

            else:

                time.sleep(1)
