# Parking lot

Out-of-scope ideas that came up during the project. Reviewed at each phase boundary
to see if any should be promoted into the next phase.

## Promoted to next phase
(none yet)

## Phase 2+
- Magnetometer calibration: figure-8 waving procedure to fully converge BNO055 NDOF mode. Needed for accurate absolute heading in Phase 3+ (BLE, untethered). Phase 1 only needs stable relative rotation.
- DIY sensor fusion: implement Madgwick or Mahony filter from scratch on the host side (bypassing BNO055 NDOF mode, using raw accel/gyro/mag). Pure learning exercise — understand what the BNO055 is doing internally.

## Future / v3+
- SteamVR / OpenGloves driver integration
- Second glove (left hand)
- 3D-printed knuckle mounts and wristband enclosure
- DW3000 UWB for 6DOF world-space position
- ML-based pose model (UltraGlove-style neural network)
- WiFi CSI ambient sensing as a bonus channel
- HC-SR04 ultrasonic learning project (kit includes one — could prototype ranging before CH-101 arrives in Phase 5)
