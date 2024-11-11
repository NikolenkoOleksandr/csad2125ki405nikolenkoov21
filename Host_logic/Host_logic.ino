void setup() {
  Serial.begin(115200);
}

void loop() {
  if (Serial.available() > 0) {
    String buffer = Serial.readStringUntil('\n');  //змінна що зчитує дані з serial монітора 
    buffer += " - Modified by server";
    Serial.println(buffer);
  }
}
