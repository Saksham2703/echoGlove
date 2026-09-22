# EchoGlove — Personal Statement Source Brief

**Prepared:** 2026-09-04

**Purpose:** Source material for a graduate personal statement (robotics MS, Fall 2027 entry, applications due Nov 2026).

**Scope:** Not just what EchoGlove is, but how it was conceived, decomposed, sourced, built, debugged, and governed — with the specific decisions, mistakes, and self-imposed constraints that make the account personal rather than generic.

**How to use this document:** Sections 1–4 are the project. Sections 5–10 are the person: process, decisions, failures, methodology. Section 11 is a bank of concrete, verifiable details for anecdotes. Section 12 flags what must *not* be claimed.

---

## 1. The one-paragraph version

EchoGlove is a camera-free, drift-resistant hand-tracking glove that fuses MEMS ultrasonic time-of-flight, IR laser ToF, and IMU sensing to reconstruct hand and finger pose — no cameras, no magnetic base station, no line of sight. It is a solo, self-directed, from-scratch build: bill of materials, soldering, ESP32-S3 firmware, host-side sensor fusion, and a real-time 3D viewer, on a budget under $500 and a sustainable 5–8 hrs/week. It is deliberately structured as a *learning instrument* as much as a device — the roadmap is a curriculum with verification gates, and the repository is instrumented with the process artifacts (phase specs, retros, a learnings log, a parking lot) that make a long solo project survive multi-week interruptions.

---

## 2. Why this project, personally

Three threads converge on it, and the statement should braid them rather than pick one.

### 2.1 The professional thread — ultrasonic hand tracking, seen from the driver side

At Rivet Industries (AR glasses / XR hardware startup, Palo Alto), the work is embedded and perception-adjacent: Linux kernel drivers, AOSP/BSP, device bring-up, USB/I²C/GPIO, and a multi-sensor tracking pipeline on compute-constrained AR glasses. Part of that work involved **integrating an XR input controller from Sensoryx** — a company whose tracking technology is patented ultrasonic 6DoF, sub-millimeter and drift-free, explicitly positioned for the real-world conditions where cameras, magnetic, and IMU-only systems fail.

That is the seed. EchoGlove's central architectural bet — ultrasonic as the *primary* pose modality rather than a novelty — is not a bet made from a literature search. It is a bet made after handling a commercial system built on exactly that principle and seeing it work where camera tracking does not.

**The honest framing of the gap this project closes:** the professional work is on the software side of hardware someone else designed and built. Drivers get written for boards that arrive already made; sensor pipelines get tuned with algorithms someone else authored. EchoGlove is the first project where the whole stack is owned — choosing the parts, soldering the headers, wiring the bus, writing the firmware, designing the wire protocol, and building the fusion and visualization on the host. **Professional on the software side of embedded; a genuine beginner at the bench.** No prior soldering, no prior breadboard work, no prior board bring-up done personally. That asymmetry is the interesting part of the story and should not be smoothed over in either direction.

### 2.2 The origin thread — a crude demo that was interesting for the wrong reason

The immediate trigger was a post on X showing hand tracking built from an IR LED and a photoresistor: emit infrared, measure how much bounces back, map brightness to position. It is reflectance sensing, not ranging — sensitive to ambient IR, skin tone, surface texture, and clothing color, and it yields one dimension of proximity per sensor pair.

The instinct was not "that's clever, let me copy it." It was "that's the wrong physics for this problem — but the *form factor* intuition is right." That distinction is the whole project. `RESEARCH.md` opens with a full teardown of why bare IR reflectance cannot do finger pose, and then explains why IR was nevertheless **kept in the stack in a different role**: outward-facing laser ToF sensors on the fingertips as a 0–20 cm close-interaction layer, filling exactly the sub-2 cm blind spot where ultrasonic is weakest. Nothing was discarded that could be repurposed at the right level of abstraction.

### 2.3 The academic thread — a published idea with no buildable implementation

A survey of arXiv, IEEE Xplore, the ACM DL, GitHub, Hackaday, and Instructables produced a clear finding: **no published project — academic or hobbyist — combines ultrasonic ToF + IR laser ToF + IMU on a single glove.**

