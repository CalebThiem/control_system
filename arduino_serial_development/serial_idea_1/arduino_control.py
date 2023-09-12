"""

The idea is to send up to 300 (8 leading characters for checksum, 
292 other) characters, 1 or 0, to an Arduino in order to control output pins.
The position of the character denotes the pin number, and the value the pin state. 


Dependencies:

"""

import serial
import time
import random
import binascii
from timeit import default_timer


# Adds a checksum to the start of a message

def add_checksum(data):

  # Calculate the CRC32 checksum and format it as a zero-padded 8-digit hexadecimal string

  checksum = format(binascii.crc32(data.encode()) & 0xffffffff, '08x')

  # Return the checksum followed by the original data

  checksum = checksum.upper()

  return checksum + data

# Checks a zero-padded HEX CRC32 checksum in the first eight characters of a string beginning with "<" and ending with ">"

def validate_checksum(received_data):

  # Isolate the first 8 bytes of the transmission (not including the start character "<")

  checksum = received_data[1:9]

  # Isolate the rest of the transmission (not including the end character ">")

  message = received_data[9:-1]

  # Calculate the checksum of the message

  calculated_checksum = format(binascii.crc32(message.encode()) & 0xffffffff, '08x')

  # Compare locally calculated and transmitted checksums

  if calculated_checksum.upper() == checksum:

      return "checksum_validated"



# Sends string over serial (beginning witth "<" and ending with ">"), receives confirmaiton/failure message, receives and validates data sent from recipient

def serial_communicate(serial_port, data):

  # Send the data

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




def receive_data(serial_port):

  received_data = serial_port.readline().decode().strip()

  # Check for message start and end characters

  if received_data[0] == "<" and received_data[-1] == ">":

    if validate_checksum(received_data) != "checksum_validated":

      return "download_failed"

  # Return message body (ninth character and onwards, 0 - 8 is checksum)

  return received_data[9:-1]



# Tests functions above

def test(serial_port, reps, message_length, sleep_time, print_output):

  upload_successes = 0
  upload_failures = 0
  download_successes = 0
  download_failures = 0

  start = default_timer()

  # Send random data for testing

  for i in range(reps):

    # Generate random data

    data = ''.join(random.choice('10') for _ in range(message_length))  

    # Transmit data, receive response transmitted by Arduino

    message = serial_communicate(serial_port, add_checksum(data))

    # Comment line above and uncomment line below to test Arduino checksum validation
    
    # message = serial_communicate(serial_port, data)

    if message == "upload_failed":

        upload_failures += 1

    else:

        upload_successes += 1

    if print_output == "true":

      print(message)

    # Request data transmission from Arduino

    serial_communicate(serial_port, add_checksum("?"))

    message = receive_data(serial_port)

    if message == "download_failed":

      download_failuers += 1

    else:

      download_successes += 1

    if print_output == "true":

      print(message)
  


    time.sleep(sleep_time)

  end = default_timer()

  print('Upload successes:', upload_successes)
  print('Upload failures:', upload_failures)
  print('Download successes:', download_successes)
  print('Download failures:', download_failures)
  print('Time elapsed: %s seconds' % (end - start))
