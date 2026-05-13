# Phase 0 — Fundamentals: Kickoff

## Goal

Stand up the EchoGlove dev environment end-to-end and prove the loop
hardware → firmware → USB serial → Python works on the Mac.

## Success criteria (from orchestration spec §6)

1. Onboard LED on ESP32-S3 blinks.
2. Pressing a breadboard-mounted button increments a counter printed over USB serial.
3. Python script on Mac reads the serial stream cleanly for 60 s.
4. One I²C sensor from the Freenove kit (MPU-6050) prints raw readings over the same channel.

## Hardware note

Phase 0 firmware targets the **ESP32-S3 DevKitC-1** (ordered as a 2-pack, item 5 of the BOM).
The Freenove kit's bundled board is **ESP32-WROVER-E** (original ESP32, not S3); it acts as
the source of sensors, the breadboard, jumpers, LEDs, and discretes. We don't flash the
WROVER board in Phase 0.

## Concept primer: I²C in 90 seconds

I²C ("Inter-Integrated Circuit") is a two-wire serial bus. It lets multiple sensor
chips share two pins on the microcontroller:

- **SDA** (Serial DAta): the data line.
- **SCL** (Serial CLock): the clock line, driven by the microcontroller (master).

Each sensor on the bus has a 7-bit address. The master sends "address + read/write
bit" first; only the sensor with that address responds. Two sensors with the same
address can't share a bus directly — that's why we need a TCA9548A mux in Phase 2.

I²C requires pull-up resistors on SDA and SCL (typically 4.7 kΩ to 3.3 V). Almost
every Adafruit/SparkFun breakout already includes these on-board; the Freenove
kit's MPU-6050 module will too. We won't need to add external pull-ups in Phase 0.

The MPU-6050 lives at I²C address `0x68` by default (`0x69` if the AD0 pin is tied
high). In Task 9 we'll scan the bus to confirm, then read its WHO_AM_I register
(`0x75`), which should return `0x68`.

## Concept primer: USB serial in 90 seconds

The ESP32-S3 has native USB. When you plug it into the Mac, macOS sees it as a
USB-CDC (Communications Device Class) device and exposes it as a file at
`/dev/tty.usbmodem*` (the exact suffix is per-board). Anything we write to
`Serial.println()` in firmware appears as bytes on that file. `pyserial` opens
the file and reads the bytes.

Baud rate (e.g. 115200) is the bit rate. Both ends must agree.

Our wire format is **newline-delimited JSON**: every firmware print is a complete
JSON object on its own line, e.g. `{"t_ms":105,"button_count":3}`. This is the
same line format the host uses through all later phases, so the Phase 0 reader
keeps working as we add more fields.

## Out of scope for Phase 0

- BNO055 / advanced IMU (Phase 1)
- VL6180X ToF / TCA9548A I²C mux (Phase 2)
- BLE / wireless (Phase 3)
- Permanent solder joints to sensors (Phase 3)
- Sensor fusion / Kalman filter / 3D viewer (Phase 4)
- CH-101 ultrasonic (Phase 5+)
