# Phase 2 design — IR fingertip layer + I²C mux

**Date:** 2026-09-22
**Phase:** 2 of 6
**Depends on:** Phase 1 (shipped, tag `phase-1`)
**Ship gate:** §6 of `docs/superpowers/specs/2026-05-12-echoglove-orchestration-design.md`

Five VL6180X time-of-flight sensors, one per finger, read through a TCA9548A
multiplexer because all five share the fixed I²C address 0x29. Output is a
per-finger range stream over USB serial. Finger *curl* — the conversion from
millimetres to joint angles — is Phase 4's problem, not this one.

Mount geometry was settled separately on 2026-09-21 and is recorded in
`hardware/bom-phase2.md`: palm side, at the base of each finger, aimed distally
and tilted toward the finger, working over roughly 20–90 mm. This spec assumes
that geometry and does not revisit it.

## 1. Scope

**In scope:** firmware reading five VL6180X behind the mux; a host-side reader,
tests and three verification scripts; a rigid bench jig; closing the three open
geometry questions; re-attaching the BNO055 at the end.

**Out of scope:** range-to-curl calibration, any Kalman or fusion work, the
wearable glove, BLE, and the 3D viewer. Those are Phases 3 and 4. Ideas that
surface for them go to `docs/phases/parking-lot.md`, not into this phase.

## 2. Deliverables

| Path | What |
|---|---|
| `firmware/phase2-tof/` | Self-contained PlatformIO project, pinned `lib_deps` |
| `host/src/echoglove/tof_reader.py` | Range line parser, mirrors `imu_reader.py` |
| `host/tests/test_tof_reader.py` | Parser tests, no hardware needed |
| `host/scripts/verify_tof_rate.py` | V2 |
| `host/scripts/verify_isolation.py` | V3 |
| `hardware/wiring/phase2-tof.md` | Wiring diagram + measured final geometry |
| `docs/phases/phase2-kickoff.md` | Kickoff notes |
| `docs/phases/phase2-retro.md` | Retro |
| `hardware/bom-phase3.md` | Phase 3 parts, **including the CH-101 order** |

No Phase 1 file is modified. `serial_reader.py` and `imu_reader.py` are left
alone; both readers filter by key presence, so the merged line at step 6 feeds
both without changes.

The CH-101 is called out because §3 of the orchestration doc specifies ordering
it at the *start of Phase 3*, not at Phase 5 where it is finally used. Long lead
time. It is easy to miss and blocks Phase 5 if missed.

## 3. Bring-up order

Six checkpoints. Each one adds exactly one new variable, so a failure has an
unambiguous cause.

1. **One VL6180X direct on the trunk bus, no mux.** Confirms 0x29 answers, the
   pinned `Adafruit_VL6180X` works, and ranges match a ruler. Proves sensor,
   library and wiring before multiplexing exists.
2. **Mux alone on the bus.** Scan finds 0x70. Write a channel byte, re-scan,
   confirm nothing appears on an empty channel. Write 0x00, confirm it
   disconnects everything.
3. **One sensor behind channel 0.** Must read the same as step 1. Any
   difference is the mux, not the sensor.
4. **Two sensors, channels 0 and 1.** The first point at which the 0x29
   collision is genuinely being solved. Both must read independently.
5. **Five sensors, channels 0–4**, then the jig, then V1–V3.
6. **BNO055 back on the trunk bus**, alongside the mux. 0x28 and 0x70 coexist;
   the IMU needs no channel because it is not a 0x29 device.

Step 6 has its own gate so the merge is not an unverified tail: quaternion plus
five ranges on one line, with per-sensor range rate still ≥ 50 Hz while the IMU
shares the bus.

## 4. Firmware

`firmware/phase2-tof/src/main.cpp`. Five `Adafruit_VL6180X` instances, one per
channel, all at 0x29 — legal because the mux routes between them.

**Trap to design around:** `begin()` writes a full initialisation sequence to
the device, so the channel must be selected before every `begin()` call, not
only before every read. Getting this wrong initialises one sensor five times
and leaves four unconfigured, with symptoms that look like bad wiring.

One helper is the entire mux abstraction:

```c
void tca_select(uint8_t channel);   // one control byte to 0x70, one bit per channel
```

The TCA9548A has no register map. Writing `0x00` disconnects all channels.
Enabling two channels at once is legal and is exactly the 0x29 collision the
mux exists to prevent.

**Fill-in-the-blank sections** (project convention — left blank deliberately for
the builder to complete):

- the body of `tca_select`
- the range-read call inside the main loop

**Error handling.** Phase 1 halts forever when the BNO055 is absent. Phase 2
must not do that. A channel that fails to enumerate produces an error event
naming the channel, and the remaining sensors keep running. With five sensors a
bad solder joint is routine, and firmware that dies on one makes steps 4 and 5
much harder to debug.

## 5. Wire format

Main body of the phase, ToF only:

```
{"t_ms":123,"rt_ms":116,"r":[12,34,56,78,90],"s":[0,0,0,0,0]}
```

`rt_ms` is carried from the very first line even though ToF-only mode emits one
line per fresh range set and could get away without it. Keeping it makes the
schema identical before and after step 6, so `tof_reader.py` and
`verify_tof_rate.py` are written once and do not change when the IMU joins.