The closest precedent is **UltraGlove** (Princeton, SIGGRAPH Asia 2023, [arXiv:2306.12652](https://arxiv.org/abs/2306.12652)), which uses CH-101 MEMS ultrasonic sensors as the *sole* modality, feeding a pairwise inter-sensor distance matrix into a neural network to reconstruct hand pose — deliberately excluding IMU and optical sensing on drift and occlusion grounds. It is a research paper, not open-source and not a buildable kit.

The DIY landscape, meanwhile, is almost entirely flex sensors and potentiometers (LucidGloves and its descendants), and the commercial landscape has converged on IMU + electromagnetic-field fusion (Manus Quantum ~$7.5–9k, Rokoko Coil Pro ~$895–2.5k, HaptX enterprise-only). Ultrasonic is the one modality the commercial players have not embraced, despite UltraGlove's published case that it solves the same drift problem EMF solves — without a precision wound-coil transmitter and its price tag.

**The gap, stated precisely:** EchoGlove is an attempt at the open-source, buildable implementation of UltraGlove's core insight, extended with an IR close-range layer and an IMU orientation/interpolation layer, for a parts cost under $500.

---

## 3. What it is, technically

### 3.1 Sensor stack — each modality covers the others' blind spots

| Modality | Part | Role | Range | Rate |
|---|---|---|---|---|
| Ultrasonic MEMS ToF | TDK/Chirp CH-101 PMUT (3.5 × 3.5 mm) | Primary pose source — pairwise inter-sensor distance matrix → hand pose | 2 cm – 1.2 m | ~60 Hz |
| IR laser ToF | ST VL6180X | Fingertip close-range layer — pinch detection, surface contact | 5–200 mm | ~100 Hz |
| IMU | Bosch BNO055 (NDOF fusion) | Global hand orientation + high-rate fill-in between ultrasonic frames | — | 100–400 Hz |

The design logic: **the hand is its own reference frame.** Ultrasonic sensors on fingertips and palm range against *each other*, so no external anchors, no line of sight to a base station, and no degradation when the hand is under a desk or in the dark. The IMU supplies the one thing inter-finger ranging cannot — absolute orientation in world space — plus high-rate pose deltas that smooth the slower ultrasonic frames. IR covers the sub-2 cm regime where ultrasonic degrades.

### 3.2 System architecture

```
Glove:    CH-101 ×5 (fingertips) + ×1 (palm) | VL6180X ×5 (fingertips)
          BNO055 (dorsum) | ESP32-S3 + 500 mAh LiPo (wristband) | BLE/USB
             │
             ▼  newline-delimited JSON over USB serial → BLE
Host:     Kalman fusion (IMU orientation + IR-derived curl → ultrasonic-driven IK)
          → real-time 3D hand rig in Python
```

### 3.3 Deliberate scope discipline: what v1 is *not*

Explicit non-goals, written into the design doc on day one so that scope creep is a visible violation rather than a drift: no SteamVR/OpenGloves integration, no 3D-printed enclosure, no ML pose model, no absolute world-space position (UWB), no second glove.

**v1 ships when live 3D hand pose renders in a Python viewer on the Mac at ≥30 fps, <100 ms latency, holding without drift for 5 minutes, and re-running cleanly from a single command a week later.** That last clause is deliberate — it is the anti-demo criterion.

---

## 4. Current status (honest)

| Phase | Content | Status |
|---|---|---|
| **0 — Fundamentals** | Toolchain, LED blink, button + JSON serial, first I²C sensor read | **Shipped** 2026-05-24 (`git tag phase-0`), all 4 verification criteria met |
| **1 — IMU bring-up** | BNO055 quaternions @100 Hz, wireframe-cube viewer | **In progress** — all host software, tests, viewer, and both automated verification scripts complete and committed; firmware skeleton written with intentional gaps; blocked on hardware, then paused |
| 2 — IR + I²C mux | 5× VL6180X via TCA9548A | BOM researched and committed ahead of schedule |
| 3 — Wearable integration | Protoboard, cotton glove, LiPo, BLE | Planned |
| 4 — Fusion + 3D viewer | **v1 ships** | Planned |
| 5–6 — CH-101 ranging + array | **v2 ships** | Planned |

**Timeline:** started 2026-05-12. Phase 0 took ~10 active hours over 12 calendar days. Phase 1 software completed 2026-05-25. Paused ~May–Sept 2026; resuming now. 32 commits.

**Phase 0 actual spend:** $141.82 post-tax against a $124–161 estimate.

The pause is worth owning rather than hiding — it is precisely what the repository's process infrastructure was designed for, and Section 6.4 covers how a three-month gap is recoverable in a single read.

---

## 5. How the project was run — the part that differentiates

This is the section a robotics admissions committee should care about most. The device is a hobby build; the *way* it is run is engineering management applied to a solo project.

### 5.1 Phase decomposition with hard verification gates

The project is decomposed into seven phases (0–6), each a bi-weekly work unit with its own **brainstorm → spec → plan → execute → verify → retro** cycle. Each phase has its own design spec and implementation plan committed to the repo before any code is written. Phase 0's plan is 1,230 lines; Phase 1's is 1,040.

**Every phase has objective, pre-registered pass/fail criteria written before the work starts.** Not "looks fine." Examples:

- **Phase 1 V1:** quaternion stream ≥ 95 Hz average measured over 10 s (automated).
- **Phase 1 V3:** record 5 minutes of quaternions; assert `|dot(q_n, q_{n+1})| ≥ 0.99` for every consecutive pair (automated — catches fusion glitches and dropped samples that a human watching a cube would never see).
- **Phase 2:** stepping one finger close→far must change *exactly one* sensor reading; the other four stay stable (a crosstalk test, both electrical and I²C).
- **Phase 3:** glove worn 30+ minutes with no wire breaks at flex points; BLE latency < 50 ms.

A phase does not ship until its criteria pass. Then, and only then: `git tag phase-N`, write the retro, update state.

### 5.2 The two-week rule

Written into the design doc from the start: **if a phase blocks for more than two weeks, explicitly re-scope — simplify, escalate to the community, or reorder phases. No infinite tunneling.** This is a pre-commitment made while calm, to govern a future self who will be frustrated and sunk-cost-attached.

### 5.3 A risk register written before the first part was ordered

The design doc contains a full risk register across hardware, software, and process — with likelihood and mitigation per risk, written before purchasing anything. A sample:

| Risk | Likelihood | Mitigation baked into the plan |
|---|---|---|
| Frying the ESP32 by miswiring 5 V into a 3.3 V pin | High (first month) | Spare boards budgeted into the Phase 0 BOM; wiring photographed and reviewed before *every* first power-on |
| Charge-only USB-C cable silently preventing flashing | High (first week) | Data-rated cables explicitly spec'd in the BOM with the reason written next to the line item |
| Cold solder joints | Medium-high | Multimeter continuity check on every joint; wiggle test before declaring done |
| CH-101 multi-month stockout at the only viable vendor | Medium | v1 is architected to be a complete working glove *without* CH-101; parts ordered two phases early; backup vendor identified; worst-case v2 pivot documented |
| Wire fatigue at finger flex points | Very high | Silicone-sheathed wire, service loops at joints, strain relief — and a plan to re-solder once during glove lifetime, treated as expected maintenance rather than failure |
| LiPo fire | Low likelihood / high consequence | Dedicated safety brief at Phase 3; never charge unattended; TP4056 with overcurrent protection |

The register also contains a **"normal, not risk"** section, which is the most self-aware thing in the document: *the first flash will feel mysterious and within a month will be automatic; at some point a three-hour debug will turn out to be one wrong wire — universal; the learning is in the debug, not the result; Kalman will not click on the first explanation, and that is fine.* Failure modes were pre-labeled as normal so they could not later be mistaken for evidence of unfitness.

### 5.4 Buy in phases, not upfront

**Principle: order roughly one week before each phase starts, because earlier phases change later BOMs.** The stated example proved literally true — Phase 0's inventory of the starter kit determined what Phase 1 actually needed to purchase.

Mid-project, this evolved into a stricter, self-imposed rule after a supply-chain block: **"BOM one phase ahead."** While executing phase N, research and commit `hardware/bom-phase(N+1).md` with links and prices — so parts can be ordered the instant phase N ships — but *do not plan or implement* phase N+1. Only the BOM. This was written into the project conventions file as a durable rule (commit `3b26ba0`) and immediately exercised: the Phase 2 BOM was researched and committed while Phase 1 was still blocked.

That is a process improvement derived from a real blocker, formalized as a rule, and applied — in the same working session.

### 5.5 An explicit human/machine working agreement

Each phase follows a fixed rhythm with a written division of labor: which tasks are hands-only (soldering, wiring, multimeter measurements, observing physical behavior), which are research/scaffolding, and which are collaborative (debugging from serial output, implementation tradeoffs, concept explanation). A short list of hard prohibitions is written into the project conventions and enforced: no pushing to the remote, no changes outside the current phase's scope, no skipping verification, and — the important one — **no completing the fill-in-the-blank firmware sections that exist for learning.**

---

## 6. Self-imposed learning constraints (the most personal part)

### 6.1 Fill-in-the-blank firmware — a rule against the easy path

Every firmware skeleton in this project is committed with **deliberate gaps at the conceptually load-bearing lines**, marked and explained but not filled. The reasoning is the builder's own: *the point is to learn this, not to have it done for me.*

The Phase 1 firmware (committed 2026-05-25) is the concrete example. Everything scaffolding-shaped is written — I²C init, the `millis()`-based 100 Hz timer, the JSON serialization, the heartbeat LED, the calibration-status readout. Two things are blank:

```cpp
// FILL IN: pass OPERATION_MODE_NDOF as the mode argument to begin().
// Hint: look in Adafruit_BNO055.h for the adafruit_bno055_opmode_t enum.
if (!bno.begin(/* YOUR_MODE_CONSTANT_HERE */)) { ... }

// FILL IN: call bno.getQuat() and assign to q.
// Hint: return type is imu::Quaternion; access fields as q.w(), q.x(), etc.
imu::Quaternion q = /* YOUR_READ_CALL_HERE */;
```

Those two lines are the entire conceptual content of the phase: *which fusion mode the chip runs in*, and *what shape the data comes out as*. The hints point at the library header rather than at the answer — the exercise is reading vendor source, which is the actual embedded skill.

**On tooling, stated plainly:** an AI assistant was used throughout as a tutor and research partner — for concept primers, datasheet triage, and rubber-duck debugging. The fill-in-the-blank convention exists specifically to prevent that from becoming a substitute for understanding. It is a constraint imposed *on the tool*, by the learner, in writing, in the repository's conventions file, before it could become a temptation.

### 6.2 A curriculum mapped onto the build

The design doc contains an explicit concept-per-phase curriculum, so that each hardware milestone is also a named learning objective:

| Phase | Concepts to learn |
|---|---|
| 0 | Voltage/current/ground, GPIO, digital vs analog, I²C, breadboard convention, soldering, PlatformIO toolchain, USB serial |
| 1 | Quaternions and why they beat Euler angles, on-chip sensor fusion as a black box, interrupt vs polled reads, real-time streaming |
| 2 | I²C addressing and collisions, the multiplexing pattern, laser ToF physics, sensor calibration |
| 3 | Power budget, LiPo safety, BLE GATT services and characteristics, wearable mechanical design, wire-fatigue mitigation |
| 4 | Linear Kalman filtering (state, process model, measurement model), per-finger inverse kinematics, real-time 3D graphics, frame-rate vs latency budgeting |
| 5 | ESP-IDF vs Arduino, FreeRTOS tasks/priorities/queues, PMUT acoustic ToF, pulse coding, vendor SDK integration |
| 6 | Crosstalk sequencing, biomechanical hand model (21 joints, joint constraints), extended Kalman filtering, distance-matrix → pose IK |

With a further rule: **the two hardest concepts — quaternions in Phase 1, Kalman in Phase 4 — each get a dedicated written primer and an extra budgeted week.** Difficulty was scheduled for, not discovered.

### 6.3 A parking lot, so curiosity doesn't become scope creep

Out-of-scope ideas go to `docs/phases/parking-lot.md` and are reviewed at each phase boundary. It currently holds, among others:

- **Implement Madgwick or Mahony fusion from scratch on the host**, bypassing the BNO055's internal NDOF mode and working from raw accel/gyro/mag. Filed explicitly as a *pure learning exercise — understand what the BNO055 is doing internally.* This came directly out of the Phase 0 retro, where the answer to "what do you want more depth on" was **"how does Madgwick/Mahony fusion work under the hood?"** The chip does it for you; the parking lot records the intent to do it anyway, later, on purpose.
- **Rewrite the viewer with modern OpenGL vertex/fragment shaders** instead of immediate-mode `glBegin`/`glEnd` — "a stepping stone to understanding how games actually render." Deferred until after Phase 4, when the viewer is stable.
- Magnetometer figure-8 calibration; and the v3+ list: SteamVR/OpenGloves, second glove, 3D-printed mounts, UWB, an ML pose model.

The pattern: the interesting tangent is *written down with its rationale and a trigger condition*, then closed — instead of either being lost or eating the current phase.

### 6.4 Instrumentation for the interruption

Two root-level files exist purely to make a 5–8 hrs/week project survive gaps:

- **`STATE.md`** — updated at the end of every working session. Five fields at the top (last updated, current phase, last commit, next step, blocked on) plus a "for the next session" quick-start listing which five documents to read in which order, a task-status table, and a "critical context — gotchas already resolved, don't redo" section. It is written *to a future self who has forgotten everything*, and it is why a three-month pause is recoverable in one read rather than one weekend.
- **`LEARNINGS.md`** — append-only, timestamped, never rewritten. One entry per non-obvious thing learned, in the format `## YYYY-MM-DD — <short title>` plus 1–3 sentences on what was learned and why it matters going forward. Nine entries at pause.

Both are conventions written into the project's rules file, not habits that happened to form.

---

## 7. Technical judgment calls worth citing

These are the moments where the interesting work was *deciding*, not building.

### 7.1 Ruling out WiFi CSI on physics, before spending a dollar

WiFi Channel State Information sensing was investigated seriously as a possible modality — it runs on the ESP32-S3 for free, and published work reports ~99% accuracy on coarse gestures. It was then ruled out by a first-principles calculation rather than by experiment:

> WiFi wavelength at 2.4 GHz is ~12.5 cm. Spatial features smaller than roughly half a wavelength (~6 cm) cannot be resolved. Individual finger joints are 1–3 cm apart. **Finger-level pose reconstruction is physically impossible with 2.4 GHz WiFi CSI.**

The analysis is written up in full, with its references, in `RESEARCH.md` §8 — and it ends by noting that the ESP32-S3's CSI capability is retained as a *free* coarse presence channel (is the hand in the "under desk" zone or not), because zero-cost optionality is worth keeping even when the primary use is dead. **Killing an attractive idea with a wavelength calculation, then salvaging the part that still pays, is a more useful signal than any successful build step.**

### 7.2 The "bat model," rejected — but its insight kept

The first architectural instinct was echolocation from a fixed base station: ping the room, let the hand reflect, reconstruct pose from the echo pattern, no glove needed. It was rejected on the grounds that a hand is an articulated 27-joint reflector with heavy self-occlusion, and echo→pose is an unsolved inverse problem at useful accuracy.

The write-up on the rejection is explicit about what survived: *the echolocation intuition is valid — it just needs to be on the hand itself rather than at a base station.* Same for the rejected distributed-anchor-network idea, where the transponder concept was kept but the "ultrasonic emitters everywhere" infrastructure was traded for 3–4 UWB pucks in the v2 design.

Every rejected idea in `RESEARCH.md` §5 is documented with **why rejected** *and* **what was kept**. That is a habit of thought worth naming in a statement.

### 7.3 Designing the failure mode of the supply chain

CH-101 sensors come from a single practical vendor with a history of multi-month TDK-driven stockouts. Rather than accept that as an unmanaged risk, the architecture was arranged around it: **v1 (Phase 4) is a complete, working, shippable glove that contains no CH-101 at all.** If ultrasonic supply collapses entirely, there is still a glove. Parts are ordered at Phase 3 for a Phase 5 need; a backup vendor is named; and a worst-case pivot (v2 becomes an ML gesture-classification milestone on the existing modalities) is written down in advance.

Sequencing the project so that its riskiest dependency sits *after* the shipping milestone is a scheduling decision, not a technical one — and it is the kind of decision that separates a project that ships from one that doesn't.

### 7.4 Refusing to silently absorb a budget overrun

The Phase 2 BOM came in at ~$98 against a $50–75 estimate, because Adafruit VL6180X breakouts are $13.95 each and six are needed. Rather than quietly overspending or quietly downgrading, the BOM document states the overrun, prices the alternative (no-name 4-packs, ~$30–40 for eight units, saving ~$50), names the specific risk of the cheap path — **clone boards frequently omit onboard pull-up resistors and have address-collision issues** — recommends the safer part *for a first-time I²C-mux build specifically*, and then explicitly defers the call to ordering time. The reasoning is preserved so the decision can be revisited with better information rather than re-derived from scratch.

### 7.5 Choosing a wire protocol in Phase 0 that survives to Phase 6

The Phase 0 firmware emits **newline-delimited JSON**, one complete object per line: `{"t_ms":105,"button_count":3}`. The kickoff doc states the reason at the time of the choice: *this is the same line format the host uses through all later phases, so the Phase 0 reader keeps working as we add more fields.*

It held. The Phase 1 host code parses `{"t_ms":...,"w":...,"x":...,"y":...,"z":...,"cal_sys":...}` through the *same* `stream_port()` function written for a button counter, with a thin `quaternion_stream()` filter layered on top that skips non-quaternion lines (boot events, I²C scan results) rather than choking on them. Additive schema evolution, designed in on day one, with forward-compatible parsing.

### 7.6 Treating `platformio.ini` as a lockfile

Exact library versions are pinned and committed (`platform = espressif32@6.7.0`, `adafruit/Adafruit BNO055@^1.6.3`, …), and each phase gets its own self-contained PlatformIO project under `firmware/phaseN-<name>/`. The stated rationale: each phase's firmware stays independently buildable, library drift in one phase can't break another, and a future contributor can point at `firmware/phase1-imu/` as a minimum-viable BNO055 example without dragging in the whole glove. Reproducibility and reusability decided up front, not retrofitted.

---

## 8. Debugging stories (verified, with the actual lesson)

All of these are recorded in `LEARNINGS.md` with dates, which is itself the point — the log exists so that lessons compound.

### 8.1 The button that was rotated ninety degrees *(builder's pick)*

`digitalRead` never changed on press. The instinct — for someone who writes software — is to suspect the firmware, then the pull-up, then the GPIO. It was none of those. A 4-pin tactile switch has **two internally-shorted pairs of legs along its long axis**; placed in the wrong rotation, pressing it connects two legs that were already connected. The component was electrically perfect and mechanically working. It was simply installed 90° off.

**The lesson, as written down:** *if `digitalRead` never changes on press, try rotating the button 90° before suspecting wiring or firmware.* The broader one, which belongs in a personal statement: physical-layer bugs have a failure grammar that software instincts do not cover. The first real hardware bug was not a bug in anything.

### 8.2 The invisible LED and the bootloader dance *(builder's pick)*

Two Phase 0 lessons that arrived together on 2026-05-24:

- `digitalWrite(2, HIGH)` does nothing on an ESP32-S3 DevKitC-1. There is no LED on GPIO 2 on this board. The onboard LED is an **addressable WS2812B RGB on GPIO 48**, driven by `neopixelWrite(48, r, g, b)`. The canonical first program in all of embedded — blink an LED — failed because the LED was a different *kind of device* than assumed, on a different pin than the tutorials say.
- Flashing requires a manual ritual every single time: hold BOOT, tap RST, release BOOT. The board then **re-enumerates under a different `/dev/tty.usbmodem*` path in bootloader mode than in run mode**, so the upload port changes between states. And after flashing, esptool's RTS hard-reset does not reliably exit bootloader mode with native USB-CDC — the reliable move is to unplug and replug the cable.

Neither is in a datasheet's headline. Both were recorded the day they were learned, and both are quoted in `STATE.md`'s "don't redo this" section — which is why they cost time once instead of repeatedly.

### 8.3 The bug that was in `~/.zshrc`

PlatformIO builds failed with errors pointing into `/Library/Developer/CommandLineTools/SDKs/MacOSX.sdk/`. The cause was **line 41 of `~/.zshrc`**, which appended macOS C++ SDK headers to `CPLUS_INCLUDE_PATH` — making host system headers visible to the Xtensa *cross-compiler*, which is exactly what a cross-compiler must never see.

Nothing in the project was wrong. The bug was in the shell environment, predated the project, and would break any GCC cross-compiler on that machine. It was fixed with a dated comment explaining why the line is disabled, logged, and — notably — a *recurrence check* was written into `STATE.md`: if Xtensa builds ever fail with macOS SDK paths again, check that line first.

### 8.4 The wrong chip in the box

The starter kit on hand was assumed (and specified throughout the design doc) to contain an ESP32-S3. Reading the official parts list carefully revealed an **ESP32-WROVER-E** — original ESP32, Xtensa LX6, micro-USB. The entire plan named the S3.

Two options: rewrite the plan around the WROVER, or change what the kit is *for*. The decision was the second — **demote the starter kit to a component source** (breadboard, jumpers, sensors, discretes) and keep the separately-ordered ESP32-S3 DevKitC-1 two-pack as the sole firmware target, leaving the spec intact end to end. The decision, the reasoning, and the specific trap it creates (*do not "fix" the build by switching to `board = esp32dev`*) are all recorded, in three places.

Catching a foundational assumption error from a parts-list image *before* wiring anything is worth more than most successful build steps.

### 8.5 The abstraction that was elegant and unusable

`parse_lines()` was written first as the clean, pure, fully unit-testable function: take a byte stream, yield parsed dicts. It has tests. It works.

It cannot be used on a live serial port. It reads chunks into a buffer until the stream ends — and **a live serial port never ends**. The function would buffer forever and yield nothing. The fix was a second function, `stream_port()`, built on a `readline()` loop, with a docstring that states the split honestly: *"Not unit-tested (needs hardware). Use `parse_lines()` for anything testable."*

The lesson is a real software-engineering one, learned from hardware: **testability pressure had produced an interface whose semantics silently didn't match the real data source.** The resolution was not to force one abstraction to cover both, but to keep two with an explicit, documented boundary between the testable and the physical.

### 8.6 A dependency that wasn't resolved transitively

`Adafruit BNO055` depends on `Adafruit BusIO`, but PlatformIO on `espressif32@6.7.0` does not reliably resolve it as a transitive dependency — the build fails deep inside BusIO with `SPI.h: No such file or directory`, an error that points nowhere near the actual cause. Fix: list `adafruit/Adafruit BusIO@^1.16.1` explicitly in `lib_deps`. Generalized in the log: *this applies to any Adafruit sensor library that pulls in BusIO.*

---

## 9. Working while blocked — Phase 1 as a case study

The BNO055 had not arrived. The obvious move is to wait. What actually happened, on 2026-05-25, in a single working session, is the most quietly impressive sequence in the git history:

| Commit | Work |
|---|---|
| `1a7017e` | Phase 1 kickoff doc with concept primers (quaternions, on-chip fusion, interrupt vs polled) |
| `104308a` | PlatformIO project scaffolded, libraries pinned |
| `a810714` | The BusIO dependency gotcha, hit and logged, before the sensor existed |
| `89b970b` | Firmware skeleton — complete except the two intentional learning gaps |
| `1854248` | Host dependencies added (numpy, pygame, PyOpenGL) |
| `4a625f6` | `imu_reader` with `parse_quaternion` **and its unit tests** |
| `f49e26f` | pygame + PyOpenGL wireframe-cube viewer, threaded, with a latest-wins queue |
| `306671b` | **Both automated verification scripts — V1 (rate) and V3 (no-jumps)** |
| `f69e9a2` | State updated: software done, blocked on hardware |
| `7d18098`, `3b26ba0`, `f9b3558` | Phase 2 BOM researched + the new "BOM one phase ahead" convention that came out of the block |

Everything that could be built against a *specified wire protocol* rather than against a physical device was built, tested, and committed — including the pass/fail criteria the hardware will eventually be judged against. **The verification scripts were written before the sensor existed.** When the BNO055 arrives, the sequence is: solder, wire, photograph, fill in two lines, flash, run three scripts. Pass or fail is already decided by code that exists.

Two details in the viewer worth noting as evidence of real-time thinking rather than tutorial-following:

- The serial reader runs in a **daemon thread** feeding a `queue.Queue(maxsize=10)`, and on a full queue it **drains an entry before putting a new one** — so the display always shows the freshest pose and never accumulates lag. That is a latency decision, made deliberately: *drop old frames, never queue them.*
- `viewer.py` is explicitly **not** unit-tested, and the design doc says so and says why (needs a display and hardware), with the manual verification criterion named instead. Deciding where automated testing stops, and writing that decision down, is more mature than pretending to 100% coverage.

And the V3 verification criterion itself — `|dot(q_n, q_{n+1})| ≥ 0.99` across five minutes of samples — is a genuinely good test. It catches quaternion sign flips, fusion resets, and dropped samples, none of which a human watching a cube rotate would reliably notice.

---

## 10. Self-assessment, in the builder's own words

From the Phase 0 retrospective (`docs/phases/phase0-retro.md`), written at the phase gate:

- **What surprised me:** `neopixelWrite` vs `digitalWrite` for the RGB LED · the ESP32-S3 bootloader entry dance · **how easy it is once you know the basics**
- **What felt rote / I'd skim next time:** verifying the connections, once I got hold of the basics
- **What I want more depth on in Phase 1:** **how does Madgwick/Mahony fusion work under the hood?** · how does the code work?
- **Time:** ~2 weeks calendar, ~10 active hours
- **Cost:** $141.82 post-tax vs. a $124–161 estimate

Three things a reader should take from that retro. First, the honest arc of a beginner's first month — mystery to routine, and the willingness to say "how easy it is once you know the basics" rather than dramatize the difficulty. Second, the depth question: the chip does the sensor fusion, and the response to that convenience was to want to know what it's doing internally — which then became a filed parking-lot item to implement Madgwick from scratch, on purpose, later. Third: the estimate was tracked against actuals, at a phase gate, in writing.

---

## 11. Concrete detail bank

Facts, numbers, and specifics that can be dropped into prose. All verified against the repository.

**Numbers**
- 32 commits · 7 phases (0–6) · 2 shipped-milestone gates (v1 at Phase 4, v2 at Phase 6)
- Phase 0: 10 active hours, 12 calendar days, 4/4 verification criteria met, `git tag phase-0`
- ~2,500 lines of specification and planning documents committed before the corresponding code
- Budget: $200–400 planned; ~$225–320 for v1; $141.82 actual for Phase 0
- Target: 5–8 hrs/week, 6–9 months to v1
- v1 gate: ≥30 fps, <100 ms latency, no drift over 5 min, **re-runs from one command a week later**

**Parts and stack**
- ESP32-S3-DevKitC-1 (WROOM-1, N16R8) · Arduino framework via PlatformIO for Phases 1–4, ESP-IDF for 5–6 (FreeRTOS needed for CH-101 crosstalk timing)
- BNO055 @ I²C `0x28`, NDOF mode · VL6180X @ `0x29` ×5 behind a TCA9548A mux @ `0x70` · CH-101 PMUT ×6 · 500 mAh LiPo + TP4056
- Host: Python 3.12 via `uv`, pyserial, bleak, numpy/scipy/filterpy, pygame + PyOpenGL, pytest
- macOS on Apple Silicon, exclusively. No NVIDIA GPU. No 3D printer. No VR headset.

**Phrases with teeth**
- "The hand is its own reference frame." (why no external anchors are needed)
- "No subjective 'looks fine' passes." (the verification-gate rule)
- "Buy in phases, not upfront."
- "Two-week rule: no infinite tunneling."
- "Treat `platformio.ini` as a lockfile."
- "The learning is in the debug, not the result." (from the risk register's "normal, not risk" section)
- "Ultrasonic is the one modality the commercial players haven't embraced."

**Contrast anchors**
- Manus Quantum: ~$7,500–9,000 · Rokoko Coil Pro: ~$895–2,500 · HaptX G1: enterprise-only, requires a pneumatics backpack · CyberGlove: ~$10,000+
- LucidGloves (the DIY standard): potentiometers + string + badge reels, ~$22/pair
- EchoGlove target: under $500 all-in, open-source, MIT licensed

**Forward-looking, and honest about it**
- Phase 6 requires either a learned distance-matrix→pose model (needing ground-truth labels from a Quest 3 or Leap Motion) or a biomechanical skeletal model. **The skeletal model is the chosen v1 path** — joint constraints reduce the degrees of freedom enough to replace the learned mapping, and it needs no additional hardware. That choice, and its reasoning, is already written down.
- Robotics teleoperation is named in the research as the strongest secondary market: Manus has pivoted there, and DOGlove (arXiv 2025) identifies low-cost open-source teleop gloves as an unmet need. **This is the natural bridge from EchoGlove to a robotics program** — imitation-learning data collection needs exactly this device at exactly this price.

---

## 12. Guardrails — what must not be claimed

The project's own stated principle is *"I won't claim something I didn't build."* Hold the statement to it.

**True and claimable:**
- Designed the full system architecture, the seven-phase roadmap, the verification criteria, and the risk register.
- Researched the prior art thoroughly enough to identify a genuine gap, and documented every rejected alternative with its reasoning.
- Shipped Phase 0 against four objective criteria: toolchain, LED, button + JSON serial, and a raw MPU-6050 I²C read at 10 Hz.
- Wrote and tested the complete Phase 1 host stack — parser, viewer, unit tests, and two automated verification scripts — plus the firmware skeleton.
- First-time solderer, first-time board bring-up, on a Mac-only toolchain.

**Not yet true — do not imply otherwise:**
- ❌ The glove does not exist as a wearable. No sensors on fabric, no LiPo, no BLE.
- ❌ No ultrasonic sensor has been touched. CH-101 is Phase 5; none purchased.
- ❌ No Kalman filter has been implemented. Phase 4.
- ❌ The BNO055 has not been read from hardware — the Phase 1 firmware is still a skeleton with two intentional blanks, and V1/V2/V3 have not been run.
- ❌ No inverse kinematics, no hand rig, no pose reconstruction of any kind yet.
- ❌ Nothing is published; the repository is private.

**The right frame:** this is a rigorously planned, actively-in-progress build with one phase formally shipped and the next one's software complete and blocked on hardware. Its strength as an application artifact is not a finished device — it is the demonstrated *method*: a hard problem correctly scoped, honestly researched, decomposed into verifiable increments, and executed with the discipline to stop at gates, write down what was learned, park the tangents, and survive a three-month interruption without losing the thread.

---

*Sources: `README.md`, `RESEARCH.md`, `STATE.md`, `LEARNINGS.md`, `CLAUDE.md`, `docs/superpowers/specs/`, `docs/superpowers/plans/`, `docs/phases/`, `hardware/`, `firmware/`, `host/`, and 32 commits from 2026-05-12 to 2026-05-25.*
