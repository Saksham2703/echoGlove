#include <Arduino.h>

const int RGB_PIN = 48;
const int BUTTON_PIN = 4;
const unsigned long PRINT_INTERVAL_MS = 100;  // 10 Hz

int button_count = 0;
int last_button_state = HIGH;
unsigned long last_print_ms = 0;
unsigned long last_blink_ms = 0;
bool led_on = false;

void setup() {
  Serial.begin(115200);
  pinMode(BUTTON_PIN, INPUT);  // external pull-up wired; not INPUT_PULLUP
  while (!Serial && millis() < 3000) delay(10);
  Serial.println("{\"event\":\"boot\",\"phase\":0}");
}

void loop() {
  unsigned long now = millis();

  // Blink RGB LED at 1 Hz (blue = running, off = off)
  if (now - last_blink_ms >= 500) {
    led_on = !led_on;
    neopixelWrite(RGB_PIN, 0, 0, led_on ? 16 : 0);
    last_blink_ms = now;
  }

  // Detect button press (HIGH → LOW transition, active-low wiring)
  int state = digitalRead(BUTTON_PIN);
  if (last_button_state == HIGH && state == LOW) {
    button_count++;
    delay(20);  // crude debounce
  }
  last_button_state = state;

  // Emit one JSON line at 10 Hz
  if (now - last_print_ms >= PRINT_INTERVAL_MS) {
    Serial.print("{\"t_ms\":");
    Serial.print(now);
    Serial.print(",\"button_count\":");
    Serial.print(button_count);
    Serial.println("}");
    last_print_ms = now;
  }
}
