# Catode32 Hardware Port Plan

## References
- **Main Project:** [Catode32](https://github.com/moonbench/catode32)
- **UI/Concept Inspiration:** [LeeByte](https://github.com/Sylvia3366/leebyte)
- **Hardware Reference:** [Thermostat-C3](https://github.com/engkon6/Thermostat-C3)

## Project Overview
Porting the **Catode32** virtual pet (originally for ESP32-C6/C3) to a **Wemos LOLIN C3 PICO** hardware setup using MicroPython.

## Hardware Configuration
The project uses a restricted 4-button input system and a SH1106 OLED display.

### Display
- **Type:** SH1106 OLED (128x64)
- **Interface:** I2C
- **Pins:** 
  - SDA: `GPIO 8`
  - SCL: `GPIO 10`
- **Note:** A 2-pixel horizontal offset adjustment may be required for SH1106 compatibility.

### Inputs (Linear Mapping)
Since the original game expects 8 buttons (D-pad + A/B/Menu), the following linear mapping is implemented:

| Physical Pin | Game Function | Role |
| :--- | :--- | :--- |
| **GPIO 2** | `BTN_LEFT` / `BTN_UP` | Move Left / Previous |
| **GPIO 4** | `BTN_RIGHT` / `BTN_DOWN` | Move Right / Next |
| **GPIO 5** | `BTN_A` | Confirm / Select |
| **GPIO 6** | `BTN_B` / `BTN_MENU` | Back / Menu |

---

## Implementation Steps

### Phase 1: Toolchain Setup
- Install build prerequisites: `cmake`, `ninja-build`, `dfu-util`.
- Set up `ESP-IDF v5.5.1` and `MicroPython` source repositories.
- Build `mpy-cross` for bytecode compilation.

### Phase 2: Configuration
- Clone the Catode32 repository to `~/catode32`.
- Modify `src/config.py`:
  - Set `BOARD_TYPE = "ESP32-C3"`.
  - Map I2C pins to 8 and 10.
  - Implement the 4-button linear mapping described above.

### Phase 3: Firmware Build & Deployment
- **Build:** Execute `./tools/build_firmware.sh build esp32c3` to create a custom MicroPython binary with frozen assets.
- **Flash:** Erase device flash and write the custom MicroPython binary.
- **Upload:** Deploy `.py` and `.mpy` game logic using `./upload.sh` (Linux) or `upload_all.py` (Windows).

### Phase 4: Calibration & Testing
- Verify 4-button navigation works across all game scenes.
- Apply rendering offsets if the SH1106 display is misaligned.
- Test WiFi-based proximity and social features.

## Display Driver (SH1106)

The original codebase uses `ssd1306`, but the hardware uses an SH1106 OLED. The solution:

1. **`src/sh1106.py`** - Full SH1106 driver (from [robert-hh/SH1106](https://github.com/robert-hh/SH1106)).
2. **`src/ssd1306.py`** - Compatibility shim that wraps `SH1106_I2C` as `SSD1306_I2C`, so existing code works unchanged.
3. **`src/renderer.py`** - Modified to auto-detect:
   ```python
   try:
       from sh1106 import SH1106_I2C as OLED_I2C
   except ImportError:
       from ssd1306 import SSD1306_I2C as OLED_I2C
   ```
4. **`upload.sh`** - Step 4 modified to skip `mp mip install ssd1306` (driver is compiled and uploaded with game files).

## Upload Methods

### Linux/WSL (Bash)
```bash
./upload.sh COM4
```

### Windows (Python)
```cmd
python.exe upload_all.py
```
Uses `mpremote` via Windows Python to upload compiled `.mpy` files to device on COM4.

---

## Known Issues
- **boot.py Pin Mismatch:** `boot.py` hardcodes `BTN_A = 1, BTN_B = 0` (ESP32-C6 pins). For LOLIN C3 PICO, these should be `BTN_A = 5, BTN_B = 6` to match `config.py`. Currently the A+B hold-to-REPL feature doesn't work because it reads the wrong GPIO pins.

## Revision 7: Hardware Expansion (Planned)

A detailed plan exists for adding joystick, DS18B20 temperature sensor, and piezo buzzer.
See: **[`docs/revision7_hardware_expansion.md`](revision7_hardware_expansion.md)**

**Summary:** Add analog joystick for free-roam movement, real temperature sensor for environmental reactions (ported from LeeByte), and buzzer for sound effects. Resolves ADC pin conflict by using joystick on both ADC pins and keeping existing tactile A/B buttons.

---

## Risks & Constraints
- **Firmware Overwrite:** Flashing the custom MicroPython binary wipes all previous Arduino/C++ firmware from the device.
- **RAM Limits:** High dependence on frozen bytecode to prevent Out-of-Memory (OOM) crashes on the ESP32-C3.
- **Input Limitation:** Navigation is simplified from 2D (D-pad) to 1D (Linear Cycle). (Resolved in Revision 7 with joystick addition)
