"""
config.py - Hardware configuration and game constants
"""

# ============================================================================
# BOARD SELECTION - Change this to match your ESP32 board
# ============================================================================
# Supported boards:
#   "ESP32-C6"            - generic ESP32-C6 dev board
#   "ESP32-C3"            - Catode32 (onboard OLED on SDA=5/SCL=6)
#   "WEMOS-LOLIN-C3-PICO" - Wemos Lolin C3 Pico (OLED on LOLIN I2C port 8/10,
#                           analog joystick D-pad on GPIO2/4, A/B on GPIO5/6)
BOARD_TYPE = "WEMOS-LOLIN-C3-PICO"  # Change to match your board

# ============================================================================
# Board-Specific Pin Configurations
# ============================================================================

# ESP32-C6 Pin Configuration (SuperMini)
_ESP32_C6_CONFIG = {
    'I2C_SDA': 4,
    'I2C_SCL': 7,
    'BTN_UP': 14,
    'BTN_DOWN': 18,
    'BTN_LEFT': 20,
    'BTN_RIGHT': 19,
    'BTN_A': 1,
    'BTN_B': 0,
    'BTN_MENU1': 3,
    'BTN_MENU2': 2,
}

# ESP32-C3 Pin Configuration
# Uses lower GPIO pins that are commonly available on ESP32-C3 boards
# Avoids strapping pins (GPIO2, GPIO8, GPIO9)
# NOTE: This board's onboard OLED (SSD1306 @ 0x3C) is wired to SDA=GPIO5, SCL=GPIO6
_ESP32_C3_CONFIG = {
    'I2C_SDA': 5,
    'I2C_SCL': 6,
    'BTN_UP': 0,
    'BTN_DOWN': 1,
    'BTN_LEFT': 2,
    'BTN_RIGHT': 3,
    'BTN_A': 4,
    # NOTE (Catode32): BTN_B is provisionally GPIO7. The old GPIO5 value collided
    # with the OLED's I2C SDA (onboard wiring: SDA=GPIO5, SCL=GPIO6) — creating
    # Pin(5) after the I2C bus kills SDA and the game boot-loops on I2C
    # ETIMEDOUT. GPIO7 is free/non-strapping; update to the physical B button's
    # real GPIO once the board pinout is confirmed. input.py additionally skips
    # any button pin that collides with I2C SDA/SCL as a safety net.
    'BTN_B': 7,
    'BTN_MENU1': 10,
    'BTN_MENU2': 11,
}

# Wemos Lolin C3 Pico
# - OLED on the onboard LOLIN I2C port: SDA=GPIO8, SCL=GPIO10.
# - D-pad is an analog joystick on GPIO2 (X) / GPIO4 (Y), both ADC1.
# - A/B on GPIO5/GPIO6.
# - MENU1/MENU2 (plus a spare) come from a 3-button analog resistor ladder on
#   GPIO0 (see BTN_LADDER_* below).
# - WS2812 RGB LED on GPIO7 (reserved, not driven by the game yet).
# - Buttons may be None (unassigned); a button whose pin collides with the
#   I2C pins is skipped by input.py as a safety net.
_LOLIN_C3_PICO_CONFIG = {
    'I2C_SDA': 8,
    'I2C_SCL': 10,
    'OLED_DRIVER': 'SH1106',
    'JOY_X_ADC': 2,
    'JOY_Y_ADC': 4,
    'BTN_UP': None,
    'BTN_DOWN': None,
    'BTN_LEFT': None,
    'BTN_RIGHT': None,
    'BTN_A': 5,
    'BTN_B': 6,
    'BTN_MENU1': None,
    'BTN_MENU2': None,
    'BTN_LADDER_ADC': 0,
    'RGB_LED': 7,
}

# Select configuration based on board type
if BOARD_TYPE == "ESP32-C3":
    _CONFIG = _ESP32_C3_CONFIG
elif BOARD_TYPE == "ESP32-C6":
    _CONFIG = _ESP32_C6_CONFIG
elif BOARD_TYPE == "WEMOS-LOLIN-C3-PICO":
    _CONFIG = _LOLIN_C3_PICO_CONFIG
else:
    raise ValueError(f"Unknown BOARD_TYPE: {BOARD_TYPE}. "
                     "Supported: 'ESP32-C6', 'ESP32-C3', 'WEMOS-LOLIN-C3-PICO'")

# Display Configuration
DISPLAY_WIDTH = 128
DISPLAY_HEIGHT = 64
I2C_SDA = _CONFIG['I2C_SDA']
I2C_SCL = _CONFIG['I2C_SCL']
I2C_FREQ = 400000
OLED_DRIVER = _CONFIG.get('OLED_DRIVER', 'SH1106')

