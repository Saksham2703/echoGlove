# BOM — Phase 1: IMU bring-up

| # | Item | Part | Source | Link | Est. price | Status |
|---|---|---|---|---|---|---|
| 1 | IMU breakout | Adafruit BNO055 Absolute Orientation Sensor #2472 | Amazon | [B017PEIGIG](https://www.amazon.com/Adafruit-Absolute-Orientation-Fusion-Breakout/dp/B017PEIGIG) | ~$35 | ordered / arrived |

## Notes
- Ships with headers unsoldered. Solder the 6-pin male header before wiring.
  Use the soldering iron from the Phase 0 BOM. See `hardware/wiring/phase1-imu.md`.
- Runs on 3.3 V. Do not connect VIN to 5 V.
- ADR pin left unconnected → I²C address 0x28 (internal pull-down on the Adafruit board).
