"""gardening_ui.py - Interactive UI modes for the plant system.

PlacementMode handles the cursor-based pot/seed placement flow that replaces
normal scene panning when the player is placing a new pot.
"""

import config
from plant_system import place_empty_pot
from assets.plants import POT_SPRITES
from assets.icons import PLACE_DOWN_ICON
from environment import PARALLAX_FACTORS

_DEFAULT_SURFACE = {'y_snap': 63, 'layer': 'foreground'}

_STEP = 8   # px per d-pad press

# Secondary sort key for surfaces with the same y_snap.
# Foreground sorts last so start_idx always lands on the fg floor.
_LAYER_ORDER = {'background': 0, 'midground': 1, 'foreground': 2}


class PlacementMode:
    """Cursor mode for placing a pot in a scene.

    Usage:
        mode = PlacementMode()
        mode.enter(pot_type, scene)          # activate from menu action
        mode.handle_input(input, environment) # call from handle_input
        mode.draw(renderer, environment)      # call from draw
    """

    # Bounce period in seconds: icon alternates between two positions.
    _BOUNCE_PERIOD = 0.4

    def __init__(self):
        self.active = False
        self._pot_type    = None
        self._surfaces    = []    # sorted surface list (y_snap ascending)
        self._surface_idx = 0
        self._cursor_x    = 0
        self._scene       = None  # weak ref to host scene (not persisted)
        self._bounce_t    = 0.0   # accumulator for bounce animation

    # ------------------------------------------------------------------
    # Activation
    # ------------------------------------------------------------------

    def enter(self, pot_type, scene):
        """Activate placement mode for the given pot type in the given scene."""
        raw = list(getattr(scene, 'PLANT_SURFACES', None) or [_DEFAULT_SURFACE])
        # Primary sort: y_snap ascending (higher on screen first).
        # Secondary sort: layer order ascending so foreground is always last —
        # start_idx lands on the fg floor, and up/down feel natural.
        surfaces = sorted(raw, key=lambda s: (s['y_snap'], _LAYER_ORDER.get(s['layer'], 1)))
        start_idx = len(surfaces) - 1   # start on foreground floor
        surf = surfaces[start_idx]
        x_min = surf.get('x_min', 0)
        x_max = surf.get('x_max', self._surface_x_max(surf, scene.environment.world_width))
        cursor_x = int(scene.environment.camera_x) + config.DISPLAY_WIDTH // 2
        cursor_x = max(x_min, min(x_max, cursor_x))

        self.active        = True
        self._pot_type     = pot_type
        self._surfaces     = surfaces
        self._surface_idx  = start_idx
        self._cursor_x     = cursor_x
        self._scene        = scene

    def cancel(self):
        self.active = False
        self._bounce_t = 0.0
        self._scene = None

    # ------------------------------------------------------------------
    # Input handling
    # ------------------------------------------------------------------

    def update(self, dt):
        self._bounce_t = (self._bounce_t + dt) % (self._BOUNCE_PERIOD * 2)

    def handle_input(self, input_handler, environment):
        """Process one frame of placement input.  Returns None always."""
        if input_handler.was_just_pressed('b'):
            self.cancel()
            return None

        if input_handler.was_just_pressed('a'):
            self._confirm(environment)
            return None

        # Left / Right: move cursor in fixed steps.
        dx = 0
        if input_handler.was_just_pressed('right'):
            dx = _STEP
        elif input_handler.was_just_pressed('left'):
            dx = -_STEP
        if dx:
            surf = self._surfaces[self._surface_idx]
            x_min = surf.get('x_min', 0)
            x_max = surf.get('x_max', self._surface_x_max(surf, self._scene.environment.world_width))
            self._cursor_x = max(x_min, min(x_max, self._cursor_x + dx))
            self._follow_camera(environment)

        # Up / Down: cycle between surfaces, adjusting cursor_x to keep
        # the same screen position across layers.
        surfaces = self._surfaces
        sidx = self._surface_idx
        if input_handler.was_just_pressed('up') and sidx > 0:
            self._switch_surface(sidx - 1, environment.camera_x)
        elif input_handler.was_just_pressed('down') and sidx < len(surfaces) - 1:
            self._switch_surface(sidx + 1, environment.camera_x)

        return None

    # ------------------------------------------------------------------
    # Drawing
    # ------------------------------------------------------------------

    def draw(self, renderer, environment):
        surf    = self._surfaces[self._surface_idx]
        pot_spr = POT_SPRITES.get(self._pot_type)
        if pot_spr is None:
            return
        parallax = PARALLAX_FACTORS.get(surf.get('layer', 'foreground'), 1.0)
        sx = self._cursor_x - int(environment.camera_x * parallax)
        sy = surf['y_snap'] - pot_spr['height']
        renderer.draw_sprite_obj(pot_spr, sx, sy)
        # Bounce the placement icon above the pot: 2-position up/down.
        bounce_offset = 0 if self._bounce_t < self._BOUNCE_PERIOD else 2
        icon_x = sx + pot_spr['width'] // 2 - PLACE_DOWN_ICON['width'] // 2
        icon_y = sy - PLACE_DOWN_ICON['height'] - 2 + bounce_offset
        renderer.draw_sprite_obj(PLACE_DOWN_ICON, icon_x, icon_y)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _follow_camera(self, environment):
        surf     = self._surfaces[self._surface_idx]
        parallax = PARALLAX_FACTORS.get(surf.get('layer', 'foreground'), 1.0)
        margin   = 32
        sx = self._cursor_x - int(environment.camera_x * parallax)
        if sx < margin:
            environment.set_camera(int((self._cursor_x - margin) / parallax))
        elif sx > config.DISPLAY_WIDTH - margin:
            environment.set_camera(int((self._cursor_x - (config.DISPLAY_WIDTH - margin)) / parallax))

    def _surface_x_max(self, surf, world_width):
        """Compute the maximum world-x for a surface that keeps the pot on screen.

        A plant at world_x on a layer with parallax p appears at
        screen_x = world_x - camera_x * p.  At maximum camera pan the
        effective right edge in world-space is:
            DISPLAY_WIDTH * (1 - p) + world_width * p
        """
        p = PARALLAX_FACTORS.get(surf.get('layer', 'foreground'), 1.0)
        return int(config.DISPLAY_WIDTH * (1.0 - p) + world_width * p)

    def _switch_surface(self, new_idx, camera_x):
        """Switch to a new surface index, adjusting cursor_x to keep screen position."""
        old_surf = self._surfaces[self._surface_idx]
        old_p    = PARALLAX_FACTORS.get(old_surf.get('layer', 'foreground'), 1.0)
        self._surface_idx = new_idx
        new_surf = self._surfaces[new_idx]
        new_p    = PARALLAX_FACTORS.get(new_surf.get('layer', 'foreground'), 1.0)
        # Solve for new world_x that gives the same screen_x:
        # screen_x = world_x - camera_x * parallax
        self._cursor_x = int(self._cursor_x + camera_x * (new_p - old_p))
        x_min = new_surf.get('x_min', 0)
        x_max = new_surf.get('x_max', self._surface_x_max(new_surf, self._scene.environment.world_width))
        self._cursor_x = max(x_min, min(x_max, self._cursor_x))

    def _confirm(self, environment):
        scene = self._scene
        surf  = self._surfaces[self._surface_idx]
        scene_count = sum(1 for p in scene.context.plants
                          if p['scene'] == scene.SCENE_NAME)
        if scene_count < 16:
            place_empty_pot(
                scene.context,
                scene.SCENE_NAME,
                surf['layer'],
                self._cursor_x,
                surf['y_snap'],
                self._pot_type,
            )
        self.cancel()
