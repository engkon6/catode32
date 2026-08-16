# Project Documentation: LOLIN C3 PICO Input/Display System

This project implements an input system using a Wemos LOLIN C3 PICO, an SH1106 I2C OLED display, a dual-axis analog joystick, and a 3-button analog resistor ladder.

## 1. Hardware Pinout Mapping

| Component | Pin Function | ESP32-C3 (LOLIN C3 PICO) Pin |
| :--- | :--- | :--- |
| **OLED Display** | VCC | 3.3V |
| | GND | GND |
| | SDA | IO8 |
| | SCL | IO10 |
| **Joystick** | X-Axis | IO2 |
| | Y-Axis | IO4 |
| **Buttons (Ladder)** | Signal | IO0 |

## 2. Software Configuration

### Library Dependencies (`platformio.ini`)
```ini
[env:esp32-c3-devkitm-1]
platform = espressif32
board = esp32-c3-devkitm-1
framework = arduino
monitor_speed = 115200
lib_deps =
    olikraus/U8g2 @ ^2.36.2
```

### U8g2 Display Constructor
The system uses the SH1106 driver for a 128x64 display over I2C:
```cpp
U8G2_SH1106_128X64_NONAME_F_HW_I2C u8g2(U8G2_R0, /* reset=*/ U8X8_PIN_NONE, /* clock=*/ 10, /* data=*/ 8);
```

### Analog Button Logic (GPIO0)
The buttons are connected via a resistor ladder. The firmware detects pressed buttons based on the following raw `analogRead(0)` ranges (0-4095):

| Button | Raw Value Range |
| :--- | :--- |
| None | 0 - 50 |
| K1 | 890 - 920 |
| K2 | 1810 - 1850 |
| K3 | 2760 - 2800 |

**Verified on hardware (2026-08-14):** MicroPython `ADC(Pin(0))` with `ATTN_11DB`, `read()` gives the same 0–4095 scale and the measured values sit squarely inside the ranges above: None≈16, K1≈910, K2≈1848, K3≈2796. `read_u16()` equivalents (for `input.py`): None≈128–304, K1≈14707, K2≈29623, K3≈44778 (≈ r × 16.01).

**Game-input mapping (decided 2026-08-14):**
| Ladder button | Game input | Notes |
| :--- | :--- | :--- |
| K1 | **B** (Back/cancel) | Ladder A/B pins are GPIO5/6; K1 is an alternate Back. |
| K2 | **MENU2** (contextual) on single tap, **MENU1** (global) on double tap | Single-tap MENU2 fires `LADDER_DOUBLE_TAP_MS` (450 ms) after release to disambiguate. |
| K3 | **A** (Select/confirm) | Alternate Select. |

Implemented in `src/config.py` (`BTN_LADDER_*`, `LADDER_*`) and `src/input.py` (K2 tap decoder). Ladder buttons are ADC-polled, so they can't wake the device from sleep — digital A/B (GPIO5/6) remain the wake buttons.

> **Current state (2026-08-15):** Fully deployed and verified on hardware. Firmware was rebuilt with frozen modules (assets + boot graph + pinned modules, per `manifest.py`) and flashed, the full current codebase was uploaded, and the game runs standalone from `boot.py`. On-device press tests confirmed **K1→B ✓, K3→A ✓, K2 single-tap→MENU2 ✓, K2 double-tap→MENU1 ✓** (double-tap window widened 350→450 ms). See README "Verification log (2026-08-15)" and "Build & Deployment Status (2026-08-15)" for details.
