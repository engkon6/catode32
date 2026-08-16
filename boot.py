# boot.py - Auto-run game unless A+B buttons held during boot
#
# Hold A+B during the 1-second startup window to enter REPL mode.
# The same window also lets mpremote interrupt via Ctrl+C.
#
# After the game exits for any reason, all game modules are cleared
# from sys.modules so that a subsequent `mpremote mount ... exec`
# re-imports clean modules from the mounted filesystem.
#
# A+B detection: a real digital A button is preferred.  On boards with no
# digital A (an analog-only joystick on config.JOY_Y_ADC), "A held" is
# detected via ADC as a joystick deflection beyond the deadzone - the same
# logic input.py uses - because a plain digital read of that pin reads LOW
# whenever the stick rests near center and would false-trigger REPL mode.

from machine import Pin
import time
import gc

_skip_check = False
_center_y = None
_deadzone = None
try:
    import config
    BTN_A = config.BTN_A
    BTN_B = config.BTN_B
    JOY_Y_ADC = config.JOY_Y_ADC
    _center_y = config.JOY_CENTER_Y
    _deadzone = int(config.JOY_DEADZONE * 32768)
except Exception:
    print("[boot] config not available - REPL escape disabled")
    _skip_check = True

btn_a = None
btn_b = None
joy_y = None
if not _skip_check:
    # Prefer a real digital A button (e.g. the Lolin C3 Pico's A on GPIO5).
    # Boards with no digital A fall back to reading the analog joystick Y
    # axis as "A held" (a deflection beyond the deadzone, mirroring
    # input.py) - a plain digital read of that pin is meaningless because
    # it sits low whenever the stick is centered.
    if BTN_A is not None:
        btn_a = Pin(BTN_A, Pin.IN, Pin.PULL_UP)
    elif JOY_Y_ADC is not None:
        from machine import ADC
        try:
            joy_y = ADC(Pin(JOY_Y_ADC))
            joy_y.atten(ADC.ATTN_11DB)
            # Auto-calibrate the rest center (median of 5) exactly like
            # input.py, so an off-center resting stick is not a "press".
            _samples = []
            for _i in range(5):
                _samples.append(joy_y.read_u16())
                time.sleep_ms(10)
            _samples.sort()
            _center_y = _samples[2]
        except Exception:
            joy_y = None
    if BTN_B is not None:
        btn_b = Pin(BTN_B, Pin.IN, Pin.PULL_UP)


def _a_held():
    """True when "A" is genuinely pressed (digital low or analog deflection)."""
    if btn_a is not None:
        return btn_a.value() == 0
    if joy_y is not None:
        return abs(joy_y.read_u16() - _center_y) > _deadzone
    return False


def _b_held():
    """True when "B" is pressed (digital low)."""
    if btn_b is not None:
        return btn_b.value() == 0
    return False


# Sample A+B repeatedly across the boot window and require the combo held at
# EVERY sample.  A real hold stays true throughout; transient spikes (a nudge
# of the stick, a floating WS2812 line) do not.  The sleep stays interruptible
# so mpremote can still break in with Ctrl+C.
_skip = False
if not _skip_check:
    _skip = True
    for _i in range(6):
        time.sleep_ms(40)
        if not (_a_held() and _b_held()):
            _skip = False
            break

if _skip:
    print("[boot] A+B held - REPL mode")
else:
    print("[boot] Starting game...")
    try:
        import main
        main.main()
    except Exception as e:
        import sys
        print("[boot] Error:")
        sys.print_exception(e)
    finally:
        # Clear all game modules from sys.modules.
        # This ensures that a subsequent `mpremote mount <dir> exec "import main; main.main()"`
        # re-imports everything fresh from the mounted filesystem rather than
        # getting the stale cached versions from device flash.
        import sys
        _keep = frozenset(('micropython', 'gc', 'sys', 'machine', 'time', 'builtins', 'uos'))
        for _k in list(sys.modules):
            if _k not in _keep:
                try:
                    del sys.modules[_k]
                except Exception:
                    pass
        gc.collect()
        print("[boot] Module cache cleared")
