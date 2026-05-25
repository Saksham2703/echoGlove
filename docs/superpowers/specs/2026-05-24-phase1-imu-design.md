# EchoGlove Phase 1 — IMU Bring-Up Design

**Date:** 2026-05-24
**Status:** Approved
**Author:** Saksham Jain (with Claude)
**Phase:** 1 — IMU bring-up (follows Phase 0 — Fundamentals)

---

## 1. Goal

Stream BNO055 absolute orientation quaternions at 100 Hz over USB serial and display them as a live rotating wireframe cube in a Python viewer on the Mac. This is the orientation-only hand viewer that underpins all downstream phases.

**Phase ships when all three verification criteria pass (§6).**

---

## 2. Bill of Materials

| Item | Part | Source | Est. price |
|---|---|---|---|
| IMU breakout | [Adafruit BNO055 Absolute Orientation Sensor #2472](https://www.amazon.com/Adafruit-Absolute-Orientation-Fusion-Breakout/dp/B017PEIGIG) | Amazon | ~$35 |

**Notes:**
- Runs on 3.3 V, direct I²C connection to ESP32-S3 — no level shifter needed.
- Default I²C address `0x28` (Adafruit pulls ADR low).
- Ships with headers unsoldered — first real soldering use on actual hardware. Photo wiring before first power-on; Claude sanity-checks.
- No spare budgeted; BNO055 is robust and wiring is simple.

**Phase 1 budget:** ~$35. Slightly above the $15–30 estimate in the orchestration doc; acceptable given Adafruit quality vs. clone risk.

---

## 3. Hardware wiring

Same I²C bus as Phase 0:

| BNO055 pin | ESP32-S3 pin |
|---|---|
| VIN | 3.3 V |
| GND | GND |
| SDA | GPIO 8 |
| SCL | GPIO 9 |
| ADR | (leave unconnected — floats low → address 0x28) |
| INT | (not connected in Phase 1) |

Wiring diagram saved to `hardware/wiring/phase1-imu.md` (created during kickoff).

---

## 4. Firmware

**Project:** `firmware/phase1-imu/` — self-contained PlatformIO project.

**Board / framework:** `esp32-s3-devkitc-1`, Arduino framework. Same toolchain as Phase 0.

**Libraries (pinned in `platformio.ini`):**
- `Adafruit BNO055`
- `Adafruit Unified Sensor` (dependency)

### 4.1 Initialization

```
Wire.begin(SDA=8, SCL=9)
bno.begin()
bno.setMode(OPERATION_MODE_NDOF)
Serial.begin(115200)
```

`OPERATION_MODE_NDOF` — 9-DOF absolute fusion mode. The BNO055's internal DSP fuses accelerometer + gyroscope + magnetometer and outputs calibrated quaternions directly. The host never sees raw sensor data in this mode.

### 4.2 Main loop (polled timer, 100 Hz)

```
every 10 ms (millis() timer):
  read imu::Quaternion q from BNO055
  emit: {"t_ms":<millis>,"w":<q.w>,"x":<q.x>,"y":<q.y>,"z":<q.z>}
```

No blocking delays in loop. Timer check via `millis()` — same pattern as Phase 0.

### 4.3 Heartbeat

1 Hz RGB LED blink (blue) on GPIO 48 via `neopixelWrite` — board is alive indicator.

### 4.4 Fill-in-the-blank sections (intentional learning gaps)

The firmware skeleton shipped in the kickoff doc leaves two blanks for the student to fill in:
1. The BNO055 operating mode constant passed to `setMode()`.
2. The library call to read the quaternion and the struct field names (`q.w`, `q.x`, etc.).

The kickoff doc explains what each blank does and where to find the answer in the Adafruit library source.

### 4.5 Interrupt-driven reads (concept only)

The kickoff doc explains the INT pin approach as a stretch concept — how to configure the data-ready interrupt register and write an ISR. No INT pin wiring is required for Phase 1 verification.

---

## 5. Host architecture

### 5.1 New files

```
host/src/echoglove/
    imu_reader.py          # quaternion extraction from serial stream
    viewer.py              # pygame + PyOpenGL wireframe-cube renderer
host/tests/
    test_imu_reader.py     # unit tests, no hardware
```

### 5.2 `imu_reader.py`

**`parse_quaternion(d: dict) -> tuple[float, float, float, float]`**
Validates that `d` contains keys `w`, `x`, `y`, `z`. Returns `(w, x, y, z)`. Raises `ParseError` (re-exported from `serial_reader`) on missing keys or non-numeric values.

**`quaternion_stream(port: str, baud: int = 115200) -> Iterator[tuple]`**
Wraps `stream_port()`. Skips lines that lack quaternion keys (boot events, scan events, etc.). Calls `parse_quaternion` on matching lines and yields the result.

### 5.3 `viewer.py`

**`SerialReaderThread`** (daemon thread):
- Runs `quaternion_stream()` in a background thread.
- Pushes quaternion tuples into a `queue.Queue(maxsize=10)`.
- On queue full: drains one entry with `get_nowait()` before putting (viewer always shows latest pose, never builds lag).
- Stopped via a threading `Event` on viewer exit.

**`run_viewer(port: str, baud: int = 115200)`**:
1. `pygame.init()` + OpenGL context setup (perspective projection, depth test).
2. Start `SerialReaderThread`.
3. Main loop at ~60 fps:
   - Drain queue; keep the most recently received quaternion.
   - Convert quaternion `(w,x,y,z)` → 3×3 rotation matrix (via numpy).
   - Apply rotation to the 8 unit-cube vertices.
   - Draw 12 edges with `GL_LINES`.
   - `pygame.display.flip()`.
4. On window close or `KeyboardInterrupt`: stop thread, `pygame.quit()`, exit cleanly.

**Entry point:** `python -m echoglove.viewer /dev/tty.usbmodemXXXX`

### 5.4 New dependencies

Added to `host/pyproject.toml`:

```
pygame >= 2.5
PyOpenGL >= 3.1
numpy >= 1.26
```

### 5.5 Tests

`test_imu_reader.py` covers:
- `parse_quaternion` with a valid dict → correct tuple.
- `parse_quaternion` with a missing key → `ParseError`.
- `quaternion_stream` with a mix of quaternion and non-quaternion dicts → only quaternion lines yielded.

`viewer.py` is not unit-tested (requires display + hardware). Verified manually per V2 criterion.

---

## 6. Verification criteria

| # | Criterion | Pass condition |
|---|---|---|
| V1 | BNO055 quaternion stream at 100 Hz | Automated: count lines over 10 s, average ≥ 95 Hz |
| V2 | Wireframe-cube viewer tracks real hand rotation | Manual: tilt board in all axes, cube follows with no visible lag |
| V3 | No quaternion glitches over 5 min | Automated: record 5 min, assert `dot(q_n, q_{n+1}) > 0.99` for all consecutive pairs |

**Pre-verification step (required before V2/V3):** perform BNO055 magnetometer calibration — move the board in a figure-8 pattern until all four calibration status bytes (sys, gyro, accel, mag) read 3. The firmware reports calibration status on each JSON line during a calibration mode (added to kickoff firmware as a diagnostic, not the main 100 Hz loop).

**Not a pass/fail criterion in Phase 1:** absolute heading accuracy, magnetometer drift under interference. Tracked in parking lot for Phase 2+.

---

## 7. Concept primer topics (in kickoff doc)

1. **Quaternions** — why Euler angles have gimbal lock; what `(w, x, y, z)` means geometrically; the quaternion → rotation matrix formula. Kept practical: enough to read and write the viewer code.
2. **On-chip sensor fusion** — what NDOF mode does internally (Bosch BSX algorithm, behaviorally similar to Madgwick/Mahony); why the magnetometer provides absolute heading while gyro+accel provide dynamic stability; what happens if you skip magnetometer calibration.
3. **Interrupt vs polled reads** — concept explanation with pseudocode showing INT pin configuration and ISR structure. No hardware change required. Stretch exercise for the curious.

---

## 8. File layout after Phase 1

```
firmware/
    phase1-imu/              ← new PlatformIO project
        platformio.ini
        src/main.cpp
host/src/echoglove/
    serial_reader.py         ← unchanged from Phase 0
    imu_reader.py            ← new
    viewer.py                ← new
host/tests/
    test_serial_reader.py    ← unchanged
    test_imu_reader.py       ← new
hardware/
    bom-phase1.md            ← new
    wiring/
        phase1-imu.md        ← new
docs/phases/
    phase1-kickoff.md        ← new
    phase1-retro.md          ← written at phase end
```

---

## 9. Out of scope for Phase 1

- Magnetometer calibration as a formal verification step (parking lot → Phase 2+).
- Absolute heading accuracy.
- Multiple IMUs.
- BLE transport (Phase 3).
- 3D hand rig (Phase 4).
- Interrupt-driven reads as implemented hardware (concept only).

---

**End of design.**
