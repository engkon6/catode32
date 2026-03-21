import gc
from scene import Scene
from ui import Scrollbar

_AUTH_MODES = {0: 'Open', 1: 'WEP', 2: 'WPA', 3: 'WPA2', 4: 'WPA/2', 6: 'WPA3'}


class DebugWifiScene(Scene):
    """Debug scene that scans for nearby WiFi access points."""

    LINES_VISIBLE = 8
    LINE_HEIGHT = 8

    def __init__(self, context, renderer, input):
        super().__init__(context, renderer, input)
        self.scrollbar = Scrollbar(renderer)
        self.scroll_offset = 0
        self.lines = []

    def load(self):
        super().load()

    def unload(self):
        super().unload()

    def enter(self):
        self.scroll_offset = 0
        self._scan()

    def exit(self):
        pass

    def _scan(self):
        self.lines = ["Scanning WiFi..."]
        try:
            import network
            wlan = network.WLAN(network.STA_IF)
            was_active = wlan.active()
            wlan.active(True)
            aps = wlan.scan()
            if not was_active:
                wlan.active(False)

            aps_sorted = sorted(aps, key=lambda x: -x[3])
            self.lines = [f"WiFi: {len(aps)} APs (A=rescan)"]
            for ap in aps_sorted:
                try:
                    ssid = ap[0].decode('utf-8') if ap[0] else '(hidden)'
                except Exception:
                    ssid = '(binary)'
                channel = ap[2]
                rssi = ap[3]
                auth = _AUTH_MODES.get(ap[4], '?')
                self.lines.append(f" {ssid[:18]}")
                self.lines.append(f"  ch{channel} {rssi}dBm {auth}")
        except Exception as e:
            self.lines = ["WiFi error:", f" {e}"]
        gc.collect()

    def update(self, dt):
        return None

    def draw(self):
        visible_end = min(self.scroll_offset + self.LINES_VISIBLE, len(self.lines))
        for i, line in enumerate(self.lines[self.scroll_offset:visible_end]):
            self.renderer.draw_text(line[:21], 0, i * self.LINE_HEIGHT)
        if len(self.lines) > self.LINES_VISIBLE:
            self.scrollbar.draw(len(self.lines), self.LINES_VISIBLE, self.scroll_offset)

    def handle_input(self):
        max_scroll = max(0, len(self.lines) - self.LINES_VISIBLE)
        if self.input.was_just_pressed('up'):
            self.scroll_offset = max(0, self.scroll_offset - 1)
        if self.input.was_just_pressed('down'):
            self.scroll_offset = min(max_scroll, self.scroll_offset + 1)
        if self.input.was_just_pressed('a'):
            self.scroll_offset = 0
            self._scan()
        if self.input.was_just_pressed('b'):
            return ('change_scene', 'last_main')
        return None
