# BOM — Phase 2: IR fingertip layer + I²C mux

**Researched:** 2026-05-25  
**Budget estimate from orchestration doc:** $50–75  
**Actual estimate (Adafruit, recommended):** ~$98 — see note below

| # | Item | Part | Source | Link | Est. price | Qty | Subtotal | Status |
|---|---|---|---|---|---|---|---|---|
| 1 | ToF distance sensor | Adafruit VL6180X Time of Flight Distance Ranging Sensor #3316 | Amazon | [B01N0ODI3Q](https://www.amazon.com/dp/B01N0ODI3Q) | ~$13.95 ea | 6 (5 + 1 spare) | ~$83.70 | not ordered |
| 2 | I²C multiplexer | Adafruit TCA9548A 1-to-8 I²C Multiplexer Breakout #2717 | Amazon | [B017C09ETS](https://www.amazon.com/dp/B017C09ETS) | ~$6.95 ea | 2 (1 + 1 spare) | ~$13.90 | not ordered |

**Estimated total: ~$98**

## Budget note

The orchestration doc estimated $50–75. Adafruit's VL6180X at $13.95/unit × 6 pushes this to ~$98.
A no-name 4-pack (e.g. UrbanHui [B0G5JMQBY9](https://www.amazon.com/dp/B0G5JMQBY9)) costs ~$15–20
for 4 units — two packs gives 8 sensors for ~$30–40, saving ~$50. The risk: clone boards often
omit onboard pull-ups and may have address-collision issues. For a beginner doing I²C mux work for
the first time, the Adafruit board is the safer choice. Decide at ordering time.

## Wiring and compatibility notes

### VL6180X (one per finger, channels 0–4 on the mux)
- Supply voltage: 2.7–5.5 V (onboard regulator + level-shifters). 3.3 V from ESP32 works directly.
- Fixed I²C address: **0x29** — all five sensors share the same address, which is why the mux is required.
- Onboard pull-ups: **yes** (on the STEMMA QT connector lines). No external pull-up resistors needed.
- Range: 5–200 mm. Optimal range for finger proximity (0–20 cm) is well within spec.
- XSHUT pin: not needed when each sensor is on its own mux channel. Leave unconnected or tie high.
- Adafruit library: `Adafruit_VL6180X` (Arduino), maintained and tested with the BNO055 on the same I²C bus in prior projects.

### TCA9548A (one unit driving all five VL6180X sensors)
- Supply voltage: 1.65–5.5 V. 3.3 V works directly.
- Default I²C address: **0x70**. Configurable to 0x70–0x77 via A0/A1/A2 pins — no conflict expected with BNO055 (0x28) or VL6180X (0x29 per channel).
- 8 independently switchable I²C output channels. Channels 0–4 → one VL6180X each.
- Onboard capacitors and pull-ups: **yes**. Plug-and-play at 3.3 V.
- Adafruit library: none required — communicate via raw `Wire.write(1 << channel)` to register 0x70 to select a channel.
- Reset pin: available on the breakout header if a firmware reset is needed.

### Wiring topology
```
ESP32-S3 3V3 ─── VIN (TCA9548A)
ESP32-S3 GND ─── GND (TCA9548A)
ESP32-S3 SDA ─── SDA (TCA9548A)
ESP32-S3 SCL ─── SCL (TCA9548A)

TCA9548A SD0/SC0 ─── SDA/SCL (VL6180X finger 0 — thumb)
TCA9548A SD1/SC1 ─── SDA/SCL (VL6180X finger 1 — index)
TCA9548A SD2/SC2 ─── SDA/SCL (VL6180X finger 2 — middle)
TCA9548A SD3/SC3 ─── SDA/SCL (VL6180X finger 3 — ring)
TCA9548A SD4/SC4 ─── SDA/SCL (VL6180X finger 4 — pinky)

Each VL6180X: VIN ← 3V3, GND ← GND (power from ESP32 rail, not through mux)
```

Note: power the VL6180X sensors directly from the 3V3 rail, not through the mux channels. The mux only switches the I²C lines.
