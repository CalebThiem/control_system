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

    # Wait for the Arduino to send back the data

    received_data = serial_port.readline().decode().strip()

    # Verify the data

    if received_data == "Validated":
        
        pass

    if received_data == "ChecksumFailed":

        return "upload_failed"

    received_data = serial_port.readline().decode().strip()

    # Check for message start and end characters

    if received_data[0] == "<" and received_data[-1] == ">":

        if validate_checksum(received_data) != "checksum_validated":

            return "download_failed"

    # Return message body (ninth character and onwards, 0 - 8 is checksum)

    return received_data[9:-1]

# Tests functions above

def test(serial_port, reps, message_length, sleep_time):

    upload_successes = 0
    upload_failures = 0
    download_successes = 0
    download_failures = 0

    start = default_timer()

    # Send random data for testing

    for i in range(reps):

        data = ''.join(random.choice('10') for _ in range(message_length))  # Generate random data

        # Transmit data, receive response and data transmitted by Arduino

        message = serial_communicate(serial_port, add_checksum(data))
        
        # message = serial_communicate(serial_port, data)

        if message == "upload_failed":

            upload_failures += 1

        elif message == "download_failed":

            download_failures += 1

        else:

            upload_successes += 1

            download_successes += 1

        time.sleep(sleep_time)

    end = default_timer()

    print('Upload successes:', upload_successes)
    print('Upload failures:', upload_failures)
    print('Download successes:', download_successes)
    print('Download failures:', download_failures)
    print('Time elapsed: %s seconds' % (end - start))


'''

Arduino code:

#include <FastCRC.h> // Library for CRC hash function

FastCRC32 CRC32;

// Define characters to signify beginning and end of transmission

#define START_MARKER '<'

#define END_MARKER '>'

#define MAX_MESSAGE_LENGTH 301


char receivedData[MAX_MESSAGE_LENGTH + 1];  // Extra space for the null terminator

unsigned int receivedDataLength = 0;

char message[MAX_MESSAGE_LENGTH + 1];

bool receiving = false;

int dataIndex = 0;

bool serialReceive(void);

int verify_checksum(char * message);

void generate_checksum(char * message);


void setup() {

  Serial.begin(460800);

}

void loop() {

    // serialReceive() returns 2 if the incoming transmission's checksum is validated

    if (serialReceive()) {

    // Put code to run here

    Serial.write("Validated\n");

    // Reset the array used for outgoing transmissions to null bytes
    // Ensures that transmission will always be null terminated

    for (int i = 0; i <= MAX_MESSAGE_LENGTH; i++) { 
    
      message[i] = '\0';

    }

    // Populate outgoiong transmission array with random data for testing (eighth byte and onward)

    for (int i = 7; i <= 292; i++) {

      message[i] = ((random(0, 9)) + '0');

    }

    // Populate the first 8 bytes of the outgoing transmission array with a checksum of the rest

    generate_checksum(message);

    // Transmit character that signifies start of transmission

    Serial.write('<');

    Serial.write(message);

    // Transmit character that signifies end of transmission

    Serial.write('>');

    Serial.write('\n');

  }
  
} 


// Communicate via serial connection. Retuns 2 if checksum is verified

bool serialReceive() {

  unsigned int dataIndex = 0;

  while (Serial.available() > 0) { // Check if the serial buffer contains data, if not skips loop and returns false

    char receivedChar = Serial.read();

    if (receivedChar == START_MARKER) { // Check for transmission start

      while (true) { // Reads from the serial buffer until the end character is found, or the maxumum length is reached

        if (Serial.available() > 0) {

          receivedChar = Serial.read(); // Read a character from the serial buffer

          if (receivedChar == END_MARKER) { // End of transmission
            
            receivedData[dataIndex] = '\0';  // Null-terminate the data

            // Verify the checksum received in the leading 8 bytes of the transmission

            if (verify_checksum(receivedData) == 2) {

              /*
              Serial.print("Checksum verified");
              Serial.print('\n');
              Serial.print("Serial Receive: Returning true\n");
              */

              return true;

            } else {

              Serial.write("ChecksumFailed\n");

              return false;
              
            }

          }

          if (dataIndex < MAX_MESSAGE_LENGTH) { // Writes the received char to the message array

            receivedData[dataIndex] = receivedChar;

            dataIndex++; // Moves cursor to next char in message array

          }

          else {

            receivedData[MAX_MESSAGE_LENGTH] = '\0'; // Max transmission length without end character

            return false;

          } 

        }

      }

    }

  }

  return false;

}


// Checks the CRC32 checksum in the first 8 bytes of a string (zero padded hexadecimal), returns 2 if successful

int verify_checksum(char* message) {

  int status = 0;

  // Extract the first 8 characters (checksum in hex)

  char received_checksum[9];

  strncpy(received_checksum, message, 8);

  received_checksum[8] = '\0';  // Null-terminate the checksum string

  // Convert hexadecimal checksum to integer

  unsigned long received_checksum_value = strtoul(received_checksum, NULL, 16);

  // Calculate the checksum of the rest of the message

  unsigned long calculated_checksum = CRC32.crc32((uint8_t*)&message[8], strlen(&message[8]));

  // Compare the received and calculated checksums

  if (received_checksum_value == calculated_checksum) {

    status = 2;

  }

  return status;

}

// Adds a checksum of the information in an array (the eigth byte onwards) to the beginning 8 bytes of the array

void generate_checksum(char * message) {

  // Calculate the checksum of the message

  unsigned long calculated_checksum = CRC32.crc32((uint8_t*)&message[8], strlen(&message[8]));

  // Copy the checksum into the first 8 characters of the message array as a string 
  // representing a 0-padded hexadecimal number

  char checksumHex[9];

  sprintf(checksumHex, "%08lX", calculated_checksum);

  /*

  In the format specifier "%08lX":

    % begins the format specifier.
    0 indicates that padding should be done with zeros.
    8 specifies the minimum width of the field (8 characters in this case).
    l (lowercase L) is a modifier that indicates a long integer argument.
    X specifies that the value should be formatted as an uppercase hexadecimal number.

  */

  for (int i = 0; i < 8; i++) {

    message[i] = checksumHex[i];

  }

}

'''
