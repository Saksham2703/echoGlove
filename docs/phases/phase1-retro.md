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
- How quiet a wrong graphics program is. The black window threw no error, no warning, no failed assertion — `gluPerspective` landed on the wrong matrix stack and OpenGL happily rendered nothing.
- Calibration is not a step you complete. `cal_sys` drifts around on its own, and the accelerometer wanted six deliberate orientations before it moved off zero. Also it may be `3` but fluctuate but it doesn't mean its uncalibrated now. It's still calibrated and usable.

## What felt rote / I'd skim next time
- Wiring a STEMMA/Qwiic-class I²C breakout. Vin/GND/SDA/SCL is the same four wires every time now; the only real question is the address.

## What I want more depth on in Phase 2
- What the fusion is actually doing. Phase 1 consumed a quaternion as a black box; I'd like to understand the filter well enough to know when to distrust its output. (There is already a parked entry for a DIY fusion exercise.)
- Driving the TCA9548A directly with `Wire.write(1 << channel)` — no library, so this is the first time reading a datasheet and writing the register transaction myself.

## Time spent
- Calendar: 2026-05-24 (spec written) → 2026-09-20 (shipped), ~4 months, almost all of it an idle gap rather than work.
- Active hours: ~6 hours

## Costs
- BNO055 (Amazon B017PEIGIG): ~$35. No other Phase 1 spend.

## Anything for the parking lot
- Already parked this phase: the VL6180X range claim in `bom-phase2.md` (documented 5–200 mm vs ~5–100 mm reliable) — to be settled by measuring actual fingertip geometry during the Phase 2 brainstorm.
