#include <Arduino.h>
#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BNO055.h>
#include <utility/imumaths.h>

const int RGB_PIN = 48;
const int SDA_PIN = 8;
const int SCL_PIN = 9;
const unsigned long PRINT_INTERVAL_MS = 10;  // 100 Hz

Adafruit_BNO055 bno = Adafruit_BNO055(55, 0x28, &Wire);

unsigned long last_print_ms = 0;
unsigned long last_blink_ms = 0;
bool led_on = false;

void setup() {
  Serial.begin(115200);
  while (!Serial && millis() < 3000) delay(10);
  Wire.begin(SDA_PIN, SCL_PIN);

  // FILL IN: pass OPERATION_MODE_NDOF as the mode argument to begin().
  // Hint: look in Adafruit_BNO055.h for the adafruit_bno055_opmode_t enum.
  // Kickoff doc §Fill-in-the-blank guide has more detail.
  if (!bno.begin(/* YOUR_MODE_CONSTANT_HERE */)) {
    Serial.println("{\"event\":\"error\",\"msg\":\"BNO055 not found\"}");
    while (true) delay(100);
  }

  delay(100);  // let mode switch settle
  Serial.println("{\"event\":\"boot\",\"phase\":1}");
}

void loop() {
  unsigned long now = millis();

  // Blink RGB LED at 1 Hz (blue = running)
  if (now - last_blink_ms >= 500) {
    led_on = !led_on;
    neopixelWrite(RGB_PIN, 0, 0, led_on ? 16 : 0);
    last_blink_ms = now;
  }

  if (now - last_print_ms >= PRINT_INTERVAL_MS) {
    // FILL IN: call bno.getQuat() and assign to q.
    // Hint: return type is imu::Quaternion; access fields as q.w(), q.x(), etc.
    // Kickoff doc §Fill-in-the-blank guide has more detail.
    imu::Quaternion q = /* YOUR_READ_CALL_HERE */;

    uint8_t sys, gyro, accel, mag;
    bno.getCalibration(&sys, &gyro, &accel, &mag);

    Serial.print("{\"t_ms\":");
    Serial.print(now);
    Serial.print(",\"w\":"); Serial.print(q.w(), 6);
    Serial.print(",\"x\":"); Serial.print(q.x(), 6);
    Serial.print(",\"y\":"); Serial.print(q.y(), 6);
    Serial.print(",\"z\":"); Serial.print(q.z(), 6);
    Serial.print(",\"cal_sys\":"); Serial.print(sys);
    Serial.print(",\"cal_gyro\":"); Serial.print(gyro);
    Serial.print(",\"cal_accel\":"); Serial.print(accel);
    Serial.print(",\"cal_mag\":"); Serial.print(mag);
    Serial.println("}");

    last_print_ms = now;
  }
}
