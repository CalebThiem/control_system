"""

Written by Caleb Thiem and GPT-4. The idea is to send up to 300 (8 leading characters for checksum, 
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

from timeit import default_timer

print_status_messages = 1


def add_checksum(data):

    # Calculate the CRC32 checksum and format it as a zero-padded 8-digit hexadecimal string

    checksum = format(binascii.crc32(data.encode()) & 0xffffffff, '08x')

    # Return the checksum followed by the original data

    checksum = checksum.upper()

    return checksum + data


def validate_checksum(received_data):

    # Isolate the first 8 bytes of the transmission (not including the start character "<")

    checksum = received_data[1:9]

    # Isolate the rest of the transmission (not including the end character ">")

    message = received_data[9:-1]

    # Calculate the checksum of the message

    calculated_checksum = format(binascii.crc32(message.encode()) & 0xffffffff, '08x')

    '''

    print("Received data: %s" % received_data)
    
    print("Checksum received: %s" % checksum)

    print("Message: %s" % message)

    print("Calculated checksum: %s" % calculated_checksum)

    '''

    # Compare locally calculated and transmitted checksums

    if calculated_checksum.upper() == checksum:

        if print_status_messages == 1:
            print("Transmission from Arduino validated", end=" ")

        return 0


# Open serial connection

ser = serial.Serial('/dev/ttyACM0', 460800)  # replace '/dev/ttyACM0' with your serial port

# Wait for the Arduino to reset

time.sleep(2)

upload_successes = 0
upload_failures = 0
download_successes = 0
download_failures = 0

# Sends data, receives confirmaiton/failure message, receives and validates data sent from recipient

def serial_communicate(data):

    global upload_successes
    global upload_failures
    global download_successes
    global download_failures

    # Send the data

    # Send message start character

    ser.write(b'<')

    # Transmit data one character at a time

    for char in data:

        ser.write(char.encode())

    # Transmit message end character

    ser.write(b'>')

    if print_status_messages == 1:
        print("Transmitted data to Arduino", end=" ... ")

    '''
    Print out the sent data
    print('Sent data:    ', data)
    '''
    '''
    Wait for Arduino to start transmission (increases reliablity when waiting for transmission from Arduino)
    time.sleep(0.05)
    '''

    # Wait for the Arduino to send back the data

    received_data = ser.readline().decode().strip()

    # Verify the data

    if received_data == "Validated":

        if print_status_messages == 1:
            print("Arduino validated checksum", end=" ... ")

        upload_successes += 1

    if received_data == "ChecksumFailed":

        upload_failures += 1

        if print_status_messages == 1:
            print('Failed: checksum mismatch', end=" ... ")

        #serial_communicate(data)

    received_data = ser.readline().decode().strip()

    '''
    print(received_data[0])
    print(received_data[-1])
    print(received_data)
    '''

    # Check for message start and end characters

    if received_data[0] == "<" and received_data[-1] == ">":

        if print_status_messages == 1:
            print("Received Message", end=" ... ")
        
        if validate_checksum(received_data) == 0:

            download_successes += 1

        else:

            download_failures += 1

            if print_status_messages == 1:
                print("Message checksum mismatch", end="")

            # serial_communicate(data)


    '''
    # Print out debug info from the Arduino
    while ser.in_waiting > 0:
        print(ser.readline().decode().strip())
    '''

    if print_status_messages == 1:
        print("")

    # Return message body (ninth character and onwards, 0 - 8 is checksum)

    return received_data[9:-1]


start = default_timer()


# Send random data for testing

for i in range(10):

    data = ''.join(random.choice('01') for _ in range(292))  # Generate random data

    '''
    # Break transmission for testing
    transmit = add_checksum(data)
    print(transmit)
    transmit = transmit[:-1]
    print(transmit)
    serial_communicate(transmit)
    '''

    # Transmit data, receive response and data transmitted by Arduino

    '''
    print("Sent:     ", data)
    print("Received: ", serial_communicate(add_checksum(data)))
    '''



    serial_communicate(add_checksum(data))

    #time.sleep(0.07)

 
end = default_timer()

print('Upload successes:', upload_successes)
print('Upload failures:', upload_failures)
print('Download successes:', download_successes)
print('Download failures:', download_failures)
print('Time elapsed: %s seconds' % (end - start))


# Close serial connection

ser.close()