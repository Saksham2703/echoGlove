# EchoGlove — Orchestration Design

**Date:** 2026-05-12

**Status:** Draft — awaiting user review

**Author:** Saksham Jain (with Claude)

**Scope:** End-to-end plan for building EchoGlove v1 (live hand pose in a Python viewer) and v2 (ultrasonic-augmented pose), spanning hardware sourcing, firmware, perception/fusion, and the learning curriculum that goes with it.

---

## 1. Builder profile & constraints

This plan is tuned to a specific builder. Choices that follow are downstream of these constraints — if any change, revisit the plan.

| Constraint | Value |
|---|---|
| Hardware experience | Total beginner (no prior soldering, breadboards, or firmware) |
| Coding experience | Strong Python, some C/C++ |
| Time commitment | 5–8 hrs/week, sustainable |
| Timeline horizon | 6–9 months to v1, ~10 months to v2 |
| Budget | $200–400 across project lifetime |
| Dev OS | macOS (Apple Silicon) |
| On-hand | Freenove ESP32-S3 Ultimate Starter Kit |
| Missing | Soldering iron, multimeter, no 3D printer, no VR headset |
| Sourcing rule | Amazon-first; SparkFun acceptable for CH-101 (Phase 5) and DW3000 (v3+) |
| v1 ship criterion | Live 3D hand pose in a Python viewer on the Mac (no VR/SteamVR required) |
| Motivation | Learn embedded systems end-to-end and perception (sensor fusion, state estimation, IK) |

**Explicit non-goals for v1:**
- SteamVR / OpenGloves integration
- 3D-printed enclosure
- ML-based pose models
- Absolute 6DOF world-space position (DW3000 / UWB)
- A second glove (left hand)

These may become v3+ work but are out of scope through v2.

---

## 2. Phase roadmap

Six phases. v1 ships at end of Phase 4. v2 ships at end of Phase 6. Each phase is its own bi-weekly-cadence work unit with its own spec, plan, and verification criteria.

| Phase | Calendar | Build | Learn | Ship |
|---|---|---|---|---|
| **0 — Fundamentals** | wks 1–4 | First LED blink, button input, USB serial print, one I²C sensor read using Freenove kit | Voltage/current/ground, GPIO, I²C basics, breadboard convention, soldering, PlatformIO toolchain, USB serial on Mac, Python serial reader | First sensor stream visible in Python |
| **1 — IMU bring-up** | wks 5–8 | BNO055 absolute orientation @ 100 Hz over USB serial, 3D rotating cube in Python viewer | Quaternions, sensor fusion as a black box, interrupt vs polled reads, real-time streaming | Orientation-only hand viewer |
| **2 — IR fingertip layer + I²C mux** | wks 9–14 | 5× VL6180X via TCA9548A multiplexer, all reading independently | I²C addressing + collisions, multiplexing pattern, laser ToF physics, sensor calibration | 5 finger-bend proxies streaming live |
| **3 — Cotton-glove integration** | wks 15–17 | Move from breadboard to wearable: protoboard, sensors sewn to cotton glove, wristband-mounted ESP32 + LiPo, BLE replaces USB | Power budget, LiPo safety, BLE GATT basics, wearable mechanical design, wire fatigue mitigation | Untethered glove streaming over BLE |
| **4 — Host-side fusion + 3D viewer ⭐** | wks 18–21 | Python: BLE receiver → Kalman filter (IMU orientation + IR-derived per-finger curl) → real-time 3D hand rig in Open3D/PyVista | Linear Kalman filter, per-finger inverse kinematics, real-time 3D graphics, frame-rate vs latency budgeting | **v1 SHIPS** |
| **5 — CH-101 single-pair ranging** | wks 22–26 | 2× SparkFun CH-101 eval boards on protoboard, pairwise distance measurement between thumb–index proxies | SmartSonic SDK, FreeRTOS tasks/queues, PMUT acoustic ToF, ESP-IDF (Arduino framework swap-out) | Two-sensor distance stream |
| **6 — Ultrasonic array + UltraGlove fusion ⭐** | wks 27–34 | 6× CH-101 on glove, time-division multiplexed, pairwise distance matrix → biomechanical-model IK replaces IR-derived curl as primary pose source | Crosstalk sequencing, biomechanical hand model (21 joints, joint constraints), extended Kalman filter, distance-matrix → pose IK | **v2 SHIPS** |

