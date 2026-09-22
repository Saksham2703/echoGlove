# BOM — Phase 2: IR fingertip layer + I²C mux

**Researched:** 2026-05-25
**Re-checked:** 2026-09-20 — sourcing changed from Amazon to Adafruit direct, see below
**Budget estimate from orchestration doc:** $50–75
**Actual at checkout:** $103.30 + $6.99 USPS Ground Advantage + $8.91 tax = **$119.20**

| # | Item | Part | Source | Link | Price | Qty | Subtotal | Status |
|---|---|---|---|---|---|---|---|---|
| 1 | ToF distance sensor | Adafruit VL6180X Time of Flight Distance Ranging Sensor #3316 | Adafruit | https://www.adafruit.com/product/3316 | $13.95 ea | 6 (5 + 1 spare) | $83.70 | ordered 2026-09-20 |
| 2 | I²C multiplexer | Adafruit TCA9548A 1-to-8 I²C Multiplexer Breakout #2717 | Adafruit | https://www.adafruit.com/product/2717 | $6.95 ea | 2 (1 + 1 spare) | $13.90 | ordered 2026-09-20 |
| 3 | Sensor lead | STEMMA QT / Qwiic JST-SH 4-pin to Premium Male Headers Cable | Adafruit | add-on at checkout | $0.95 ea | 6 | $5.70 | ordered 2026-09-20 |

**Subtotal: $103.30.** With shipping ($6.99) and tax ($8.91): **$119.20**.

Over the orchestration doc's $50–75 Phase 2 budget by ~$45. The overage is
entirely the sensor count — five fingers plus a spare at Adafruit MSRP is
$83.70 on its own. Accepted rather than re-scoped: dropping the spare saves
$13.95 and leaves no recovery path if one sensor arrives dead mid-phase.

### Note on the STEMMA cables (item 3)

The VL6180X ships with an unsoldered 0.1" header strip and carries two STEMMA
QT connectors, so item 3 is a convenience, not a requirement — it avoids
soldering headers onto six more boards and gives each sensor a flexible lead
for fingertip placement. The four wires break out to individual male pins, so
SDA/SCL can go to a mux channel while VIN/GND go straight to the 3V3 rail, as
the wiring topology below requires. Cable length not verified; assume ~150 mm
and re-check before relying on it for glove reach in Phase 3.

The STEMMA-QT-to-STEMMA-QT cable and the female-socket cable are **not**
useful here. The TCA9548A has no STEMMA connector, so a STEMMA-to-STEMMA cable
cannot join sensor to mux — and daisy-chaining sensors to each other would put
two 0x29 devices on one bus segment, which is the exact collision the mux
exists to prevent.

### Mounting geometry (decided 2026-09-21)

Both sensors have a ~25° field of view (ST datasheets), which gives a useful
rule of thumb:

    spot diameter ≈ 0.44 × distance

| Mount distance | Spot diameter | vs ~20 mm finger pitch |
|---|---|---|
| 200 mm | 89 mm | covers 4+ fingers |
| 140 mm | 62 mm | covers 3 fingers |
| 85 mm | 38 mm | covers 2 fingers |
| **45 mm** | **20 mm** | **≈ one finger — isolation threshold** |
| 25 mm | 11 mm | cleanly inside one finger |

Measured hand geometry: fingertip sits 40–60 mm from a wrist / back-of-hand
mount when fully curled, 140–200 mm when fully extended. That span is both
past the VL6180X's reliable range *and* wide enough that one sensor's cone
covers three or four fingers — which would fail Phase 2's crosstalk criterion
regardless of which sensor is fitted.

**Decision: mount close, not at the wrist.** A sensor just proximal to each
MCP knuckle, ranging the nearest phalanx rather than the fingertip, works over
roughly 10–60 mm of travel. At those distances the spot stays at or under one
finger width, so crosstalk is solved geometrically instead of with baffles,
and the whole travel sits inside the VL6180X's reliable band.

Open question for the Phase 2 brainstorm: confirm the actual knuckle pitch
(assumed ~20 mm here) and the real close-mount travel, and check the curl
response is monotonic over it.

Note: because the mux addresses one sensor at a time, single-shot ranging per
channel means only one emitter ever fires. Sensor-to-sensor optical
interference is prevented by the mux sequencing, separately from the
geometric crosstalk above.

