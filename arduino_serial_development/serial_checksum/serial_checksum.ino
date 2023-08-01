#define START_MARKER 'a'
#define END_MARKER 'z'
#define MAX_MESSAGE_LENGTH 152

char receivedData[MAX_MESSAGE_LENGTH + 3];  // Extra space for the checksum and lead/end characters
char pinArray[MAX_MESSAGE_LENGTH + 1];
uint8_t receivedChecksum;
unsigned int convertLastTwoCharsToHex(char* str);
bool receiving = false;
int dataIndex = 0;

void setup() {
  Serial.begin(115200);
}

void loop() {
  while (Serial.available() > 0) {
    char receivedChar = Serial.read();

    if (receivedChar == START_MARKER) {
      receiving = true;
      dataIndex = 0;
    } else if (receivedChar == END_MARKER) {
      receiving = false;
      receivedChecksum = convertLastTwoCharsToHex(receivedData);
      receivedData[dataIndex] = '\0';  // Null-terminate the data
      strncpy(pinArray, receivedData, MAX_MESSAGE_LENGTH -2);
      uint8_t calculatedChecksum = calculateChecksum(pinArray);
      // Serial.write(pinArray);
      // Serial.write("\n");
      if (calculatedChecksum == receivedChecksum) {
        Serial.write("valid\n");
        // Serial.print("Arduino: Checksum Valid\n");
      } else {
        Serial.write("error\n");
        // Serial.print("Error: Invalid data or checksum\n");
      }
      // Serial.print("Arduino Received data: ");
      // Serial.println(receivedData);
      // Serial.print("Arduino pinArray data: ");
      // Serial.println(pinArray);
      // Serial.print("Arduino checksum data: ");
      // Serial.println(receivedChecksum, HEX);
      // Serial.print("Arduino Calculated checksum: ");
      // Serial.println(calculatedChecksum, HEX);
    } else if (receiving) {
      if (dataIndex < MAX_MESSAGE_LENGTH + 2) {
        receivedData[dataIndex] = receivedChar;
        dataIndex++;
      }
    }
  }
}

uint8_t calculateChecksum(char* data) {
  uint8_t crc = 0;
  // Serial.print(strlen(pinArray));
  for (int i = 0; i < strlen(pinArray); i++) {
    crc ^= data[i];
    for (int j = 0; j < 8; j++) {
      if (crc & 0x80) {
        crc = (crc << 1) ^ 0x07;
      } else {
        crc <<= 1;
      }
    }
    // Serial.print("Intermediate checksum: ");
    
  }
  // Serial.println(crc, HEX);
  return crc;
}

unsigned int convertLastTwoCharsToHex(char* str) {
    // Length of the input string
    int len = strlen(str);

    // Check if string length is less than 2
    if (len < 2) {
        printf("Error: The string length should be at least 2.\n");
        exit(1);
    }

    // Take the last two characters
    char lastTwoChars[3];
    lastTwoChars[0] = str[len-2];
    lastTwoChars[1] = str[len-1];
    lastTwoChars[2] = '\0'; // Null-terminate the new string

    // Convert the last two characters to hexadecimal
    unsigned int hex;
    sscanf(lastTwoChars, "%02x", &hex);

    return hex;
}
