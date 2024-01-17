/*
Written by Caleb Thiem. 

# Description #

Communicates with an Arduino over serial, sending and receiving strings up to 300 characters in length. 
Upon receiving a string of 1s and 0s, the script sets digital out pins on two MuxShield2 boards, with 
1 representing HIGH, and 0 representing LOW, and the position of the character in the string representing
the pin number. 

Example:  

111001

Will set the first six pins on the first MuxShield2 board, with pins 1, 2, 3, and 6 being set HIGH, and pins 4 and 5 
being set low.

If requested, the states of digital input pins 30 through 53, and analog pins A6 through A15 are trasmitted.

Advantages: easy to understand and modify

Disadvantages: inefficient

# General Behaviour #

# Baud Rate #

Arduino opens serial port at 460800 baud.

# Serial Transmission #

Message is up to 300 bytes long. Each byte represents an ASCII text character.

The first byte is a '<'. This signifies the start of the message. 

The next 8 bytes comprise a zero-padded, capitalised hexadecimal CRC32 checksum of the rest of the message, excluding the last character.

The last byte is a '>'. This signifies the end of the message.

Upon receiving a properly formatted message, the Arduino will respond with one of the following ASCII text transmissions:

    "Verified" is sent if the checksum matches the computed checksum

    "ChecksumFailed" is sent if the checksum does not match the computed checksum


If the first character after the checksum was a '?', the Arduino will then send
a message of its own, with identical formatting.

This message is composed of 24 "1" or "0" characters, with each consecutive character representing the state of a digital input pin, 
representing pins 30 through 53, inclusive. Following this string of 1s and 0s is a dash, followed by ten dash-seperated four digit numbers, 
each holding the value (0 to 1023) of an analog input pin, beginning with A6 and ending with A15. 


Input example:

<8758F833101010111000010101010011110000101010101010>

<checksum-----------output pin states-------------->


Output example:

<BC90042C111111111111111111111111-0473-0526-0644-0622-0636-0654-0705-0714-0715-0725>

<checksum---digital pin states--- -A6- -A7- -A8- -A9- -A10 -A11 -A12 -A13 -A14 -A15>


Full communication example:

Sent: <8758F833101010111000010101010011110000101010101010>

Received: Validated\n

Sent: <6464C2B0?>

Received: Validated\n

Received: <8F147D37111111111111111111111111-0530-0505-0494-0471-0434-0385-0343-0327-0293-0242>

Sent: <ED82CD11abcx>

Received: ChecksumFailed\n

Sent: <ED82CD11abcd>

Received: Validated\n



IMPORTANT!

Move the declerations

int _shiftReg1[16]={0};
int _shiftReg2[16]={0};
int _shiftReg3[16]={0};

from the header of MuxShield.cpp (in the MuxShield library) to the definition of the MuxShield class (private) in MuxShield.h. 
This prevents flickering of the pin states when using more than one board.

*/

// const int digitalReadPins[24] = {30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53};

// Digital out (PWM capable) pins 2 through 13 are available if needed

//const int analogReadPins[10] = {A6, A7, A8, A9, A10, A11, A12, A13, A14, A15};

// Analog pins A0 to A5 are used for MuxShield2 communication

const int digitalReadPins[12] = {2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13};

const int analogReadPins[6] = {A0, A1, A2, A3, A4, A5};

#define digitalReadPinMode INPUT_PULLUP

#define analogReadPinMode INPUT

#include <FastCRC.h> // Library for CRC hash function

#include <MuxShield.h> // Library for the MuxShield2

FastCRC32 CRC32;

//Initialize the first MuxShield2

int S10 = 22;
int S11 = 23;
int S12 = 24;
int S13 = 25;

int IO11 = A0;
int IO12 = A1;
int IO13 = A2;

int OUTMD1 = 200; // Nonexistant pins, hardware pins tied to 5V
int IOS11 = 200;
int IOS12 = 200;
int IOS13 = 200; 

MuxShield muxShield1(S10, S11, S12, S13, OUTMD1, IOS11, IOS12, IOS13, IO11, IO12, IO13);

// Initialize the second MuxShield2

int S20 = 26;
int S21 = 27;
int S22 = 28;
int S23 = 29;

int IO21 = A3;
int IO22 = A4;
int IO23 = A5;

int OUTMD2 = 200; // Nonexistant pins, hardware pins tied to 5V
int IOS21 = 200;
int IOS22 = 200;
int IOS23 = 200;

MuxShield muxShield2(S20, S21, S22, S23, OUTMD2, IOS21, IOS22, IOS23, IO21, IO22, IO23);

// Define characters to signify beginning and end of transmission

#define START_MARKER '<'

#define END_MARKER '>'

#define MAX_MESSAGE_LENGTH 301

#define MUX_BOARD_PIN_COUNT 48

#define CHECKSUM_LENGTH 8


char receivedData[MAX_MESSAGE_LENGTH + 1];  // Extra space for the null terminator

char message[MAX_MESSAGE_LENGTH + 1];

unsigned int dataIndex = 0;

void setMuxShieldPins(char * receivedData);

void sendMessage(char * message);

bool serialReceive(void);

int verify_checksum(char * message);

void generate_checksum(char * message);

void toggle_outputs(int toggle);

void mux_shield_1_control(unsigned int relayNumber, int state);

void mux_shield_2_control(unsigned int relayNumber, int state);

