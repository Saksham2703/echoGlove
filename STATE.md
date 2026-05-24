# STATE — where I left off

**Last updated:** 2026-05-24
**Current phase:** Phase 0 — Fundamentals (5 of 10 tasks done; all hardware in hand)
**Last commit:** `def5fb4 Add serial JSON-line reader and parser`
**Next step:** Task 5 — plug in ESP32-S3 DevKitC-1, flash LED blink. Tasks 6, 7, 9, 10 follow in sequence.
**Blocked on:** Nothing.

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
| 5 | LED blink | **pending — needs hardware** | `firmware/phase0-blink/` (to be created) |
| 6 | Button + JSON serial | **pending — needs hardware** | same firmware project |
| 7 | Soldering practice | **pending — needs hardware** | `hardware/wiring/phase0-soldering-notes.md` |
| 8 | Python serial reader + pytest | ✓ committed | `host/src/echoglove/serial_reader.py`, `host/tests/test_serial_reader.py`, commit `def5fb4` |
| 9 | I²C sensor wiring + raw read | **pending — needs hardware** | same firmware project + `hardware/wiring/phase0-i2c.md` |
| 10 | Verification + retro + `git tag phase-0` | **pending** | `docs/phases/phase0-retro.md` |

Task 8 is complete. **Task 5 is next** — plug in the ESP32-S3 DevKitC-1, verify `ls /dev/tty.usb*` shows it, create `firmware/phase0-blink/`, and flash the LED blink firmware.

## Critical context (gotchas already resolved — don't redo)

- **Chip identity:** The Freenove kit (Amazon B0CJJJ7BCY) contains an **ESP32-WROVER-E** dev board, NOT an ESP32-S3 (the previous-session conclusion was wrong). The orchestration spec assumes S3 throughout; Phase 0 firmware target is the **ESP32-S3 DevKitC-1 2-pack** ordered separately (BOM item 5). The Freenove WROVER board is a component source (sensors, breadboard, jumpers, discretes) and is NOT flashed in Phase 0. Don't try to use `board = esp32dev` — stay on `board = esp32-s3-devkitc-1`.
- **MPU-6050 confirmed as Task 9 sensor.** Visible in the Freenove parts list image as "Accelerometer Module" (GY-521 style). I²C @ `0x68`, WHO_AM_I reg `0x75` returns `0x68`.
- **`CPLUS_INCLUDE_PATH` shell-env trap:** Line 41 of `~/.zshrc` previously appended the macOS C++ SDK headers to GCC's search path — this broke PlatformIO builds (and would break any GCC cross-compiler). Commented out on 2026-05-13 with a dated note. New shell sessions are clean. If a future session sees Xtensa builds failing with errors mentioning `/Library/Developer/CommandLineTools/SDKs/MacOSX.sdk/`, the env var is back — check the same line in `~/.zshrc`.
- **Host Python layout:** uv 0.11.14 created the `host/src/echoglove/` layout (modern uv default). This is intentional — we kept the src/ layout rather than flattening to `host/echoglove/` as the plan originally suggested. Imports work as `from echoglove.serial_reader import ...` via uv's editable install. The plan's "flatten" step in Task 3 was skipped on purpose.
- **PlatformIO Core path:** Lives at `~/.platformio/penv/bin/pio`. Add to PATH or use the full path. VS Code's PlatformIO extension uses the same install.
- **uv version:** `0.11.14` (Homebrew). Python pinned to `3.12` for the host package.
- **Commit messages:** No conventional-commit prefixes (no `feat:`/`chore:`). Short title (<50 chars), imperative; body only when there's real work to explain. **Never** add `Co-Authored-By: Claude ...` trailers (durable rule, also recorded in global `~/Projects/CLAUDE.md` §5).
- **Git pushes:** Repo is private and stays local. Never push to remote without asking.

## Hardware arrival checklist (run this once the Freenove kit lands)

1. Photograph the kit contents laid out on a table.
2. Cross-check against the pre-filled "Kit inventory" section in `hardware/bom-phase0.md` — flag any missing or substituted parts in "As-arrived inventory".
3. Confirm the **Accelerometer Module** is in fact a GY-521 / MPU-6050. If it's an MPU-9250 or LSM6DS3 instead, the Task 9 register addresses change — paste the actual silkscreen text into the next session and we'll adapt.
4. Confirm the included USB cable is a **data** cable (not charge-only) by plugging the Freenove board in and checking `ls /dev/tty.usbmodem* /dev/tty.usbserial*` — at least one entry should appear. (Note: this is the WROVER board, which uses a CP2102 USB-UART bridge — it shows up as `tty.usbserial-*`, not `tty.usbmodem*`.)
5. When the ordered ESP32-S3 DevKitC-1 2-pack arrives separately, plug one in with one of the new UGREEN USB-C cables — it should appear as `/dev/tty.usbmodem*` (S3 has native USB-CDC, different device name from the WROVER).

## Convention

End every working session by updating the five fields above. Keep the body of the top section to ~3 lines. The "For the next session" / "Critical context" / "Hardware arrival checklist" sections below evolve with the project and may grow or shrink as needed.
