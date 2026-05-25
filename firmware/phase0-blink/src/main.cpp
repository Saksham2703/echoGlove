#include <Arduino.h>
#include <Wire.h>

const int RGB_PIN = 48;
const int BUTTON_PIN = 4;
const int SDA_PIN = 8;
const int SCL_PIN = 9;
const uint8_t MPU_ADDR = 0x68;
const unsigned long PRINT_INTERVAL_MS = 100;  // 10 Hz

int button_count = 0;
int last_button_state = HIGH;
unsigned long last_print_ms = 0;
unsigned long last_blink_ms = 0;
bool led_on = false;

void i2c_scan() {
  Serial.println("{\"event\":\"i2c_scan_begin\"}");
  for (uint8_t addr = 1; addr < 127; addr++) {
    Wire.beginTransmission(addr);
    if (Wire.endTransmission() == 0) {
      Serial.print("{\"event\":\"i2c_found\",\"addr\":\"0x");
      Serial.print(addr, HEX);
      Serial.println("\"}");
    }
  }
  Serial.println("{\"event\":\"i2c_scan_end\"}");
}

void mpu_init() {
  // Wake MPU-6050 from sleep: write 0 to PWR_MGMT_1 (reg 0x6B).
  Wire.beginTransmission(MPU_ADDR);
  Wire.write(0x6B);
  Wire.write(0);
  Wire.endTransmission(true);
}

void mpu_read_and_print() {
  Wire.beginTransmission(MPU_ADDR);
  Wire.write(0x3B);  // start of accel registers
  Wire.endTransmission(false);
  Wire.requestFrom(MPU_ADDR, (uint8_t)14);  // 6 accel + 2 temp + 6 gyro

  int16_t ax = (Wire.read() << 8) | Wire.read();
  int16_t ay = (Wire.read() << 8) | Wire.read();
  int16_t az = (Wire.read() << 8) | Wire.read();
  int16_t temp = (Wire.read() << 8) | Wire.read();
  int16_t gx = (Wire.read() << 8) | Wire.read();
  int16_t gy = (Wire.read() << 8) | Wire.read();
  int16_t gz = (Wire.read() << 8) | Wire.read();
  (void)temp;  // not reported yet

  Serial.print("{\"t_ms\":");
  Serial.print(millis());
  Serial.print(",\"button_count\":");
  Serial.print(button_count);
  Serial.print(",\"ax\":");  Serial.print(ax);
  Serial.print(",\"ay\":");  Serial.print(ay);
  Serial.print(",\"az\":");  Serial.print(az);
  Serial.print(",\"gx\":");  Serial.print(gx);
  Serial.print(",\"gy\":");  Serial.print(gy);
  Serial.print(",\"gz\":");  Serial.print(gz);
  Serial.println("}");
}

void setup() {
  Serial.begin(115200);
  pinMode(BUTTON_PIN, INPUT);  // external pull-up wired; not INPUT_PULLUP
  while (!Serial && millis() < 3000) delay(10);

  Wire.begin(SDA_PIN, SCL_PIN);
  Serial.println("{\"event\":\"boot\",\"phase\":0}");
  i2c_scan();
  mpu_init();
  Serial.println("{\"event\":\"mpu_ready\"}");
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
    mpu_read_and_print();
    last_print_ms = now;
  }
}
