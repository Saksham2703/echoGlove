# Phase 1 kickoff — IMU bring-up

**Goal:** BNO055 quaternion stream at 100 Hz over USB serial.
Python wireframe-cube viewer rotates to match real hand rotation.

**Verification:** see Phase 1 design spec §6 (`docs/superpowers/specs/2026-05-24-phase1-imu-design.md`).

---

## Concept primer: Quaternions

### Why not Euler angles?

Euler angles (roll, pitch, yaw) are intuitive but have a fatal flaw: **gimbal lock**.
When two rotation axes align, you lose a degree of freedom — the sensor can't
distinguish rotations around the aligned axes. This causes jitter and discontinuities
near certain orientations (e.g. looking straight up or straight down).

Try it mentally: tilt your hand 90° forward (pitch = 90°). Now try to roll it.
Depending on how you define the axes, "roll" and "yaw" collapse into the same
physical rotation. That's gimbal lock.

Quaternions avoid this by representing rotation as a **single axis + angle**, encoded
as four numbers:

```
q = w + xi + yj + zk
```

Where:
- `w` is the scalar part: `cos(θ/2)`, where θ is the rotation angle
- `(x, y, z)` is the vector part: `sin(θ/2) × (axis_x, axis_y, axis_z)`
- Unit quaternion constraint: `w² + x² + y² + z² = 1`

You don't need to deeply understand the algebra to use them. What matters:

1. A quaternion describes a complete 3D orientation without ambiguity.
2. No gimbal lock — ever.
3. You can convert a quaternion to a 3×3 rotation matrix to apply it to 3D points.

### Quaternion → rotation matrix

Given unit quaternion `(w, x, y, z)`, the rotation matrix R is:

```
R = [ 1-2(y²+z²)    2(xy-zw)     2(xz+yw) ]
    [  2(xy+zw)   1-2(x²+z²)     2(yz-xw) ]
    [  2(xz-yw)    2(yz+xw)   1-2(x²+y²)  ]
```

To rotate a 3D point `p`, compute `R @ p` (matrix-vector multiply).
The viewer does this for all 8 cube vertices on every frame.

### Sanity check: identity quaternion

`(w=1, x=0, y=0, z=0)` means "no rotation". Plug it into the formula above
and R becomes the identity matrix. When the board is flat and level, the BNO055
should output values close to this.

---

## Concept primer: On-chip sensor fusion (NDOF mode)

The BNO055 has three sensors on one chip:

| Sensor | Measures | Weakness |
|---|---|---|
| Accelerometer | Gravity + linear acceleration | Noisy; affected by vibration |
| Gyroscope | Angular velocity (how fast rotating) | Drifts over time (integrated error) |
| Magnetometer | Earth's magnetic field (absolute heading) | Sensitive to nearby metal/electronics |

No single sensor gives reliable absolute orientation. Fusion combines all three to
cancel each sensor's weakness:

- Gyroscope gives fast, smooth rotation tracking — but drifts minutes-scale.
- Accelerometer corrects gyro drift for pitch/roll via gravity reference.
- Magnetometer corrects gyro drift for yaw (heading) via magnetic North reference.

**`OPERATION_MODE_NDOF`** (Nine Degrees Of Freedom) is Bosch's proprietary fusion
mode. The BNO055's internal DSP runs a fusion algorithm (structurally similar to
Mahony/Madgwick) and outputs a calibrated quaternion directly. You call `getQuat()`
and receive a stable, drift-corrected orientation — the raw sensor data never
leaves the chip in this mode.

### Magnetometer calibration

Before the fusion fully converges, absolute heading (yaw) is unreliable. To
calibrate:

1. Power on the board and open the serial monitor.
2. Watch the `cal_mag` field in the JSON output. It starts at 0.
3. Move the board slowly in a **figure-8 pattern** for 10–20 seconds.
4. When `cal_mag == 3` and `cal_sys == 3`, calibration is complete.

Relative rotation (tilt left/right/forward/back) works immediately even without
calibration. Absolute magnetic heading needs `cal_mag == 3`.

**Note:** calibration is lost on power-cycle. The BNO055 has a feature to save
calibration offsets to its registers and restore them — this is a Phase 2+ stretch
task (see parking lot).

---

## Concept primer: Interrupt vs polled reads (stretch — no hardware required)

**Polled (what Phase 1 uses):** The main loop checks `millis()` on every iteration.
When 10 ms have passed, it reads the sensor. Simple, reliable, introduces up to
±1 ms of timing jitter (one loop iteration). Fine for 100 Hz.

**Interrupt-driven:** The BNO055 has an `INT` pin that goes HIGH when a new sample
is ready. You wire INT to a spare GPIO and attach an ISR:

```cpp
volatile bool data_ready = false;

void IRAM_ATTR bno_isr() {
    data_ready = true;  // set flag in ISR — never do I²C here
}

void setup() {
    // INT_PIN is whichever GPIO you wired BNO055 INT to
    attachInterrupt(digitalPinToInterrupt(INT_PIN), bno_isr, RISING);
}

void loop() {
    if (data_ready) {
        data_ready = false;
        imu::Quaternion q = bno.getQuat();  // read safely in loop, not in ISR
        // ... emit JSON
    }
}
```

Why bother? The sample happens at the exact moment the sensor signals readiness,
not up to 1 ms later. This matters when you need precise per-sample timestamps
(e.g. for a Kalman filter that uses dt between samples). For Phase 1 the polled
approach is sufficient.

The INT pin wiring is available as a stretch task once hardware arrives:
wire BNO055 INT → any spare GPIO, then swap the polled timer for the ISR above.

---

## Fill-in-the-blank guide

Two blanks are left in `firmware/phase1-imu/src/main.cpp` for you to fill in
before flashing. The skeleton will not compile until both are filled correctly.

### Blank 1: BNO055 operating mode

Find this line in `main.cpp`:

```cpp
if (!bno.begin(/* YOUR_MODE_CONSTANT_HERE */)) {
```

Look in the Adafruit BNO055 library header (`Adafruit_BNO055.h`) for the enum
`adafruit_bno055_opmode_t`. Find the constant that means "9-DOF absolute
orientation fusion mode". It starts with `OPERATION_MODE_`.

You can find the header at:
`~/.platformio/packages/framework-arduinoespressif32/` (after first build) or
search for `adafruit_bno055_opmode_t` in your editor.

> **Answer (try before reading):** `OPERATION_MODE_NDOF`

### Blank 2: Read the quaternion

Find this line in `main.cpp`:

```cpp
imu::Quaternion q = /* YOUR_READ_CALL_HERE */;
```

Look in `Adafruit_BNO055.h` (or the Adafruit BNO055 Arduino library source on
GitHub) for the method that returns an `imu::Quaternion`. Components are accessed
as method calls: `q.w()`, `q.x()`, `q.y()`, `q.z()`.

> **Answer (try before reading):** `bno.getQuat()`

---

## Flashing reminder (from Phase 0)

1. Hold BOOT, tap RST, release BOOT (enters bootloader mode).
2. `pio run --target upload --upload-port /dev/tty.usbmodem1101`
3. Unplug + replug after flash (RTS hard-reset unreliable with native USB-CDC).
4. Open serial monitor: `pio device monitor -p /dev/tty.usbmodem1101 -b 115200`
   or use `uv run python -m echoglove.serial_reader /dev/tty.usbmodem1101`
