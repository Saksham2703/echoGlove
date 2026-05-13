# Phase 0 — Fundamentals Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. **Note:** many steps in this plan are physical hardware actions performed by the human user (soldering, wiring, plugging in USB) — these cannot be executed by a subagent. Subagent execution should pause and wait for the user at those steps.

**Goal:** Stand up the EchoGlove dev environment end-to-end and prove the loop *hardware → firmware → USB serial → Python* works on the user's Mac, using only the Freenove ESP32-S3 kit + Phase 0 tools.

**Architecture:** Two artifacts. (1) A PlatformIO firmware project under `firmware/phase0-blink/` that blinks the onboard LED, counts button presses, and prints over USB serial. (2) A Python package under `host/echoglove/` with a serial reader and a pytest suite. They communicate via newline-delimited JSON over USB serial at 115200 baud.

**Tech Stack:** ESP32-S3 (Arduino framework on PlatformIO), VS Code + PlatformIO extension, Python 3.12 via `uv`, `pyserial` for the host reader, `pytest` for tests, `ruff` for linting.

---

## Scope & non-goals

In scope:
- Order Phase 0 BOM from Amazon.
- Install VS Code + PlatformIO + Python toolchain on Mac.
- Scaffold the repo directory structure agreed in the orchestration spec.
- Blink the onboard LED on the ESP32-S3.
- Wire a button on a breadboard and stream a click counter over USB serial.
- Read the serial stream in Python, parse JSON lines, and run for 60 s without error.
- Wire one I²C sensor from the Freenove kit (whichever the kit actually contains — likely MPU-6050) and stream raw readings to the same Python script.

Out of scope (deferred):
- BNO055 (Phase 1).
- VL6180X / TCA9548A mux (Phase 2).
- BLE (Phase 3).
- Sensor fusion / Kalman filter / 3D viewer (Phase 4).
- Any soldering of permanent connections (we practice soldering on a scrap perfboard, but Phase 0 hardware stays on a breadboard).
- Linting/typing CI on GitHub Actions (defer until host/ has more code in Phase 1).

---

## File structure

| Path | Purpose | Created in |
|---|---|---|
| `hardware/bom-phase0.md` | Phase 0 BOM with Amazon links, prices, receipts, and an "as-arrived" inventory | Task 1 |
| `docs/phases/phase0-kickoff.md` | Short kickoff doc with goals + concept primer for I²C and USB serial | Task 4 |
| `docs/phases/parking-lot.md` | Out-of-scope ideas captured during Phase 0 | Task 4 |
| `STATE.md` | 3-line "where I left off" file, updated at end of every session | Task 4 |
| `firmware/phase0-blink/platformio.ini` | PlatformIO project config | Task 5 |
| `firmware/phase0-blink/src/main.cpp` | Blink + button + serial firmware | Task 5–7, 9 |
| `host/pyproject.toml` | uv-managed Python project | Task 3 |
| `host/echoglove/__init__.py` | Python package marker | Task 3 |
| `host/echoglove/serial_reader.py` | USB serial → parsed JSON lines | Task 8 |
| `host/tests/test_serial_reader.py` | Pytest suite for the parser | Task 8 |
| `hardware/wiring/phase0-button.md` | Wiring diagram (ASCII) for breadboard | Task 6 |
| `hardware/wiring/phase0-i2c.md` | Wiring diagram for the I²C sensor | Task 9 |
| `docs/phases/phase0-retro.md` | End-of-phase retrospective | Task 10 |

---

## Task 1: Order Phase 0 BOM and document it

**Files:**
- Create: `hardware/bom-phase0.md`

**Context:** Hardware shipping is the long-pole bottleneck. We order first, then do software setup while parts arrive. The Freenove kit is already on the way per the user; this task orders the missing tools.

- [ ] **Step 1: Create `hardware/bom-phase0.md` with the cart and confirm Amazon links with the user**

Claude (this AI session) researches and provides current Amazon URLs + prices for each line item. User reviews and adjusts. Write the file with this structure:

```markdown
# Phase 0 BOM

## What we're buying (Amazon)

| # | Item | Spec | Link | Price | Ordered? | Arrived? |
|---|---|---|---|---|---|---|
| 1 | Soldering iron (USB-C pen-style) | Pinecil V2 or TS80P | <link> | $40–60 | [ ] | [ ] |
| 2 | Solder (60/40 leaded rosin-core 0.6mm) | 100g spool | <link> | $10 | [ ] | [ ] |
| 3 | Brass tip cleaner | — | <link> | $5 | [ ] | [ ] |
| 4 | Digital multimeter | Auto-ranging | <link> | $20 | [ ] | [ ] |
| 5 | Spare ESP32-S3 DevKitC × 2 | USB-C | <link> | $25 | [ ] | [ ] |
| 6 | USB-C data cable × 2 | 1m, must say "data" not just "charging" | <link> | $10 | [ ] | [ ] |
| 7 | 22 AWG hookup wire kit | Solid + stranded, 6 colors | <link> | $15 | [ ] | [ ] |
| 8 | Helping hands w/ magnifier (optional) | — | <link> | $15 | [ ] | [ ] |

**Total: ~$115–145**

## Already on hand
- Freenove ESP32-S3 Ultimate Starter Kit (Amazon B0CJJJ7BCY)

## As-arrived inventory
(Fill in after Freenove kit arrives — list everything actually included in the kit.)

## Receipts
(Save Amazon order confirmation PDFs to hardware/receipts/ once orders ship.)
```

- [ ] **Step 2: User places the Amazon order**

User confirms order placed. Updates the `Ordered?` column to ✓. **Pause until parts arrive (typically 2–5 days).** Move on to Tasks 2–4 (software setup) in parallel.

