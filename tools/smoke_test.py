#!/usr/bin/env python3
"""
smoke_test.py - Headless scripted smoke test for the Catode32 game.

Runs the real game logic (scenes, menus, adoption, save/load) on the desktop
emulator with a deterministic scripted input, without a display or keyboard.

Usage:
    python tools/smoke_test.py [--lang en]

Steps:
  1. Translates src/ into build/desktop-<lang> (same as run.py)
  2. Boot 1 (fresh state): adoption flow -> inside, contextual menu, big-menu
     navigation to outside/back, minigame load, then quit+save.
  3. Boot 2 (with save): verifies the game restores directly into 'inside'.
  4. Prints PASS/FAIL. Non-zero exit code on failure.
"""

import argparse
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(ROOT, 'src')
SAVE_DIR = os.path.join(tempfile.gettempdir(), 'catode32_smoke_save')


class ScriptedInput:
    """API-compatible InputHandler driven by a deterministic frame timeline.

    Script building:
        inp.wait(frames)       nothing pressed for N frames
        inp.tap('a', 'b')      press buttons for 2 frames, then a release gap
        inp.mark(name, probe)  at the next script frame, record probe() -> marks
        inp.quit()             post pygame.QUIT when the timeline reaches the end
    """

    BUTTON_KEYS = ('up', 'down', 'left', 'right', 'a', 'b', 'menu1', 'menu2')

    def __init__(self):
        self._timeline = {}        # script frame -> set of pressed buttons
        self._marks = {}           # script frame -> (name, probe)
        self._script_len = 0       # script pointer (advanced by wait/hold)
        self._now = 0              # runtime frame counter (advanced by update)
        self._cur = set()          # buttons pressed this frame
        self._states = {k: False for k in self.BUTTON_KEYS}
        self._just = {k: False for k in self.BUTTON_KEYS}
        self.marks = {}
        self._quit_posted = False

    # ── script building ────────────────────────────────────────────────

    def _hold(self, buttons, frames):
        for f in range(self._script_len, self._script_len + frames):
            self._timeline[f] = self._timeline.get(f, set()) | set(buttons)
        self._script_len += frames

    def wait(self, frames=1):
        self._script_len += max(1, frames)

    def tap(self, *buttons, frames=2):
        self._hold(buttons, frames)
        self.wait(1)

    def hold(self, buttons, frames):
        self._hold(buttons, frames)

    def mark(self, name, probe):
        self._marks[self._script_len] = (name, probe)

    def quit(self):
        self._marks[self._script_len] = ('__quit__', None)

    # ── runtime (input API used by the game) ───────────────────────────

    def pump(self):
        pass

    def update(self):
        f = self._now
        self._now += 1
        self._cur = self._timeline.get(f, set())
        for k in self.BUTTON_KEYS:
            now = k in self._cur
            self._just[k] = now and not self._states[k]
            self._states[k] = now
        m = self._marks.get(f)
        if m:
            name, probe = m
            if name == '__quit__':
                if not self._quit_posted:
                    import pygame
                    pygame.event.post(pygame.event.Event(pygame.QUIT))
                    self._quit_posted = True
            else:
                self.marks[name] = probe()

    def is_pressed(self, name):
        return name in self._cur

    def was_just_pressed(self, name):
        return self._just.get(name, False)

    def get_direction(self):
        dx = (1 if 'right' in self._cur else 0) - (1 if 'left' in self._cur else 0)
        dy = (1 if 'down' in self._cur else 0) - (1 if 'up' in self._cur else 0)
        return (dx, dy)

    def any_button_pressed(self):
        return bool(self._cur)

    def get_pressed_buttons(self):
        return [k for k in self.BUTTON_KEYS if k in self._cur]

    def consume_all(self):
        pass


def build_bundle(lang):
    out = os.path.join(ROOT, 'build', 'desktop-' + lang)
    subprocess.run(
        [sys.executable, os.path.join(ROOT, 'tools', 'translate.py'),
         '--lang', lang, SRC_DIR, out],
        check=True,
    )
    return out


