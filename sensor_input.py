
class SensorInput:

    '''

    Takes arduino object as argument (Arduino class in arduino.py)

    Attributes:

        sensors : dict

            Defines each sensor name as an Arduino pin. As per the protocol defined in arduino.ino,
            digital input pins are 30 through 53, and analog input pins are A6 through A15. 

    Methods:

        get_sensor_value('sensor_name')

            Returns the value of the Arduino pin correstonding to sensor_name. Correspondance is 
            defined in the sensors dictionary. The value is returned as an int, and reflects the 
            voltage on the Arduino pin an a number between 0 and 1023.
    '''

    def __init__(self, arduino):

        self.arduino = arduino

        self.sensors = dict()

        # Dictonary key is name for sensor used in steps, value is Arduino pin
        # First Arduino pin is 30, and arduino.read_inputs returns a list with [0] being the first value

        self.sensors['PVL2'] = 30
        self.sensors['PVFM'] = 31
        self.sensors['3'] = 32
        self.sensors['4'] = 33
        self.sensors['5'] = 34
        self.sensors['6'] = 35
        self.sensors['7'] = 36
        self.sensors['8'] = 37
        self.sensors['9'] = 38
        self.sensors['10'] = 39
        self.sensors['11'] = 40
        self.sensors['12'] = 41
        self.sensors['13'] = 42
        self.sensors['14'] = 43
        self.sensors['15'] = 44
        self.sensors['16'] = 45
        self.sensors['17'] = 46
        self.sensors['18'] = 47
        self.sensors['19'] = 48
        self.sensors['20'] = 49
        self.sensors['21'] = 50
        self.sensors['22'] = 51
        self.sensors['23'] = 52
        self.sensors['24'] = 53
        self.sensors['25'] = 'A6'
        self.sensors['26'] = 'A7'
        self.sensors['27'] = 'A8'
        self.sensors['28'] = 'A9'
        self.sensors['29'] = 'A10'
        self.sensors['30'] = 'A11'
        self.sensors['31'] = 'A12'
        self.sensors['32'] = 'A13'
        self.sensors['33'] = 'A14'
        self.sensors['34'] = 'A15'

    def get_sensor_value(self, sensor_name):

        if sensor_name in self.sensors:

            arduino_pin = self.sensors[sensor_name]
            
            # Check if the sensor is a digital input, which have numbers as pin names
            if type(arduino_pin) == int:

                return self.get_digital_pin_value(arduino_pin)

            else:

                return getattr(self, f"get_analog_pin_value_{arduino_pin}")()

        else:

            raise ValueError("Sensor name not in SensorInput.py sensors dictionary")


    def get_digital_pin_value(self, arduino_pin):

        with self.arduino.lock:

            return int(self.arduino.read_inputs()[arduino_pin -30])

    def get_analog_pin_value_A6(self):

        with self.arduino.lock:
            sensor_value = self.arduino.read_inputs()[18 + 6]
        sensor_value = int(sensor_value)
        return sensor_value


    def get_analog_pin_value_A7(self):

        with self.arduino.lock:
            sensor_value = self.arduino.read_inputs()[18 + 7]
        sensor_value = int(sensor_value)
        return sensor_value


    def get_analog_pin_value_A8(self):

        with self.arduino.lock:
            sensor_value = self.arduino.read_inputs()[18 + 8]
        sensor_value = int(sensor_value)
        return sensor_value


    def get_analog_pin_value_A9(self):

        with self.arduino.lock:
            sensor_value = self.arduino.read_inputs()[18 + 9]
        sensor_value = int(sensor_value)
        return sensor_value


    def get_analog_pin_value_A10(self):

        with self.arduino.lock:
            sensor_value = self.arduino.read_inputs()[18 + 10]
        sensor_value = int(sensor_value)
        return sensor_value


    def get_analog_pin_value_A11(self):

        with self.arduino.lock:
            sensor_value = self.arduino.read_inputs()[18 + 11]
        sensor_value = int(sensor_value)
        return sensor_value


    def get_analog_pin_value_A12(self):

        with self.arduino.lock:
            sensor_value = self.arduino.read_inputs()[18 + 12]
        sensor_value = int(sensor_value)
        return sensor_value


    def get_analog_pin_value_A13(self):

        with self.arduino.lock:
            sensor_value = self.arduino.read_inputs()[18 + 13]
        sensor_value = int(sensor_value)
        return sensor_value


    def get_analog_pin_value_A14(self):

        with self.arduino.lock:
            sensor_value = self.arduino.read_inputs()[18 + 14]
        sensor_value = int(sensor_value)
        return sensor_value


    def get_analog_pin_value_A15(self):

        with self.arduino.lock:
            sensor_value = self.arduino.read_inputs()[18 + 15]
        sensor_value = int(sensor_value)
        return sensor_value
