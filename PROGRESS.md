# Project Progress: Catode32 Hardware Port

## Current Status
**Status:** Game fully running on LOLIN C3 PICO - Adoption → Inside scene transition working

## Accomplishments

### Phase 1: Toolchain Setup (Complete)
- [x] Created local project folder: `~/Catode32`
- [x] Installed system dependencies: `cmake`, `ninja`, `dfu-util`, `git`, `build-essential`.
- [x] Cloned `catode32` repository to local machine.
- [x] Cloned `esp-idf` (v5.5.1) to `~/esp/esp-idf`.
- [x] Cloned `micropython` to `~/esp/micropython`.
- [x] Installed ESP-IDF tools for `esp32c3`.
- [x] Successfully built `mpy-cross`.

### Phase 2: Configuration (Complete)
- [x] Modified `src/config.py` for LOLIN C3 PICO hardware mapping.
- [x] I2C pins: SDA=GPIO 8, SCL=GPIO 10, addr=0x3C.
- [x] 4-button linear mapping configured: GPIO 2 (left/up), GPIO 4 (right/down), GPIO 5 (A), GPIO 6 (B).

### Phase 3: Firmware Build & Flash (Complete)
- [x] Compiled MicroPython firmware for ESP32-C3.
- [x] Flashed firmware to device via `esptool` on COM4.
- [x] MicroPython REPL accessible at 115200 baud.

### Phase 4: Display Driver (Complete)
- [x] Downloaded SH1106 driver from `robert-hh/SH1106` to `src/sh1106.py`.
- [x] Created SH1106 compatibility shim at `src/ssd1306.py` (wraps `SH1106_I2C` as `SSD1306_I2C`).
- [x] Modified `src/renderer.py` to auto-detect SH1106 vs SSD1306.
- [x] Updated `upload.sh` to skip `mp mip install ssd1306`.
- [x] Verified SH1106 driver works ("Hello Catode32!" displayed).

### Phase 5: Game Deployment (Complete)
- [x] Translated source files: 128 files.
- [x] Compiled all `.py` to `.mpy`: 120 files.
- [x] Converted level files: 6 platformer levels.
- [x] Created Windows upload script (`upload_all.py`).
- [x] Game boots and displays adoption scene on OLED.

### Phase 6: Memory & Boot Fixes (Complete)
- [x] **OOM Crash Fix:** Original firmware only froze `assets/` into flash. Importing `scenes.inside` consumed 102KB for its module chain, causing `MemoryError: allocating 332 bytes` during `InsideScene` setup.
  - **Root cause:** 30+ engine modules loaded as `.mpy` from filesystem, each consuming heap for bytecode.
  - **Fix:** Rebuilt firmware with 30 additional core engine modules frozen into flash via `manifest.py`:
    - `config.py`, `context.py`, `input.py`, `main.py`, `menu.py`, `scene.py`, `scene_manager.py`
    - `renderer.py`, `sprite_transform.py`, `transitions.py`, `ui.py`, `ui_keyboard.py`
    - `environment.py`, `sky.py`, `clock.py`
    - `weather_system.py`, `time_system.py`, `temperature_system.py`, `sleep_manager.py`
    - `plant_system.py`, `plant_renderer.py`, `gardening_ui.py`
    - `backup.py`, `settings.py`, `reset_context.py`, `splash.py`
    - `visit_manager.py`, `espnow_handler.py`, `espnow_manager.py`, `wifi_tracker.py`
    - `framebuf.py`, `sh1106.py`, `ssd1306.py`
  - Scenes and behaviors remain on filesystem (lazy-loadable/unloadable).
  - New firmware: 1,629,328 bytes (+97KB vs original 1,532,480).
- [x] **boot.py Pin Fix:** Changed `BTN_A = 1, BTN_B = 0` → `BTN_A = 5, BTN_B = 6` to match LOLIN C3 PICO 4-button mapping.
- [x] **Crash Loop Recovery:** Deleted stale `intent.json` and `save.json` that caused infinite OOM reboot loop (scene resume → crash → reboot → resume → ...).
- [x] **Game now transitions successfully:** Adoption → InsideScene without memory errors.

## Remaining Tasks (Current Hardware)
- [ ] **Button input testing:** Verify all 4 buttons work correctly across game scenes.
- [ ] **Display rendering:** Check for SH1106 2-pixel horizontal offset (may need adjustment).
- [ ] **WiFi/ESP-NOW testing:** Test proximity and social features.
- [ ] **Battery monitoring:** Test if battery monitoring is enabled (IO3 solder jumper).
- [ ] **Save data persistence:** Verify `save.json` write/read works.

