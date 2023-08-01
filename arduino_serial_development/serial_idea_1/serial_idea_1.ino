/*
Created by GPT-4. It receives up to 300 characters (stable), 1 or 0, from a PC via serial communication to 
control output pins. The position of the character denotes the pin number, and the value the pin state. 
It then sends back the received data for verification.

This script receives a series of binary values from a PC via serial communication. 
The data received is a string of characters, each of which is either '0' or '1'. 
The position of each character in the string corresponds to a specific pin on the Arduino, 
and the value of the character ('0' or '1') corresponds to the desired state of that pin (LOW or HIGH, respectively).

The script reads the data from the serial buffer, processes it, and then sends it back to the PC. 
The script uses start and end markers to frame the data, and includes error checking to ensure that the data is received correctly.

The script uses the Arduino's built-in Serial library to handle the serial communication. The baud rate is set to 115200.
*/

#include <FastCRC.h> // Library for CRC hash function

FastCRC32 CRC32;

#define START_MARKER '<'
#define END_MARKER '>'
#define MAX_MESSAGE_LENGTH 301

#define LED_BUILTIN 13  // Most Arduino boards have a built-in LED on pin 13

char receivedData[MAX_MESSAGE_LENGTH + 1];  // Extra space for the null terminator
bool receiving = false;
int dataIndex = 0;

void setup() {
  Serial.begin(115200);
  pinMode(LED_BUILTIN, OUTPUT);  // Initialize the digital pin as an output.
}

void loop() {
    if (serialCommunicate() == true) {
      if (receivedData[8] == '1') {
        digitalWrite(LED_BUILTIN, HIGH);
      } else if (receivedData[8] == '0') {
        digitalWrite(LED_BUILTIN, LOW);
      }
    }
      
}


// Communicate via serial connection. Retuns true if checksum is verified

int serialCommunicate() {
  while (Serial.available() > 0) {
      char receivedChar = Serial.read();

      if (receivedChar == START_MARKER) {
        receiving = true;
        dataIndex = 0;
      } else if (receivedChar == END_MARKER) {
        receiving = false;
        receivedData[dataIndex] = '\0';  // Null-terminate the data
        Serial.write(receivedData);
        Serial.write("\n");
        Serial.print("Received data: ");
        Serial.println(receivedData);
        if (verify_checksum(receivedData) == true) {
          Serial.print("Checksum verified");
          Serial.print('\n');
          return(true);
        }
      } else if (receiving) {
        if (dataIndex < MAX_MESSAGE_LENGTH) {
          receivedData[dataIndex] = receivedChar;
          dataIndex++;
        }
      }

  }
}

// Checks the CRC32 checksum in the first 8 bytes of a string (zero padded hexadecimal)

bool verify_checksum(char* message) {
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
    return true;
  } else {
    return false;
  }
}
