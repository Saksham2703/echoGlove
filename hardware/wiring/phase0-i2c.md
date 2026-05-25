# Phase 0 — I²C sensor wiring (MPU-6050)

## Bill of materials
- 1× MPU-6050 GY-521 breakout (from Freenove kit)
- 4× M/M jumper wires
- existing breadboard from Task 6 (button stays wired)

## Pin assignment

| MPU-6050 pin | ESP32-S3 pin |
|---|---|
| VCC | 3V3 |
| GND | GND |
| SCL | GPIO 9 |
| SDA | GPIO 8 |

INT, AD0, XCL, XDA — left unconnected.

## I²C address
- MPU-6050 default: `0x68` (AD0 pin floating/low on the GY-521 breakout).
- Confirmed via I²C scan at boot.

## Pull-up resistors
- The GY-521 breakout includes onboard 4.7 kΩ pull-ups on SDA and SCL.
- No external pull-ups needed.

## Notes
- GPIO 8/9 are the ESP32-S3 DevKitC-1 default I²C pins for the Wire library.
- The sensor is 3.3 V only — do not connect VCC to the 5 V pin.
- Raw gyro readings show ~300 LSB zero-rate offset at rest — normal MPU-6050
  behavior. Phase 1 (BNO055) replaces this with on-chip sensor fusion.
