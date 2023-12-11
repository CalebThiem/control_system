import time
import threading


class SPV_control:

    def __init__(self, pin_handler_instance, arduino_instance):

        self.pin_handler = pin_handler_instance
        self.arduino = arduino_instance

        # Rotation time in seconds

        self.rotation_time = 120
        self.pause_time = 2

        # Inflation times in seconds

        self.high_pressure_inflation = 10
        self.medium_pressure_inflation = 10
        self.low_pressure_inflation = 10
        self.venting_deflation = 60
        self.vacuum_deflation = 60

        # Set relay control system  numbers

        self.motor_clockwise = 1
        self.motor_anticlockwise = 2

        self.high_pressure = 3
        self.medium_pressure = 4
        self.low_pressure = 5

        self.vent = 6

        self.vacuum_pump = 7

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

            self.arduino.serial_communicate(self.pin_handler.pin_array)

        self.clockwise_rotations += 1

    def rotate_anticlockwise(self):

        time.sleep(self.pause_time)

        with self.pin_handler.lock:

            self.pin_handler.setRelaysOff(self.motor_clockwise)

            self.pin_handler.setRelaysOn(self.motor_anticlockwise)

        with self.arduino.lock:

            self.arduino.serial_communicate(self.pin_handler.pin_array)

        self.anticlockwise_rotations += 1

    def rotation_manager(self):

        while (self.rotate_SPV or (self.clockwise_rotations != self.anticlockwise_rotations)):

            self.rotate_clockwise()

            time.sleep(self.rotation_time)

            self.rotate_anticlockwise()

            time.sleep(self.rotation_time)

    def start_rotation(self):

        self.rotate_SPV = True

        rotation = threading.Thread(target=self.rotation_manager)
        rotation.start()

    def stop_rotation(self):

        self.rotate_SPV = False

    def set_bladder_state(self, state_to_engage):

        with self.pin_handler.lock:

            self.pin_handler.setRelaysOff(self.high_pressure)
            self.pin_handler.setRelaysOff(self.medium_pressure)
            self.pin_handler.setRelaysOff(self.low_pressure)
            self.pin_handler.setRelaysOff(self.vent)
            self.pin_handler.setRelaysOff(self.vacuum_pump)

            self.pin_handler.setRelaysOn(state_to_engage)

        with self.arduino.lock:

            self.arduino.serial_communicate(self.pin_handler.pin_array)

    def inflation_cycle(self):

        if self.inflation_cycle is True:

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

    def enable_inflation_cycle(self):

        self.inflation_cycle_running = True

    def disable_inflation_cycle(self):

        self.inflation_cycle_running = False
