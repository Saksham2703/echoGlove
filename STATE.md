# STATE — where I left off

**Last updated:** 2026-05-25
**Current phase:** Phase 1 — IMU bring-up
**Last commit:** `Add Phase 1 verification scripts (rate + no-jumps)`
**Next step:** Order BNO055 (Amazon B017PEIGIG). When it arrives: solder header → wire → photo to Claude → fill blanks in firmware/phase1-imu/src/main.cpp → flash → run V1/V2/V3.
**Blocked on:** BNO055 hardware arrival.

---

## For the next session — quick start

**Read first (in this order):**
1. `STATE.md` (this file) — top-level orientation
2. `CLAUDE.md` — project conventions (commit style, git rules, what NOT to do)
3. `docs/superpowers/specs/2026-05-12-echoglove-orchestration-design.md` — full project plan (Phases 0–6)
4. `docs/superpowers/plans/2026-05-12-phase0-fundamentals.md` — current phase's 10-task plan
5. `hardware/bom-phase0.md` — what was ordered, what arrived, the kit inventory (pre-filled from Freenove parts list)
6. `docs/phases/phase0-kickoff.md` — Phase 0 goals + I²C/USB-serial primer

**Phase 0 task status:**

| # | Task | Status | Where |
|---|---|---|---|
| 1 | Order BOM | ✓ committed | `hardware/bom-phase0.md`, commit `e637391` |
| 2 | VS Code + PlatformIO | ✓ verified building for `esp32-s3-devkitc-1` | system-level, no commit |
| 3 | Python + uv host scaffold | ✓ pytest passes | `host/`, commit `9295dbe` |
| 4 | Repo dirs + phase docs | ✓ | `docs/phases/`, `STATE.md`, commit `70feb5b` |
| 5 | LED blink | ✓ committed | `firmware/phase0-blink/`, RGB LED on GPIO 48 via neopixelWrite |
| 6 | Button + JSON serial | ✓ committed | `firmware/phase0-blink/src/main.cpp`, button on GPIO 4 |
| 7 | Soldering practice | **pending — needs hardware** | `hardware/wiring/phase0-soldering-notes.md` |
| 8 | Python serial reader + pytest | ✓ committed | `host/src/echoglove/serial_reader.py`, `host/tests/test_serial_reader.py`, commit `def5fb4` |
| 9 | I²C sensor wiring + raw read | **pending — needs hardware** | same firmware project + `hardware/wiring/phase0-i2c.md` |
| 10 | Verification + retro + `git tag phase-0` | **pending** | `docs/phases/phase0-retro.md` |

Tasks 5, 6, and 8 are complete. **Task 7 is optional** (soldering practice on scrap perfboard — skip if you have prior soldering experience). **Task 9 is the main next step** — wire the MPU-6050 from the Freenove kit to the ESP32-S3 via I²C (GPIO 8 = SDA, GPIO 9 = SCL). First do a formal photo inventory of the Freenove kit to confirm the MPU-6050 module is present (see STATE.md hardware arrival checklist).

## Critical context (gotchas already resolved — don't redo)

- **Chip identity:** The Freenove kit (Amazon B0CJJJ7BCY) contains an **ESP32-WROVER-E** dev board, NOT an ESP32-S3 (the previous-session conclusion was wrong). The orchestration spec assumes S3 throughout; Phase 0 firmware target is the **ESP32-S3 DevKitC-1 2-pack** ordered separately (BOM item 5). The Freenove WROVER board is a component source (sensors, breadboard, jumpers, discretes) and is NOT flashed in Phase 0. Don't try to use `board = esp32dev` — stay on `board = esp32-s3-devkitc-1`.
- **MPU-6050 confirmed as Task 9 sensor.** Visible in the Freenove parts list image as "Accelerometer Module" (GY-521 style). I²C @ `0x68`, WHO_AM_I reg `0x75` returns `0x68`.
- **`CPLUS_INCLUDE_PATH` shell-env trap:** Line 41 of `~/.zshrc` previously appended the macOS C++ SDK headers to GCC's search path — this broke PlatformIO builds (and would break any GCC cross-compiler). Commented out on 2026-05-13 with a dated note. New shell sessions are clean. If a future session sees Xtensa builds failing with errors mentioning `/Library/Developer/CommandLineTools/SDKs/MacOSX.sdk/`, the env var is back — check the same line in `~/.zshrc`.
- **Host Python layout:** uv 0.11.14 created the `host/src/echoglove/` layout (modern uv default). This is intentional — we kept the src/ layout rather than flattening to `host/echoglove/` as the plan originally suggested. Imports work as `from echoglove.serial_reader import ...` via uv's editable install. The plan's "flatten" step in Task 3 was skipped on purpose.
- **PlatformIO Core path:** Lives at `~/.platformio/penv/bin/pio`. Add to PATH or use the full path. VS Code's PlatformIO extension uses the same install.
- **uv version:** `0.11.14` (Homebrew). Python pinned to `3.12` for the host package.
- **Flashing workflow (learned 2026-05-24):** The ESP32-S3 requires manual bootloader entry every flash: hold BOOT, tap RST, release BOOT. The device re-enumerates at `/dev/tty.usbmodem1101` (bootloader mode) — use that port for `--upload-port`. After flash, unplug+replug to boot into firmware (RTS hard-reset is unreliable with native USB-CDC). Running firmware also appears at `/dev/tty.usbmodem1101`.
- **Onboard LED (learned 2026-05-24):** GPIO 48, WS2812B RGB. Use `neopixelWrite(48, r, g, b)` — plain `digitalWrite` does nothing. GPIO 2 has no LED on this board.
- **IDE false positives:** VS Code clang shows `'Arduino.h' file not found` and `undeclared identifier` errors in firmware files. These are clang LSP not knowing the PlatformIO include paths — not real errors. PlatformIO builds compile and flash correctly regardless.
- **serial_reader stream_port:** Uses `readline()` loop, not `parse_lines()`. `parse_lines()` buffers until EOF (never arrives on a live port). The fix is committed in `host/src/echoglove/serial_reader.py`.
- **Commit messages:** No conventional-commit prefixes (no `feat:`/`chore:`). Short title (<50 chars), imperative; body only when there's real work to explain. **Never** add `Co-Authored-By: Claude ...` trailers (durable rule, also recorded in global `~/Projects/CLAUDE.md` §5).
- **Git pushes:** Repo is private and stays local. Never push to remote without asking.

## Before Task 9 (I²C sensor wiring)

1. **Physically locate the MPU-6050 module** in the Freenove kit — it's the "Accelerometer Module" (GY-521 PCB, says MPU-6050 on the chip). Photograph the silkscreen and paste it to Claude if it's not an MPU-6050; register addresses differ for MPU-9250 or LSM6DS3.
2. Wire it up per `hardware/wiring/phase0-i2c.md`: SDA → GPIO 8, SCL → GPIO 9, VCC → 3.3V, GND → GND. Photo before power-on — Claude sanity-checks.
3. The breadboard currently has the ESP32-S3 and the button circuit (GPIO 4). The I²C sensor shares the same breadboard — leave the button wired, add the sensor in a free area.

## Convention

End every working session by updating the five fields above. Keep the body of the top section to ~3 lines. The "For the next session" / "Critical context" / "Hardware arrival checklist" sections below evolve with the project and may grow or shrink as needed.