int digitalReadPinsLength = sizeof(digitalReadPins)/sizeof(digitalReadPins[0]);

int analogReadPinsLength = sizeof(analogReadPins)/sizeof(analogReadPins[0]);


void setup() {

  //Set I/O 1, I/O 2, and I/O 3 as digital outputs
  muxShield1.setMode(1,DIGITAL_OUT);  
  muxShield1.setMode(2,DIGITAL_OUT);
  muxShield1.setMode(3,DIGITAL_OUT);

  muxShield2.setMode(1,DIGITAL_OUT);  
  muxShield2.setMode(2,DIGITAL_OUT);
  muxShield2.setMode(3,DIGITAL_OUT);
  
  for (int i = 0; i < digitalReadPinsLength; i++) {

    pinMode(digitalReadPins[i], digitalReadPinMode);

  }

  for (int i = 0; i < analogReadPinsLength; i++) {

    pinMode(analogReadPins[i], analogReadPinMode);

  }

    Serial.begin(460800);
}


void loop() {

  readPins(digitalReadPins, digitalReadPinsLength, analogReadPins, analogReadPinsLength, message);

  if (serialReceive()) {

    // Check if input pin states have been requested 

    if (receivedData[8] == '?') {

      // Send confirmation message to sender

      Serial.write("Validated\n");

      sendMessage(message);

    } else {

      setMuxShieldPins(receivedData);

      // Send confirmation message to sender

      Serial.write("Validated\n");

    }

  }
  
} 


void setMuxShieldPins(char * receivedData) {

    // Set MuxShield2 pins

    unsigned int received_data_length = strlen(receivedData);

    // Check if the control array is greater than the number of MuxShield2 pins, set pins to specified values

    if (received_data_length >= 96 + 8) {

      // Set first MuxShield2 pins

      for (unsigned int i = 8; i < 48 + 8; i++) {

        mux_shield_1_control(i - 7, receivedData[i] - '0');

      }

      // Set second MuxShield2 pins

      for (unsigned int i = 48; i < 96 + 8; i++) {

        mux_shield_2_control(i - 7, receivedData[i] - '0');

      }
      
    }

    // Check if the first MuxShield2 pins are all used, but the second's aren't, set pins to specified values

    if ((received_data_length > 48 + 8) && (received_data_length < 96 + 8)) {

      for (unsigned int i = 8; i < 48 + 8; i++) {

        mux_shield_1_control(i - 7, receivedData[i] - '0');

      }

      for (unsigned int i = 48; i < received_data_length; i++) {

        mux_shield_2_control(i - 7, receivedData[i] - '0');

      }

    }

    // Check if the first MuxShield's pins aren't all used, set pins to specified values

    if (received_data_length <= 48 + 8) {

      for (unsigned int i = 8; i < received_data_length; i++) {

        mux_shield_1_control(i - 7, receivedData[i] - '0');

      }

    }

}


void sendMessage(char * message) {

  // Populate the first 8 bytes of the outgoing transmission array with a checksum of the rest

  generate_checksum(message);

  // Transmit character that signifies start of transmission

  Serial.write('<');

  Serial.write(message);

  // Transmit character that signifies end of transmission

  Serial.write('>');

  Serial.write('\n');

}


// Read the values of digital and analog pins and write their values to a provided char array

void readPins(int* digitalReadPins, int digitalReadPinsLength, int* analogReadPins, int analogReadPinsLength, char* result) {

  // Start writing from the ninth character in the array (first eight characters will be occupied by the checksum)

  int index = 8;
  
  // Read each digital input pin and write a 1 to the array if HIGH, and 0 if LOW

  for (int i = 0; i < digitalReadPinsLength; i++) {

    int digitalPinValue = digitalRead(digitalReadPins[i]);

    result[index++] = (digitalPinValue == HIGH) ? '1' : '0';
  }

  // Read each analog input pin (returns a 10-bit binary number) and write its value to the array as a 0-padded decimal number, with each number seperated by a dash
  
  for (int j = 0; j < analogReadPinsLength; j++) {

    // Read the input pin

    int analogPinValue = analogRead(analogReadPins[j]);

    // Add a dash

    sprintf(result + index, "%c", '-');

    index += 1;

    // Write the  0-padded data to the result array

    sprintf(result + index, "%04d", analogPinValue);

    index += 4;

  }
  
  result[index] = '\0';  // Null-terminate the string

}


// Communicate via serial connection. Retuns 2 if checksum is verified

bool serialReceive() {

  unsigned int dataIndex = 0;

  while (Serial.available() > 0) { // Check if the serial buffer contains data, if not skips loop and returns false

    char receivedChar = Serial.read();

    if (receivedChar == START_MARKER) { // Check for transmission start

    // Start of reception

      while (true) { // Reads from the serial buffer until the end character is found, or the maxumum length is reached

        if (Serial.available() > 0) {

          receivedChar = Serial.read(); // Read a character from the serial buffer

          if (receivedChar == END_MARKER) { 
            
            // End of transmission:
            
            receivedData[dataIndex] = '\0';  // Null-terminate the data

            // Verify the checksum received in the leading 8 bytes of the transmission

            if (verify_checksum(receivedData) == 2) {

              return true;

            } else {

              Serial.write("ChecksumFailed\n");

              return false;
              
            }

          }

          // Reception ongoing:

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


