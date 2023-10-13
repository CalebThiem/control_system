import serial
import time 
import random
import binascii
import threading
from timeit import default_timer

# Define class that includes all Arduino I/O functionality

class Arduino:

'''

Communicates with the Arduino over serial. See arduino.ino docstring for detailed information on the communication protocol.

Attributes:

    connection_ready : bool
        
        Set to True 2 seconds after connection is made (Arduino needs time to reset after serial connection is established)

   input_pin_states : string

        Stores the latest string sent from the Arduino, reflecting the state of the Arduino's input pins

Methods:

    connect(address, baud_rate)

        Initiates the serial connection with the Arduino. Returs "connection_failed" if unsuccessful)

    disconnect()

        Ends the serial connection

    serial_communicate(message)

        Sends a string to the Arduino

    refresh(message)

        Sends a string to the Arduino, stores the Arduino's response in the input_pin_states variable, returns the Arduino's response

    read_inputs()

        Returns the Arduino's input pin state transmission

    test(reps, transmission length (1 - 292), sleep time between reps (seconds), print Arduino response string (True/False)

        Transmits a random string of 1s and 0s to the Arduino, receives response, and prints the time elapsed once the test has ended
'''


    def __init__(self):

        self.input_pin_states = ""

        self.connection_ready = False

        

    def set_ready(self):

        self.connection_ready = True

    def connect(self, address, baud_rate):

        try:

            self.serial_connection = serial.Serial(address, baud_rate, timeout = 1)

        except:

            return "connection_failed"

        else:

            threading.Timer(2, self.set_ready).start()


    def disconnect(self):

        if self.connection_ready == True:

            self.serial_connection.close()

            self.connection_ready = False

        else:

            return "no_connection"


    # Adds a checksum to the start of a message

    def add_checksum(self, data):

        # Calculate the CRC32 checksum and format it as a zero-padded 8-digit hexadecimal string

        checksum = format(binascii.crc32(data.encode()) & 0xffffffff, '08x')

        # Return the checksum followed by the original data

        checksum = checksum.upper()

        return checksum + data

    # Checks a zero-padded HEX CRC32 checksum in the first eight characters of a string beginning with "<" and ending with ">"


    def validate_checksum(self, received_data):

        # Isolate the first 8 bytes of the transmission (not including the start character "<")

        checksum = received_data[1:9]

        # Isolate the rest of the transmission (not including the end character ">")

        message = received_data[9:-1]

        # Calculate the checksum of the message

        calculated_checksum = format(binascii.crc32(message.encode()) & 0xffffffff, '08x')

        # Compare locally calculated and transmitted checksums

        if calculated_checksum.upper() == checksum:

            return "checksum_validated"


    def receive_data(self):
        
        received_data = self.serial_connection.readline().decode().strip()

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


    # Sends string over serial (beginning witth "<" and ending with ">"), receives confirmaiton/failure message, receives and validates data sent from recipient

    def serial_communicate(self, data):

        serial_port = self.serial_connection

        # Add checksum
        
        data = self.add_checksum(data)
            
        # Send message start character

        serial_port.write(b'<')

        # Transmit data one character at a time

        for char in data:

            serial_port.write(char.encode())

        # Transmit message end character

        serial_port.write(b'>')

        # Wait for the Arduino to send success/failure message

        received_data = serial_port.readline().decode().strip()

        # Verify the data

        if received_data == "ChecksumFailed":

            return "upload_failed"

        if received_data != "Validated":

            return "upload_failed"

        if received_data == "Validated":

            return "upload_success"
    

    # Transimts message and reads Arduino input pin states


    def refresh(self, pin_state_list):

        self.serial_communicate(pin_state_list)

        self.serial_communicate("?")

        input_pin_states = self.receive_data()

        return(input_pin_states)
    

    # Requests and reads Arduino input pin states    

    def read_inputs(self):

        self.serial_communicate("?")

        return self.receive_data()


    # Tests transmit and receive functionality
    
    def test(self, reps, message_length, sleep_time, print_output):

        upload_successes = 0
        upload_failures = 0
        download_successes = 0
        download_failures = 0

        if print_output == False:

            print("Test started...")

        start = default_timer()

        # Send random data for testing

        for i in range(reps):

            # Generate random data

            data = ''.join(random.choice('10') for _ in range(message_length))  

            # Transmit data, receive response transmitted by Arduino

            message = self.serial_communicate(data)

            if message == "upload_failed":

                upload_failures += 1

            else:

                upload_successes += 1

            self.serial_communicate("?")

            message = self.receive_data()

            if message == "download_failed":

                download_failures += 1

            else:

                download_successes += 1
          
                if print_output == True:
    
                    print(message)


            time.sleep(sleep_time)


        end = default_timer()

        print('Upload successes:', upload_successes)
        print('Upload failures:', upload_failures)
        print('Download successes:', download_successes)
        print('Download failures:', download_failures)
        print('Time elapsed: %s seconds' % round((end - start), 3))

