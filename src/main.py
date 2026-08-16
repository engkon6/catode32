import sys
import time
import config
import gc

_INTENT_PATH = '/intent.json'


def _mem_probe(tag):
    """[PROBE] print GC free/alloc at a named point. Remove after tuning."""
    print("[MEM] %s: free=%d alloc=%d" % (tag, gc.mem_free(), gc.mem_alloc()))


def _check_resume_intent():
    """Read /intent.json and return the scene name to resume, or None.

    Deletes the file and returns None if the attempt count has reached the
    limit, preventing a bootloop caused by a consistently-crashing scene.
    """
    try:
        import ujson
        with open(_INTENT_PATH) as f:
            data = ujson.load(f)
        scene = data.get('s', '')
        attempts = data.get('a', 0)
        if not scene or attempts >= 2:
            import uos
            uos.remove(_INTENT_PATH)
            print(f"[Boot] Intent aborted after {attempts} attempt(s): {scene}")
            return None
        print(f"[Boot] Resuming intent ({attempts} attempt(s)): {scene}")
        return scene
    except OSError:
        return None
    except Exception as e:
        print(f"[Boot] Intent check failed: {e}")
        return None


def _save_on_crash(game):
    """Best-effort: save context then write /intent.json before rebooting.

    Only writes the intent file if the context save succeeded, so we never
    resume a scene with stale stats.  Reads any existing attempt count from
    the intent file and increments it, so boot-loop detection keeps working.
    """
    import gc
    gc.collect()
    context = getattr(game, 'context', None)
    if context is None:
        return
    intent = getattr(context, 'pending_intent', None)
    if not context._write_to_flash():
        return
    if not intent:
        return
    # Read existing attempt count without ujson (low memory path)
    attempts = 0
    try:
        with open(_INTENT_PATH) as f:
            content = f.read(64)
        idx = content.find('"a":')
        if idx >= 0:
            attempts = int(content[idx + 4:].split(',')[0].split('}')[0])
    except Exception:
        pass
    with open(_INTENT_PATH, 'w') as f:
        f.write('{"s":"' + intent + '","a":' + str(attempts + 1) + '}')

from input import InputHandler
from renderer import Renderer
from context import GameContext
from scene_manager import SceneManager
from weather_system import WeatherSystem
from time_system import TimeSystem
from splash import show_splash


_WIFI_SCENES = ('outside', 'treehouse', 'social')


