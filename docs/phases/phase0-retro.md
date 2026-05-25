# Phase 0 retrospective

## What was built
- Phase 0 BOM ordered and inventoried (all items arrived).
- VS Code + PlatformIO + Python 3.12 via uv toolchain on Mac (Apple Silicon).
- Repo scaffolded: firmware/, host/, hardware/, docs/phases/.
- ESP32-S3 onboard RGB LED blinking (GPIO 48, WS2812B via neopixelWrite).
- Tactile button counter streaming over USB serial as JSON lines (GPIO 4, external pull-up).
- Python host: parse_lines() + stream_port() with 5 pytest tests passing.
- MPU-6050 (GY-521) raw accel/gyro streaming at 10 Hz on the same JSON-line protocol.
- All 4 Phase 0 verification criteria met; 60-second serial stream clean.

## What surprised me
- neopixelWrite vs digitalWrite for the RGB LED
- ESP32-S3 bootloader entry dance
- how easy it is once you know the basics

## What felt rote / I'd skim next time
- verifying the connections once I got hold of the basics

## What I want more depth on in Phase 1
- how does Madgwick/Mahony fusion work under the hood?
- how does the code work?

## Time spent
- Calendar: ~2 weeks (2026-05-12 to 2026-05-24)
- Active hours: ~10 hours

## Costs
- Tools/parts spend: ($141.82 post tax vs. $124–161 estimate)

## Anything for the parking lot
