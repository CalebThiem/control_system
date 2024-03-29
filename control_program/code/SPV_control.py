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

    set_bladder_state(state_to_engage)

        Engages a bladder inflation/deflation state. Available states:

            high_pressure
            medium_pressure
            low_pressure
            vent
            vacuum_pump
            none
'''


class SpvControl:

    def __init__(self, pin_handler_instance, arduino_instance):

        self.pin_handler = pin_handler_instance
        self.arduino = arduino_instance

        # Rotation time in seconds

        self.rotation_time = 5
        self.pause_time = 2

        # Inflation times in seconds

        self.high_pressure_inflation = 10
        self.medium_pressure_inflation = 10
        self.low_pressure_inflation = 10
        self.venting_deflation = 10
        self.vacuum_deflation = 10

        # Set relay control system  numbers

        self.motor_clockwise = [1]
        self.motor_anticlockwise = [2]

        self.high_pressure = [3]
        self.medium_pressure = [4]
        self.low_pressure = [5]
        self.vent = [6]
        self.vacuum_pump = [7]
        self.none = None
        
        self.motor_relays = [

            self.motor_clockwise,
            self.motor_anticlockwise
            
            ]

        self.motor_relays = list(itertools.chain(*self.motor_relays))

        self.bladder_relays = [

            self.high_pressure,
            self.medium_pressure,
            self.low_pressure,
            self.vent,
            self.vacuum_pump
            
            ]

        self.bladder_relays = list(itertools.chain(*self.bladder_relays))

        # Tracking for number of rotations

        self.clockwise_rotations = 0
        self.anticlockwise_rotations = 0

        self.rotate_SPV = False

        self.inflation_cycle_running = False

    def rotate_clockwise(self):

        time.sleep(self.pause_time)

        with self.pin_handler.lock:

            self.pin_handler.setRelaysOff(self.motor_anticlockwise)

            self.pin_handler.setRelaysOn(self.motor_clockwise)

        with self.arduino.lock:

            self.arduino.serial_communicate(self.pin_handler.pin_array_string())

        self.clockwise_rotations += 1

    def rotate_anticlockwise(self):

        time.sleep(self.pause_time)

        with self.pin_handler.lock:

            self.pin_handler.setRelaysOff(self.motor_clockwise)

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

            self.pin_handler.setRelaysOff(self.motor_clockwise)

            self.pin_handler.setRelaysOff(self.motor_anticlockwise)

        with self.arduino.lock:

            self.arduino.serial_communicate(self.pin_handler.pin_array_string())

    def start_rotation(self):

        self.rotate_SPV = True
        
        with self.pin_handler.lock:

            self.pin_handler.excludePins(self.motor_relays)

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

            self.set_bladder_state(self.high_pressure)

            time.sleep(self.high_pressure_inflation)

            self.set_bladder_state(self.medium_pressure)

            time.sleep(self.medium_pressure_inflation)

            self.set_bladder_state(self.low_pressure)

            time.sleep(self.low_pressure_inflation)

            self.set_bladder_state(self.vent)

            time.sleep(self.venting_deflation)

            self.set_bladder_state(self.vacuum_pump)

            time.sleep(self.vacuum_deflation)

        self.set_bladder_state(None)

    def start_inflation_cycle(self):

        self.inflation_cycle_running = True

        with self.pin_handler.lock:

            self.pin_handler.excludePins(self.bladder_relays)

        inflation_cycle_thread = threading.Thread(target=self.inflation_cycle)
        inflation_cycle_thread.start()

    def disable_inflation_cycle(self):

        self.inflation_cycle_running = False

        with self.pin_handler.lock:

            self.pin_handler.undoExcludePins(self.bladder_relays)

    
