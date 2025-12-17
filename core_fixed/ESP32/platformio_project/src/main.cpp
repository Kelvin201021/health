#include <Arduino.h>

void setup() {
  Serial.begin(115200);     // REQUIRED
  delay(2000);              // Allow monitor to attach
  Serial.println("IMMEDIATE BOOT");
}

void loop() {
  Serial.println("ALIVE");
  delay(1000);
}