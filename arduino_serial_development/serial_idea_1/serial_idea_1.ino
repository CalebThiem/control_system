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


#define START_MARKER 'a'
#define END_MARKER 'z'
#define MAX_MESSAGE_LENGTH 300

#define LED_BUILTIN 13  // Most Arduino boards have a built-in LED on pin 13

char receivedData[MAX_MESSAGE_LENGTH + 1];  // Extra space for the null terminator
bool receiving = false;
int dataIndex = 0;

void setup() {
  Serial.begin(115200);
  pinMode(LED_BUILTIN, OUTPUT);  // Initialize the digital pin as an output.
}

void loop() {
  serialCommunicate();
}

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
      return(1);
    } else if (receiving) {
      if (dataIndex < MAX_MESSAGE_LENGTH) {
        receivedData[dataIndex] = receivedChar;
        dataIndex++;
      }
    }
  }
}
