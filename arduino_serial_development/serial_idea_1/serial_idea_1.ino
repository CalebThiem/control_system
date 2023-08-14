/*
Written by Caleb Thiem and GPT-4. Receives up to 300 characters (stable), 1 or 0, from a PC via serial communication to 
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

#include <MuxShield.h>

FastCRC32 CRC32;

//Initialize the Mux Shield

int S10 = 2;
int S11 = 3;
int S12 = 4;
int S13 = 5;

int S20 = 6;
int S21 = 7;
int S22 = 8;
int S23 = 9;

int IO11 = A0;
int IO12 = A1;
int IO13 = A2;

int IO21 = A3;
int IO22 = A4;
int IO23 = A5;

int OUTMD = 11;
int IOS1 = 10;
int IOS2 = 10;
int IOS3 = 10; 

MuxShield muxShield1(S10, S11, S12, S13, OUTMD, IOS1, IOS2, IOS3, IO11, IO12, IO13);
MuxShield muxShield2(S20, S21, S22, S23, OUTMD, IOS1, IOS2, IOS3, IO21, IO22, IO23);

// Define characters to signify beginning and end of transmission

#define START_MARKER '<'

#define END_MARKER '>'

#define MAX_MESSAGE_LENGTH 301

#define LED_BUILTIN 13  // Most Arduino boards have a built-in LED on pin 13


char receivedData[MAX_MESSAGE_LENGTH + 1];  // Extra space for the null terminator

char message[MAX_MESSAGE_LENGTH + 1];

bool receiving = false;

int dataIndex = 0;

int serialReceive(void);

int verify_checksum(char * message);

void generate_checksum(char * message);

void toggle_outputs(int toggle);


void setup() {

  //Set I/O 1, I/O 2, and I/O 3 as digital outputs
  muxShield1.setMode(1,DIGITAL_OUT);  
  muxShield1.setMode(2,DIGITAL_OUT);
  muxShield1.setMode(3,DIGITAL_OUT);

  muxShield2.setMode(1,DIGITAL_OUT);  
  muxShield2.setMode(2,DIGITAL_OUT);
  muxShield2.setMode(3,DIGITAL_OUT);

  toggle_outputs(LOW);

  Serial.begin(460800);



}

void loop() {

    // serialReceive() returns 2 if the incoming transmission's checksum is validated

    if (serialReceive() == 2) {

        if (receivedData[8] == '1') {

        toggle_outputs(HIGH);

        } else if (receivedData[8] == '0') {

        toggle_outputs(LOW);

        }

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

    // Set the onboard LED according to the value of the first byte received, for testing

  
    


  
    
  }
} 


// Communicate via serial connection. Retuns 2 if checksum is verified

int serialReceive() {

  int status = 0;

  while (Serial.available() > 0) {

      char receivedChar = Serial.read();

      if (receivedChar == START_MARKER) { // Start of transmission

        receiving = true;

        dataIndex = 0;

      } else if (receivedChar == END_MARKER) { // End of transmission

        receiving = false;
        
        receivedData[dataIndex] = '\0';  // Null-terminate the data
        
        // Serial.write(receivedData);
        // Serial.write("\n");
        //Serial.print("Received data: ");
        // Serial.println(receivedData);

        // Verify the checksum received in the leading 8 bytes of the transmission

        if (verify_checksum(receivedData) == 2) {

          /*
          Serial.print("Checksum verified");
          Serial.print('\n');
          Serial.print("Serial Receive: Returning true\n");
          */

          status = 2;
          
        } else {

          Serial.write("ChecksumFailed\n");
          
        }

      } else if (receiving) { // Transmission recording in progerss, one character at a time

        if (dataIndex < MAX_MESSAGE_LENGTH) {

          receivedData[dataIndex] = receivedChar;

          dataIndex++;

        }
      }
  }

  return status;

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

  /*
  Serial.print("Received message: ");
  Serial.print(message);
  Serial.print("\n");
  Serial.print("Received Checksum: ");
  Serial.print(received_checksum);
  Serial.print("\n");
  Serial.print("Calculated Checksum: ");
  Serial.print(calculated_checksum, HEX);
  Serial.print("\n");
  */

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



void toggle_outputs(int toggle) {

    //loop to toggle all IO 1 outputs
  for (int i=0; i<16; i++)
  {
    muxShield1.digitalWriteMS(1,i,toggle);
    muxShield2.digitalWriteMS(1,i,toggle);
  }
  
  //loop to toggle all IO 2 outputs
  for (int i=0; i<16; i++)
  {
    muxShield1.digitalWriteMS(2,i,toggle);
    muxShield2.digitalWriteMS(2,i,toggle);
  }
  
  //loop to toggle all IO 3 outputs
  for (int i=0; i<16; i++)
  {
    muxShield1.digitalWriteMS(3,i,toggle);
    muxShield2.digitalWriteMS(3,i,toggle);
  }
}



