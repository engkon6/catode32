# Catode32 Adaptation: Wemos LOLIN C3 PICO

This document details the adaptation of the `catode32` virtual pet project to the Wemos LOLIN C3 PICO hardware, including joystick and button resistor ladder support.

## 1. Hardware Pinout Mapping

| Component | Pin Function | ESP32-C3 Pin (LOLIN C3 PICO) |
| :--- | :--- | :--- |
| **OLED Display** | VCC | 3.3V |
| | GND | GND |
| | SDA | IO8 |
| | SCL | IO10 |
| **Joystick** | X-Axis (Analog) | IO2 |
| | Y-Axis (Analog) | IO4 |
| **Buttons (Ladder)** | Signal (Analog) | IO0 |

## 2. Input Translation Layer (`src/input.py`)

The original game expects digital D-pad and A/B buttons. We have adapted `src/input.py` to translate your hardware inputs:

*   **Joystick**: Maps analog inputs to `up`, `down`, `left`, `right` based on thresholds.
*   **Analog Buttons (Ladder)**: Maps raw ADC values from GPIO0 to `a`, `b`, and `menu1` based on your calibrated ranges.

| Game Action | Hardware Input | Raw Value (GPIO0/ADC) |
| :--- | :--- | :--- |
| **None** | - | 0 - 50 |
| **A** | K1 | 890 - 920 |
| **B** | K2 | 1810 - 1850 |
| **Menu1** | K3 | 2760 - 2800 |

## 3. Configuration (`src/config.py`)

The board is set to `ESP32-C3` and pins are mapped as described in the hardware section.

## 4. Build & Upload

The project requires a custom MicroPython firmware build due to frozen assets.
- **Build Firmware/Flash**: `./tools/build_firmware.sh build-flash esp32c3`
- **Upload Game Logic**: `./upload.sh`