**Cadence:** bi-weekly milestone reviews. Each phase ends with a `git tag phase-N`, a short retro in `docs/phases/phaseN-retro.md`, and an update to `STATE.md`.

**Two-week rule:** if a phase blocks for > 2 weeks, we explicitly re-scope (simplify, escalate to community, or pivot to a different phase first). No infinite tunneling on a single problem.

---

## 3. Bill of materials strategy

**Principle: buy in phases, not upfront.** Order ~1 week before each phase starts. Decisions in earlier phases inform later phase BOMs (e.g. Phase 0 may reveal Freenove kit already includes a usable IMU and we skip the Phase 1 BNO055 purchase).

### Phase 0 cart (order this week, Amazon)

| Item | Spec / notes | Ballpark |
|---|---|---|
| Soldering iron + solder | USB-C powered pen-style: Pinecil V2 or TS80P. 60/40 leaded rosin-core 0.6mm solder. Brass tip cleaner. | $40–60 |
| Digital multimeter | Any $15–25 auto-ranging (AstroAI, INNOVA) | $20 |
| Spare ESP32-S3 dev boards × 2 | ESP32-S3-DevKitC clones, USB-C connector | $25 |
| USB-C data cable × 2 | Must be USB-C data, not charge-only. 1 m, USB-C to USB-C for Mac. | $10 |
| 22 AWG hookup wire kit | Solid + stranded, multi-color, 6+ colors (Plusivo / TUOFENG) | $15 |
| Helping hands w/ magnifier (optional) | Big quality-of-life uplift for soldering | $15 |

**Phase 0 subtotal: ~$110–145.**

Freenove kit is assumed to provide: breadboard, jumper wires (M/M, M/F), basic LEDs/resistors/buttons, USB cable, common practice sensors (likely MPU-6050 IMU + HC-SR04 ultrasonic + DHT11). **Confirm contents on arrival**, then update `hardware/bom-phase0.md`.

### Future phases (budget only; order later)

| Phase | Items | When | Ballpark |
|---|---|---|---|
| 1 | BNO055 IMU breakout (Adafruit/SparkFun on Amazon, or GY-BNO055 clone) | wk 3–4 | $15–30 |
| 2 | 5× VL6180X breakouts, 1× TCA9548A mux, 1 spare each | wk 7–8 | $50–75 |
| 3 | Cotton work gloves, perfboard, 22 AWG silicone wire, 500 mAh LiPo, TP4056 USB-C charger, velcro, heat-shrink | wk 13–14 | $50–70 |
| 5 | 2× CH-101 eval boards (**SparkFun**, not Amazon) — order at start of Phase 3 to avoid stockout | wk 15 | $60 |
| 6 | 4× additional CH-101 (SparkFun) | wk 21 | $120 |

**v1 total (Phases 0–4): ~$225–320.** Fits in $200–400 band.
**v2 total adds: ~$180.** Brings project total to ~$405–500. Top of band but doable.

### Notable design choices vs. README

- **VL6180X retained** (not substituted with VL53L0X). Better mm-precision in the 0–20 cm range that fingers operate in; Amazon pricing is comparable to VL53L0X.
- **CH-101 from SparkFun**, not Amazon. The two-vendor Amazon-only rule is relaxed for this part only. SparkFun is the same trust profile as Amazon for hobbyist electronics.
- **No DW3000 / UWB in this plan.** Deferred to a future v3+ design once v2 is shipped and stable.

### Sourcing risk: CH-101 specifically

SparkFun has had multi-month CH-101 stockouts historically (TDK supply issues). Mitigations baked in:

- v1 (Phase 4) is a complete working glove without CH-101. If CH-101 collapses, we still have a glove.
- Order CH-101 at start of Phase 3, not Phase 5. They sit in a drawer briefly but we don't get caught by a stockout.
- Backup vendor: Mouser stocks CH-101 modules at slightly higher cost but more reliable supply.
- Worst case: v2 pivots to a different perception milestone (ML gesture classification on existing modalities).

