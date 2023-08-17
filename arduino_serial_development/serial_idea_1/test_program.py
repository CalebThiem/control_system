

import serial
import time
import random
import binascii
from timeit import default_timer

from arduino_control import add_checksum, validate_checksum, serial_communicate, test

ser = serial.Serial('/dev/ttyACM0', 460800)  # replace '/dev/ttyACM0' with your serial port

time.sleep(2)

'''

message = []

for i in range(292):
    message.append('0')

for i in range(48):

    message[i] = '0'

pins = []

for i in pins:
    message[i -1 ] = '0'

transmit = ''.join(message)

print(transmit)

for i in range(10):

    serial_communicate(ser, add_checksum(transmit))

    time.sleep(1)

'''

test(ser, 100, 292, 0)

ser.close()