- [ ] **Step 3: User inventories the Freenove kit on arrival**

When the Freenove kit arrives, user opens it, lays everything out, photographs it, and lists every component in the "As-arrived inventory" section. Paste the list back into the chat with Claude. Claude identifies any I²C sensors in the kit (MPU-6050, BMP280, etc.) — that determines which sensor is used in Task 9.

- [ ] **Step 4: Commit the BOM**

```bash
git add hardware/bom-phase0.md
git commit -m "Add Phase 0 BOM"
```

---

## Task 2: Install VS Code + PlatformIO + verify a hello-world build

**Files:**
- None (system-level install). Verification happens in a scratch project that is *not* committed.

**Context:** PlatformIO will be the firmware build system for every phase. Get it healthy now.

- [ ] **Step 1: Install VS Code (skip if already installed)**

Run in terminal:

```bash
brew install --cask visual-studio-code
```

Verify:

```bash
code --version
```

Expected: prints a version string starting with 1.x, no error.

- [ ] **Step 2: Install the PlatformIO IDE extension in VS Code**

Open VS Code → Extensions panel (Cmd+Shift+X) → search "PlatformIO IDE" → click Install on the one by `platformio` (the popular one, millions of downloads).

PlatformIO will install its toolchain in the background. Wait for the "PlatformIO IDE installed!" notification. This can take 5–10 minutes the first time.

Verify by opening a new terminal *inside* VS Code (Terminal → New Terminal) and running:

```bash
pio --version
```

Expected: `PlatformIO Core, version 6.x.x` or similar.

- [ ] **Step 3: Build a throwaway hello-world project**

In a scratch directory (NOT inside the echoGlove repo), run:

```bash
cd ~/tmp 2>/dev/null || mkdir -p ~/tmp && cd ~/tmp
pio project init --board esp32-s3-devkitc-1 --project-option "framework=arduino"
```

This creates a basic project skeleton. Try to build:

```bash
pio run
```

Expected: Successfully downloads the ESP32-S3 toolchain (first run can take 5+ minutes), then prints `[SUCCESS]`. If anything errors out, paste the full output to Claude.

- [ ] **Step 4: Clean up the throwaway project**

```bash
cd ~ && rm -rf ~/tmp/[project-name]
```

(No commit. This was a smoke test of the toolchain only.)

---

## Task 3: Install Python 3.12 + uv + scaffold the host project

**Files:**
- Create: `host/pyproject.toml`
- Create: `host/echoglove/__init__.py`
- Create: `host/README.md`

**Context:** `uv` is a fast modern Python package manager. We use it to manage the Python virtual environment and dependencies for the host-side code.

- [ ] **Step 1: Install uv**

```bash
brew install uv
```

Verify:

```bash
uv --version
```

Expected: `uv 0.x.x` (some recent version).

- [ ] **Step 2: Initialize the host Python project**

```bash
cd /Users/saksham/Projects/echoGlove
mkdir -p host && cd host
uv init --name echoglove --package
```

This creates:
- `host/pyproject.toml`
- `host/src/echoglove/__init__.py` (uv creates a `src/` layout by default)
- `host/README.md`

**Override the default layout** so it matches our spec (flat `echoglove/`, not `src/echoglove/`):

```bash
mv src/echoglove echoglove
rm -rf src
```

Edit `host/pyproject.toml`: find the `[tool.hatch.build.targets.wheel]` section (or the project layout block) and remove any `src/` references. If unsure, paste the file to Claude for review.

- [ ] **Step 3: Pin Python 3.12 and add initial dependencies**

```bash
cd /Users/saksham/Projects/echoGlove/host
uv python pin 3.12
uv add pyserial
uv add --dev pytest ruff
```

This creates/updates `host/.python-version`, `host/pyproject.toml`, and `host/uv.lock`. It also creates `host/.venv/`.

Verify:

```bash
uv run python -c "import serial; print(serial.__version__)"
```

Expected: prints a pyserial version number (e.g. `3.5`).

- [ ] **Step 4: Smoke-test pytest**

Create `host/tests/__init__.py` (empty) and `host/tests/test_smoke.py`:

```python
def test_smoke():
    assert 1 + 1 == 2
```

Run:

```bash
uv run pytest tests/ -v
```

Expected: `1 passed`.

- [ ] **Step 5: Commit the host scaffold**

```bash
cd /Users/saksham/Projects/echoGlove
git add host/
git commit -m "Scaffold host Python package with uv"
```

---

## Task 4: Scaffold repo directories + phase docs

**Files:**
- Create: `STATE.md`
- Create: `docs/phases/phase0-kickoff.md`
- Create: `docs/phases/parking-lot.md`
- Create empty placeholders so directories appear in git (`firmware/.gitkeep`, `hardware/wiring/.gitkeep`, `notebooks/.gitkeep`)

- [ ] **Step 1: Create directory placeholders**

```bash
cd /Users/saksham/Projects/echoGlove
mkdir -p firmware hardware/wiring notebooks
touch firmware/.gitkeep hardware/wiring/.gitkeep notebooks/.gitkeep
```

- [ ] **Step 2: Write `STATE.md`**

```markdown
# STATE — where I left off

**Last updated:** 2026-05-12
**Current phase:** Phase 0 — Fundamentals
**Last commit:** scaffolding (see git log)
**Next step:** Wait for Phase 0 hardware to arrive, then start Task 5 (LED blink).
**Blocked on:** Amazon shipping.

---

## Convention

End every working session by updating the four fields above. Keep the body to ~3 lines. This is your one-screen "where am I" reference for the next session.
```

- [ ] **Step 3: Write `docs/phases/phase0-kickoff.md`**

