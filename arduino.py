import serial
import time
import random
import binascii
import threading
import os
from timeit import default_timer
# Define class that includes all Arduino I/O functionality


class Arduino:

    '''

    Communicates with the Arduino over serial. See arduino.ino docstring
    for detailed information on the communication protocol.

    Attributes:

        connection_ready : bool

            Set to True 2 seconds after connection is made
            (Arduino needs time to reset after serial connection is established)

       input_pin_states : string

            Stores the latest string sent from the Arduino, reflecting the state
            of the Arduino's input pins

    Methods:

        connect(address, baud_rate)

            Initiates the serial connection with the Arduino
            (Returns "connection_failed" if unsuccessful)

        disconnect()

            Ends the serial connection

        serial_communicate(message)

            Sends a string to the Arduino

        refresh(message)

            Sends a string to the Arduino, stores the Arduino's response in
            the input_pin_states variable, returns the Arduino's response

        read_inputs()

            Returns the Arduino's input pin state transmission

        test(reps, transmission length (1 - 292), sleep time between
        reps (seconds), print Arduino response string (True/False)

            Transmits a random string of 1s and 0s to the Arduino,
            receives response, and prints the time elapsed once
            the test has ended
    '''


    def __init__(self):

        self.input_pin_states = ""

        self.input_pin_states_list = list

        self.connection_ready = False

        self.lock = threading.Lock()

    def set_ready(self):

        self.connection_ready = True

    def connect(self, address, baud_rate):

        try:

            self.serial_connection = serial.Serial(address, baud_rate, timeout=1)

        except serial.serialutil.SerialException:

            return "connection_failed"

        else:

            threading.Timer(2, self.set_ready).start()

            return 1


    def disconnect(self):

        if self.connection_ready:

            try:

                self.serial_connection.close()

            finally:

                self.connection_ready = False

        else:

            return "no_connection"

    # Adds a checksum to the start of a message

    def add_checksum(self, data):

        # Calculate the CRC32 checksum and format it as a zero-padded
        # 8-digit hexadecimal string

        checksum = format(binascii.crc32(data.encode()) & 0xffffffff, '08x')

        # Return the checksum followed by the original data

        checksum = checksum.upper()

        return checksum + data

    # Checks a zero-padded HEX CRC32 checksum in the first eight
    # characters of a string beginning with "<" and ending with ">"

    def validate_checksum(self, received_data):

        # Isolate the first 8 bytes of the transmission (not
        # including the start character "<")

        checksum = received_data[1:9]

        # Isolate the rest of the transmission (not including the
        # end character ">")

        message = received_data[9:-1]

        # Calculate the checksum of the message

        calculated_checksum = format(binascii.crc32(message.encode()) & 0xffffffff, '08x')

        # Compare locally calculated and transmitted checksums

        if calculated_checksum.upper() == checksum:

            return "checksum_validated"

    def receive_data(self):

        try:
            
            received_data = self.serial_connection.readline().decode().strip()

        except serial.serialutil.SerialException:
            
            received_data = False

            print("Arduino.receive_data: connection error")

        if received_data:

            pass

        else:

            return "no_data_received"

        # Check for message start and end characters

        if received_data[0] == "<" and received_data[-1] == ">":

            if self.validate_checksum(received_data) != "checksum_validated":

                return "download_failed"

        # Return message body (ninth character and onwards, 0 - 8 is checksum)

        return received_data[9:-1]

    # Sends string over serial (beginning witth "<" and ending
    # with ">"), receives confirmaiton/failure message, receives
    # and validates data sent from recipient

    def serial_communicate(self, data):

        # Print data to be sent to Arduino, for debugging

        failed_uploads = 0

        serial_port = self.serial_connection

        # Add checksum

        data = self.add_checksum(data)
        
        while True:

            # Send message start character
            
            try:
                
                serial_port.write(b'<')

            except serial.serialutil.SerialException:
                
                print("Arduino.serial_communicate: connection error")

                self.connection_ready = False

                return 1
        
            # Transmit data one character at a time

            for char in data:
                
                try:

                    serial_port.write(char.encode())

                except serial.serialutil.SerialException:

                    self.connection_ready = False
                    
                    print("Arduino.serial_communicate: connection error")

                    return 1
            
            # Transmit message end character
            
            try:

                serial_port.write(b'>')

            except serial.serialutil.SerialException:

                self.connection_ready = False
                
                print("Arduino.serial_communicate: connection error")

                return 1

            # Wait for the Arduino to send success/failure message
            
            try:

                received_data = serial_port.readline().decode().strip()

            except serial.serialutil.SerialException:
                
                print("Arduino.serial_communicate.received_data: connection error")

                return 1

            # Verify the data

            if received_data == "ChecksumFailed":

                failed_uploads += 1

            if received_data == "Validated":

                return failed_uploads # If no uploads failed, returns 0
            
            else:

                failed_uploads += 1

    # Transimts message and reads Arduino input pin states

    def refresh(self, pin_state_list):
        
        while True:

            self.serial_communicate("?") 

            received_data = self.receive_data()

            if (received_data == "download_failed"):

                pass

            else:

                return received_data

    # Requests and reads Arduino input pin states

    def read_inputs(self):

        # Get sensor readings, if reception fails, retry
        
        while True:

            self.serial_communicate("?") 

            received_data = self.receive_data()

            # print(received_data)

            if (received_data == "download_failed"):

                pass

            else:

                break

        # Split the string by hyphens
        
        parts = received_data.split('-')

        # Process the first part (series of '1's) into individual digits
    
        first_part_digits = list(parts[0])

        # Combine the individual digits with the remaining parts
    
        self.input_pin_states_list = first_part_digits + parts[1:]

        return self.input_pin_states_list
        
    # Tests transmit and receive functionality

    def test(self, reps, message_length, sleep_time, print_output):

        upload_successes = 0
        upload_failures = 0

        download_successes = 0
        download_failures = 0

        if print_output is False:

            print("Test started...")

        start = default_timer()

        # Send random data for testing

        for i in range(reps):

            # Generate random data

            data = ''.join(random.choice('10') for _ in range(message_length))

            if print_output is True:

                print(data)

            # Transmit data, receive response transmitted by Arduino

            returned_value = self.serial_communicate(data)

            if returned_value != 0:

                upload_failures += 1

            else:

                upload_successes += 1

            returned_value = self.serial_communicate("?")

            if returned_value != 0:

                upload_failures += 1

            else:

                upload_successes += 1

            message = self.receive_data()

            if len(message) == 74:

                download_successes += 1

            else:

                download_failures += 1

            if print_output is True:

                print(message)

            time.sleep(sleep_time)

        end = default_timer()

        print('Upload successes:', upload_successes)
        print('Upload failures:', upload_failures)
        print('Download successes:', download_successes)
        print('Download failures:', download_failures)
        print('Time elapsed: %s seconds' % round((end - start), 3))


if __name__ == '__main__':

    arduino = Arduino()

    auto_connect = input("Connect automatically? y/n ")

    if auto_connect == "y":

        arduino_address = ""

        for address in os.listdir("/dev/serial/by-id"):

            if "Arduino" in address:

                arduino_address = '/dev/serial/by-id/' + address
 
        if arduino.connect(arduino_address, 480600):

            print(f'Connected to {arduino_address}')

            print('Class instance "arduino" created. To test connection, run arduino.test(reps=10, message_length=292, sleep_time=0, print_output=True)')   
    else:

        address_number = eval(input("enter number of serial port: "))

        if arduino.connect(f'/dev/ttyACM{address_number}', 480600):

            print(f'Connected to /dev/ttyACM{address_number}')

            print('Class instance "arduino" created. To test connection, run arduino.test(reps=10, message_length=292, sleep_time=0, print_output=True)')   

