# Phase 0 BOM

## What we're buying (Amazon)

| # | Item | Spec | Link | Price | Ordered? | Arrived? |
|---|---|---|---|---|---|---|
| 1 | Soldering iron — Pinecil V2 | USB-C PD, 60W, replaceable tips | https://www.amazon.com/dp/B096X6SG13 | ~$40–50 | ✓ | [ ] |
| 2 | 60/40 leaded rosin-core solder (HGMZZQ) | 0.8mm, 100g spool | https://www.amazon.com/dp/B07BGTSWYB | ~$9–11 | ✓ | [ ] |
| 3 | Brass sponge tip cleaner (Weller WLACCBSH-02) | Brass sponge w/ silicone holder | https://www.amazon.com/dp/B08FQBS97L | ~$7–10 | ✓ | [ ] |
| 4 | Digital multimeter (AstroAI 4000-count) | Auto-ranging, continuity beep, NCV | https://www.amazon.com/dp/B0DKXTR485 | ~$18–22 | ✓ | [ ] |
| 5 | ESP32-S3 DevKitC-1 × 2 | WROOM-1, N16R8, USB-C, 2-pack | https://www.amazon.com/dp/B0FPLSQZWF | ~$22–28 | ✓ | [ ] |
| 6 | USB-C to USB-C data cable × 2 | 1m, 100W, data-rated (UGREEN) | https://www.amazon.com/dp/B09N94MZG9 | ~$8–13 | ✓ | [ ] |
| 7 | 22 AWG hookup wire kit (TUOFENG) | Solid-core, 6 colors, 30 ft each | https://www.amazon.com/dp/B07TX6BX47 | ~$12–16 | ✓ | [ ] |
| 8 | Helping hands w/ magnifier (SE MZ101B) | Optional — skipped for now | https://www.amazon.com/dp/B000RB38X8 | ~$8–12 | — | — |

**Estimated total: $124–161**

### Notes & caveats per item

1. **Pinecil V2** — Pine64 sells direct for $26 but only via pine64.com (off-Amazon). Amazon resellers mark it up ~50%. We accept the markup to keep Amazon-only sourcing. The iron does **not** include a USB-C PD power brick — your MacBook charger (USB-C, 67W+) will drive it fine, so don't order a separate brick. Verify the "Sold by" line before checkout — pick a reseller with >100 reviews.
2. **Solder** — HGMZZQ 0.8mm 60/40 rosin-core is a no-brand value pick that matches spec exactly. **Leaded** is preferred over lead-free for beginners (lower melting temp, easier to wet). Solder in a ventilated area, wash hands after.
3. **Brass tip cleaner** — Weller WLACCBSH-02 is a top-brand brass sponge cleaner with silicone holder. Brass over wet-sponge cleaners; the wet sponge thermally shocks the tip and shortens its life.
4. **Multimeter** — AstroAI 4000-count is the most-reviewed beginner DMM on Amazon. We need: DC voltage (battery checks), continuity beep (wiring checks), resistance (pull-up confirmation). NCV is nice-to-have.
5. **ESP32-S3 spares × 2** — The 2-pack listing is a newer ASIN. If reviews look sparse at order time, the **DORHEA 2-pack at https://www.amazon.com/dp/B0CKXJKQ1F** is a well-reviewed fallback at similar pricing. Spares matter: it is normal to brick or fry a board while learning.
6. **USB-C cables** — UGREEN 2-pack confirmed data-sync (100W E-marker chip). **Cheap no-name USB-C cables are frequently charge-only and silently prevent ESP32 flashing.** This is the single most common "why won't my board show up?" gotcha for new ESP32 users. Buy these specifically.
7. **Hookup wire** — TUOFENG 22 AWG solid-core, 6 colors. Solid-core is right for breadboards (stranded frays in the holes). 22 AWG is the right gauge — thinner won't carry enough current for the ESP32's 3.3V rail under load.
8. **Helping hands** — Optional. Soldering without one is doable but frustrating. Worth the $10. The SE MZ101B is the classic budget pick.

## Already on hand
- Freenove ESP32 Ultimate Starter Kit (Amazon B0CJJJ7BCY).
  - **Chip note:** Per the kit's official parts list, the included board is **ESP32-WROVER-E** (original ESP32, Xtensa LX6, micro-USB), **not** the ESP32-S3 the orchestration spec assumes. The board silkscreen reads `FREENOVE ESP32 WROVER`.
  - **Decision:** The Freenove WROVER board is not the firmware target — it stays as a component source (sensors, breadboard, discretes). Phase 0 firmware targets the ordered **ESP32-S3 DevKitC-1 2-pack (item 5)**, matching the orchestration spec end-to-end. No changes to the Phase 0 plan are required.

## Kit inventory (from Freenove parts list)

Pre-filled from the official Freenove parts-list image (downloaded with the kit tutorial). Verify against the physical contents once the kit arrives — quantities and any substitutions go in the "As-arrived" section below.

**Microcontroller & I/O:**
- 1× ESP32-WROVER-E dev board (micro-USB, on Freenove carrier with reset+boot buttons)
- 1× GPIO Extension Board (breaks out pins next to the breadboard)
- 1× Project Board (breadboard)
- 1× USB cable (likely micro-USB-A — confirm on arrival; this is what flashes the Freenove board)

**Sensors (relevant to EchoGlove):**
- 1× **Accelerometer Module** — almost certainly GY-521 / **MPU-6050** (6-axis IMU, I²C @ 0x68). **This is our Phase 0 Task 9 sensor.**
- 1× Ultrasonic Ranging Module — HC-SR04 (40 kHz). Not CH-101, but useful for learning ultrasonic ranging concepts in Phase 5.
- 1× Temperature/Humidity Sensor — DHT11
- 1× Thermistor, 1× Photoresistor, 1× Infrared Motion Sensor (PIR), 1× Infrared Receiver
- 1× Camera module, 1× SD card + Card Reader

**Actuators / outputs:**
- 1× Servo, 1× Stepper Motor + driver board, 1× DC Motor + driver chip
- 1× Active Buzzer, 1× Passive Buzzer, 1× Speaker, 1× Audio Converter & Amplifier
- 1× 7-Segment Display, 1× 4-Digit 7-Seg Display, 1× LED Matrix, 1× LED Bar Graph, 1× LCD Module
- 1× Freenove 8 RGB LED Module, 1× Relay

**Discretes:**
- 10× Red LED, 4× Green LED, 4× Blue LED, 4× Yellow LED, 1× RGB LED
- 20× 220 Ω resistor, 10× 1 kΩ, 10× 10 kΩ
- 3× Potentiometer, 2× 0.1 µF capacitor, 2× 10 µF capacitor
- 2× Rectifier diode, 2× Switch diode, 2× NPN transistor, 2× PNP transistor

**Input devices:**
- 4× Push button (small) + 4× Big push button (with 4 colored caps: red/green/blue/yellow)
- 2× Slide switch, 1× Vibration switch, 1× 4×3 Keypad, 1× Joystick

**Power & misc:**
- 1× 2× AA battery holder, 1× 9 V battery cable
- 1× Serial-to-Parallel chip (74HC595 likely)
- 1× 40-pin Male header, 1× 40-pin Female header
- 3× General-purpose perfboard
- 65× M-M jumper wires, 20× F-F, 20× F-M
- 1× Resistor color code card, 1× Plastic storage box

## As-arrived inventory
(Confirm the above against the physical kit once it arrives — flag any missing/substituted items here. Photograph the layout and paste the list back into the next Claude session for cross-check.)

## Receipts
(Save Amazon order confirmation PDFs to `hardware/receipts/` once orders ship.)
