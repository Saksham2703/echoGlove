# Phase 1 retrospective

## What was built
- BNO055 (Adafruit #2472) 6-pin header soldered; all joints continuity-checked,
  adjacent pairs verified silent.
- Sensor wired to ESP32-S3 DevKitC-1: Vin→3V3, GND→GND, SDA→GPIO 8, SCL→GPIO 9.
  3Vo, RST and the whole 4-hole row left open; ADR floating gives address 0x28.
- `firmware/phase1-imu/` streaming quaternions + calibration status as JSON
  lines at 100 Hz, using `OPERATION_MODE_NDOF` and `bno.getQuat()`.
- `platformio.ini` Adafruit library versions pinned exactly (no caret ranges).
- `host/src/echoglove/viewer.py` fixed: projection matrix stack, and the
  duplicated rotation. Edges now colored per body axis with an axis triad.
- `hardware/wiring/phase1-imu.md` corrected — the BNO055 has two header rows on
  opposite edges, not one 6-pin row as originally documented.

## Verification against spec §6

| Criterion | Result |
|---|---|
| BNO055 quaternion stream @ 100 Hz over USB | **PASS** — V1: 99.8 Hz (999 samples / 10.01 s). Sustained 100.0 Hz across the 300 s V3 run. |
| Python wireframe-cube viewer rotates to match real hand rotation | **PASS** — V2 manual: all three axes track 1:1 and independently. |
| No quaternion glitches or jumps over 5 min continuous use | **PASS** — V3: 29,998/29,998 consecutive pairs at \|dot\| ≥ 0.99, under live hand movement. |

Timing jitter was zero: all 5999 intervals in a separate 60 s capture measured
exactly 10 ms.

## Bugs found and fixed
1. `lib_deps` caret ranges let three Adafruit libraries drift over the 4-month
   gap. Pinned exactly.
2. `hardware/wiring/phase1-imu.md` described a single 6-pin row with the wrong
   pin names. Caught by photographing the silkscreen before cutting the header.
3. `viewer.py` — `gluPerspective` on the modelview stack, so the window
   rendered black.
4. `viewer.py` — rotation applied twice, so the cube moved 2× the board.

## What surprised me
<!-- TODO: fill in -->

## What felt rote / I'd skim next time
<!-- TODO: fill in -->

## What I want more depth on in Phase 2
<!-- TODO: fill in -->

## Time spent
<!-- TODO: calendar span and active hours -->

## Costs
- BNO055 (Amazon B017PEIGIG): ~$35. No other Phase 1 spend.

## Anything for the parking lot
<!-- TODO: fill in, or leave empty -->
