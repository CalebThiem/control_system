from machine import Pin, Timer
from machine import PWM
import time

class AnalogWrite:

    def __init__(self):

        self.pwm_frequency = 10000

        # Low pass filer: 10k resistor, 100uF capacitor

    def assign_pin(self, pin):

        pwm_pin = PWM(pin)

        pwm_pin.freq(self.pwm_frequency)

        # Max 65535
        pwm_pin.duty_u16(0)

        return pwm_pin
    
    def inverse_function(self, number):

        # Function takes desired output level between 0 and 671 (the min and max
        # values observed when the PWM pin is connected to an Arduino analog input)
        # and returns the denominator for the duty cycle.

        result = (669.09 / (number + 6.46)) + 0.0124

        return result

    def calc_duty_cycle(self, number):

        result = 65535 / number

        return int(result)

    def analogWrite(self, pin, value):

        pin.duty_u16(self.calc_duty_cycle(self.inverse_function(value)))

class Test:

    def __init__(self):

        self.analog = AnalogWrite()

        self.pin = self.analog.assign_pin(Pin(22))

        self.value = 671

        self.direction = 0

        self.time = 5

        self.timer = Timer()


    def callback_function(self, timer):

        if self.direction == 0:

            if self.value == 1:

                self.direction = 1

            self.analog.analogWrite(self.pin, self.value)

            self.value -= 1
            
            return

        if self.direction == 1:

            if self.value == 670:

                self.direction = 0

            self.analog.analogWrite(self.pin, self.value)

            self.value += 1

            return
    

    def start(self):

        self.timer.init(period=self.time, callback=self.callback_function)

    def stop(self):

        self.timer.deinit()


