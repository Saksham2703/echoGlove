# Phase 0 — Button wiring

## Bill of materials
- 1× breadboard (from Freenove kit)
- 1× small tactile pushbutton (from Freenove kit)
- 1× 10 kΩ resistor (from Freenove kit — brown-black-orange-gold bands)
- 4× M/M jumper wires

## Pin assignment

| ESP32-S3 pin | Breadboard connection |
|---|---|
| GPIO 4 | One leg of the button; one end of 10 kΩ resistor |
| 3.3V | Other end of 10 kΩ resistor |
| GND | Other leg of the button |

## ASCII wiring

```
  3.3V ────[10kΩ]──┬── GPIO 4
                   │
                  [BTN]
                   │
                  GND
```

## How it works

- Button **not pressed**: GPIO 4 is pulled HIGH (3.3V) through the resistor.
- Button **pressed**: GPIO 4 is shorted to GND → reads LOW.

This is "active-low" with an external pull-up. We use an external resistor
rather than the ESP32's internal pull-up so you can see the concept physically.

## Button orientation

The 4-pin button has two internally-shorted leg pairs along its **long axis**.
Place it so those pairs straddle the two sides you want to connect (GPIO4 side
and GND side). If the button press never changes the pin state, rotate the
button 90° — that was the fix needed on this build.

## Important before powering on

1. The resistor must go to **3.3V**, not 5V — the ESP32-S3 is 3.3V logic.
2. Make sure the button straddles the center gap of the breadboard (so its
   two sides are electrically separate).
3. No bare wire ends should be touching a power rail accidentally.

Photograph the breadboard top-down and share it — Claude will sanity-check
the wiring before you plug the USB cable back in.