---

## 4. Tooling & development environment

### Firmware

| Tool | Role | Rationale |
|---|---|---|
| **VS Code** | Editor | User's existing tool. Plays nicely with Claude Code workflow. |
| **PlatformIO extension** | Build / dependency mgmt / serial monitor | Superior to Arduino IDE: proper library versioning, multi-board support, integrated debugger. Beginner-friendly defaults. |
| **Arduino framework (on PlatformIO)** | Firmware API, Phases 1–4 | Huge ecosystem; Adafruit/SparkFun maintain libraries for every sensor in this BOM. |
| **ESP-IDF (on PlatformIO)** | Firmware API, Phases 5–6 | Switch when FreeRTOS task scheduling is required for CH-101 crosstalk timing. Same editor, same workflow — different framework label in `platformio.ini`. |
| **esptool.py / PIO flasher** | Flashing | Bundled with PlatformIO. |

### Host

| Tool | Role |
|---|---|
| **Python 3.12 via [`uv`](https://github.com/astral-sh/uv)** | Package manager and venv tool. New to user; Claude assists. |
| **`pyserial`** | USB serial reader (Phases 0–2) |
| **`bleak`** | BLE client (Phase 3+) |
| **`numpy` / `scipy` / `filterpy`** | Math + Kalman filter (Phase 4) |
| **`open3d` or `pyvista`** | 3D hand-rig viewer (chosen in Phase 4 based on M-series Mac performance) |
| **`pytest`** | Tests |
| **`ruff` + `mypy`** | Lint + type-check (optional but recommended) |

### Repository structure

```
echoGlove/
├── README.md                    (exists)
├── RESEARCH.md                  (exists)
├── STATE.md                     (new — "where I left off" notes, updated each session)
├── .gitignore
├── docs/
│   ├── superpowers/specs/       (design docs)
│   └── phases/                  (per-phase kickoff + retro notes, parking lot)
├── firmware/
│   ├── phase0-blink/            (each phase = its own PlatformIO project)
│   ├── phase1-imu/
│   ├── phase2-irmux/
│   ├── phase3-wearable/
│   ├── phase5-ch101-pair/
│   └── phase6-ch101-array/
├── host/
│   ├── pyproject.toml           (uv-managed)
│   ├── echoglove/               (Python package)
│   │   ├── serial_reader.py
│   │   ├── ble_reader.py
│   │   ├── fusion.py            (Kalman)
│   │   ├── ik.py                (inverse kinematics)
│   │   └── viewer.py            (3D viz)
│   └── tests/
├── hardware/
│   ├── bom-phase0.md            (per-phase BOM with Amazon links + receipts)
│   ├── bom-phase1.md
│   ├── ...
│   └── wiring/                  (ASCII / Fritzing wiring diagrams)
├── notebooks/                   (Jupyter — exploratory data analysis, sensor calibration)
└── .github/
    └── workflows/               (CI: lint + pytest on host code; no firmware CI yet)
```

**Rationale for per-phase firmware subprojects:** each phase's firmware stays buildable independently. Library version drift in one phase doesn't block another. Future contributors can point to `firmware/phase1-imu/` as a minimum-viable IMU example without dragging in the full glove.

### GitHub

- Repo: **private** at start. Flip to public at v1 ship if desired.
- License: MIT (per existing README).
- CI: lint (`ruff`), type-check (`mypy`), test (`pytest`) on host code only. Firmware CI deferred (would require self-hosted runner with hardware).
- `platformio.ini` is committed and treated as a lockfile — exact library versions pinned.

---

## 5. Working agreement: human-in-the-loop split

Each phase follows the same rhythm:

1. **Phase kickoff (Claude ~80%):** writes `docs/phases/phaseN-kickoff.md` containing goal, success criteria, BOM with current Amazon links, wiring diagram, firmware skeleton (with deliberate fill-in-the-blanks), host code skeleton, expected pitfalls, and concept primers for the new topics.
2. **Parts arrive (user):** confirm receipt, BOM inventory check (photos for Claude to sanity-check), update `hardware/bom-phaseN.md` with actual receipts.
3. **Hands-on build (user ~70%, Claude ~30%):** wire breadboard following diagram. Photograph wiring before powering on — Claude sanity-checks.
4. **Firmware bring-up (50/50):** user flashes the skeleton, pastes serial output, both debug. **Fill-in-the-blanks left deliberately for learning.**
5. **Host-side verification (user ~30%, Claude ~70%):** Claude writes the verification script; user runs it; both iterate.
6. **Verification checklist:** check each phase's success criteria. If met, `git tag phase-N`, write retro, ship.
7. **Phase retro (user ~50%):** what surprised, what felt rote, what needs more depth. Next phase's structure adjusts based on retro.

### Task split

| Human-only | Claude-only | Together |
|---|---|---|
| Soldering, wiring, USB plug-in | Datasheets, firmware skeletons, research | Debugging from serial output / Python errors |
| Multimeter measurements | Amazon link research, alternatives | Implementation tradeoffs |
| Observing physical behavior | Python visualization code | Code review on user-written code |
| Buying parts, opening packages | Tests, CI, docs | Concept explanations |

### What Claude will *not* do without asking

- Buy parts on user's behalf (cannot; won't try).
- Push to GitHub remote (local commits only; user pushes).
- Make sweeping changes to existing files outside current phase's scope.
- Skip verification — if a criterion isn't met, the phase doesn't ship.