class Game:
    def __init__(self):
        print("==> Virtual Pet Starting...")

        self.renderer = Renderer()
        show_splash(self.renderer)
        del sys.modules['splash']

        self.input = InputHandler()
        self.context = GameContext()
        _has_save = self.context.load()
        self.context.input = self.input  # expose input to behaviors

        # WiFi is initialized NOW, while the ESP-IDF heap is still pristine.
        # Once the game's split-heap grows, it consumes the IDF heap so the
        # WiFi driver can't allocate its task stack ("WiFi Out of Memory").
        # The reduced sdkconfig keeps the driver at ~4KB so the game still
        # fits.  The WLAN stays active (ESP-NOW reuses this singleton).
        #
        # The ESP-NOW *game* stack (espnow_manager/handler/visit_manager and
        # their deps incl. ui, ~30KB) is NOT imported at boot: it is only
        # needed by outdoor scenes, and loading it at boot - on top of the
        # active WiFi driver - OOMs the C3.  It is loaded lazily the first
        # time the game enters a WiFi scene (see _ensure_espnow_stack).
        if config.WIFI_ENABLED:
            import network
            self._wlan = network.WLAN(network.STA_IF)
            self._wlan.active(True)
            try:
                import wifi_tracker
                wifi_tracker.scan_now(self.context)
                del sys.modules['wifi_tracker']
            except Exception as e:
                print("[Boot] WiFi scan failed: " + str(e))
            self._espnow_loaded = False
        else:
            self._espnow_loaded = True
        self._espnow_handler_ref = None
        self._visit_manager_ref = None

        self.scene_manager = SceneManager(self.context, self.renderer, self.input)

        # Lazy-load the ESP-NOW game stack (handlers/visit_manager, ~11KB)
        # when entering a WiFi scene.  The load happens AFTER the scene
        # switch so the outgoing scene's modules/data are purged first,
        # freeing heap for the stack (loading it before OOMs the C3).
        _orig_change = self.scene_manager.change_scene_by_name

        def _wrapped_change(name, *args, **kwargs):
            result = _orig_change(name, *args, **kwargs)
            if not self._espnow_loaded and name in _WIFI_SCENES:
                self._ensure_espnow_stack()
            return result

        self.scene_manager.change_scene_by_name = _wrapped_change

        _resume = _check_resume_intent()
        if _resume:
            self.scene_manager.change_scene_by_name(_resume)
        elif _has_save:
            self.scene_manager.change_scene_by_name('inside')
        else:
            self.scene_manager.change_scene_by_name('adoption')

        self.weather_system = WeatherSystem()
        if 'weather' not in self.context.environment:
            self.weather_system.init_environment(self.context.environment, self.context.pet_seed)

        self.time_system = TimeSystem()
        self.time_system.pet_seed = self.context.pet_seed
        self.time_system.update_moon_phase(self.context.environment)
        self.time_system.update_season(self.context.environment)
        self.time_system.update_temperature(self.context.environment)

        _mem_probe('post-init')

        # Collect frequently to limit heap fragmentation.
        # Trigger after every ~12KB of allocations rather than waiting for OOM.
        import gc as _gc
        _gc.threshold(12000)
        del _gc

        self.last_frame_time = time.ticks_ms()
        # Simulated time rate: game minutes per real second (full day = 360 real minutes, 4 game days per IRL day)
        self.time_system.game_minutes_per_second = 1/15
        if config.SLEEP_MODE:
            from sleep_manager import SleepManager
            self.sleep_manager = SleepManager(self.input, self.renderer)
        else:
            self.sleep_manager = None
        self._sleep_pending = False   # True while transition-out is playing pre-sleep
        self._woke_from_sleep = False  # True on the first frame after waking
        self._last_sleep_debug = time.ticks_ms()

    def _ensure_espnow_stack(self):
        """Import and wire the ESP-NOW game stack on first WiFi-scene entry.

        Kept out of __init__ because loading it at boot (on top of the active
        WiFi driver) OOMs the C3: the game's split-heap leaves no room.  The
        caller runs this AFTER the scene switch so the outgoing scene's
        modules have been purged.  The WiFi scene's on_enter() ran before the
        stack existed, so start ESP-NOW here if the current scene needs it.
        """
        if self._espnow_loaded:
            return
        try:
            from espnow_manager import EspNowManager
            from espnow_handler import EspNowHandler
            from visit_manager import VisitManager
            espnow = EspNowManager()
            self.context.espnow = espnow
            self._espnow_handler_ref = EspNowHandler(espnow, self.scene_manager)
            self._visit_manager_ref = VisitManager(self.context, self.scene_manager)
            self.context.visit_manager = self._visit_manager_ref
            self._espnow_loaded = True
            print("[ESPNow] Game stack loaded (lazy)")
            cs = self.scene_manager.current_scene
            if (cs is not None and getattr(self.scene_manager, 'current_scene_name', None) in _WIFI_SCENES
                    and self.context.visit is None):
                espnow.start()
        except Exception as e:
            print("[ESPNow] Lazy stack load failed: " + str(e))
        gc.collect()

    def _on_sleep_midpoint(self):
        """Called at the transition-out midpoint: enter sleep, then let transition-in play on wake."""
        # Deactivate the transition so scene updates work normally inside the sleep loop.
        # start_in_only() will re-activate it after the device wakes.
        self.scene_manager.transitions.active = False

        self.sleep_manager.enter_sleep(self._sleep_update)

        # If the pet navigated to a different location during sleep, switch scenes
        # now while the screen is still black so the transition-in reveals the
        # correct scene directly.
        self.scene_manager.apply_pending_scene_after_sleep()

        # Kick off the reveal transition and reset housekeeping state
        self.scene_manager.transitions.start_in_only()
        self.scene_manager.reset_idle_timer()
        self.scene_manager.on_device_wake()
        self._sleep_pending = False
        self._woke_from_sleep = True

    def _sleep_update(self, dt):
        """Minimal game tick called ~SLEEP_FPS times per second while sleeping."""
        dt_scaled = dt * self.context.time_speed
        self.time_system.advance(dt_scaled, self.context.environment, self.weather_system)
        self.scene_manager.sleep_update(dt_scaled)
        if self._espnow_handler_ref:
            self._espnow_handler_ref.dispatch()
            self._espnow_handler_ref.update(dt_scaled)

    def run(self):
        print("==> Starting game loop...")

        # [PROBE] peak-heap watcher. Remove after tuning.
        self._probe_peak_free = gc.mem_free()
        self._probe_ts = time.ticks_ms()

        while True:
            # After waking from sleep the elapsed time since last_frame_time spans
            # the entire sleep duration.  Reset it to one nominal frame so that
            # time_system doesn't get a massive dt on the first awake frame
            # (the sleep loop already advanced time correctly via _sleep_update).
            if self._woke_from_sleep:
                self._woke_from_sleep = False
                self.last_frame_time = time.ticks_ms() - config.FRAME_TIME_MS

            current_time = time.ticks_ms()
            delta_time = time.ticks_diff(current_time, self.last_frame_time)
            dt = delta_time / 1000.0 * self.context.time_speed

            self.scene_manager.handle_input()

            # Track button activity for the sleep inactivity timer
            if self.sleep_manager and self.input.any_button_pressed():
                self.sleep_manager.notify_activity()

            self.time_system.advance(dt, self.context.environment, self.weather_system)

            if self._espnow_handler_ref:
                self._espnow_handler_ref.dispatch()
                self._espnow_handler_ref.update(dt)

            self.scene_manager.update(dt)

            # [PROBE] track low-water mark of free heap; print every 30s
            _mf = gc.mem_free()
            if _mf < self._probe_peak_free:
                self._probe_peak_free = _mf
            if time.ticks_diff(time.ticks_ms(), self._probe_ts) >= 30000:
                self._probe_ts = time.ticks_ms()
                print("[MEM] peak_free=%d free=%d alloc=%d"
                      % (self._probe_peak_free, _mf, gc.mem_alloc()))

            if self._visit_manager_ref:
                self._visit_manager_ref.update(dt)

            try:
                self.scene_manager.draw()
                if self._espnow_handler_ref:
                    self._espnow_handler_ref.draw(self.renderer)
                self.renderer.show()
            except OSError as e:
                if e.errno == 19:  # ENODEV - display disconnected
                    print("==! Display disconnected, attempting reinit...")
                    time.sleep_ms(500)
                    self.renderer.reinit()
                else:
                    raise

            self.last_frame_time = current_time

            frame_time = time.ticks_diff(time.ticks_ms(), current_time)
            if frame_time < config.FRAME_TIME_MS:
                time.sleep_ms(config.FRAME_TIME_MS - frame_time)

            # Begin sleep if inactive long enough — but not during a visit or
            # while another transition is already running.
            if self.sleep_manager and not self._sleep_pending:
                if time.ticks_diff(time.ticks_ms(), self._last_sleep_debug) >= 60_000:
                    self._last_sleep_debug = time.ticks_ms()
                    elapsed = time.ticks_diff(time.ticks_ms(), self.sleep_manager._last_activity)
                    print(f"[Sleep] inactive={elapsed//1000}s/{config.SLEEP_TIMEOUT_SEC}s"
                          f" transition={self.scene_manager.transitions.active}"
                          f" visit={getattr(self.context, 'visit', None)}"
                          f" should_sleep={self.sleep_manager.should_sleep()}")
                if not self.scene_manager.transitions.active:
                    if getattr(self.context, 'pending_light_sleep', False):
                        self.context.pending_light_sleep = False
                        self._sleep_pending = True
                        self.scene_manager.transitions.start(on_midpoint=self._on_sleep_midpoint)
                    elif (getattr(self.context, 'visit', None) is None
                            and self.sleep_manager.should_sleep()):
                        self._sleep_pending = True
                        self.scene_manager.transitions.start(on_midpoint=self._on_sleep_midpoint)


def main():
    game = None
    _crash_save_attempted = False
    try:
        game = Game()
        game.run()
    except KeyboardInterrupt:
        print("== Interrupted ==")
    except Exception as e:
        print(f"==! Error: {e}")
        sys.print_exception(e)
        if not _crash_save_attempted:
            _crash_save_attempted = True
            try:
                _save_on_crash(game)
            except Exception as save_err:
                print(f"[Crash] Save failed: {save_err}")
        import machine
        machine.reset()


if __name__ == "__main__":
    main()
