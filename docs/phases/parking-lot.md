# Parking lot

Out-of-scope ideas that came up during the project. Reviewed at each phase boundary
to see if any should be promoted into the next phase.

## Promoted to next phase
(none yet)

## Phase 2+
- **VL6180X usable range vs. assumed finger travel.** `hardware/bom-phase2.md`
  says "Range: 5-200 mm... finger proximity (0-20 cm) is well within spec."
  That is overstated. Adafruit and ST both describe the VL6180X as ~5-100 mm
  reliable, with 150-200 mm only under good ambient conditions. A 0-20 cm
  assumption puts the top half of the travel at or past the practical limit,
  where dropouts and noise are expected. Work out the real fingertip-to-sensor
  geometry during the Phase 2 brainstorm and correct the BOM note. Phase 2's
  actual criterion is discrimination (one finger moving changes exactly one
  reading), not absolute range, so this may not bite — but decide it
  deliberately rather than discovering it at bring-up.
- Magnetometer calibration: figure-8 waving procedure to fully converge BNO055 NDOF mode. Needed for accurate absolute heading in Phase 3+ (BLE, untethered). Phase 1 only needs stable relative rotation.
- DIY sensor fusion: implement Madgwick or Mahony filter from scratch on the host side (bypassing BNO055 NDOF mode, using raw accel/gyro/mag). Pure learning exercise — understand what the BNO055 is doing internally.

## Learning / stretch
- Modern OpenGL shaders: rewrite the viewer using vertex + fragment shaders instead of immediate-mode `glBegin`/`glEnd`. A stepping stone to understanding how games actually render. Good to attempt after Phase 4 when the viewer is stable.

## Future / v3+
- SteamVR / OpenGloves driver integration
- Second glove (left hand)
- 3D-printed knuckle mounts and wristband enclosure
- DW3000 UWB for 6DOF world-space position
- ML-based pose model (UltraGlove-style neural network)
- WiFi CSI ambient sensing as a bonus channel
- HC-SR04 ultrasonic learning project (kit includes one — could prototype ranging before CH-101 arrives in Phase 5)
