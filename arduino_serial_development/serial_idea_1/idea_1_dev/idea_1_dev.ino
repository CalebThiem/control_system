#define START_MARKER 'a'
#define END_MARKER 'z'
#define MAX_MESSAGE_LENGTH 150
#define LED_PIN 13

char receivedData[MAX_MESSAGE_LENGTH + 1];  // Extra space for the null terminator
bool receiving = false;
int dataIndex = 0;

void setup() {
  Serial.begin(115200);
  pinMode(LED_PIN, OUTPUT);
}

void loop() {
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
    } else if (receiving) {
      if (dataIndex < MAX_MESSAGE_LENGTH) {
        receivedData[dataIndex] = receivedChar;
        dataIndex++;
      }
    }
  }

  if (Serial.find("Proceed")) {
    for (int i = 0; i < 50; i++) {
      digitalWrite(LED_PIN, HIGH);
      delay(10);
      digitalWrite(LED_PIN, LOW);
      delay(10);
    }
  }
}
