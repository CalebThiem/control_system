"""

Created by GPT-4. The idea is to send up to 300 (8 leading characters for checksum, 
292 other) characters, 1 or 0, to an Arduino in order to control output pins.
The position of the character denotes the pin number, and the value the pin state. 

GPT-4:

This script sends a series of binary values to an Arduino via serial communication. 
The data sent is a string of characters, each of which is either '0' or '1'. 
The position of each character in the string corresponds to a specific pin on the Arduino, 
and the value of the character ('0' or '1') corresponds to the desired state of that pin (LOW or HIGH, respectively).

The script sends the data to the Arduino, waits for the Arduino to process the data and send it back, 
and then verifies that the data received from the Arduino matches the data that was sent. 
This process is repeated 1000 times, and the number of successful and failed transmissions is tracked and printed out at the end.

The script uses the pySerial library to handle the serial communication. 
The baud rate is set to 115200, and the script includes a delay after sending each character to 
prevent the Arduino's serial buffer from overflowing. The script also includes a delay after sending the 
data and before reading the Arduino's response, to give the Arduino time to process the data and start its transmission.


"""


import serial
import time
import random
import binascii


def add_checksum(data):
    # Calculate the CRC32 checksum and format it as a zero-padded 8-digit hexadecimal string
    checksum = format(binascii.crc32(data.encode()) & 0xffffffff, '08x')

    # Return the checksum followed by the original data
    return checksum + data

ser = serial.Serial('/dev/ttyACM0', 115200)  # replace '/dev/ttyACM0' with your serial port

# Wait for the Arduino to reset
time.sleep(2)

successes = 0
failures = 0

def serial_communicate(data):

    global successes
    global failures

    # Send the data
    ser.write(b'<')
    for char in data:
        ser.write(char.encode())
        time.sleep(0.00001)  # Delay to prevent Arduino's serial buffer from overflowing
    ser.write(b'>')

    # Print out the sent data
    print('Sent data:    ', data)

    # Wait for Arduino to start transmission (human intuition that fixed the program!)
    time.sleep(0.05)

    # Wait for the Arduino to send back the data
    received_data = ser.readline().decode().strip()

    # Verify the data
    if received_data == data:
        successes += 1
    else:
        failures += 1
        print('Error: Data verification failed')

    # Print out debug info from the Arduino
    while ser.in_waiting > 0:
        print(ser.readline().decode().strip())

for i in range(100):

    data = ''.join(random.choice('01') for _ in range(160))  # Generate random data

    serial_communicate(add_checksum(data))

print('Successes:', successes)
print('Failures:', failures)


ser.close()