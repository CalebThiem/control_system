/*
Written by Caleb Thiem and GPT-4. Receives up to 300 characters (stable), 1 or 0, from a PC via serial communication to 
control output pins. The position of the character denotes the pin number, and the value the pin state. 
It then sends back the received data for verification.

This script receives a series of binary values from a PC via serial communication. 
The data received is a string of characters, each of which is either '0' or '1'. 
The position of each character in the string corresponds to a specific pin on the Arduino, 
and the value of the character ('0' or '1') corresponds to the desired state of that pin (LOW or HIGH, respectively).

The script reads the data from the serial buffer, processes it, and then sends it's own data back to the PC. 
The script uses start and end markers to frame the data, and includes error checking to ensure that the data is received correctly.

The script uses the Arduino's built-in Serial library to handle the serial communication. The baud rate is set to 460800.

IMPORTANT!

Move the declerations

int _shiftReg1[16]={0};
int _shiftReg2[16]={0};
int _shiftReg3[16]={0};

from the header of MuxShield.cpp to the definition of the MuxShield class (private) in MuxShield.h. 
This prevents flickering of the pin states when using more than one board.

*/

#include <FastCRC.h> // Library for CRC hash function

#include <MuxShield.h> // Library for the Mux Shield 2

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

int OUTMD1 = 200; // Nonexistant pin, hardware pins tied to 5V
int OUTMD2 = 200;

int IOS11 = 200;
int IOS12 = 200;
int IOS13 = 200; 

int IOS21 = 200;
int IOS22 = 200;
int IOS23 = 200;




MuxShield muxShield1(S10, S11, S12, S13, OUTMD1, IOS11, IOS12, IOS13, IO11, IO12, IO13);
MuxShield muxShield2(S20, S21, S22, S23, OUTMD2, IOS21, IOS22, IOS23, IO21, IO22, IO23);

// Define characters to signify beginning and end of transmission

#define START_MARKER '<'

#define END_MARKER '>'

#define MAX_MESSAGE_LENGTH 301

#define LED_BUILTIN 13  // Most Arduino boards have a built-in LED on pin 13

#define MUX_BOARD_PIN_COUNT 48

#define CHECKSUM_LENGTH 8


char receivedData[MAX_MESSAGE_LENGTH + 1];  // Extra space for the null terminator

// unsigned int receivedDataLength = 0;

char message[MAX_MESSAGE_LENGTH + 1];

unsigned int dataIndex = 0;

bool serialReceive(void);

int verify_checksum(char * message);

void generate_checksum(char * message);

void toggle_outputs(int toggle);

void mux_shield_1_control(unsigned int relayNumber, int state);

void mux_shield_2_control(unsigned int relayNumber, int state);


void setup() {

  //Set I/O 1, I/O 2, and I/O 3 as digital outputs
  muxShield1.setMode(1,DIGITAL_OUT);  
  muxShield1.setMode(2,DIGITAL_OUT);
  muxShield1.setMode(3,DIGITAL_OUT);

  muxShield2.setMode(1,DIGITAL_OUT);  
  muxShield2.setMode(2,DIGITAL_OUT);
  muxShield2.setMode(3,DIGITAL_OUT);

  Serial.begin(460800);
}

void loop() {

    if (serialReceive()) {

      unsigned int received_data_length = strlen(receivedData);

      if (received_data_length >= 96 + 8) {

        for (unsigned int i = 8; i < 48 + 8; i++) {

          mux_shield_1_control(i - 7, receivedData[i] - '0');

        }

        for (unsigned int i = 48; i < 96 + 8; i++) {

          mux_shield_2_control(i - 7, receivedData[i] - '0');

        }
        
      }

      if ((received_data_length > 48 + 8) && (received_data_length < 96 + 8)) {

        for (unsigned int i = 8; i < 48 + 8; i++) {

          mux_shield_1_control(i - 7, receivedData[i] - '0');

        }

        for (unsigned int i = 48; i < received_data_length; i++) {

          mux_shield_2_control(i - 7, receivedData[i] - '0');

        }

      }

      if (received_data_length <= 48 + 8) {

        for (unsigned int i = 8; i < received_data_length; i++) {

          mux_shield_1_control(i - 7, receivedData[i] - '0');

        }

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

  if (strlen(message) <= 8) {

    return 1;

  }

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


void mux_shield_1_control(unsigned int relayNumber, int state) {

  if (relayNumber <= 16) {

    relayNumber = relayNumber - 1;

    muxShield1.digitalWriteMS(1, relayNumber, state);

    return;

   
    
  }

  if (relayNumber <= 32) {

    relayNumber = relayNumber - 2;

    muxShield1.digitalWriteMS(2, relayNumber - 15, state);

    return;

  }

  if (relayNumber <= 48) {

    relayNumber = relayNumber - 3;

    muxShield1.digitalWriteMS(3, relayNumber - 30, state);

    return;

  }

}


void mux_shield_2_control(unsigned int relayNumber, int state) {

  if (relayNumber <= 64) {

    relayNumber = relayNumber - 4;

    muxShield2.digitalWriteMS(1, relayNumber - 45, state);

    return;
  }

  if (relayNumber <= 80) {

    relayNumber = relayNumber - 5;

    muxShield2.digitalWriteMS(2, relayNumber - 60, state);

    return;
  }

  if (relayNumber <= 96) {

    relayNumber = relayNumber - 6;

    muxShield2.digitalWriteMS(3, relayNumber - 75, state);

    return;

  }

}


