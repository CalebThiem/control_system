int high[250];

void setup()
{
  Serial.begin(115200);
  Serial.setTimeout(1);
}

void loop()
{
  while (Serial.available() != 0)
}