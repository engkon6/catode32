# Revision 7: Hardware Expansion Plan

**Status:** PLANNED (not yet implemented)
**Date:** 2026-07-24
**Prerequisites:** Current game must be fully working (Phases 1-6 complete)

---

## Overview

Add analog joystick, real temperature sensor (DS18B20), and piezo buzzer to the Catode32 LOLIN C3 PICO build. Inspired by the [LeeByte](https://github.com/Sylvia3366/leebyte) project's hardware features.

## Motivation

The LeeByte project demonstrates several features Catode32 currently lacks:
- **Joystick** for free-roam movement (Catode32 only has digital D-pad)
- **Temperature sensor** for real-world environmental reactions
- **Buzzer** for audio feedback (feeding sounds, mood chimes, alerts)

Adding these features brings Catode32 closer to a complete tamagotchi experience.

---

## Hardware Components

### New Components to Add

| Component | Source | Purpose |
|-----------|--------|---------|
| PS2 Joystick Module (2-axis analog) | AliExpress 4000965985489 | Free-roam movement, minigame input (D-pad replacement) |
| Piezo Buzzer | Standard module | Sound effects (feeding, playing, alerts) |
| DS18B20 Temperature Sensor | OneWire digital | Real-world temperature reactions |
| OPEN-SMART 3-Channel Analog Button Module | AliExpress 1005003404607069 | A/B/extra via resistor ladder on one ADC pin |

### Components Dropped

| Component | Reason |
|-----------|--------|
| 2x Digital Tactile Buttons | Superseded by 3-CH analog module (one ADC pin instead of two GPIOs) |

---

## Pin Mapping (Updated)

### ESP32-C3 LOLIN C3 PICO GPIO Allocation

| GPIO | Function | Component | Type | Notes |
|------|----------|-----------|------|-------|
| 0 | Joystick X | PS2 Module VRx | ADC (analog) | ADC1_CH0 |
| 1 | Joystick Y | PS2 Module VRy | ADC (analog) | ADC1_CH1 |
| 2 | BTN_UP | Tactile button | Digital INPUT_PULLUP | Existing, keep |
| 3 | DS18B20 DATA | Temperature sensor | Digital (OneWire) | Needs 4.7k pull-up to 3.3V |
| 4 | 3-CH Analog Buttons | Resistor ladder module | ADC (analog) | ADC1_CH4; 3 buttons on one pin |
| 5 | BTN_A (Confirm) | Tactile button | Digital INPUT_PULLUP | Existing, keep |
| 6 | BTN_B (Back) | Tactile button | Digital INPUT_PULLUP | Existing, keep |
| 7 | WS2812B LED | Onboard RGB | - | Not used by game |
| 8 | I2C SDA | SH1106 OLED | I2C | Existing, keep |
| 9 | Boot Button | Onboard | - | Not available |
| 10 | I2C SCL | SH1106 OLED | I2C | Existing, keep |
| 11 | Buzzer | Piezo speaker | PWM output | Tone generation |
| 12 | Joystick SW | PS2 Module button | Digital INPUT_PULLUP | Joystick press |
| 13-21 | Spare | - | - | Available for future use |

### ADC Pin Constraint

ESP32-C3 has **5 ADC-capable pins** (ADC1_CH0-4 → GPIO 0-4). After the joystick takes GPIO 0 (X) and GPIO 1 (Y), **GPIO 4 remains free** and hosts the 3-CH analog button module via its internal resistor ladder (no-press + 3 buttons = 4 distinct voltage levels read from one ADC). GPIO 2 is a strapping pin and GPIO 3 is reserved for the DS18B20 / battery monitor, so they are not used for analog input.

---

## Software Changes Required

### 1. New Files to Create

#### `src/ds18b20.py` — OneWire Temperature Sensor Driver
```python
# Minimal DS18B20 driver for MicroPython
# Uses machine.Pin for OneWire protocol
# Functions:
#   read_temperature(pin) -> float (Celsius)
#   - Returns None if sensor not found or CRC error
#   - Supports multiple sensors on same bus (skip ROM for single sensor)
```

**MicroPython OneWire Implementation Notes:**
- ESP32-C3 doesn't have hardware OneWire, must bit-bang the protocol
- Timing-critical: use `machine.time_pulse_us()` for read slots
- CRC-8 checksum validation required
- 4.7k pull-up resistor required on DATA line to 3.3V

#### `src/buzzer.py` — PWM Tone Generation
```python
# Piezo buzzer driver using machine.PWM
# Functions:
#   play_tone(pin, frequency, duration_ms)
#   play_melody(pin, notes_list)
#   beep(pin)  # short confirmation beep
#   alert(pin) # attention-getting pattern
#   silence(pin)
```

**Sound Effects to Implement (from LeeByte):**
| Event | Sound | Frequency | Duration |
|-------|-------|-----------|----------|
| Feed | Short chirp | 880 Hz | 100ms |
| Play | Rising tone | 440→880 Hz | 200ms |
| Sleep | Descending tone | 660→220 Hz | 300ms |
| Mood happy | Major chord | 523+659+784 Hz | 150ms |
| Mood sad | Minor chord | 440+523+622 Hz | 200ms |
| Cold shiver | Rapid clicking | 100 Hz | 50ms×4 |
| Hot pant | Slow pulse | 200 Hz | 300ms×3 |
| Item found | Victory jingle | 523→659→784 Hz | 100ms each |
| Low health | Warning beep | 1000 Hz | 50ms×3 |

### 2. Files to Modify

#### `src/config.py`
Add new pin definitions:
```python
# Joystick (analog)
JOYSTICK_X_PIN = 0    # ADC1_CH0
JOYSTICK_Y_PIN = 1    # ADC1_CH1
JOYSTICK_SW_PIN = 12  # Digital button press

# 3-CH analog button module (resistor ladder)
ANALOG_BTN_PIN = 4    # ADC1_CH4; 3 buttons share this pin
ANALOG_BTN_THRESHOLDS = (1024, 2048, 3072)  # Tune per module: 4 levels = 3 buttons

# Joystick calibration
JOYSTICK_DEADZONE = 150   # Center ±150 of 2048 (12-bit ADC)
JOYSTICK_CENTER_X = 2048  # Midpoint (0-4095 range)
JOYSTICK_CENTER_Y = 2048

# Temperature sensor
DS18B20_PIN = 3       # OneWire data pin

# Buzzer
BUZZER_PIN = 11       # PWM output
BUZZER_ENABLED = True
```

#### `src/input.py`
Add joystick reading to InputHandler:
```python
# New methods:
def read_joystick(self):
    """Read analog joystick values, apply deadzone, return direction."""
    # Returns: (-1, 0, 1) for each axis after deadzone

def get_joystick_direction(self):
    """Return cardinal direction from joystick input."""
    # Returns: 'up', 'down', 'left', 'right', 'center'

def is_joystick_pressed(self):
    """Check if joystick button is pressed."""
```

Add 3-CH analog button reading:
```python
def read_analog_buttons(self):
    """Read resistor-ladder buttons from one ADC pin.
    ADC values: no-press ≈ 0, BTN1 ≈ 1/4 range, BTN2 ≈ 1/2, BTN3 ≈ 3/4.
    Returns which of 3 buttons is pressed (or None)."""
    val = self.analog_btn.read_u16()
    for i, thresh in enumerate(config.ANALOG_BTN_THRESHOLDS):
        if val > thresh:
            return i  # BTN0/BTN1/BTN2
    return None

**Integration Strategy:**
- Joystick方向 merges with existing D-pad logic
- If joystick is pushed UP, equivalent to BTN_UP
- If joystick is pushed LEFT, equivalent to BTN_LEFT (new)
- If joystick is pushed RIGHT, equivalent to BTN_RIGHT (new)
- Joystick SW button maps to BTN_A (confirm)
- 3-CH analog module supplies BTN_B (back) + 2 spare buttons (e.g. menu toggle)
- This gives full 4-directional + confirm/back input without extra GPIOs

#### `src/temperature_system.py`
Add real sensor fallback chain:
```python
def get_temperature(day_number, season_offset, hour, weather, pet_seed, real_sensor_pin=None):
    """Return temperature in Celsius.
    
    Fallback chain:
    1. If real_sensor_pin provided and DS18B20 responding → use real sensor
    2. Otherwise → use deterministic simulation (existing logic)
    """
    if real_sensor_pin is not None:
        from ds18b20 import read_temperature
        real_temp = read_temperature(real_sensor_pin)
        if real_temp is not None:
            return real_temp
    # Fallback to simulation
    return _simulate_temperature(day_number, season_offset, hour, weather, pet_seed)
```

#### `src/entities/behaviors/*.py`
Add temperature reactions (port from LeeByte):

**LeeByte Temperature Behavior Reference:**
```c
// From Tamagotchi.ino lines 1411-1444
if (currentTemp < 10) {
    pet.energy -= 5;
    pet.hunger -= 2;
    pet.happiness -= 2;
    // Show petCold sprite
} else if (currentTemp > 30) {
    pet.energy -= 3;
    pet.hunger -= 2;
    pet.happiness -= 3;
    // Show petHot sprite
} else {
    // Normal decay
    pet.hunger -= 1;
    pet.energy -= 3;
    if (idleTime > 15) pet.happiness -= 1;
}
```

**Catode32 Equivalent Behaviors to Add:**

1. **Cold Reaction** (temp < 10°C):
   - Trigger shivering animation
   - Energy decays faster (-5 per tick instead of -3)
   - Happiness decreases if outside
   - Cat may refuse to go outside
   - Buzzer: rapid clicking sound

2. **Hot Reaction** (temp > 30°C):
   - Trigger panting animation
   - Hunger increases faster
   - Cat seeks shade/inside
   - Happiness decreases if outside
   - Buzzer: slow pulse sound

3. **Comfortable** (10-30°C):
   - Normal stat decay
   - No special reactions

**Files to Modify:**
- `src/entities/behaviors/base.py` — Add temperature check in tick()
- `src/entities/behaviors/playing.py` — Temperature affects play energy cost
- `src/entities/behaviors/eating.py` — Temperature affects hunger rate
- `src/behavior_manager.py` — Temperature influences location preference

#### `src/sky.py`
Update sky rendering based on real temperature:
- Hot day → more intense sun sprite
- Cold day → add frost/breath particles
- Line 561 already has `SUN_HOT if self.temperature > 30`

#### `manifest.py`
Add new frozen modules:
```python
freeze(_src, (
    # ... existing entries ...
    "ds18b20.py",
    "buzzer.py",
))
```

---

## LeeByte Comparison

### Features to Port from LeeByte

| LeeByte Feature | Catode32 Equivalent | Difficulty |
|-----------------|---------------------|------------|
| Joystick free-roam | New movement system in scenes | Medium |
| Temperature reactions | Modify behavior_manager.py | Easy |
| Buzzer sounds | New buzzer.py module | Easy |
| Item discovery while walking | Could add to InsideScene | Medium |
| Tic-Tac-Toe (already exists) | Already in minigames | Done |

### Features NOT to Port

| LeeByte Feature | Reason to Skip |
|-----------------|----------------|
| Custom PCB design | Catode32 uses off-the-shelf modules |
| 3D printed case | Not in scope |
| DallasTemperature library | Need MicroPython OneWire bit-bang |

---

## Testing Checklist

### Hardware Verification
- [ ] Joystick X/Y reads correctly (0-4095 range)
- [ ] Joystick deadzone works (no drift at center)
- [ ] Joystick SW button registers press
- [ ] DS18B20 returns valid temperature (-55 to +125°C)
- [ ] DS18B20 CRC check passes
- [ ] Buzzer produces audible tones at various frequencies
- [ ] All existing buttons still work (GPIO 2, 4, 5, 6)

### Software Verification
- [ ] Joystick方向 integrates with D-pad navigation
- [ ] Temperature sensor fallback works (sensor disconnected → simulation)
- [ ] Cold reactions trigger below 10°C
- [ ] Hot reactions trigger above 30°C
- [ ] Buzzer sounds play for all events
- [ ] No OOM crashes with new modules frozen
- [ ] Game saves/loads correctly with new features

### Integration Testing
- [ ] Walk cat around room with joystick
- [ ] Observe temperature reactions in real-time
- [ ] Play minigames with joystick input
- [ ] Verify battery life not significantly impacted

---

## Implementation Order

1. **Backup** — `cp -r Catode32 Catode32.bak`
2. **Create `src/ds18b20.py`** — OneWire driver (test standalone first)
3. **Create `src/buzzer.py`** — PWM tone driver (test with simple beep)
4. **Update `src/config.py`** — Add all new pin definitions
5. **Update `src/input.py`** — Add joystick reading + deadzone
6. **Update `src/temperature_system.py`** — Add real sensor fallback
7. **Update `src/temperature_system.py`** — Add `update_temperature()` to use real sensor
8. **Update behavior files** — Add temperature reactions
9. **Update `src/sky.py`** — Visual temperature effects
10. **Update `manifest.py`** — Freeze new modules
11. **Rebuild firmware** — Include new frozen modules
12. **Test on device** — Full integration test
13. **Update documentation** — PROGRESS.md, project_plan.md

---

## Risk Assessment

| Risk | Mitigation |
|------|------------|
| ADC routing (3 free pins: 0, 1, 4) | Joystick on 0/1, 3-CH analog buttons on 4; no conflict |
| OneWire timing issues | Use proven MicroPython OneWire implementation |
| Buzzer PWM conflicts with LED | Ensure different timers; test both simultaneously |
| OOM with new modules | Keep modules small; freeze critical ones |
| DS18B20 not responding | Fallback to simulated temperature |
| Joystick drift | Implement deadzone calibration |

---

## Future Considerations

### Optional Enhancements
1. **Analog stick for minigames** — Snake, Maze could use smooth analog input
2. **Haptic feedback** — Vibration motor instead of/in addition to buzzer
3. **Light sensor** — Adjust screen brightness based on ambient light
4. **Battery monitoring** — LOLIN C3 PICO supports via IO3 (requires solder jumper)

### Hardware Version 2
If more ADC pins are needed:
- Switch to **XIAO ESP32-C3** (4 ADC pins: GPIO 2-5)
- Or use **ESP32-S2/S3** (many more ADC channels)
- Or add external ADC (MCP3008 via SPI)

---

## References

- **LeeByte Source:** `firmware/Tamagotchi.ino` lines 1411-1444 (temperature decay)
- **LeeByte BOM:** Adafruit #444 PSP1000 joystick ($3.50)
- **DS18B20 MicroPython:** https://github.com/micropython/micropython-lib (onewire module)
- **ESP32-C3 Pinout:** LOLIN C3 PICO datasheet / ESP32-C3 TRM (ADC1_CH0-4 = GPIO 0-4)
- **Project Plan:** `docs/catode32_project_plan.md`
