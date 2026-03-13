import machine
import neopixel
from scene import Scene

# ESP32-C6 onboard WS2812 RGB LED is on GPIO8
_LED_PIN = 8
_STEP = 16  # Color adjustment step per button press


class DebugLedScene(Scene):
    """Debug scene to control the onboard WS2812 RGB LED on GPIO8."""

    MODULES_TO_KEEP = []

    # Menu rows
    _ROW_TOGGLE = 0
    _ROW_R = 1
    _ROW_G = 2
    _ROW_B = 3
    _NUM_ROWS = 4

    def __init__(self, context, renderer, input):
        super().__init__(context, renderer, input)
        self.np = None
        self.led_on = True
        self.color = [255, 255, 255]  # Start white so it's visible if already on
        self.cursor = 0

    def load(self):
        super().load()
        try:
            pin = machine.Pin(_LED_PIN, machine.Pin.OUT)
            self.np = neopixel.NeoPixel(pin, 1)
        except Exception as e:
            print(f"LED init error: {e}")
            self.np = None

    def unload(self):
        self._apply()
        super().unload()

    def enter(self):
        self.cursor = 0

    def exit(self):
        pass

    def _apply(self):
        if self.np is None:
            return
        if self.led_on:
            self.np[0] = (self.color[0], self.color[1], self.color[2])
        else:
            self.np[0] = (0, 0, 0)
        self.np.write()

    def update(self, dt):
        return None

    def draw(self):
        r = self.renderer
        r.clear()

        r.draw_text("LED Control", 10, 0)

        labels = [
            ("Toggle", "ON" if self.led_on else "OFF"),
            ("R", str(self.color[0])),
            ("G", str(self.color[1])),
            ("B", str(self.color[2])),
        ]

        for i, (label, val) in enumerate(labels):
            y = 16 + i * 9
            prefix = ">" if i == self.cursor else " "
            r.draw_text(f"{prefix}{label}: {val}   ", 0, y)

        r.draw_text("B:back", 0, 56)

    def handle_input(self):
        inp = self.input

        if inp.was_just_pressed('up'):
            self.cursor = (self.cursor - 1) % self._NUM_ROWS

        if inp.was_just_pressed('down'):
            self.cursor = (self.cursor + 1) % self._NUM_ROWS

        pressed_left = inp.was_just_pressed('left')
        pressed_right = inp.was_just_pressed('right')
        if pressed_left or pressed_right:
            delta = _STEP if pressed_right else -_STEP
            if self.cursor == self._ROW_TOGGLE:
                self.led_on = not self.led_on
            else:
                ch = self.cursor - 1  # 0=R, 1=G, 2=B
                self.color[ch] = max(0, min(255, self.color[ch] + delta))
            self._apply()

        # A: quick turn off
        if inp.was_just_pressed('a'):
            self.led_on = False
            self._apply()

        if inp.was_just_pressed('b'):
            return ('change_scene', 'normal')

        return None