### Why not the VL53L0X (#3317, ~30–1000 mm)

Considered and rejected — twice, for different reasons.

First rejection assumed a fully curled fingertip would fall inside its 30 mm
dead zone. Measurement disproved that: curled is 40–60 mm at a wrist mount.

It was then reconsidered when those measurements showed full extension at
140–200 mm, past the VL6180X's reliable range. Rejected again, and this is the
reason that holds: the fix for that range problem is a close mount (above),
and under a close mount the **30 mm minimum** puts most of the 10–60 mm working
travel in the dead zone. The extra range is worthless there, and the floor is
disqualifying. It is also fixed at 0x29, so it never removed the need for the
mux. Revisit only if the close mount proves mechanically impossible.

## Sourcing note (2026-09-20)

The original Amazon sourcing no longer works. Re-checked today:

- **TCA9548A — ASIN B017C09ETS is "Currently unavailable"** on Amazon, with
  "we don't know when or if this item will be back in stock". No alternative
  Amazon listing for the genuine Adafruit board was identified.
- **VL6180X — ASIN B01N0ODI3Q is available but has no featured offer** (no Buy
  Box). Third-party offers only, all above MSRP: PiShop US $14.99 + $4.99
  shipping, PiShop US $21.61 Prime, Electronics123 $18.95 + $6.53 shipping.
  At 6 units that is ~$120–130 against the $83.70 this BOM had budgeted.

Both parts are confirmed **in active production and in stock at Adafruit** at
list price ($13.95 and $6.95, verified 2026-09-20), so this is a listing/seller
problem rather than an end-of-life problem.

Sourcing moved to **Adafruit direct** with the user's agreement that trustworthy
non-Amazon vendors are acceptable. This is the only confirmed source for the
multiplexer and is ~$46 cheaper on the sensors than the Amazon Prime offer.
DigiKey and Mouser are authorized Adafruit distributors and are acceptable
equivalents if preferred — not yet checked for stock.

## Clone alternative — not recommended

A no-name VL6180X 4-pack (e.g. UrbanHui B0G5JMQBY9, ~$15–20 for 4) would save
money, and the module is genuinely VL6180X-based. Two risks were never
resolved: these boards commonly omit the onboard I²C pull-ups, and address
configurability may differ. The same OEM board is resold under many storefront
brands (HiLetgo, PAMEENCOS, Rakstore, flashtree...), so listing reviews do not
reliably describe the batch received. With Adafruit direct at MSRP the saving
is much smaller than it looked in May, and missing pull-ups on a five-sensor
bus behind a mux is a bad first debugging experience. Buy the Adafruit boards.

## Wiring and compatibility notes

### VL6180X (one per finger, channels 0–4 on the mux)
- Supply voltage: 2.7–5.5 V (onboard regulator + level-shifters). 3.3 V from ESP32 works directly.
- Fixed I²C address: **0x29** — all five sensors share the same address, which is why the mux is required.
- Onboard pull-ups: **yes** (on the STEMMA QT connector lines). No external pull-up resistors needed.
- Range: **5–100 mm reliable**; Adafruit reports 150–200 mm only "with good
  ambient conditions". Treat 100 mm as the design limit. See the mounting
  geometry section below — the mount distance is chosen to stay inside this.
- XSHUT pin: not needed when each sensor is on its own mux channel. Leave unconnected or tie high.
- Adafruit library: `Adafruit_VL6180X` (Arduino), maintained and tested with the BNO055 on the same I²C bus in prior projects.

### TCA9548A (one unit driving all five VL6180X sensors)
- Supply voltage: 1.65–5.5 V. 3.3 V works directly.
- Default I²C address: **0x70**. Configurable to 0x70–0x77 via A0/A1/A2 pins — no conflict expected with BNO055 (0x28) or VL6180X (0x29 per channel).
- 8 independently switchable I²C output channels. Channels 0–4 → one VL6180X each.
- Onboard capacitors and pull-ups: **yes**. Plug-and-play at 3.3 V.
- Adafruit library: none required. The mux has no register map, just a single
  control byte written to its device address (0x70), one bit per channel:
  `Wire.beginTransmission(0x70); Wire.write(1 << channel); Wire.endTransmission();`
  Writing 0x00 disconnects all channels. Enabling two channels at once is
  legal and is exactly the 0x29 collision the mux exists to prevent.
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