## Planned: Revision 7 — Hardware Expansion
**Status:** Documented, not yet implemented
**Plan:** See [`docs/revision7_hardware_expansion.md`](docs/revision7_hardware_expansion.md)

**Components to add:**
- Analog joystick (PS2 module) on GPIO 0/1 for free-roam movement
- DS18B20 temperature sensor on GPIO 3 for real-world temperature reactions
- Piezo buzzer on GPIO 11 for sound effects
- Joystick SW button on GPIO 12

**Key changes:** New files `ds18b20.py` and `buzzer.py`, modifications to `input.py`, `temperature_system.py`, behavior files, and `manifest.py`. Drops 3-CH analog button module (ADC pin conflict).

## Build & Upload Methods

### Full Rebuild (WSL/Linux)
```bash
# Build firmware with frozen modules
cd ~/project/Catode32
bash -c '. ~/esp/esp-idf/export.sh 2>/dev/null && \
  export PETPYTHON_SRC="$(pwd)/src" && \
  idf.py -D MICROPY_BOARD="ESP32_GENERIC_C3" \
         -D MICROPY_FROZEN_MANIFEST="$(pwd)/manifest.py" \
         -D MICROPY_PY_BTREE=0 build'

# Compile and upload game
python3 tools/translate.py --lang en src build/translated-en
find build/translated-en -name "*.py" -not -path "*/assets/*" | while read f; do
    out="build/$(echo $f | sed 's|build/translated-en/||' | sed 's|\.py$|.mpy|')"
    mkdir -p "$(dirname $out)"
    mpy-cross -march=xtensawin "$f" -o "$out"
done
python3 tools/convert_level.py levels/level_*.txt
```

### Flash Firmware (Windows)
```cmd
esptool --port COM4 --baud 460800 erase_flash
esptool --port COM4 --baud 460800 write-flash 0x0 bootloader.bin partition-table.bin micropython.bin
```

### Upload Game (Windows)
```cmd
python.exe upload_all.py
```

### REPL Access (Windows)
```cmd
python.exe -m mpremote connect COM4 repl
```

### Break into REPL (when game is running)
When boot.py auto-starts the game, mpremote can't get REPL. Use this script to interrupt during boot:
```cmd
python.exe break_in.py
```
Or manually: open serial at 1200 baud, close, reopen at 115200, spam Ctrl-C within 250ms.

## Key Files
| File | Purpose |
|------|---------|
| `manifest.py` | Frozen module manifest (assets + 30 core engine modules) |
| `src/renderer.py` | Display rendering - auto-detects SH1106/SSD1306 |
| `src/sh1106.py` | SH1106 OLED driver (from robert-hh/SH1106) |
| `src/ssd1306.py` | Compatibility shim: SH1106_I2C wrapped as SSD1306_I2C |
| `src/config.py` | Hardware configuration (pins, display, buttons) |
| `boot.py` | Auto-run/REPL selector (GPIO 5=A, GPIO 6=B) |
| `upload_all.py` | Windows game upload script |
| `break_in.py` | Serial interrupt script for REPL access |
| `firmware/` | Compiled MicroPython .bin files |

## Memory Budget (ESP32-C3)
| Component | Heap Usage |
|-----------|-----------|
| MicroPython firmware | ~224KB SRAM reserved |
| Free heap at REPL | ~177KB |
| `scenes.inside` import chain | ~102KB (before freeze fix) |
| `BehaviorManager` import | ~18KB |
| CharacterEntity creation | ~5KB |
| Scene setup (environment, furniture, sky) | ~20KB |
| **Available for runtime** | **~57KB** (tight but workable) |

## Log
- **2026-07-12:** Initialized local build environment and completed toolchain setup.
- **2026-07-13:** Compiled MicroPython firmware. Flashed to LOLIN C3 PICO. SH1106 driver working. Game boots and displays adoption scene.
- **2026-07-24:** Fixed OOM crash on InsideScene transition by rebuilding firmware with 30 frozen core modules. Fixed boot.py pin mapping (GPIO 1/0 → GPIO 5/6). Game now runs full loop: adoption → inside scene. All button testing, display alignment, and WiFi features pending.
- **2026-07-24 (Revision 7 Plan):** Documented hardware expansion plan. Added joystick (GPIO 0/1), DS18B20 temperature sensor (GPIO 3), and buzzer (GPIO 11) to roadmap. Dropped 3-CH analog button module due to ADC pin conflict (ESP32-C3 has only 2 ADC pins). Plan captures LeeByte temperature reactions, buzzer sound effects, and joystick integration. See `docs/revision7_hardware_expansion.md`.
