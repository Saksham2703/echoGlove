# LEARNINGS

Timestamped record of non-obvious things learned during the project.
Append-only. Never edit past entries.

---

## 2026-05-13 — Freenove kit contains ESP32-WROVER-E, not ESP32-S3

The Freenove ESP32 Ultimate Starter Kit (Amazon B0CJJJ7BCY) ships with an
**ESP32-WROVER-E** dev board (original ESP32, Xtensa LX6, micro-USB connector),
not an ESP32-S3. The orchestration spec assumes S3 throughout. Decision: treat
the Freenove board as a parts source only (sensors, breadboard, discretes) and
flash the separately-ordered ESP32-S3 DevKitC-1 2-pack as the firmware target.
Do not use `board = esp32dev` in `platformio.ini` — stay on `board = esp32-s3-devkitc-1`.

## 2026-05-13 — `CPLUS_INCLUDE_PATH` in ~/.zshrc breaks PlatformIO cross-compiler

Line 41 of `~/.zshrc` previously appended the macOS CommandLineTools C++ SDK
headers to `CPLUS_INCLUDE_PATH`. This makes the macOS system headers visible
to GCC's cross-compiler, which causes build failures (wrong SDK, wrong arch).
Commented out with a dated note. If Xtensa builds start failing with errors
mentioning `/Library/Developer/CommandLineTools/SDKs/MacOSX.sdk/`, this env
var has crept back — check `~/.zshrc`.

## 2026-05-13 — uv creates src/ layout by default; we kept it

`uv init --name echoglove --package` produces `host/src/echoglove/`, not
`host/echoglove/`. The plan originally said to flatten it, but we skipped that
step intentionally — uv's editable install handles the src layout transparently.
Imports work as `from echoglove.serial_reader import ...`. Don't "fix" this.

## 2026-05-13 — Charge-only USB-C cables silently prevent ESP32 flashing

The most common "why won't my board show up in /dev/tty.*?" failure is a
charge-only USB-C cable. The ESP32-S3 will power on but macOS won't enumerate
it as a USB-CDC device. Always test with a cable spec'd as "data" (the UGREEN
100W E-marker cables in the BOM are confirmed data-capable).

## 2026-05-13 — ESP32-S3 DevKitC-1 shows up as /dev/tty.usbmodem*, not tty.usbserial*

The S3 has native USB-CDC, so it appears as `tty.usbmodem*` on macOS (no
CH340/CP2102 driver needed). The Freenove WROVER board uses a CP2102 bridge
and appears as `tty.usbserial-*`. Knowing which pattern to look for avoids
confusion when both boards are plugged in simultaneously.

## 2026-05-24 — ESP32-S3 DevKitC-1 onboard LED is WS2812 RGB on GPIO 48, not a plain LED

`digitalWrite(2, HIGH)` does nothing visible — GPIO 2 has no LED on this board.
The onboard LED is an addressable WS2812B RGB LED on GPIO 48. Use
`neopixelWrite(48, r, g, b)` (built into the Arduino ESP32 framework, no extra
library needed). Also: after flashing, esptool's RTS hard-reset doesn't reliably
exit bootloader mode with native USB-CDC — unplug and replug the USB cable for a
clean boot into firmware.

## 2026-05-24 — 4-pin tactile button orientation matters on a breadboard

A 4-pin tactile button has two internally-shorted pairs of legs along its long
axis. If placed in the wrong rotation, pressing it connects two already-shorted
legs instead of bridging the two sides. If `digitalRead` never changes on press,
try rotating the button 90 degrees before suspecting wiring or firmware.

## 2026-05-24 — Bootloader mode re-enumerates under a different /dev/tty.usbmodem* path

When the ESP32-S3 is put into download mode (BOOT+RST), macOS assigns it a
different device node than when running firmware (e.g. `usbmodem1234561` →
`usbmodem1101`). This is normal. Always check `ls /dev/tty.usb*` after the
BOOT+RST sequence and use the new path for `--upload-port`.

## 2026-05-25 — Adafruit BusIO must be listed explicitly in platformio.ini lib_deps

`Adafruit BNO055` depends on `Adafruit BusIO`, but PlatformIO does not always
resolve it as a transitive dependency on `espressif32@6.7.0` — the build fails
with `SPI.h: No such file or directory` from inside the BusIO source. Fix: add
`adafruit/Adafruit BusIO@^1.16.1` explicitly to `lib_deps`. This applies to any
Adafruit sensor library that pulls in BusIO.

## 2026-09-19 — Caret ranges in lib_deps are not a lockfile

`platformio.ini` listed `@^1.6.3` style carets, so over a 4-month gap the
Adafruit libraries silently floated (BNO055 1.6.3→1.6.4, Unified Sensor
1.1.14→1.1.15, BusIO 1.16.1→**1.17.4**, a minor bump). CLAUDE.md's "treat
platformio.ini as a lockfile" means exact `@1.6.4` pins, no caret. Pinned to
the versions verified to compile today rather than rolling back, since no
version of this stack had ever run against real hardware — there was no
known-good baseline to preserve. If the BNO055 misbehaves on first bring-up,
these pins are what make a version bisect possible.

## 2026-09-19 — Shiny solder can still be a bad joint; shape is the real tell

First practice joints on scrap perfboard came out bright and shiny but
ball-shaped, with the pin fully engulfed and two pads bridged. Shiny only
proves the alloy melted and cooled undisturbed — it does NOT prove the joint
wetted. The diagnostic is shape: a convex bead means the pad never got hot
enough to accept solder (solder was carried in on the iron tip), while a
concave cone with the pin visible at its summit means it bonded. Shiny +
balled + over-volumed specifically rules OUT a temperature problem, so the fix
is technique (tip in the crotch of pin and pad, feed solder to the far side),
not a hotter iron. Also: the Freenove perfboard is FR-2 phenolic, not FR-4 —
pads lift under repeated reheating, so redo bad joints in fresh holes rather
than reworking them.