```markdown
# Phase 0 — Fundamentals: Kickoff

## Goal

Stand up the EchoGlove dev environment end-to-end and prove the loop
hardware → firmware → USB serial → Python works on the Mac.

## Success criteria (from orchestration spec §6)

1. Onboard LED on ESP32-S3 blinks.
2. Pressing a breadboard-mounted button increments a counter printed over USB serial.
3. Python script on Mac reads the serial stream cleanly for 60 s.
4. One I²C sensor from the Freenove kit prints raw readings over the same channel.

## Concept primer: I²C in 90 seconds

I²C ("Inter-Integrated Circuit") is a two-wire serial bus. It lets multiple sensor
chips share two pins on the microcontroller:

- **SDA** (Serial DAta): the data line.
- **SCL** (Serial CLock): the clock line, driven by the microcontroller (master).

Each sensor on the bus has a 7-bit address. The master sends "address + read/write
bit" first; only the sensor with that address responds. Two sensors with the same
address can't share a bus directly — that's why we need a TCA9548A mux in Phase 2.

I²C requires pull-up resistors on SDA and SCL (typically 4.7kΩ to 3.3V). Almost
every Adafruit/SparkFun breakout already includes these on-board; the Freenove
kit's sensors will too. We won't need to add external pull-ups in Phase 0.

## Concept primer: USB serial in 90 seconds

The ESP32-S3 has native USB. When you plug it into the Mac, macOS sees it as a
USB-CDC (Communications Device Class) device and exposes it as a file at
`/dev/tty.usbmodem*` (the exact suffix is per-board). Anything we write to
`Serial.println()` in firmware appears as bytes on that file. `pyserial` opens
the file and reads the bytes.

Baud rate (e.g. 115200) is the bit rate. Both ends must agree.

## Out of scope for Phase 0
- BNO055 / advanced IMU (Phase 1)
- Multiple sensors via mux (Phase 2)
- BLE / wireless (Phase 3)
- Permanent solder joints to sensors (Phase 3)
```

- [ ] **Step 4: Write `docs/phases/parking-lot.md`**

```markdown
# Parking lot

Out-of-scope ideas that came up during the project. Reviewed at each phase boundary
to see if any should be promoted into the next phase.

## Promoted to next phase
(none yet)

## Future / v3+
- SteamVR / OpenGloves driver integration
- Second glove (left hand)
- 3D-printed knuckle mounts and wristband enclosure
- DW3000 UWB for 6DOF world-space position
- ML-based pose model (UltraGlove-style neural network)
- WiFi CSI ambient sensing as a bonus channel
```

- [ ] **Step 5: Commit**

```bash
cd /Users/saksham/Projects/echoGlove
git add STATE.md docs/phases/ firmware/.gitkeep hardware/wiring/.gitkeep notebooks/.gitkeep
git commit -m "Scaffold repo directories and phase docs"
```

---

## Task 5: First LED blink on the ESP32-S3

**Files:**
- Create: `firmware/phase0-blink/platformio.ini`
- Create: `firmware/phase0-blink/src/main.cpp`
- Create: `firmware/phase0-blink/.gitignore`

**Context:** This is the first moment hardware is touched. The ESP32-S3 dev board has an onboard LED — no breadboard wiring needed yet. **Blocked on parts arrival** (Freenove kit and USB-C data cable).

- [ ] **Step 1: Verify the board is recognized by macOS**

Plug the ESP32-S3 into the Mac with a USB-C data cable. Press the **BOOT** button momentarily (this puts it in download mode reliably).

```bash
ls /dev/tty.usb*
```

Expected: prints one or more lines like `/dev/tty.usbmodem101` or `/dev/tty.usbserial-0001`.

If nothing appears:
- Try a different USB-C cable (the most common failure — many cables are charge-only).
- Try a different USB port.
- Hold BOOT, plug in, release BOOT.
- Paste error / behaviour to Claude.

Note the exact `/dev/tty...` path; we'll use it later. Multiple `tty.usb*` entries are normal — usually the longer-named one is the right port.

- [ ] **Step 2: Create the PlatformIO project structure**

```bash
cd /Users/saksham/Projects/echoGlove
mkdir -p firmware/phase0-blink/src
cd firmware/phase0-blink
```

- [ ] **Step 3: Write `firmware/phase0-blink/platformio.ini`**

```ini
[env:esp32-s3-devkitc-1]
platform = espressif32@6.7.0
board = esp32-s3-devkitc-1
framework = arduino
monitor_speed = 115200
monitor_filters = direct
build_flags =
    -DARDUINO_USB_MODE=1
    -DARDUINO_USB_CDC_ON_BOOT=1
```

The `ARDUINO_USB_*` flags enable native USB-CDC so `Serial.println()` goes over the same USB cable used to flash.

- [ ] **Step 4: Write `firmware/phase0-blink/src/main.cpp` — blink only (no button or serial yet)**

```cpp
// Phase 0 — Step 1: blink the onboard LED.
// Onboard LED on most ESP32-S3 DevKitC boards is GPIO 48 (RGB) or GPIO 2.
// If GPIO 2 doesn't blink anything, try GPIO 48. The Freenove board's pinout
// PDF will say definitively.

#include <Arduino.h>

const int LED_PIN = 2;  // FILL THIS IN if 2 doesn't work: check Freenove pinout

void setup() {
  pinMode(LED_PIN, OUTPUT);
}

void loop() {
  digitalWrite(LED_PIN, HIGH);
  delay(500);
  digitalWrite(LED_PIN, LOW);
  delay(500);
}
```

