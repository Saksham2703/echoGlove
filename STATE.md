# STATE — where I left off

**Last updated:** 2026-09-22
**Current phase:** Phase 2 — IR fingertip layer + I²C mux — design done, not started
**Last commit:** `Add Phase 2 design spec`
**Next step:** Write the Phase 2 implementation plan from `docs/superpowers/specs/2026-09-22-echoglove-phase2-tof-design.md`. Parts ordered 2026-09-20 from Adafruit; nothing can be built until they land. While executing Phase 2, research and commit `hardware/bom-phase3.md` — it must include the CH-101, which §3 of the orchestration doc wants ordered at the *start* of Phase 3.
**Blocked on:** Phase 2 hardware in transit (5+1 VL6180X, 1+1 TCA9548A, 6 STEMMA cables).

---

## For the next session — quick start

**Read first (in this order):**
1. `STATE.md` (this file) — top-level orientation
2. `CLAUDE.md` — project conventions (commit style, git rules, what NOT to do)
3. `docs/superpowers/specs/2026-05-12-echoglove-orchestration-design.md` — full project plan (Phases 0–6)
4. `docs/superpowers/specs/2026-09-22-echoglove-phase2-tof-design.md` — the approved Phase 2 design
5. `docs/phases/phase1-retro.md` — what last shipped and what broke along the way
6. `LEARNINGS.md` — accumulated gotchas
7. `hardware/bom-phase2.md` — Phase 2 parts (ordered) and the settled mount geometry

**Phase 0 task status — all complete, shipped at commit `e47e0f0`, tag `phase-0`:**

| # | Task | Status | Where |
|---|---|---|---|
| 1 | Order BOM | ✓ | `hardware/bom-phase0.md`, commit `e637391` |
| 2 | VS Code + PlatformIO | ✓ | system-level, no commit |
| 3 | Python + uv host scaffold | ✓ | `host/`, commit `9295dbe` |
| 4 | Repo dirs + phase docs | ✓ | `docs/phases/`, `STATE.md`, commit `70feb5b` |
| 5 | LED blink | ✓ | `firmware/phase0-blink/`, RGB LED on GPIO 48 via neopixelWrite |
| 6 | Button + JSON serial | ✓ | `firmware/phase0-blink/src/main.cpp`, button on GPIO 4 |
| 7 | Soldering practice | ✓ done 2026-09-19 | 12 joints on scrap perfboard, continuity-verified both ways |
| 8 | Python serial reader + pytest | ✓ | `host/src/echoglove/serial_reader.py`, commit `def5fb4` |
| 9 | I²C sensor wiring + raw read | ✓ | MPU-6050 @ 0x68 streamed raw accel/gyro at 10 Hz |
| 10 | Verification + retro + `git tag phase-0` | ✓ | `docs/phases/phase0-retro.md`, all 4 criteria met |

**Phase 1 — all 3 spec §6 criteria met.** V1: 99.8 Hz. V2: cube tracks all three
axes 1:1. V3: 29,998/29,998 consecutive pairs at |dot| ≥ 0.99 over 5 min.
Details in `docs/phases/phase1-retro.md`.

## Critical context (gotchas already resolved — don't redo)

- **Chip identity:** The Freenove kit (Amazon B0CJJJ7BCY) contains an **ESP32-WROVER-E**, NOT an ESP32-S3. Firmware target is the **ESP32-S3 DevKitC-1 2-pack** ordered separately. The Freenove board is a component source only. Stay on `board = esp32-s3-devkitc-1`.
- **Which S3 board:** the 2-pack means two identical boards. The one currently wired is the second unit (was factory-fresh, running the r→g→b demo, until flashed with Phase 1 firmware on 2026-09-20). A board cycling r→g→b is unflashed; Phase 0 firmware blinks blue only.
- **`CPLUS_INCLUDE_PATH` shell-env trap:** Line 41 of `~/.zshrc` appended macOS C++ SDK headers to GCC's search path, breaking PlatformIO builds. Commented out 2026-05-13. If Xtensa builds fail with errors mentioning `/Library/Developer/CommandLineTools/SDKs/MacOSX.sdk/`, it's back.
- **Host Python layout:** `host/src/echoglove/` src-layout is intentional. Imports work as `from echoglove.serial_reader import ...`. Don't flatten it.
- **PlatformIO Core path:** `~/.platformio/penv/bin/pio`.
- **uv version:** `0.11.14` (Homebrew). Python pinned to `3.12`.
- **Flashing workflow:** manual bootloader entry every flash — hold BOOT, tap RST, release BOOT. The device re-enumerates under a *different* node in download mode (`/dev/tty.usbmodem1101` running → `/dev/tty.usbmodem101` in bootloader). Always `ls /dev/tty.usb*` after the sequence and use the new path for `--upload-port`. After flashing, unplug+replug — the RTS hard-reset is unreliable over native USB-CDC.
- **Onboard LED:** GPIO 48, WS2812B RGB. Use `neopixelWrite(48, r, g, b)`.
- **`platformio.ini` is a lockfile:** exact `@1.6.4`-style pins, never carets. Caret ranges silently drifted three Adafruit libraries over the 4-month gap.
- **I²C bus:** GPIO 8 = SDA, GPIO 9 = SCL. BNO055 @ `0x28` (ADR floating), MPU-6050 @ `0x68`. Phase 1 firmware has no I²C scan — reflash `firmware/phase0-blink/` to get its `i2c_scan()` when the bus needs diagnosing.
- **BNO055 calibration:** gyro self-calibrates at rest; mag needs a figure-8; accel needs ~6 stable orientations held a few seconds each. Get `cal_accel` to 3 *before* running the 5-minute jump test.
- **IDE false positives:** VS Code clang shows `'Arduino.h' file not found` in firmware files. Not real — PlatformIO builds fine.
- **serial_reader stream_port:** uses a `readline()` loop, not `parse_lines()` (which buffers until EOF that never arrives on a live port).
- **Commit messages:** no conventional-commit prefixes. Short imperative title (<50 chars); body only when there's real work to explain. **Never** add `Co-Authored-By: Claude ...` trailers.
- **Git pushes:** repo is private and stays local. Never push to remote without asking.

## Hardware state

The breadboard currently holds the ESP32-S3 and the BNO055 only. Phase 0's
button circuit and MPU-6050 were removed on 2026-09-20 to free the single
breadboard; both are documented in `hardware/wiring/phase0-button.md` and
`hardware/wiring/phase0-i2c.md` and can be rebuilt from those.

## Convention

End every working session by updating the five fields above. Keep the body of
the top section to ~3 lines. The sections below evolve with the project.
