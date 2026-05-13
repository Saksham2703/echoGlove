# EchoGlove — Research Library

> This document is a living reference capturing all research, prior art, design decisions, and rejected ideas explored during the EchoGlove project. It is intended as a "why we built it this way" document for contributors and future development.

---

## Table of Contents

1. [Origin: IR Photodiode Hand Tracking](#1-origin-ir-photodiode-hand-tracking)
2. [Sensor Stack Design](#2-sensor-stack-design)
3. [Prior Art & Existing Implementations](#3-prior-art--existing-implementations)
4. [Commercial Landscape](#4-commercial-landscape)
5. [Rejected Ideas](#5-rejected-ideas)
6. [Under-Desk Tracking Analysis](#6-under-desk-tracking-analysis)
7. [6DOF World-Space Position](#7-6dof-world-space-position)
8. [WiFi CSI Sensing — Investigated & Ruled Out](#8-wifi-csi-sensing--investigated--ruled-out)
9. [Feasibility & Engineering Concerns](#9-feasibility--engineering-concerns)
10. [Market & Use Cases](#10-market--use-cases)
11. [Key References](#11-key-references)

---

## 1. Origin: IR Photodiode Hand Tracking

The project originated from a Twitter/X post showing hand tracking using an **IR LED + photoresistor** pair. Understanding this baseline is useful context.

### How simple IR reflectance sensing works

- An IR LED emits infrared light (typically ~940 nm wavelength)
- A photoresistor or photodiode measures how much IR light bounces back from the hand
- When the hand is closer, more light reflects → higher reading; farther away → lower reading
- A microcontroller reads this analog value and maps it to a position

This is **reflectance-based proximity sensing**, not true ranging — it measures brightness of reflected light, not time-of-flight. It is sensitive to ambient IR light (sunlight, incandescent bulbs), skin tone, surface texture, and clothing colour.

### Limitations of bare IR reflectance for hand tracking

- Gives 1D proximity only from a single sensor pair
- 2D tracking requires multiple pairs or scanning (reduces effective framerate)
- Ambient light interference is significant without modulation
- Accuracy degrades with distance nonlinearly
- Not suitable for precise finger pose reconstruction

### Why we kept IR in the stack

Rather than discarding IR entirely, we repurposed it. On a glove, the hand is the sensor platform — outward-facing IR ToF sensors (e.g. STMicro VL6180X) on fingertips become a **short-range close-interaction layer** (0–20 cm), complementing ultrasonic (which struggles below ~2 cm). This covers pinch detection, fingertip-to-surface contact, and fine finger proximity that ultrasonic cannot resolve cleanly.

---

## 2. Sensor Stack Design

EchoGlove's three-modality stack was designed so each sensor covers the blind spots of the others.

### 2.1 Ultrasonic ToF (primary pose sensor)

**Chosen part:** TDK/Chirp CH-101 MEMS PMUT (Piezoelectric Micromachined Ultrasonic Transducer)

- Package: 3.5 × 3.5 mm — small enough for fingertip mounting
- Range: ~2 cm to 1.2 m
- Accuracy: millimetre-level
- Interface: I²C / SPI
- Power: low (key for battery-powered glove)
- Update rate: ~60 Hz practical with sequenced firing

**How it works for hand pose:** Sensors are distributed across fingertips and palm. Each sensor measures time-of-flight distances to the others. The resulting **pairwise distance matrix** is fed into either a biomechanical skeletal model or a learned neural network (as demonstrated in UltraGlove) to reconstruct full hand pose. The hand is its own reference frame — no external anchors needed for finger pose.

**Key engineering challenge — crosstalk:** Multiple CH-101s cannot fire simultaneously or they cannot distinguish which ping came from where. Mitigation:
- Time-division multiplexing: sensors fire in sequence
- Digital mux (e.g. TCA9548A I²C multiplexer) for bus management
- Expected-range thresholding: discard readings inconsistent with hand geometry

### 2.2 IR Proximity / ToF (close-range fingertip layer)

**Chosen part:** STMicroelectronics VL6180X (0–20 cm) or VL53L0X (up to 1.2 m)

- Uses laser ToF, not raw IR reflectance — immune to ambient light and skin tone variance
- I²C interface, hobbyist-grade, well-documented
- Mounted outward-facing on fingertips

**Role:** Fills the sub-2 cm gap where ultrasonic is weakest. Primary applications:
- Pinch detection (index finger to thumb proximity)
- Fingertip-to-surface contact
- Finger-to-finger close interaction (e.g. crossing fingers)

### 2.3 IMU (orientation + high-rate interpolation)

**Chosen part:** Bosch BNO055 (or ICM-42688-P for higher performance)

- Provides absolute orientation via sensor fusion of accelerometer + gyroscope + magnetometer
- Update rate: 100–400 Hz — much faster than ultrasonic's ~60 Hz
- Mounted on back of hand (dorsum)

**Two roles:**
1. **Global hand orientation** — critical for VR/SteamVR integration where the system needs to know which way the hand is pointing in world space, not just finger curl values
2. **High-rate fill-in** — IMU quaternion delta fills in pose estimates between slower ultrasonic frames, smoothing output and reducing perceived latency

**Known IMU limitation:** Gyroscope drift accumulates over time. Magnetometer is susceptible to interference from motors, speakers, and electronics (especially relevant in robotics). Ultrasonic pose estimates serve as a periodic correction anchor for IMU drift.

### 2.4 Sensor fusion architecture

```
Ultrasonic distance matrix (~60 Hz)  ─┐
                                       ├→ Kalman filter / learned model → Hand pose (6DOF fingers)
IMU quaternion + accel (~200–400 Hz) ─┘

IR fingertip proximity (~100 Hz) ──────→ Layered on top as interaction events (pinch, contact)

(Optional v2) UWB ranging (~100 Hz) ───→ Wrist position in world space (3DOF translation)
IMU orientation ───────────────────────→ Hand orientation in world space (3DOF rotation)
```

### 2.5 Microcontroller

**Chosen part:** ESP32-S3

- Dual-core, sufficient compute for on-device sensor preprocessing
- WiFi + BLE built-in — flexible output options
- Large enough flash/RAM for lightweight ML inference if needed
- ESP-IDF CSI support: WiFi Channel State Information accessible as a bonus ambient sensing signal (not used for hand tracking, but available)
- Mature ecosystem, widely used in DIY wearables

---

## 3. Prior Art & Existing Implementations

After reviewing arXiv, IEEE Xplore, ACM Digital Library, GitHub, Hackaday, and Instructables, **no published project uses the exact ultrasonic + IR ToF + IMU combination on a single glove**. The three-modality stack represents a genuine open-source gap.

### 3.1 UltraGlove (Princeton / SIGGRAPH Asia 2023) — closest academic precedent

- **Paper:** [arXiv:2306.12652](https://arxiv.org/abs/2306.12652) / [ACM](https://dl.acm.org/doi/10.1145/3610548.3618202)
- Uses CH-101 MEMS ultrasonic sensors as the *sole* modality
- Pairwise distance matrix → neural network → hand pose
- Explicitly excludes IMU and optical sensing (citing drift and occlusion problems)
- Demonstrated size-agnostic, magnetically-immune hand tracking
- **Not open-source, not a buildable kit** — research paper only
- EchoGlove is effectively the open-source implementation of UltraGlove's core idea, extended with IMU and IR layers

### 3.2 Visual-Inertial Gloves (IR + IMU, no ultrasonic)

- University of Delaware / IROS 2019 workshop: five MPU-9250 IMUs on fingers/dorsum + IR LED beacons tracked by external camera
- IR here is used for external localisation (camera tracks the beacon), not on-glove proximity sensing
- [Paper](https://udel.edu/~ghuang/iros19-vins-workshop/papers/05.pdf)

### 3.3 Wearable Ultrasonic Arm Tracking (ultrasonic + IMU, no IR, no glove)

- Qi et al. (IEEE EMBC 2014): body-mounted ultrasonic anchors + unscented Kalman filter for arm joint reconstruction
- Covers arm-level tracking, not fingers
- [IEEE Xplore](https://ieeexplore.ieee.org/document/6944986/)

### 3.4 EMG + Ultrasound Armband (ETH Zurich, arXiv 2025)

- Fuses 8-channel EMG + 4-channel A-mode ultrasound on a wrist armband
- Tracks 23 DoF hand/wrist kinematics at sub-50 mW
- Demonstrates ultrasound + another modality is viable in wearable power envelopes
- [arXiv:2510.02000](https://arxiv.org/html/2510.02000v2)

### 3.5 DIY / hobbyist glove landscape

The DIY space is dominated by **flex sensors + IMU** and **potentiometer + string** designs. No DIY project found uses on-glove ultrasonic ToF sensors.

| Project | Sensors | Notes |
|---|---|---|
| **LucidGloves / LucidVR** | Potentiometers + string + badge reels | De facto DIY VR standard, ~$22/pair, OpenGloves compatible |
| **OpenGloves driver** | Hardware-agnostic | SteamVR driver accepting finger curl/splay from any hardware |
| **Fngrs** | Similar to LucidGloves | Weekend project by same author, <£50 |
| **SlimeGloveVR** | LucidGloves + SlimeVR IMU trackers | Full-body + finger tracking integration |
| **nfelber/IMU-Motion-Tracking-Glove** | 6× IMUs + BLE | Open-source, Rust driver |
| **Modular IMU glove (arXiv 2024)** | 11× IMUs + ESP32 | 9.17° avg joint RMSE, ~21.8 Hz, ~63 min battery |
| **Helping Hand** | Flex sensors + IMU + TensorFlow | Rehab gesture classification |
| **Mocap Fusion Gloves** | 5× flex sensors + nRF24 + Vive Tracker | SteamVR mocap |
| **Kobakant / mi.mu DIY** | 8× bend sensors + ArduIMU | Textile glove, music-focused |
| **Manucon** | MPU-6050 + flex sensor | RC aircraft control |
| **ASLglove** | 4× flex + 1× IMU | ASL alphabet classification |

### 3.6 Sign language & accessibility gloves

A large body of academic work uses flex sensor + IMU combinations for sign language translation. Most recent work adds ML classifiers (SVM, CNN, LSTM). No ultrasonic or IR ToF sensors appear in this literature.

---

## 4. Commercial Landscape

### 4.1 Summary table

| Product | Sensing | Price (approx) | Notes |
|---|---|---|---|
| **CyberGlove II/III** | 18–22 resistive bend sensors | ~$10,000+ | Oldest professional lineage; known nonlinearity at low flex |
| **Manus Prime II** | Flex sensors + IMU + external tracker | ~$1,500–3,000 | 11 DoF/finger |
| **Manus Quantum Metagloves** | EMF transmitter + EM receivers + IMU | ~$7,500–9,000 | Sub-mm fingertip accuracy, drift-free |
| **Rokoko Smartgloves II** | IMU + EMF fusion ("Volta Tracking") | ~$895–2,500 | Cheapest good commercial option; Coil Pro needed for drift-free |
| **HaptX Gloves G1** | Magnetic mocap (30 DoF) + 133 haptic actuators | Enterprise only | Requires backpack pneumatics |
| **StretchSense MoCap Pro** | 32 capacitive stretch sensors + ML | — | No IMU/EMF; immune to magnetic interference |
| **Noitom Hi5** | IMU + Vive Tracker | ~$999 | One of first consumer mocap gloves |
| **Contact CI Maestro EP** | Finger caps + force feedback | ~$3,750 | Typically paired with Ultraleap for pose |
| **SenseGlove Nova 2** | Force + vibrotactile + optical tracking | ~$5,999 | — |
| **Ultraleap Leap Motion 2** | NOT a glove — stereo IR cameras | ~$149 | Main camera-based alternative |
| **mi.mu Gloves** | Bend sensors + IMU + WiFi | ~$2,000+ | Music-focused, commercial since 2019 |
| **UDCAP VR Gloves** | 12 sensors, 15 joints | ~$300–500 | Prosumer VRChat/VTubing |
| **Diver-X Contact Glove 2** | Finger curl + haptics | ~$400 | VRChat-focused, 2024 |

### 4.2 The commercial trajectory

The industry has moved from **bend-sensor-only** (CyberGlove era) → **IMU + flex** (early Manus Prime) → **IMU + EMF fusion** (Rokoko, Manus Quantum, HaptX). The EMF layer solves IMU drift and gives absolute position without cameras. Ultrasonic is the one modality the commercial players haven't embraced, despite UltraGlove's published case that it solves the same problem EMF solves — at lower cost and without a precision wound-coil transmitter.

### 4.3 Robotics teleoperation — emerging market

Manus has explicitly pivoted to humanoid robot teleoperation and imitation learning data collection. Papers like DOGlove (arXiv 2025) identify low-cost open-source haptic teleop gloves as an unmet need. This is a strong secondary target market for EchoGlove.

---

## 5. Rejected Ideas

### 5.1 Bat model — pure acoustic echolocation from a fixed base station

**Idea:** A fixed base station emits ultrasonic pulses; the hand reflects echoes; the station reconstructs hand pose from the echo pattern. No glove required.

**Why rejected:**
- A hand is a complex, articulated reflector with 27 joints and significant self-occlusion between fingers
- Echo-based full hand pose reconstruction is an open, unsolved research problem at useful accuracy
- Reconstructing from a messy waveform back to precise 3D pose requires solving a very hard inverse problem
- Microsoft and others have explored acoustic gesture recognition but not full hand pose from echo

**What was kept:** The insight that echolocation-inspired sensing is valid — it just needs to be on the hand itself (UltraGlove architecture) rather than at a base station.

### 5.2 Distributed anchor network (ultrasonic nodes at multiple locations)

**Idea:** Multiple ultrasonic emitter/receiver nodes at known positions around the workspace; fingertip transponders on the glove respond to pings and trilaterate position.

**Why rejected:**
- Requires "ultrasonic emitters everywhere" — not practical for a consumer/hobbyist setup
- Anchor proliferation defeats the portability goal
- Same problem solved more elegantly by UWB (see Section 7)

**What was kept:** The transponder concept — a minimal glove responding to external pings rather than doing all sensing internally — is architecturally sound. It's just that UWB does this with 3–4 small pucks instead of a full anchor array.

### 5.3 WiFi CSI as a primary sensing modality

**Idea:** Use WiFi Channel State Information to sense hand movements — no glove at all.

**Why rejected:** See Section 8 for full analysis. Short version: WiFi CSI cannot resolve features smaller than roughly half the WiFi wavelength (~6 cm at 2.4 GHz), making finger-level pose reconstruction physically impossible. It is good for coarse gesture classification but not hand pose tracking.

**What was kept:** The ESP32-S3's CSI capability remains accessible as a bonus ambient channel, potentially useful for room-scale hand presence detection as a complement to on-glove sensing.

---

## 6. Under-Desk Tracking Analysis

A key design requirement is that EchoGlove must work when the hand is below the desk — a common position during computer use.

### What works without degradation

- **IMU** — orientation measurement is entirely unaffected by occlusion or position. Works identically everywhere.
- **IR fingertip ToF** — measures finger-to-finger and fingertip-to-surface distances. No external reference needed. Works identically under a desk.
- **Ultrasonic inter-finger ranging** — sensors measure distances *between each other* on the same glove. The hand is its own reference frame. No external line-of-sight needed.

### The one real concern: desk underside reflections

With the hand under the desk, ultrasonic pulses may reflect off the desk underside before reaching the intended target sensor, creating spurious short-distance readings.

**Mitigations:**
- CH-101 uses coded pulse sequences — sensors can be distinguished by their codes
- A flat desk surface has a very different echo signature than curved finger/palm geometry
- Expected-range thresholding: discard readings outside the anatomically plausible range for any given sensor pair
- Directional transducer mounting (angled away from desk surface)

### What is genuinely lost under a desk

**Absolute hand position in world space** — i.e. where the hand is in the room in XYZ coordinates. The IMU provides orientation but its position estimate drifts over time (all IMUs do), and without periodic external correction it becomes unreliable within seconds to minutes.

### Why this is acceptable for most use cases

| Use case | Needs absolute world position? |
|---|---|
| VR / VRChat finger tracking | No — finger pose + relative hand orientation sufficient |
| Gesture control (media, smart home) | No — gesture classification only |
| Robotics teleoperation | Sometimes — depends on robot arm workspace |
| Music / OSC performance | No — gesture and orientation sufficient |
| Motion capture for animation | Sometimes — depends on capture setup |

For the cases that do need absolute position, see Section 7.

---

## 7. 6DOF World-Space Position

For applications requiring absolute 6DOF position (3 translational + 3 rotational) in world space, the following options were evaluated.

### 7.1 UWB — recommended approach

**Technology:** Ultra-Wideband (IEEE 802.15.4a/4z)

**Chosen chip:** Qorvo / Decawave DW3000

**How it works:** UWB emits extremely short (nanosecond) radio pulses and measures time-of-flight with centimetre-level accuracy. A small UWB tag on the glove wristband ranges against 3–4 fixed anchor pucks at known positions. Trilateration yields wrist XYZ position. Combined with BNO055 IMU orientation, this gives full 6DOF.

**Why UWB:**
- Centimetre-level position accuracy
- Works under desks, through occlusion, in the dark
- 3–4 anchors only — manageable infrastructure
- Consumer-proven (Apple AirTag, iPhone U1, Samsung SmartTag+)
- DW3000 is hobbyist-accessible, I²C/SPI interfaced, ~$5–15 per chip
- Adds ~$20–30 to BOM for the glove-side tag
- Independent of the finger-pose architecture — can be added as v2 without redesigning the glove

**Limitations:**
- Anchors required — not completely infrastructure-free
- ~3–4 anchor pucks needed for good 3D coverage
- Anchors need to be placed with clear line-of-sight to the wrist (not always guaranteed)

### 7.2 Visual-Inertial Odometry (VIO) — rejected for v1

A wrist-mounted camera tracks visual features in the environment (SLAM-style) to estimate position. Works under desks with sufficient ambient light. Compute-heavy; adds a camera, partially defeating the "no camera" philosophy. Kept as a future option for environments where UWB anchors are impractical.

### 7.3 Acoustic beacons — rejected

3 fixed ultrasonic beacons at known positions, wrist transponder ranging against them. Leverages existing ultrasonic hardware knowledge. Rejected because it reintroduces the infrastructure problem from the rejected anchor network idea, just at smaller scale. UWB is simpler, more accurate, and better proven.

### 7.4 Electromagnetic (EMF) — rejected

A single EM transmitter coil at known position, EM receiver on wrist. This is what Manus Quantum and Rokoko Coil Pro use. Sub-millimetre accuracy, works through occlusion. Rejected because: (a) sensitive to nearby metal and electronics, (b) proprietary and expensive at commercial quality, (c) UWB solves the same problem without magnetic interference issues.

### 7.5 Periodic drift correction — simple fallback

Use IMU for position between corrections; snap back to a known reference when the hand touches a fiducial surface (e.g. a specific spot on the desk). Crude but effective for use cases that only occasionally need absolute position. This requires no additional hardware and is available as a baseline even without UWB.

### 7.6 Recommended implementation plan

- **v1:** No absolute position. IMU orientation only. Covers all primary use cases.
- **v2:** Add DW3000 UWB tag to wristband + 3–4 anchor pucks. Full 6DOF. Designed as a drop-in module that communicates with ESP32-S3 over SPI without redesigning the rest of the glove.

---

## 8. WiFi CSI Sensing — Investigated & Ruled Out

WiFi Channel State Information (CSI) sensing was investigated as a potential modality. This section documents the findings.

### What WiFi CSI sensing is

Every WiFi transmission travels across multiple frequencies simultaneously (subcarriers). When a body or hand moves through the space, it disturbs the path of those waves in measurable ways. By measuring amplitude and phase of each subcarrier (CSI), rather than just aggregate signal strength (RSSI), it is possible to infer information about movement in the environment.

### What it can do

- Coarse gesture recognition — push, swipe, wave, stop — at ~99% accuracy in controlled environments (HandFi, University of Hyderabad, 2024)
- Activity recognition — sitting, standing, walking, breathing
- Through-wall presence detection and coarse body pose
- Runs on an ESP32-S3 (CSI data accessible via Espressif's esp-idf)

### Why it cannot track hand pose

The fundamental physical limit: WiFi wavelength at 2.4 GHz is ~12.5 cm. You cannot resolve spatial features smaller than roughly half a wavelength (~6 cm). Individual finger joints are 1–3 cm apart. **Finger-level pose reconstruction is physically impossible with 2.4 GHz WiFi CSI.**

Additionally, CSI is highly sensitive to environmental changes — other people moving, furniture rearrangement, different rooms — making it unreliable for a portable device used in varying environments.

### Why the ESP32-S3's CSI capability is still kept

The ESP32-S3 exposes CSI data as a byproduct of its WiFi radio at zero additional hardware cost. This could be useful as a coarse room-scale presence/activity layer — knowing that the hand is in the "under desk" zone vs. "above desk" zone — as a complement to on-glove precise sensing. This is a future research direction, not a primary modality.

### Key references

- HandFi (University of Hyderabad, 2024): [ACM](https://dl.acm.org/doi/10.1016/j.procs.2024.04.042)
- WiFi CSI gesture recognition survey: [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S0952197619302441)
- ESP32 CSI tool: [GitHub](https://github.com/wrlab/Wi-ESP)
- WiFi hand pose detection (body-level only): [GitHub](https://github.com/euaziel/WiFi-CSI-Human-Pose-Detection)

---

## 9. Feasibility & Engineering Concerns

### 9.1 I²C bus management

Running 10+ I²C sensors (CH-101 × 6, VL6180X × 5, BNO055 × 1) on a single bus is not possible due to address collisions. Solution: **TCA9548A I²C multiplexer** (or multiple muxes). This is a well-documented pattern in IMU-glove research. Each sensor group gets its own I²C channel, selected by the mux.

### 9.2 Ultrasonic crosstalk sequencing

Multiple CH-101 sensors cannot fire simultaneously. Time-division multiplexing is mandatory. Each sensor fires in sequence; others listen. UltraGlove uses digital muxes and synchronised I²C buses for this. The sequencing reduces effective update rate — with 6 sensors, naively sequential firing at 60 Hz per sensor yields ~10 Hz full-hand updates. Pipelining (one sensor fires while previous echo is still being processed) can recover much of this.

### 9.3 Power budget

Rokoko Smartgloves: ~1 hour per 1000 mAh with 7 sensors. EchoGlove's sensor count is higher. Rough estimates:

| Component | Est. current draw |
|---|---|
| ESP32-S3 (active) | ~80–240 mA |
| CH-101 × 6 | ~6 mA total (1 mA each) |
| VL6180X × 5 | ~10 mA total (2 mA each) |
| BNO055 | ~3.4 mA |
| DW3000 UWB (v2) | ~30–50 mA active |
| **Total (v1 est.)** | **~100–270 mA** |

A 500 mAh LiPo on the wristband gives roughly 2–5 hours depending on radio activity and sampling rates. Power gating inactive sensors between measurements will extend this significantly.

### 9.4 Flex wiring and form factor

All sensors need to route wires along fingers that flex 90°+. Options:
- Thin silicone-sheathed wire at flex points
- Flexible PCB strips along finger dorsum
- 3D-printed knuckle mounts with wire channels
- Fabric-integrated conductive threads (higher resistance, but avoids hard wire fatigue)

The ESP32-S3, LiPo, and mux ICs should be on the wristband — only sensors and their local decoupling capacitors go on the fingers.

### 9.5 Calibration and ML

UltraGlove's accuracy depends on a neural network trained to map distance matrices to hand pose, requiring ground-truth labels from another system (e.g. a Leap Motion or Manus glove for labelling). A DIY builder will need either:
- Access to a Quest 3 or Leap Motion 2 for initial labelling
- A biomechanical skeletal model (known joint constraints reduce degrees of freedom and can replace learned mapping)
- Community-contributed datasets if the project gains traction

The skeletal model approach is recommended for v1 — it requires no additional hardware and leverages the known anatomy of the hand.

---

## 10. Market & Use Cases

### 10.1 Market sizing (directional)

The VR glove / data glove market is projected to grow significantly through 2030, driven by VR/AR, healthcare rehabilitation, industrial training, and robotics. Multiple analyst reports place the market in the billions USD with 20%+ CAGR. Treat these numbers as directional rather than precise — they vary widely between sources.

### 10.2 Target use cases

**Primary (v1 target):**

- **VR social platforms (VRChat, VSeeFace, ChilloutVR)** — large community actively seeking affordable finger tracking gloves. OpenGloves SteamVR driver provides plug-and-play compatibility. LucidGloves community has proven this market is real and underserved.
- **VTubing / motion capture** — finger tracking for avatar animation. UDCAP, Rokoko Smartgloves target this. A sub-$100 open alternative would be disruptive.

**Secondary:**

- **Robotics teleoperation** — humanoid robot training data collection is a hot area (NVIDIA, Tesla, Figure, 1X, etc.). Manus has pivoted heavily here. DOGlove (arXiv 2025) identifies this as an unmet open-source need.
- **Accessibility (sign language translation)** — active research area; Wulala Technology launched a commercial product in 2024. EchoGlove's modality stack may offer advantages in robustness.
- **Music / live performance** — mi.mu Gloves (Imogen Heap) established this market. OSC output target in EchoGlove architecture.
- **Medical rehabilitation** — stroke rehab, joint monitoring. Dominated by flex-sensor gloves currently.

### 10.3 Differentiation vs. existing options

| vs. LucidGloves | Higher accuracy, drift-resistant, magnetically immune. Higher complexity and cost. |
|---|---|
| vs. Rokoko Smartgloves | Open-source, no proprietary EMF coil required, significantly cheaper. Comparable accuracy goal. |
| vs. Manus Quantum | Much cheaper, open-source, no proprietary infrastructure. Lower accuracy. |
| vs. UltraGlove (paper) | EchoGlove is the buildable, open-source implementation of UltraGlove's core idea, extended with IR and IMU. |

---

## 11. Key References

### Academic papers

| Paper | Relevance |
|---|---|
| UltraGlove — Hand Pose Estimation with MEMS Ultrasonic Sensors (SIGGRAPH Asia 2023) | Primary inspiration; proves CH-101-based hand pose tracking works | [arXiv](https://arxiv.org/abs/2306.12652) / [ACM](https://dl.acm.org/doi/10.1145/3610548.3618202) |
| A modular architecture for IMU-based data gloves (arXiv 2024) | IMU glove reference design; 9.17° avg RMSE with 11 IMUs | [arXiv](https://arxiv.org/html/2401.13254v1) |
| Wearable and Ultra-Low-Power Fusion of EMG and A-Mode Ultrasound (ETH, arXiv 2025) | Proves ultrasound + other modality wearable fusion at sub-50 mW | [arXiv](https://arxiv.org/html/2510.02000v2) |
| Wearable visual-inertial hand tracking glove (UDel / IROS 2019) | IR + IMU fusion glove reference | [PDF](https://udel.edu/~ghuang/iros19-vins-workshop/papers/05.pdf) |
| Development of a Wearable Glove System with Multiple Sensors for Hand Kinematics (PMC 2021) | Multi-sensor glove accuracy benchmark | [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC8066750/) |
| HandFi: WiFi CSI Hand Gesture Recognition (2024) | WiFi CSI gesture accuracy reference | [ACM](https://dl.acm.org/doi/10.1016/j.procs.2024.04.042) |
| DOGlove: Low-cost haptic teleop glove (arXiv 2025) | Identifies open-source teleop glove gap | [arXiv](https://arxiv.org/html/2502.07730v1) |

### Open-source projects

| Project | URL |
|---|---|
| LucidGloves (LucidVR) | [GitHub](https://github.com/LucidVR/lucidgloves) |
| OpenGloves SteamVR driver | [GitHub](https://github.com/LucidVR/opengloves-driver) |
| nfelber/IMU-Motion-Tracking-Glove | [GitHub](https://github.com/nfelber/IMU-Motion-Tracking-Glove) |
| WiFi-CSI-Human-Pose-Detection | [GitHub](https://github.com/euaziel/WiFi-CSI-Human-Pose-Detection) |
| Awesome-WiFi-CSI-Sensing list | [GitHub](https://github.com/Marsrocky/Awesome-WiFi-CSI-Sensing) |
| Wi-ESP (ESP32 CSI tool) | [GitHub](https://github.com/wrlab/Wi-ESP) |

### Datasheets

| Part | URL |
|---|---|
| TDK CH-101 MEMS Ultrasonic ToF | [TDK](https://invensense.tdk.com/download-pdf/ch101-datasheet/) |
| STMicro VL6180X IR ToF | [Adafruit guide](https://learn.adafruit.com/adafruit-vl6180x-time-of-flight-micro-lidar-distance-sensor-breakout) |
| Bosch BNO055 IMU | [Bosch](https://www.bosch-sensortec.com/products/smart-sensor-systems/bno055/) |
| Qorvo DW3000 UWB | [Qorvo](https://www.qorvo.com/products/p/DW3000) |
| TCA9548A I²C Mux | [TI](https://www.ti.com/product/TCA9548A) |