---

## 6. Verification criteria per phase

The "phase ships" gate. No subjective "looks fine" passes.

| Phase | Criteria |
|---|---|
| **0** | Onboard LED blinks. Button press increments a counter printed over USB serial. Python script on Mac reads serial stream cleanly for 60 s. One I²C sensor from Freenove kit prints raw readings. |
| **1** | BNO055 quaternion stream @ 100 Hz over USB. Python wireframe-cube viewer rotates to match real hand rotation. No quaternion glitches or jumps over 5 min continuous use. |
| **2** | 5× VL6180X all readable independently via TCA9548A. Per-sensor read rate ≥ 50 Hz. Stepping a finger close→far changes exactly one reading; others stay stable (no electrical or I²C crosstalk). |
| **3** | Glove worn 30+ min, no wire breaks at flex points. ESP32 + LiPo on wristband, no USB tether. BLE stream stable to Mac at < 50 ms latency. |
| **4 — v1 ⭐** | 3D hand model in Python viewer matches real hand pose. ≥ 30 fps end-to-end. Latency < 100 ms. Pose holds without drift over 5 min continuous use. Re-runs cleanly from a single command a week later. |
| **5** | Two CH-101 on protoboard measure inter-sensor distance to ±5 mm from 3 cm to 40 cm. SmartSonic SDK integrated under ESP-IDF. |
| **6 — v2 ⭐** | 6× CH-101 on glove, time-multiplexed without crosstalk. Pairwise distance matrix → biomechanical-model IK supersedes IR-derived curl as primary pose source. Updates ≥ 10 Hz. |

---

## 7. Learning curriculum mapped to phases

| Phase | Concepts |
|---|---|
| 0 | Voltage/current/ground, GPIO, digital vs analog, I²C basics, breadboard convention, soldering, PlatformIO toolchain, USB serial |
| 1 | Quaternions (and why they beat Euler angles), on-chip sensor fusion as a black box, interrupt vs polled reads, real-time streaming |
| 2 | I²C addressing + collisions, I²C multiplexing pattern, laser ToF physics, sensor calibration |
| 3 | Power budget, LiPo safety, BLE GATT services + characteristics, wearable mechanical design, wire-fatigue mitigation, heat-shrink wire dressing |
| 4 | Linear Kalman filter (state, process model, measurement model), simple per-finger inverse kinematics, real-time 3D graphics, frame-rate vs latency budgeting |
| 5 | ESP-IDF vs Arduino framework, FreeRTOS tasks/priorities/queues, PMUT acoustic ToF, pulse coding, vendor SDK integration |
| 6 | Multi-sensor crosstalk sequencing, biomechanical hand model (21 joints, joint constraints), extended Kalman filter, distance-matrix → pose IK |