**Fill-in-the-blank:** the `LED_PIN` value. The user looks up the onboard-LED GPIO from the Freenove pinout PDF (in the kit's documentation) and changes it if 2 doesn't work.

- [ ] **Step 5: Write `firmware/phase0-blink/.gitignore`**

```
.pio/
.vscode/
```

- [ ] **Step 6: Build and flash**

In VS Code, open the `firmware/phase0-blink/` folder. PlatformIO will detect the project. From the terminal:

```bash
cd /Users/saksham/Projects/echoGlove/firmware/phase0-blink
pio run -t upload
```

Expected: downloads frameworks (first time only), compiles, then uploads. Final line should contain `Wrote ... bytes` and `Hard resetting via RTS pin...`.

If upload fails with "Failed to connect": hold BOOT, press and release RESET, release BOOT, then re-run.

- [ ] **Step 7: Observe**

The onboard LED on the ESP32-S3 should now blink at 1 Hz (500 ms on, 500 ms off). If it doesn't:
- Tweak `LED_PIN` (try 48, then 21, then 38 — different ESP32-S3 boards use different GPIOs).
- Re-flash after each change.
- If still nothing, photograph the board and paste the photo + the flash output to Claude.

- [ ] **Step 8: Commit**

```bash
cd /Users/saksham/Projects/echoGlove
git add firmware/phase0-blink/
git commit -m "Add Phase 0 firmware: blink onboard LED

First milestone of Phase 0. Single PlatformIO project under
firmware/phase0-blink. Pins, framework flags, and monitor speed
locked in platformio.ini. LED GPIO is board-dependent; current
value works on the Freenove ESP32-S3 board."
```

---

## Task 6: Wire a button on the breadboard and stream a click counter over USB serial

**Files:**
- Modify: `firmware/phase0-blink/src/main.cpp`
- Create: `hardware/wiring/phase0-button.md`

**Context:** This introduces breadboard wiring and USB serial output. The button is the first physical input we read.

- [ ] **Step 1: Write `hardware/wiring/phase0-button.md` — wiring diagram**

```markdown
# Phase 0 — Button wiring

## Bill of materials
- 1× breadboard
- 1× tactile pushbutton (Freenove kit)
- 1× 10kΩ resistor (Freenove kit, color bands: brown-black-orange-gold)
- 4× M/M jumper wires

## Pin assignment
- Button → GPIO 4 (one side)
- GND → other side of button
- 10kΩ resistor: GPIO 4 → 3.3V (acts as pull-up)

## ASCII wiring

```
  3.3V ────[10kΩ]──┬── GPIO 4
                   │
                   └── [BTN] ── GND
```

When the button is **not pressed**: GPIO 4 is pulled HIGH (3.3V) through the resistor.
When the button is **pressed**: GPIO 4 is connected to GND, reads LOW.

This is "active-low" wiring with an external pull-up resistor.

(Alternative: use ESP32's internal pull-up via `INPUT_PULLUP` and skip the
external resistor. We use the external resistor here so the user sees the
pull-up concept physically. We'll switch to `INPUT_PULLUP` in later phases.)
```

- [ ] **Step 2: User wires the breadboard per the diagram and photographs it**

User wires the button + resistor on the breadboard, takes a clear top-down photograph, and pastes it to Claude. **Claude sanity-checks the photo before the user powers the board on with the USB cable.**

Specifically Claude should verify:
1. Button is across two rows that aren't already shorted.
2. Resistor goes from GPIO 4 to 3.3V (not 5V — the ESP32-S3 is 3.3V logic).
3. No bare wires touching the board's power rails unintentionally.

- [ ] **Step 3: Update `firmware/phase0-blink/src/main.cpp` — replace contents with button + JSON serial**

```cpp
// Phase 0 — Step 2: blink + read button + emit JSON over USB serial.

#include <Arduino.h>

const int LED_PIN = 2;       // FILL THIS IN if board uses different pin
const int BUTTON_PIN = 4;
const unsigned long PRINT_INTERVAL_MS = 100;  // 10 Hz status pings

int button_count = 0;
int last_button_state = HIGH;
unsigned long last_print_ms = 0;
unsigned long last_blink_ms = 0;
bool led_state = false;

void setup() {
  Serial.begin(115200);
  pinMode(LED_PIN, OUTPUT);
  pinMode(BUTTON_PIN, INPUT);   // external pull-up wired; no INPUT_PULLUP
  // Wait for USB-CDC to be ready before printing.
  while (!Serial && millis() < 3000) {
    delay(10);
  }
  Serial.println("{\"event\":\"boot\",\"phase\":0}");
}

void loop() {
  unsigned long now = millis();

  // Blink LED at 1 Hz, non-blocking.
  if (now - last_blink_ms >= 500) {
    led_state = !led_state;
    digitalWrite(LED_PIN, led_state);
    last_blink_ms = now;
  }

  // Sample the button. Detect a HIGH → LOW transition (press).
  int button_state = digitalRead(BUTTON_PIN);
  if (last_button_state == HIGH && button_state == LOW) {
    button_count++;
    delay(20);  // crude debounce. FILL THIS IN later with a proper debouncer.
  }
  last_button_state = button_state;

  // Every PRINT_INTERVAL_MS, print one JSON line over USB serial.
  if (now - last_print_ms >= PRINT_INTERVAL_MS) {
    Serial.print("{\"t_ms\":");
    Serial.print(now);
    Serial.print(",\"button_count\":");
    Serial.print(button_count);
    Serial.println("}");
    last_print_ms = now;
  }
}
```

**Fill-in-the-blanks:**
- `LED_PIN` (still board-dependent).
- The 20 ms `delay(20)` debounce — flagged for later replacement with a proper debouncer.

- [ ] **Step 4: Flash and observe in the PlatformIO serial monitor**

```bash
cd /Users/saksham/Projects/echoGlove/firmware/phase0-blink
pio run -t upload
pio device monitor
```

Expected output (LED still blinking; no button press yet):

```
{"event":"boot","phase":0}
{"t_ms":105,"button_count":0}
{"t_ms":206,"button_count":0}
{"t_ms":307,"button_count":0}
...
```

Press the button a few times. Expected: `button_count` increments by 1 per press. If it jumps by 2+ on a single press, the debounce is too short — increase to 40 ms.

Exit the monitor with **Ctrl+C** (NOT Cmd+C — Ctrl+C even on Mac, that's the PlatformIO convention).

- [ ] **Step 5: Commit**

```bash
cd /Users/saksham/Projects/echoGlove
git add firmware/phase0-blink/src/main.cpp hardware/wiring/phase0-button.md
git commit -m "Add button counter and JSON serial output

Reads a tactile button on GPIO 4 with external pull-up, debounces
crudely, and emits a JSON line at 10 Hz containing the elapsed
time in ms and the click count. This is the first JSON-line-
protocol message the Python host will eventually read."
```

---

## Task 7: Practice soldering on a scrap perfboard

**Files:**
- None. Optional `docs/phases/phase0-soldering-notes.md` if the user wants to keep notes.

**Context:** Phase 3 will require soldered joints on a real glove. Phase 0 includes a *no-stakes* soldering practice session on scrap so the user's first solder joint isn't on a $25 sensor breakout. **Skip this task if the user has prior soldering experience.**

- [ ] **Step 1: Watch one soldering tutorial**

Recommended (8 minutes): EEVblog "Soldering Tutorial Part 1: Tools" — search YouTube for it. Or any other primer the user prefers. The goal is to learn:
- Tin the iron tip before each joint.
- Heat the *joint*, not the solder. Apply solder *to the joint*, not the iron.
- A good joint is shiny and concave; a dull or bumpy joint is "cold" and unreliable.

- [ ] **Step 2: Set up workspace safely**

- Well-ventilated room (open a window).
- Non-flammable surface (kitchen counter, tile, or a silicone mat).
- Damp sponge or brass wool nearby for tip cleaning.
- Safety glasses on. Solder splatter goes for eyes.

- [ ] **Step 3: Practice 10 joints on a scrap perfboard**

Solder header pins or random component leads onto a scrap piece of perfboard. Aim for 10 clean joints. Photograph the result and paste to Claude for feedback on joint quality.

- [ ] **Step 4: Multimeter sanity check**

Set the multimeter to continuity mode (beeper symbol). Probe both ends of each joint:
- If it beeps → joint is electrically connected. ✓
- If silent → cold joint. Re-flow with the iron.

- [ ] **Step 5: (No commit; this is practice not code.)**

---

## Task 8: Python host-side serial reader with pytest

**Files:**
- Create: `host/echoglove/serial_reader.py`
- Create: `host/tests/test_serial_reader.py`

**Context:** Now the host side. We write a small Python module that reads JSON lines from the ESP32 over USB serial, parses them, and yields parsed dicts. Tests are TDD-driven against a stubbed stream (no hardware required for tests; tests must pass on CI later without a board attached).

- [ ] **Step 1: Write the failing test (`host/tests/test_serial_reader.py`)**

```python
import io
import json

import pytest

from echoglove.serial_reader import parse_lines, ParseError


def test_parse_valid_json_lines():
    """Lines of well-formed JSON should be yielded as dicts in order."""
    raw = b'{"t_ms": 100, "button_count": 0}\n{"t_ms": 200, "button_count": 1}\n'
    stream = io.BytesIO(raw)
    result = list(parse_lines(stream))
    assert result == [
        {"t_ms": 100, "button_count": 0},
        {"t_ms": 200, "button_count": 1},
    ]


def test_partial_final_line_is_dropped():
    """A trailing line without a newline is incomplete and skipped."""
    raw = b'{"t_ms": 100}\n{"t_ms": 200, "incomplete'
    stream = io.BytesIO(raw)
    result = list(parse_lines(stream))
    assert result == [{"t_ms": 100}]


def test_blank_lines_skipped():
    """Empty lines (heartbeat or transient) are silently dropped."""
    raw = b'\n{"t_ms": 100}\n\n\n{"t_ms": 200}\n'
    stream = io.BytesIO(raw)
    result = list(parse_lines(stream))
    assert result == [{"t_ms": 100}, {"t_ms": 200}]


def test_malformed_json_raises_parse_error():
    """A non-blank line that is not valid JSON raises ParseError."""
    raw = b'{"t_ms": 100}\nnot-json\n'
    stream = io.BytesIO(raw)
    with pytest.raises(ParseError) as exc_info:
        list(parse_lines(stream))
    assert "not-json" in str(exc_info.value)
```

- [ ] **Step 2: Run the test, confirm it fails (expected: import error)**

```bash
cd /Users/saksham/Projects/echoGlove/host
uv run pytest tests/test_serial_reader.py -v
```

Expected: `ImportError` or `ModuleNotFoundError` on `echoglove.serial_reader`. That's the goal — red bar before we implement.

- [ ] **Step 3: Write the minimal implementation (`host/echoglove/serial_reader.py`)**

```python
"""Parse JSON lines from a byte stream (typically a serial port).

Used by the host-side reader to consume the firmware's USB serial output.
The contract: each newline-terminated line is exactly one JSON object.
Blank lines are silently dropped. Malformed JSON raises ParseError.

Designed so it can be unit-tested against any binary file-like object
(e.g. io.BytesIO in tests) without needing a real serial port.
"""

from __future__ import annotations

import json
from typing import BinaryIO, Iterator


class ParseError(ValueError):
    """Raised when a non-blank line is not valid JSON."""


def parse_lines(stream: BinaryIO) -> Iterator[dict]:
    """Yield one parsed dict per newline-terminated JSON line in stream.

    A trailing line without a newline is treated as incomplete and dropped.
    Blank lines are skipped silently.
    """
    buf = b""
    while True:
        chunk = stream.read(1024)
        if not chunk:
            break
        buf += chunk

    *lines, tail = buf.split(b"\n")
    # `tail` is whatever followed the last newline. If non-empty, it's a
    # partial trailing line; drop it per the contract.
    del tail

    for raw in lines:
        line = raw.strip()
        if not line:
            continue
        try:
            yield json.loads(line)
        except json.JSONDecodeError as e:
            raise ParseError(f"could not parse line: {line!r}") from e
```

- [ ] **Step 4: Run the tests, confirm all four pass**

```bash
cd /Users/saksham/Projects/echoGlove/host
uv run pytest tests/test_serial_reader.py -v
```

Expected: `4 passed in 0.0Xs`.

- [ ] **Step 5: Add a live-port runner as a script (optional integration test)**

Append to `host/echoglove/serial_reader.py`:

```python
def stream_port(port: str, baud: int = 115200) -> Iterator[dict]:
    """Open a real serial port and yield parsed dicts forever.

    Not unit-tested (needs hardware). Use the parse_lines() function for
    anything testable. This helper is a thin convenience wrapper.
    """
    import serial  # imported lazily so tests don't need hardware

    with serial.Serial(port, baud, timeout=1) as ser:
        yield from parse_lines(ser)


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("usage: python -m echoglove.serial_reader /dev/tty.usbmodemXXXX")
        raise SystemExit(2)
    for msg in stream_port(sys.argv[1]):
        print(msg)
```

- [ ] **Step 6: Run the script against the live ESP32**

With the ESP32 plugged in and running the Task 6 firmware:

```bash
cd /Users/saksham/Projects/echoGlove/host
uv run python -m echoglove.serial_reader /dev/tty.usbmodemXXXX  # use real port
```

(Replace `/dev/tty.usbmodemXXXX` with the actual path from `ls /dev/tty.usb*`.)

Expected: dicts stream to terminal at 10 Hz. Press the button — `button_count` increments. Let it run for at least 60 s without errors or stalls. Ctrl+C to stop.

If the PlatformIO serial monitor is still open in another terminal, it owns the port — close it first. Only one process can hold the serial port at a time.

- [ ] **Step 7: Commit**

```bash
cd /Users/saksham/Projects/echoGlove
git add host/echoglove/serial_reader.py host/tests/test_serial_reader.py
git commit -m "Add serial JSON-line reader and parser

parse_lines() is the testable core: takes a binary stream, yields
one dict per JSON line, skips blanks, raises ParseError on bad
input. stream_port() is the thin wrapper that opens a real serial
port and pipes through parse_lines() — covered by integration not
unit tests."
```

---

## Task 9: Wire one I²C sensor from the Freenove kit and stream raw readings

**Files:**
- Modify: `firmware/phase0-blink/src/main.cpp` (rename project to `phase0-fundamentals` if preferred, but keep simple — just add to existing project)
- Create: `hardware/wiring/phase0-i2c.md`

**Context:** This is the I²C bring-up step. The Freenove kit *probably* contains an MPU-6050. If it does, use that. If it contains a different I²C sensor (e.g. BMP280, GY-521, ADXL345), use whichever is present — the I²C scan code is generic.

The point of this task is the *I²C concept* (address, scan, read) — not any specific sensor's data.

- [ ] **Step 1: Confirm which I²C sensor is in the Freenove kit**

User looks at the kit inventory from Task 1 and identifies the I²C sensor(s). Common Freenove kit sensors:
- MPU-6050 (6-axis IMU, address 0x68)
- BMP280 / BMP180 (barometric pressure, 0x76 or 0x77)
- ADXL345 (3-axis accelerometer, 0x53)
- HDC1080 / SHT3x (humidity/temp, 0x40 or 0x44)

Pick one. If the kit has none, claude orders an MPU-6050 GY-521 breakout from Amazon (~$5) before continuing.

For the rest of this task, assume **MPU-6050**. Adjust the I²C address and any sensor-specific register reads if you're using a different chip.

- [ ] **Step 2: Write `hardware/wiring/phase0-i2c.md`**

```markdown
# Phase 0 — I²C sensor wiring (MPU-6050)

## Bill of materials
- 1× MPU-6050 GY-521 breakout
- 4× F/M jumper wires (or M/M if the breakout has headers and is breadboarded)
- existing breadboard from Task 6 (button stays wired)

## Pin assignment
- ESP32-S3 GPIO 8  → MPU-6050 SDA
- ESP32-S3 GPIO 9  → MPU-6050 SCL
- ESP32-S3 3.3V    → MPU-6050 VCC
- ESP32-S3 GND     → MPU-6050 GND

(GPIO 8 and 9 are the default I²C pins on the ESP32-S3 DevKitC for Wire library use.
Some boards default to GPIO 21/22. If GPIO 8/9 don't work, try 21/22. The Freenove
pinout PDF in the kit confirms which pair the board exposes.)

## I²C address
- MPU-6050 default: 0x68 (with AD0 pin tied LOW, which is the breakout default).
- Will appear in the I²C scan output as `0x68`.

## Pull-up resistors
- The MPU-6050 GY-521 breakout includes onboard 4.7kΩ pull-ups on SDA and SCL.
- No external pull-ups needed.
```

- [ ] **Step 3: User wires the sensor, photographs, Claude sanity-checks**

User powers down (unplug USB), wires per the diagram, plugs back in. Photo + paste to Claude before any code is flashed.

- [ ] **Step 4: Update `firmware/phase0-blink/src/main.cpp` to add I²C scan and raw read**

Full replacement file:

```cpp
// Phase 0 — Step 3: blink + button + USB serial + I²C sensor.
// Adds an I²C scan on boot and continuous raw register reads.

#include <Arduino.h>
#include <Wire.h>

const int LED_PIN = 2;          // FILL THIS IN if board uses different pin
const int BUTTON_PIN = 4;
const int SDA_PIN = 8;          // FILL THIS IN if board uses different pin
const int SCL_PIN = 9;          // FILL THIS IN if board uses different pin
const uint8_t MPU_ADDR = 0x68;
const unsigned long PRINT_INTERVAL_MS = 100;

int button_count = 0;
int last_button_state = HIGH;
unsigned long last_print_ms = 0;
unsigned long last_blink_ms = 0;
bool led_state = false;

void i2c_scan() {
  Serial.println("{\"event\":\"i2c_scan_begin\"}");
  for (uint8_t addr = 1; addr < 127; addr++) {
    Wire.beginTransmission(addr);
    if (Wire.endTransmission() == 0) {
      Serial.print("{\"event\":\"i2c_found\",\"addr\":\"0x");
      Serial.print(addr, HEX);
      Serial.println("\"}");
    }
  }
  Serial.println("{\"event\":\"i2c_scan_end\"}");
}

void mpu_init() {
  // Wake MPU-6050 from sleep: write 0 to PWR_MGMT_1 (0x6B).
  Wire.beginTransmission(MPU_ADDR);
  Wire.write(0x6B);
  Wire.write(0);
  Wire.endTransmission(true);
}

void mpu_read_and_print() {
  Wire.beginTransmission(MPU_ADDR);
  Wire.write(0x3B);                          // start of accel registers
  Wire.endTransmission(false);
  Wire.requestFrom(MPU_ADDR, (uint8_t)14);   // 6 accel + 2 temp + 6 gyro

  int16_t ax = (Wire.read() << 8) | Wire.read();
  int16_t ay = (Wire.read() << 8) | Wire.read();
  int16_t az = (Wire.read() << 8) | Wire.read();
  int16_t temp = (Wire.read() << 8) | Wire.read();
  int16_t gx = (Wire.read() << 8) | Wire.read();
  int16_t gy = (Wire.read() << 8) | Wire.read();
  int16_t gz = (Wire.read() << 8) | Wire.read();

  Serial.print("{\"t_ms\":");
  Serial.print(millis());
  Serial.print(",\"button_count\":");
  Serial.print(button_count);
  Serial.print(",\"ax\":");
  Serial.print(ax);
  Serial.print(",\"ay\":");
  Serial.print(ay);
  Serial.print(",\"az\":");
  Serial.print(az);
  Serial.print(",\"gx\":");
  Serial.print(gx);
  Serial.print(",\"gy\":");
  Serial.print(gy);
  Serial.print(",\"gz\":");
  Serial.print(gz);
  Serial.println("}");
}

void setup() {
  Serial.begin(115200);
  pinMode(LED_PIN, OUTPUT);
  pinMode(BUTTON_PIN, INPUT);
  while (!Serial && millis() < 3000) delay(10);

  Wire.begin(SDA_PIN, SCL_PIN);
  Serial.println("{\"event\":\"boot\",\"phase\":0}");

  i2c_scan();
  mpu_init();
  Serial.println("{\"event\":\"mpu_ready\"}");
}

void loop() {
  unsigned long now = millis();

  if (now - last_blink_ms >= 500) {
    led_state = !led_state;
    digitalWrite(LED_PIN, led_state);
    last_blink_ms = now;
  }

  int button_state = digitalRead(BUTTON_PIN);
  if (last_button_state == HIGH && button_state == LOW) {
    button_count++;
    delay(20);
  }
  last_button_state = button_state;

  if (now - last_print_ms >= PRINT_INTERVAL_MS) {
    mpu_read_and_print();
    last_print_ms = now;
  }
}
```

**Fill-in-the-blanks:**
- `LED_PIN`, `SDA_PIN`, `SCL_PIN` (board-dependent).

- [ ] **Step 5: Flash and observe in the PlatformIO serial monitor**

```bash
cd /Users/saksham/Projects/echoGlove/firmware/phase0-blink
pio run -t upload
pio device monitor
```

Expected boot output:

```
{"event":"boot","phase":0}
{"event":"i2c_scan_begin"}
{"event":"i2c_found","addr":"0x68"}
{"event":"i2c_scan_end"}
{"event":"mpu_ready"}
{"t_ms":123,"button_count":0,"ax":1234,"ay":-567,"az":16380,"gx":3,"gy":-12,"gz":1}
...
```

When you pick up the breadboard and tilt it, `ax`/`ay`/`az` should change. When it's flat on the desk, `az` should be near ±16384 (±1g in raw counts). When still, `gx`/`gy`/`gz` should be near 0.

Press the button: `button_count` still increments.

- [ ] **Step 6: Run the Python reader against the I²C stream**

```bash
cd /Users/saksham/Projects/echoGlove/host
uv run python -m echoglove.serial_reader /dev/tty.usbmodemXXXX
```

Expected: dicts stream including the new ax/ay/az/gx/gy/gz fields. Run for 60 s without errors.

- [ ] **Step 7: Commit**

```bash
cd /Users/saksham/Projects/echoGlove
git add firmware/phase0-blink/src/main.cpp hardware/wiring/phase0-i2c.md
git commit -m "Add I2C scan and MPU-6050 raw read

On boot, scan the I2C bus and report any responding addresses,
then wake the MPU-6050 and stream raw accel/gyro registers in the
same JSON-line protocol. This is the first multi-sensor message
shape — Phase 1 will swap MPU-6050 for BNO055 and add quaternion
parsing on the host side."
```

---

## Task 10: Phase 0 verification + ship

**Files:**
- Modify: `STATE.md`
- Create: `docs/phases/phase0-retro.md`

**Context:** All four verification criteria from the orchestration spec §6 must pass before we tag the phase.

- [ ] **Step 1: Run the verification checklist**

Open `docs/phases/phase0-kickoff.md` and walk the success criteria. For each, paste a screenshot or output:

1. **LED blinks** — video of LED blinking, or just "yes confirmed".
2. **Button increments counter** — terminal screenshot showing `button_count` incrementing on press.
3. **Python script reads serial cleanly for 60s** — run `time uv run python -m echoglove.serial_reader /dev/tty.usbmodemXXXX | head -n 600`; confirm 60 s × 10 Hz ≈ 600 lines with no errors.
4. **I²C sensor raw readings** — terminal screenshot showing the `ax/ay/az/gx/gy/gz` fields varying when the board is tilted.

Each criterion must pass. If any fails, do NOT proceed — debug it, then re-verify.

- [ ] **Step 2: Run host tests one final time**

```bash
cd /Users/saksham/Projects/echoGlove/host
uv run pytest tests/ -v
```

Expected: all tests pass.

- [ ] **Step 3: Write the retro `docs/phases/phase0-retro.md`**

Template — user fills in honestly:

```markdown
# Phase 0 retrospective

## What was built
- Phase 0 BOM ordered and inventoried.
- VS Code + PlatformIO + Python (uv) toolchain on the Mac.
- Repo scaffolded (firmware/, host/, hardware/, docs/phases/).
- ESP32-S3 onboard LED blinking.
- Tactile button counter streaming over USB serial as JSON lines.
- Python reader parsing the stream, with pytest coverage.
- MPU-6050 (or other I²C sensor from Freenove kit) raw accel/gyro
  streaming on the same channel.

## What surprised me
(fill in: e.g. "USB-C charge-only cables are a real thing", "I²C scanning
is much simpler than I expected", "the LED was on a different GPIO than
the docs said".)

## What felt rote / I'd skim next time
(fill in)

## What I want more depth on in Phase 1
(fill in: e.g. "what does the BNO055 do internally that the MPU-6050
doesn't?", "how does the Madgwick filter actually work?")

## Time spent
- Calendar: ~X weeks
- Active hours: ~Y hours

## Costs
- Tools/parts spend so far: $Z (vs. $110–145 estimate)

## Anything for the parking lot
(fill in: out-of-scope ideas that surfaced)
```

- [ ] **Step 4: Update `STATE.md`**

```markdown
# STATE — where I left off

**Last updated:** <YYYY-MM-DD>
**Current phase:** Phase 1 — IMU bring-up (Phase 0 shipped)
**Last commit:** Ship Phase 0
**Next step:** Brainstorm Phase 1: order BNO055, write Phase 1 spec + plan.
**Blocked on:** Nothing.
```

- [ ] **Step 5: Final commit + tag**

```bash
cd /Users/saksham/Projects/echoGlove
git add docs/phases/phase0-retro.md STATE.md
git commit -m "Ship Phase 0

All four orchestration-spec verification criteria met:
LED blinks, button-counter streams over USB serial, Python
reader runs cleanly for 60+ seconds, and the Freenove kit's I2C
sensor (MPU-6050 in this build) streams raw accel/gyro on the
same JSON-line protocol. Toolchain healthy, repo scaffolded,
ready for Phase 1."
git tag phase-0
```

- [ ] **Step 6: Celebrate**

You just took a complete beginner from "never touched a breadboard" to "I have a working hardware-to-Python data pipeline on my desk." That is a real milestone. Phase 1 begins with its own brainstorm cycle.

---

## Self-review

**Spec coverage** (against orchestration spec §6 Phase 0 criteria):

| Criterion | Task(s) |
|---|---|
| Onboard LED blinks | Task 5 |
| Button press increments counter over USB serial | Task 6 |
| Python script reads serial cleanly for 60 s | Task 8 step 6, Task 10 step 1.3 |
| One I²C sensor from Freenove kit prints raw readings | Task 9 |

All four covered. ✓

**Concept primer coverage** (against orchestration spec §7 Phase 0 learning concepts):

| Concept | Where introduced |
|---|---|
| Voltage / current / ground | Task 6 wiring diagram (pull-up explanation) |
| GPIO digital vs analog | Task 6 (digital pin), Task 9 wiring |
| I²C basics | Task 4 kickoff primer, Task 9 scan + read |
| Breadboard convention | Task 6 |
| Soldering | Task 7 (optional practice) |
| PlatformIO toolchain | Task 2, Task 5 |
| USB serial on Mac | Task 4 kickoff primer, Task 5 step 1 |
| Python serial reader | Task 8 |

All covered. ✓

**Placeholder scan:** All "FILL THIS IN" comments in firmware are intentional learning hooks with explicit context for the user. No vague "add error handling" or "TBD". ✓

**Type consistency:** `parse_lines()` consistent in test and implementation. `ParseError` defined once, imported by tests. JSON message shape `{"t_ms": int, "button_count": int, ...}` consistent across firmware versions in Tasks 6 and 9. ✓

**Hardware-physical adaptation:** TDD applied where it fits (Task 8 host code). Verification-by-output used for firmware (Tasks 5, 6, 9) — explicit expected outputs given. Human-only physical steps (wiring, soldering, observing LED) flagged with photo-and-paste-to-Claude sanity checks. ✓

---

## Execution handoff

This is a hardware-heavy phase with substantial human-only physical steps. Subagent-driven execution would have to pause at every physical step and wait for the human anyway, so the benefit over inline execution is small.

**Recommendation: inline execution via the executing-plans skill.** Claude walks the user through each task in the active session, pausing for parts shipping and physical-action steps.

Confirm with the user before invoking the execution skill.
