# Parking lot

Out-of-scope ideas that came up during the project. Reviewed at each phase boundary
to see if any should be promoted into the next phase.

## Resolved
- **VL6180X usable range vs. finger travel** (raised 2026-09-20, settled
  2026-09-21). Measured by hand: fully curled 40-60 mm, fully extended
  140-200 mm from a wrist / back-of-hand mount. That extended figure is past
  the VL6180X's ~5-100 mm reliable band, which briefly looked like a case for
  swapping to the VL53L0X. It is not. Mount distance is a design variable, not
  a given, and moving the sensor close to each finger fixes both the range and
  the crosstalk problem at once -- see the mounting geometry section in
  `hardware/bom-phase2.md`. Keeping the VL6180X; the VL53L0X's 30 mm floor
  makes it the wrong part for a close mount.

## Promoted to next phase
(none yet)

## Phase 2+
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
