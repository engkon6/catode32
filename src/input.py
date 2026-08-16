"""
input.py - Button input handling with debouncing, plus an analog D-pad and an
analog button ladder.

The D-pad (up/down/left/right) can come from either digital buttons or an
analog joystick on two ADC pins (see config.JOY_*).  The joystick is sampled
once per frame in update(); call it at the top of your per-frame input
handling (scene_manager.handle_input does this).  Both modes expose the same
interface (is_pressed / was_just_pressed / get_direction), so scenes don't
need to care which one is wired.

Several buttons can also share one ADC pin via a resistor ladder (see
config.BTN_LADDER_ADC).  Each ladder button maps onto a game input: K1 → B,
K3 → A, and K2 is tap-counted so a single tap fires MENU2 while a double tap
fires MENU1 (the MENU2 is deferred by LADDER_DOUBLE_TAP_MS to disambiguate).
Ladder buttons are sampled with the joystick in update() (and throttled
re-samples from the poll methods) and cannot wake the device from sleep —
keep the digital A/B buttons for that.
"""

from machine import Pin, ADC
import time
import config


class InputHandler:
    """Handles button inputs with debouncing and state tracking"""

    def __init__(self):
        # Initialize all buttons with internal pull-ups.
        #
        # A button pin may be None (not wired) and is then skipped.  A button
        # whose GPIO collides with the I2C SDA/SCL pins is also skipped:
        # reconfiguring an in-use I2C line as a GPIO input disconnects the I2C
        # controller from that pin, so every later OLED transaction times out
        # (errno 116) and the device vanishes from i2c.scan().  The Catode32's
        # BTN_B was GPIO5 == I2C SDA and caused exactly this boot loop.
        _i2c_pins = (config.I2C_SDA, config.I2C_SCL)
        _pin_map = {
            'up': config.BTN_UP,
            'down': config.BTN_DOWN,
            'left': config.BTN_LEFT,
            'right': config.BTN_RIGHT,
            'a': config.BTN_A,
            'b': config.BTN_B,
            'menu1': config.BTN_MENU1,
            'menu2': config.BTN_MENU2,
        }
        self.buttons = {}
        for _name, _gpio in _pin_map.items():
            if _gpio is None:
                continue
            if _gpio in _i2c_pins:
                _role = "SDA" if _gpio == config.I2C_SDA else "SCL"
                print("[Input] Skipping '%s' on GPIO%d: conflicts with I2C %s"
                      % (_name, _gpio, _role))
                continue
            self.buttons[_name] = Pin(_gpio, Pin.IN, Pin.PULL_UP)

        # Analog D-pad (joystick).  Sampled once per frame in update().
        self._joy = None
        self._joy_center = {}
        self._raw_dir = {'up': False, 'down': False, 'left': False, 'right': False}
        if config.JOY_X_ADC is not None and config.JOY_Y_ADC is not None:
            try:
                self._joy = {
                    'x': ADC(Pin(config.JOY_X_ADC)),
                    'y': ADC(Pin(config.JOY_Y_ADC)),
                }
                for _axis in self._joy.values():
                    _axis.atten(ADC.ATTN_11DB)
                print("[Input] Analog D-pad on GPIO%d(X)/GPIO%d(Y)"
                      % (config.JOY_X_ADC, config.JOY_Y_ADC))
                # Auto-calibrate: cheap joystick pots sit off-center.  Sample
                # the neutral position at startup (stick untouched) and use the
                # median as the per-axis center.  Falls back to config centers
                # if anything goes wrong.
                import time as _time
                _self_center = self._joy_center
                _center_fb = {'x': config.JOY_CENTER_X, 'y': config.JOY_CENTER_Y}
                for _axis_name, _axis_obj in self._joy.items():
                    _samples = []
                    for _i in range(8):
                        _samples.append(_axis_obj.read_u16())
                        _time.sleep_ms(30)
                    _samples.sort()
                    _self_center[_axis_name] = _samples[4]
                print("[Input] Joystick centers: x=%d y=%d (defaults %d/%d)"
                      % (_self_center['x'], _self_center['y'],
                         _center_fb['x'], _center_fb['y']))
            except Exception as e:
                print("[Input] Joystick init failed: %r" % (e,))
                self._joy = None

        # Analog button ladder (several buttons sharing one ADC pin).  Slots
        # are classified by raw read_u16() voltage bands (config.LADDER_*).
        # K1/K3 map onto single-press game inputs (a/b); K2 feeds a tap
        # decoder so a single tap emits menu2 and a double tap emits menu1.
        # Sampled in _update_ladder(), which is throttled to keep the ADC
        # reads bounded.
        self._ladder = None
        self._ladder_raw = {}          # slot ('k1'/'k2'/'k3') -> pressed bool
        self._ladder_slot_of_name = {} # game input -> slot (single-press only)
        self._ladder_last_sample_ms = 0
        self._k2 = {
            'raw': False,
            'last_change_ms': 0,
            'count': 0,
            'last_press_ms': 0,
            'menu1_armed': False,
            'menu2_at': None,
        }
        if config.BTN_LADDER_ADC is not None:
            try:
                self._ladder = ADC(Pin(config.BTN_LADDER_ADC))
                self._ladder.atten(ADC.ATTN_11DB)
                for _slot, _name in (('k1', config.BTN_LADDER_K1),
                                     ('k2', config.BTN_LADDER_K2),
                                     ('k3', config.BTN_LADDER_K3)):
                    self._ladder_raw[_slot] = False
                    # MENU1/MENU2 are virtual (tap-decoded) events, so the raw
                    # pressed state is only exposed for single-press mappings.
                    if _name not in ('menu1', 'menu2'):
                        self._ladder_slot_of_name[_name] = _slot
                print("[Input] Analog button ladder on GPIO%d: K1=%s K2=%s(+double→%s) K3=%s"
                      % (config.BTN_LADDER_ADC, config.BTN_LADDER_K1,
                         config.BTN_LADDER_K2, config.BTN_LADDER_K2_DOUBLE,
                         config.BTN_LADDER_K3))
            except Exception as e:
                print("[Input] Ladder init failed: %r" % (e,))
                self._ladder = None

        # Track button states for debouncing
        self.button_states = {}
        self.last_press_time = {}
        self.debounce_time_ms = 50  # 50ms debounce

        # Initialize state tracking (directions included so was_just_pressed
        # works for the joystick before any update() has run)
        _all_names = list(self.buttons)
        if self._joy:
            for _d in self._raw_dir:
                if _d not in _all_names:
                    _all_names.append(_d)
        for btn_name in _all_names:
            self.button_states[btn_name] = False
            self.last_press_time[btn_name] = 0

    def _sample_axis(self, axis):
        raw = self._joy[axis].read_u16()  # 0..65535
        center = self._joy_center.get(axis)
        if center is None:
            center = config.JOY_CENTER_X if axis == 'x' else config.JOY_CENTER_Y
        invert = config.JOY_INVERT_X if axis == 'x' else config.JOY_INVERT_Y
        v = raw - center
        if invert:
            v = -v
        return v / 32768.0  # ~ -1.0..1.0

    def _read_ladder_slot(self):
        """Classify one ADC sample into a ladder slot ('k1'/'k2'/'k3') or None."""
        v = self._ladder.read_u16()
        if v < config.LADDER_K1_MIN:
            return None
        if v <= config.LADDER_K1_MAX:
            return 'k1'
        if v <= config.LADDER_K2_MAX:
            return 'k2'
        if v <= config.LADDER_K3_MAX:
            return 'k3'
        return None

    def _update_ladder(self):
        """Sample the ladder ADC (throttled) and advance the K2 tap decoder.

        Called from update() and from the poll methods so that input gets
        fresh samples between frames; the sample-interval throttle keeps the
        ADC reads bounded.
        """
        now = time.ticks_ms()
        if self._ladder is None:
            return
        if self._ladder_last_sample_ms and \
                time.ticks_diff(now, self._ladder_last_sample_ms) < \
                config.LADDER_SAMPLE_INTERVAL_MS:
            return
        self._ladder_last_sample_ms = now

        slot = self._read_ladder_slot()
        self._ladder_raw['k1'] = (slot == 'k1')
        self._ladder_raw['k2'] = (slot == 'k2')
        self._ladder_raw['k3'] = (slot == 'k3')

        k2 = self._k2
        pressed = (slot == 'k2')
        if pressed != k2['raw'] and \
                time.ticks_diff(now, k2['last_change_ms']) >= \
                config.LADDER_EDGE_DEBOUNCE_MS:
            k2['raw'] = pressed
            k2['last_change_ms'] = now
            if pressed:
                # Press edge.
                k2['count'] += 1
                if k2['count'] == 1:
                    k2['last_press_ms'] = now
                elif k2['count'] == 2:
                    if time.ticks_diff(now, k2['last_press_ms']) <= \
                            config.LADDER_DOUBLE_TAP_MS:
                        # Double tap → MENU1; cancel the pending single-tap MENU2.
                        k2['menu1_armed'] = True
                        k2['menu2_at'] = None
                    else:
                        # Too slow — the first tap was a single (its MENU2 is
                        # already scheduled); this press starts a new sequence.
                        k2['count'] = 1
                        k2['last_press_ms'] = now
                else:
                    # Defensive: 3+ presses — restart as a fresh single tap.
                    k2['count'] = 1
                    k2['last_press_ms'] = now
                    k2['menu2_at'] = None
            else:
                # Release edge.
                if k2['count'] == 1:
                    # First tap complete — schedule MENU2 unless a 2nd tap
                    # arrives within the double-tap window.
                    k2['menu2_at'] = now + config.LADDER_DOUBLE_TAP_MS
                elif k2['count'] == 2:
                    # Double tap complete.
                    k2['count'] = 0

    def _consume_menu1(self):
        k2 = self._k2
        if k2['menu1_armed']:
            k2['menu1_armed'] = False
            return True
        return False

    def _consume_menu2(self):
        k2 = self._k2
        if k2['menu2_at'] is not None and \
                time.ticks_diff(time.ticks_ms(), k2['menu2_at']) >= 0:
            k2['menu2_at'] = None
            return True
        return False

    def update(self):
        """Sample the analog D-pad + ladder once. Call once per frame before polling input."""
        if self._ladder is not None:
            self._update_ladder()
        if not self._joy:
            return
        x = self._sample_axis('x')
        y = self._sample_axis('y')
        if config.JOY_SWAP_AXES:
            x, y = y, x
        dz = config.JOY_DEADZONE
        self._raw_dir = {
            'up': y < -dz,
            'down': y > dz,
            'left': x < -dz,
            'right': x > dz,
        }

    def is_pressed(self, button_name):
        """
        Check if a button is currently pressed (raw state, no debouncing)
        Returns True if pressed, False otherwise
        """
        if self._ladder is not None:
            self._update_ladder()
        if button_name in self.buttons:
            # Button is active low (0 = pressed)
            pressed = self.buttons[button_name].value() == 0
            slot = self._ladder_slot_of_name.get(button_name)
            if slot is not None and self._ladder_raw.get(slot):
                pressed = True
            return pressed
        if self._joy and button_name in self._raw_dir:
            return self._raw_dir[button_name]
        return False

    def was_just_pressed(self, button_name):
        """
        Check if a button was just pressed (with debouncing)
        Returns True only on the rising edge of a button press
        """
        if self._ladder is not None:
            self._update_ladder()
        # MENU1/MENU2 come from the K2 tap decoder, not from raw edges.
        if button_name == 'menu1':
            return self._consume_menu1()
        if button_name == 'menu2':
            return self._consume_menu2()
        if button_name not in self.button_states:
            return False

        current_time = time.ticks_ms()
        is_currently_pressed = self.is_pressed(button_name)
        was_previously_pressed = self.button_states[button_name]
        time_since_last = time.ticks_diff(current_time, self.last_press_time[button_name])

        # Button just pressed (wasn't pressed before, is pressed now)
        if is_currently_pressed and not was_previously_pressed:
            # Check debounce time
            if time_since_last > self.debounce_time_ms:
                self.button_states[button_name] = True
                self.last_press_time[button_name] = current_time
                return True

        # Button released
        if not is_currently_pressed and was_previously_pressed:
            self.button_states[button_name] = False

        return False

    def get_direction(self):
        """
        Get the current direction from D-pad buttons
        Returns tuple (dx, dy) for movement delta
        """
        dx = 0
        dy = 0

        if self.is_pressed('up'):
            dy -= 1
        if self.is_pressed('down'):
            dy += 1
        if self.is_pressed('left'):
            dx -= 1
        if self.is_pressed('right'):
            dx += 1

        return (dx, dy)

    def _all_input_names(self):
        names = list(self.buttons)
        if self._joy:
            for _d in self._raw_dir:
                if _d not in names:
                    names.append(_d)
        return names

    def any_button_pressed(self):
        """Check if any button is currently pressed"""
        return any(self.is_pressed(btn) for btn in self._all_input_names())

    def get_pressed_buttons(self):
        """Get list of all currently pressed button names"""
        return [name for name in self._all_input_names() if self.is_pressed(name)]

    def consume_all(self):
        """Mark all currently-pressed buttons as already seen.

        Call after waking from sleep so the button that triggered the wake
        is not passed through to game logic as a fresh press.
        """
        now = time.ticks_ms()
        for btn_name in self._all_input_names():
            self.button_states[btn_name] = self.is_pressed(btn_name)
            self.last_press_time[btn_name] = now
        # Discard any in-flight K2 tap sequence too.
        if self._ladder is not None:
            self._k2['count'] = 0
            self._k2['menu1_armed'] = False
            self._k2['menu2_at'] = None
