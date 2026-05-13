# 🤚 EchoGlove

> A camera-free, drift-resistant hand tracking glove fusing ultrasonic time-of-flight, IR proximity, and IMU sensing — built open-source, for VR, robotics, and beyond. Optional UWB for full 6DOF world-space positioning.

---

## What is EchoGlove?

EchoGlove is a DIY wearable glove that tracks hand and finger pose in 3D space **without cameras, without magnetic coils, and without a base station**. It works in the dark, through occlusion, and in magnetically noisy environments like robotics labs.

It fuses three complementary sensing modalities:

| Sensor | Role | Range |
|---|---|---|
| **Ultrasonic ToF** (MEMS, e.g. TDK CH-101) | Pairwise finger-to-finger distances → full hand pose | 2 cm – 1.2 m |
| **IR proximity / ToF** (e.g. VL6180X) | Fingertip close-range interaction & pinch detection | 0 – 20 cm |
| **IMU** (e.g. BNO055) | Global hand orientation, high-rate motion fill-in | — |

Together, they cover what no single sensor can: **spatial position, orientation, and fine finger interaction**, fused into a continuous 6DOF hand pose stream.

---

## Motivation

Commercial drift-free gloves (Manus Quantum, Rokoko Coil Pro) rely on proprietary electromagnetic field transmitters costing thousands of dollars. Camera-based solutions (Ultraleap, Quest hand tracking) fail under occlusion and require line-of-sight. IMU-only gloves drift over time.

EchoGlove is an attempt to build the open-source equivalent of a professional-grade data glove — using commodity sensors, an ESP32, and a Kalman-fused sensor stack — for under $100 in parts.

---

## Architecture

```
┌──────────────────── EchoGlove ────────────────────┐
│                                                    │
│  Fingertips        Back of hand       Wristband   │
│  ──────────        ────────────       ─────────   │
│  CH-101 ×5         CH-101 ×1          ESP32-S3    │
│  VL6180X ×5        BNO055 IMU         LiPo 500mAh │
│                                       BLE / USB   │
└────────────────────────────────────────────────────┘
        │
        ▼ Bluetooth / USB Serial
┌──────────────────── Host ─────────────────────────┐
│  Sensor fusion (Kalman / learned model)           │
│  → OpenGloves SteamVR driver  (VR / VRChat)       │
│  → ROS2 topic                 (robotics teleop)   │
│  → OSC output                 (music / live perf) │
└────────────────────────────────────────────────────┘
```

---

## Key Design Decisions

- **Ultrasonic as primary pose source** — inspired by Princeton's UltraGlove (SIGGRAPH Asia 2023), which demonstrated that pairwise MEMS ultrasonic distances can reconstruct full hand pose without IMU drift or magnetic interference.
- **IR for close range** — ultrasonic struggles below ~2 cm; IR ToF fills this gap for pinch detection and fingertip-to-surface contact.
- **IMU for orientation + interpolation** — provides global hand orientation (critical for VR) and high-rate (200–400 Hz) pose deltas between slower ultrasonic frames (~60 Hz).
- **ESP32-S3** — WiFi/BLE built-in, sufficient compute for on-device preprocessing, CSI accessible as a bonus ambient sensing channel.
- **OpenGloves compatible** — plugs into the existing SteamVR finger tracking ecosystem without reinventing the driver layer.

---

## Under-Desk Tracking

Because all sensing is self-contained on the glove, EchoGlove works under a desk with no degradation to finger pose tracking. The IMU and IR sensors are entirely unaffected by occlusion. The ultrasonic inter-finger ranging may pick up reflections off the desk underside, but these are mitigable via coded pulse sequences, echo signature filtering, and expected-range thresholding.

The only thing lost under a desk is **absolute position in world space** — which most use cases (VR, gesture control, robotics teleop, music) don't actually need.

---

## Optional: Full 6DOF World-Space Position (v2)

For applications that do need absolute position, EchoGlove is designed to accept a **UWB (Ultra-Wideband) module** on the wristband as an optional v2 add-on.

| Component | Role |
|---|---|
| DW3000 UWB chip (wristband) | Trilaterate wrist position in world space |
| 3–4 UWB anchor pucks (fixed) | Known reference points around the workspace |
| BNO055 IMU (already present) | Handles orientation — UWB handles translation |

UWB gives centimetre-level position accuracy, works through occlusion, under desks, and in the dark. It uses the same approach as Apple's AirTag / iPhone U1 chip. 3–4 small anchor pucks around the desk is a reasonable infrastructure ask. This is kept as a v2 scope item — finger pose tracking is validated first, world-space position layered on top.

---

## Status

> 🚧 Early concept / research phase

- [ ] Hardware BOM finalised
- [ ] Ultrasonic crosstalk sequencing prototype
- [ ] IMU + ultrasonic Kalman fusion
- [ ] IR fingertip layer integration
- [ ] OpenGloves driver mapping
- [ ] Enclosure & flex wiring
- [ ] (v2) UWB anchor + wristband module
- [ ] (v2) 6DOF world-space position fusion

---

## Inspiration & Prior Art

- [UltraGlove — Princeton / SIGGRAPH Asia 2023](https://arxiv.org/abs/2306.12652)
- [LucidGloves / OpenGloves](https://github.com/LucidVR/lucidgloves)
- [Rokoko Smartgloves](https://www.rokoko.com/products/smartgloves)
- [Manus Quantum Metagloves](https://www.manus-meta.com/products/quantum-metagloves)

---

## License

MIT — build it, break it, improve it.