# Analog D-pad (joystick) Configuration
# The joystick maps to the game's up/down/left/right inputs.  Values below are
# raw ADC read_u16() readings (0..65535).
#
# JOY_CENTER_* are only FALLBACKS: input.py auto-calibrates the neutral
# position at startup by sampling each axis 8x (stick untouched) and using the
# median, because cheap joystick pots sit well off mid-scale.  The config
# centers are used only if that auto-calibration fails.  JOY_INVERT_*/JOY_SWAP_AXES
# correct for wiring/orientation.
# None disables the analog D-pad (digital BTN_* buttons are used instead).
JOY_X_ADC = _CONFIG.get('JOY_X_ADC')
JOY_Y_ADC = _CONFIG.get('JOY_Y_ADC')
JOY_CENTER_X = 32768  # fallback only; input.py auto-calibrates at boot
JOY_CENTER_Y = 32768  # fallback only; input.py auto-calibrates at boot
JOY_DEADZONE = 0.20   # fraction of half-scale before a direction registers
JOY_INVERT_X = False
# This unit's Y-axis polarity is reversed: pushing the stick up reads above
# center (which would register as 'down').  Invert so up → 'up', down → 'down'.
JOY_INVERT_Y = True
JOY_SWAP_AXES = False

# Onboard RGB LED (WS2812) if the board has one (reserved; not driven yet)
RGB_LED = _CONFIG.get('RGB_LED')

# Button Pin Mappings (None = button not wired; skipped by input.py)
BTN_UP = _CONFIG['BTN_UP']
BTN_DOWN = _CONFIG['BTN_DOWN']
BTN_LEFT = _CONFIG['BTN_LEFT']
BTN_RIGHT = _CONFIG['BTN_RIGHT']
BTN_A = _CONFIG['BTN_A']
BTN_B = _CONFIG['BTN_B']
BTN_MENU1 = _CONFIG['BTN_MENU1']
BTN_MENU2 = _CONFIG['BTN_MENU2']

# Analog button ladder (three buttons on one ADC pin, e.g. GPIO0 on the Lolin
# C3 Pico).  Each button pulls a different resistor into a divider, so each
# produces its own raw read_u16() voltage band.  Measured on hardware
# (2026-08-14, ATTN_11DB): None≈128-304, K1≈14707, K2≈29623, K3≈44778.
# LADDER_K*_MIN/MAX are wide read_u16() windows around those measurements;
# a reading below LADDER_K1_MIN means "no button pressed".  Setting
# BTN_LADDER_ADC to None disables the ladder entirely.
BTN_LADDER_ADC = _CONFIG.get('BTN_LADDER_ADC')

LADDER_K1_MIN = 8000    #  K1 band (measured ≈14707)
LADDER_K1_MAX = 20000
LADDER_K2_MIN = 22000   #  K2 band (measured ≈29623)
LADDER_K2_MAX = 36000
LADDER_K3_MIN = 38000   #  K3 band (measured ≈44778)
LADDER_K3_MAX = 65535

# Ladder button → game input mapping.  K1/K3 are plain single-press inputs;
# K2 is tap-counted so a single tap fires MENU2 and a double tap fires MENU1
# (delivered as a single was_just_pressed() event).
BTN_LADDER_K1 = 'b'
BTN_LADDER_K2 = 'menu2'
BTN_LADDER_K2_DOUBLE = 'menu1'
BTN_LADDER_K3 = 'a'

# K2 tap timing (ms).  A single tap's MENU2 fires this long after the button
# is released, giving the second tap of a double tap time to arrive.  450 ms
# comfortably covers a natural double-tap measured at the game's ~12 FPS
# sample rate (the double tap is detected between press-down edges).
LADDER_DOUBLE_TAP_MS = 450
LADDER_SAMPLE_INTERVAL_MS = 15   # min gap between ADC samples
LADDER_EDGE_DEBOUNCE_MS = 40     # min gap before a ladder edge is accepted

# Free the raw config dicts — all values have been extracted above
del _ESP32_C6_CONFIG, _ESP32_C3_CONFIG, _LOLIN_C3_PICO_CONFIG, _CONFIG

# WiFi Features
# Disable if wlan.scan() causes hard freezes on your firmware/board combination.
WIFI_ENABLED = False  # TODO(catode32-c3): True OOMs the ESP32-C3 RAM budget

# Debug Features
SHOW_DEBUG_MENUS = True

# Desktop (config_desktop overrides these on PC builds)
IS_DESKTOP = False
SAVE_PATH = '/save.json'
BACKUP_PATH = '/backup.json'
BACKUP_OLD_PATH = '/backup.old.json'

# Software Version
VERSION = "0.9.1"

# Game Constants
FPS = 12  # Target frames per second
FRAME_TIME_MS = 1000 // FPS  # Milliseconds per frame

# Transition Settings
TRANSITION_DURATION = 0.25      # seconds per half-transition (total is 2x this)

# Panning Settings
PAN_SPEED = 4  # pixels per frame when D-pad held

# Sleep / Power Saving
# SLEEP_MODE controls the device sleep behaviour when idle:
#   None    - sleep disabled
#   "basic" - screen off, reduced game tick rate, CPU still running
#   "deep"  - (not yet implemented) true deep sleep with hardware wake-up
SLEEP_MODE = "basic"
SLEEP_TIMEOUT_SEC = 900      # Seconds of inactivity before sleeping (15 minutes)
SLEEP_FPS = 2                # Game update rate while in basic sleep
SLEEP_FRAME_TIME_MS = 1000 // SLEEP_FPS