import gc
from scene import Scene
from ui import Scrollbar


class DebugEspnowScene(Scene):
    """Debug scene that shows ESP-NOW status and registered peers."""

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

    def _fmt_mac(self, mac_bytes):
        return ':'.join(f'{b:02x}' for b in mac_bytes)

    def _scan(self):
        self.lines = []
        try:
            import network
            import espnow

            wlan = network.WLAN(network.STA_IF)
            was_active = wlan.active()
            wlan.active(True)

            mac = wlan.config('mac')
            self.lines.append("Own MAC (STA):")
            self.lines.append(f" {self._fmt_mac(mac)}")
            self.lines.append("")

            e = espnow.ESPNow()
            e.active(True)

            peers = list(e.get_peers())
            self.lines.append(f"Peers: {len(peers)} (A=refresh)")
            for peer in peers:
                peer_mac = peer[0]
                channel = peer[2] if len(peer) > 2 else '?'
                self.lines.append(f" {self._fmt_mac(peer_mac)}")
                self.lines.append(f"  ch{channel}")

            if not peers:
                self.lines.append(" None registered")

            # Check for any buffered incoming packets
            self.lines.append("")
            buf_count = 0
            while True:
                try:
                    host, msg = e.recv(0)
                    if host is None:
                        break
                    buf_count += 1
                except Exception:
                    break
            self.lines.append(f"Buffered msgs: {buf_count}")

            e.active(False)
            if not was_active:
                wlan.active(False)

        except Exception as e:
            self.lines = ["ESP-NOW error:", f" {e}"]
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