**Concept primer convention:** the two hardest concepts (quaternions in Phase 1, Kalman in Phase 4) each get an explicit concept-primer section in their phase kickoff doc — quaternions via rotation animations, Kalman via a 1D example before the 6D one. Budget 1 extra week each.

---

## 8. Risk register

### Hardware

| Risk | Likelihood | Mitigation |
|---|---|---|
| Frying ESP32 by miswiring 5 V to a 3.3 V pin | High (first month) | Spare ESP32s in Phase 0 BOM. Wiring-photo sanity check before every first power-on. |
| Static damage to BNO055 / VL6180X | Medium | Touch grounded metal before handling sensors. Full ESD-mat not in scope at this budget. |
| Cold solder joints | Medium-High | Multimeter continuity check on every joint. Wiggle test before declaring done. |
| Charge-only USB-C cable | High (first week) | "USB-C data" spec'd in BOM. `ls /dev/tty.*` no-show on plug-in usually = cable issue. |
| Mac USB-serial driver (CH340/CP210x clones) | Medium | ESP32-S3 has native USB-CDC (no driver). Cheap clones may expose CH340 — single signed driver install if so. |
| Counterfeit / DOA Amazon sensors | Medium | Spares budgeted. Multimeter resistance check on power rails before assuming code bug. |
| LiPo fire / battery damage | Low likelihood, high consequence | Dedicated Phase 3 safety brief. Charge on non-flammable surface, never unattended, never punctured. TP4056 charger has overcurrent protection. |
| Wire fatigue at finger flex points | Very high (Phase 3+) | Silicone-sheathed 22 AWG, service loops at joints, strain relief at solder points. Plan to re-solder once during glove lifetime. |

### Software

| Risk | Mitigation |
|---|---|
| PlatformIO library version drift | Pin versions in `platformio.ini`. Treat as lockfile. |
| Mac BLE permission prompts (bleak) | Phase 3 kickoff includes Bluetooth-permission step in writing. |
| ESP-IDF install fiddliness on macOS | Deferred to Phase 5. PlatformIO's ESP-IDF integration handles 95% of pain by then. |
| Quaternions / Kalman confusion | Concept-primer subsections in Phase 1 and Phase 4 kickoffs. 1 extra week each. |

### Project / process

| Risk | Mitigation |
|---|---|
| Scope creep | Out-of-scope ideas go to `docs/phases/parking-lot.md`. Each phase has explicit scope. |
| Stuck-for-a-week burnout | Two-week rule: re-scope, escalate, or pivot. No infinite tunneling. |
| Context loss after 2+ week break | Every session ends with 3-line `STATE.md` update. Resume = read `STATE.md` first. |
| Holiday gaps in parts shipping | Order Phase 5 parts at Phase 3 start to absorb shipping uncertainty. |

### Normal-not-risk

- First firmware flash will feel mysterious. Within a month, automatic.
- At some point a 3-hour debug session turns out to be one wrong wire. Universal. The learning is in the debug, not the result.
- Kalman won't click on first explanation. Fine.

---

## 9. Decomposition into future spec/plan cycles

This document is the orchestration spec. It does not double as the implementation plan for any single phase. **Each phase gets its own brainstorm → spec → plan → execution cycle**, starting with Phase 0.

Next step after user approval of this doc: invoke the `writing-plans` skill to create a detailed implementation plan for **Phase 0 only** — fundamentals + Phase 0 BOM finalization + repo scaffolding + first LED blink + first sensor read. Subsequent phases each get their own plan when their predecessor ships.

---

## 10. Open questions / parking lot

Items deferred from this design:
- Final choice of `open3d` vs `pyvista` for the 3D hand viewer (decide in Phase 4).
- Whether the Phase 3 BLE protocol is custom GATT characteristics or a JSON-over-Nordic-UART-Service format (decide in Phase 3).
- Whether to add inertial-only dead reckoning for under-desk position estimate in Phase 4, or defer to v3 (decide based on Phase 1 IMU drift measurements).
- Long-term: SteamVR/OpenGloves integration, second glove, 3D-printed enclosure, ML pose model, UWB.

---

**End of design.**
