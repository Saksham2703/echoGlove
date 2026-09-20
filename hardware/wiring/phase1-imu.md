# Wiring — Phase 1: BNO055 IMU

## Before wiring: solder the header
The Adafruit BNO055 (#2472) ships without headers soldered. It has **two
separate header rows on opposite edges**:

- **6-hole row:** `Vin · 3Vo · GND · SDA · SCL · RST`
- **4-hole row:** `PS0 · PS1 · INT · ADR`

Phase 1 only needs the **6-hole row** — VIN, GND, SDA and SCL all live there.
Solder a 6-pin male header into that row. The 4-hole row is left unsoldered;
ADR and INT are unused in Phase 1 (see the table below), and that row can be
added later without disturbing the first, since it is on the opposite edge.

Technique: use a breadboard as a jig — push the header in long-pins-down, drop
the BNO055 over the short stubs, solder on the top face. Iron at 330 °C, tip
touching pad and pin together, feed solder to the far side of the joint, 2–3 s.
Tack the two end pins first and check the board is sitting square before doing
the middle four. Check each joint with the multimeter in continuity mode
before wiring — and check adjacent pins do *not* beep, to rule out bridges.

## Pin connections

| BNO055 pin | ESP32-S3 DevKitC-1 pin | Notes |
|---|---|---|
| VIN | 3V3 | 3.3 V only — never 5 V |
| GND | GND | any GND rail |
| SDA | GPIO 8 | same bus as Phase 0 (was MPU-6050) |
| SCL | GPIO 9 | same bus as Phase 0 |
| ADR | (leave open) | on the 4-hole row; floats low → address 0x28 |
| INT | (leave open) | on the 4-hole row; not used in Phase 1 |
| 3Vo | (leave open) | regulator **output**, not an input — connect nothing |
| RST | (leave open) | not used in Phase 1 |

## ASCII diagram

```
BNO055 (Adafruit #2472)            ESP32-S3 DevKitC-1
                                   ┌──────────────────────┐
  4-hole row (NOT soldered)        │                      │
  ┌────────────────────┐           │                      │
  │ PS0  PS1  INT  ADR │           │                      │
  ├────────────────────┤           │                      │
  │                    │           │                      │
  │   [ BNO055 chip ]  │           │                      │
  │                    │           │                      │
  ├────────────────────┤           │                      │
  │ Vin ───────────────┼───────────┼─ 3V3                 │
  │ 3Vo   (leave open) │           │                      │
  │ GND ───────────────┼───────────┼─ GND                 │
  │ SDA ───────────────┼───────────┼─ GPIO 8 (SDA)        │
  │ SCL ───────────────┼───────────┼─ GPIO 9 (SCL)        │
  │ RST   (leave open) │           │                      │
  └────────────────────┘           └──────────────────────┘
  6-hole row (solder this one)
```

## Safety checklist (before first power-on)
1. Confirm VIN → 3V3 (not 5V or VBUS).
2. Confirm GND connected.
3. Multimeter continuity: VIN pin to ESP32 3V3 pin — beep.
4. Multimeter continuity: GND pin to GND rail — beep.
5. No stray solder bridges on BNO055 header (inspect with good light).
6. **Photo the breadboard and paste to Claude for sanity-check before powering on.**