`s` carries per-sensor range status and is not optional. `readRange()` returns a
`uint8_t` in which a large value is ambiguous — 255 mm of real distance and "no
target found" are indistinguishable without `readRangeStatus()`. A host that
cannot tell them apart will feed a nonexistent finger into Phase 4's IK. Status
is on the wire from the first line.

After step 6, one line type rather than two:

```
{"t_ms":123,"w":..,"x":..,"y":..,"z":..,"cal_sys":..,"cal_gyro":..,
 "cal_accel":..,"cal_mag":..,"rt_ms":116,"r":[..],"s":[..]}
```

`rt_ms` remains the `millis()` value at which the range set completed. Because the
IMU runs at 100 Hz and the ToF layer is slower, ranges repeat across several
lines; an unchanged `rt_ms` means repeated, a changed one means fresh.

Timestamping at *measurement* time rather than transmission time is what lets
Phase 4 run a multi-rate filter correctly — a range that finished converging
7 ms before the line carrying it must be applied at the instant it was taken, or
the correction lands late and produces lag no motion model explains. This single
field replaces a bare freshness counter and does strictly more.

**Bandwidth note.** ~180 bytes at 100 Hz is ~18 kB/s, which exceeds a real
115200 baud UART. It works only because native USB-CDC ignores the baud setting.
That headroom disappears in Phase 3 over BLE.

## 6. Ranging strategy — decided by measurement

The ≥ 50 Hz criterion and the "one emitter at a time" crosstalk argument are in
tension. Five sensors at 50 Hz is 250 ranges/sec, a 4 ms budget each, while a
VL6180X single-shot conversion is roughly 5–10 ms. Strict sequential ranging may
therefore land at 20–40 Hz and miss the gate.

Convergence time scales with how hard the return is, and at 20–90 mm with strong
returns the real number is unknown until measured. So it gets measured, not
guessed.

**Instrumentation:** wrap the range call in `micros()` and print the measured
per-range time from firmware. Do not infer it from host-side line rate; that
folds in serial and loop overhead and measures the wrong thing.

**Decision ladder, in order:**

1. Five sequential single-shots. If round-robin clears 50 Hz, stop here — the
   crosstalk argument stays airtight because only one emitter ever fires.
2. If it misses, trim `SYSRANGE__MAX_CONVERGENCE_TIME`. The default is set for
   far harder targets than a finger at 40 mm.
3. Only if that still misses, move to continuous mode on all five with the mux
   used for reads only. This reaches ~100 Hz per sensor easily, but the mux
   gates I²C alone — power is direct from the 3V3 rail — so all five emitters
   then fire asynchronously and optical isolation rests entirely on the mount
   geometry. **Taking this step invalidates the crosstalk result, so V3 is
   re-run from scratch afterwards.**

## 7. Bench jig

A rigid flat fixture (foam board or cardboard) holding five sensors at measured
finger pitch, held against the palm. Pitch and tilt become settable, repeatable
parameters, which is what the open geometry questions need in order to close.
Keeps Phase 2 about electronics and geometry rather than wearability.

The jig's geometry is not identical to a real glove's. Phase 3 revalidates.

## 8. Verification

The three §6 criteria, made falsifiable.

**V1 — five sensors readable independently.** Firmware emits a boot enumeration
event listing which channels answered at 0x29; all five must be found. Then, per
channel individually, a target at a ruler-measured 50 mm reads within ±5 mm.
This is a per-channel test rather than a restatement of V3.

**V2 — per-sensor read rate ≥ 50 Hz.** `verify_tof_rate.py`, same shape as
Phase 1's `verify_rate.py`: 10 s sample, pass at ≥ 50 Hz. It counts **distinct
`rt_ms` values, not lines** — line rate is the IMU's rate and would pass
trivially while the ToF layer crawled.

**V3 — isolation.** `verify_isolation.py`, interactive because it cannot move a
hand: prompt for a close hold, sample 2 s; prompt for a far hold, sample 2 s.

Pass requires all of:

- the target sensor moves ≥ 30 mm between holds
- the other four each stay within ±5 mm peak-to-peak across the whole trial
- every reading carries status 0

Five trials, one per finger. All must pass.

The ±5 mm budget is mostly hand tremor — sensor noise at this range is 1–2 mm.
Sanity-check it on the bench before treating it as fixed.

**Step 6 gate.** Quaternion plus five ranges on one line; per-sensor range rate
still ≥ 50 Hz with the BNO055 on the bus.

## 9. Open questions closed during this phase

Carried over from `hardware/bom-phase2.md`. All three close on the jig during
step 5, and the answers are written to `hardware/wiring/phase2-tof.md`.

1. **Finger pitch.** Assumed ~20 mm. The 45 mm isolation threshold scales
   directly with it, so the assumption has to be confirmed with a ruler.
2. **Mounting tilt.** Undecided; ~10–20° is the starting guess. Found by
   sweeping the jig. Aimed flat, an extended finger never crosses the beam;
   tilted too steeply, the top of the range collapses.
3. **Monotonicity.** Whether range increases consistently as the finger extends
   across the whole 20–90 mm travel. If it does not, that is a geometry problem
   worth discovering before Phase 3 bonds anything to a glove.

## 10. Safety

Before first power-on of the five-sensor wiring, photograph the breadboard and
check it against `hardware/wiring/phase2-tof.md`. No LiPo is involved in this
phase; batteries arrive in Phase 3.