def run_tour(game, inp, expect_adoption):
    sm = game.scene_manager
    probe = lambda: getattr(sm.current_scene, 'SCENE_NAME', type(sm.current_scene).__name__)

    if expect_adoption:
        inp.wait(40)
        inp.tap('a'); inp.wait(10)        # grid -> profile
        inp.tap('a'); inp.wait(10)        # profile -> confirm menu
        inp.tap('a'); inp.wait(10)        # confirm -> adopt -> naming keyboard
        inp.tap('menu1'); inp.wait(280)   # keyboard confirms default name -> moment -> inside
        inp.mark('after_adoption', probe)
    else:
        inp.wait(30)
        inp.mark('after_adoption', probe)

    # contextual pet menu (menu2)
    inp.tap('menu2'); inp.wait(5)
    inp.tap('down');  inp.wait(5)
    inp.tap('a');     inp.wait(20)
    inp.tap('menu2'); inp.wait(5)
    inp.tap('b');     inp.wait(5)

    # big menu (menu1) -> Locations -> Outside
    inp.tap('menu1'); inp.wait(5)
    inp.tap('down');  inp.wait(5)         # Locations (submenu)
    inp.tap('right'); inp.wait(5)
    inp.tap('down');  inp.wait(4)
    inp.tap('down');  inp.wait(4)
    inp.tap('down');  inp.wait(4)         # Outside
    inp.tap('a');     inp.wait(40)        # transition + load
    inp.mark('after_outside', probe)

    # big menu -> Locations -> Living Room (back inside)
    inp.tap('menu1'); inp.wait(5)
    inp.tap('down');  inp.wait(5)
    inp.tap('right'); inp.wait(5)
    inp.tap('a');     inp.wait(40)
    inp.mark('back_inside', probe)

    # big menu -> Minigames -> Memory
    inp.tap('menu1'); inp.wait(5)
    inp.tap('down');  inp.wait(4)
    inp.tap('down');  inp.wait(4)
    inp.tap('down');  inp.wait(4)         # Minigames (submenu)
    inp.tap('right'); inp.wait(5)
    inp.tap('down');  inp.wait(4)
    inp.tap('down');  inp.wait(4)
    inp.tap('down');  inp.wait(4)
    inp.tap('down');  inp.wait(4)         # Memory
    inp.tap('a');     inp.wait(40)
    inp.mark('memory', probe)
    inp.wait(20)


def run_boot(expect_adoption):
    import pygame

    pygame.init()
    pygame.event.clear()
    import main_desktop as md

    md.InputHandler = ScriptedInput
    game = md.Game()
    inp = game.input

    try:
        run_tour(game, inp, expect_adoption=expect_adoption)
        inp.quit()
        game.run()
    except SystemExit:
        pass
    except Exception:
        import traceback
        traceback.print_exc()
        print('[SMOKE] FAIL (boot %s)' % ('fresh' if expect_adoption else 'saved'))
        sys.exit(1)

    expected = {'after_adoption': 'inside',
                'after_outside': 'outside',
                'back_inside': 'inside',
                'memory': 'MemoryScene'}
    for name, want in expected.items():
        got = inp.marks.get(name)
        print('[SMOKE] %-14s expected=%-8s got=%s' % (name, want, got))
        assert got == want, 'boot %s: %s expected %s, got %s' % (
            'fresh' if expect_adoption else 'saved', name, want, got)


def main():
    parser = argparse.ArgumentParser(description='Headless smoke test')
    parser.add_argument('--lang', default='en')
    parser.add_argument('--phase', choices=['fresh', 'saved'], default=None,
                        help='Run an individual boot phase directly')
    args = parser.parse_args()

    os.environ['SDL_VIDEODRIVER'] = 'dummy'
    os.environ['CATODE32_SRC'] = SAVE_DIR
    os.makedirs(SAVE_DIR, exist_ok=True)

    out = build_bundle(args.lang)
    os.chdir(out)
    sys.path.insert(0, out)

    if args.phase == 'fresh':
        run_boot(expect_adoption=True)
        return
    elif args.phase == 'saved':
        run_boot(expect_adoption=False)
        return

    # Runner mode: clean save, then run each boot in an isolated sub-process
    for f in ('save.json',):
        p = os.path.join(SAVE_DIR, f)
        if os.path.exists(p):
            os.remove(p)

    # Boot 1: fresh state exercises the adoption flow
    cmd_fresh = [sys.executable, __file__, '--lang', args.lang, '--phase', 'fresh']
    subprocess.check_call(cmd_fresh)

    save_path = os.path.join(SAVE_DIR, 'save.json')
    assert os.path.exists(save_path), 'save.json was not written'
    print('[SMOKE] save.json written OK (%d bytes)' % os.path.getsize(save_path))

    # Boot 2: saved game should restore directly into 'inside'
    cmd_saved = [sys.executable, __file__, '--lang', args.lang, '--phase', 'saved']
    subprocess.check_call(cmd_saved)

    print('[SMOKE] ALL PASS')


if __name__ == '__main__':
    main()
