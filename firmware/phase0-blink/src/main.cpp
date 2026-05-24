#include <Arduino.h>

// ESP32-S3 DevKitC-1 has a WS2812 RGB LED on GPIO 48.
// neopixelWrite() is built into the Arduino ESP32 framework — no extra library.
const int RGB_PIN = 48;

void setup()
{
  // Nothing to init for neopixelWrite.
}

void loop()
{
  neopixelWrite(RGB_PIN, 32, 0, 0); // dim blue ON
  delay(500);
  neopixelWrite(RGB_PIN, 0, 32, 0); // off
  delay(1000);
  neopixelWrite(RGB_PIN, 0, 0, 32); // off
  delay(500);
}
