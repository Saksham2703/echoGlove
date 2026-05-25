# Wiring — Phase 1: BNO055 IMU

## Before wiring: solder the header
The Adafruit BNO055 ships without headers soldered. Solder a 6-pin male header
into the holes labelled VIN, GND, SDA, SCL, ADR, INT. Tip: clip the board into
helping hands, apply flux, heat pad + pin together for 2–3 s, flow solder.
Check each joint with the multimeter continuity mode before wiring.

## Pin connections

| BNO055 pin | ESP32-S3 DevKitC-1 pin | Notes |
|---|---|---|
| VIN | 3V3 | 3.3 V only — never 5 V |
| GND | GND | any GND rail |
| SDA | GPIO 8 | same bus as Phase 0 (was MPU-6050) |
| SCL | GPIO 9 | same bus as Phase 0 |
| ADR | (leave open) | floats low → address 0x28 |
| INT | (leave open) | not used in Phase 1 |

## ASCII diagram

```
BNO055 (Adafruit #2472)            ESP32-S3 DevKitC-1
┌──────────────────────┐           ┌──────────────────────┐
│ VIN ─────────────────┼───────────┼─ 3V3                 │
│ GND ─────────────────┼───────────┼─ GND                 │
│ SDA ─────────────────┼───────────┼─ GPIO 8 (SDA)        │
│ SCL ─────────────────┼───────────┼─ GPIO 9 (SCL)        │
│ ADR  (leave open)    │           │                      │
│ INT  (leave open)    │           │                      │
└──────────────────────┘           └──────────────────────┘
```

## Safety checklist (before first power-on)
1. Confirm VIN → 3V3 (not 5V or VBUS).
2. Confirm GND connected.
3. Multimeter continuity: VIN pin to ESP32 3V3 pin — beep.
4. Multimeter continuity: GND pin to GND rail — beep.
5. No stray solder bridges on BNO055 header (inspect with good light).
6. **Photo the breadboard and paste to Claude for sanity-check before powering on.**
