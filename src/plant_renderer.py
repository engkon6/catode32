"""plant_renderer.py - Drawing callbacks for the living plant system.

Call register_plant_draws(scene) from a MainScene subclass's enter() path
(via the base-class _register_plant_draws hook) to attach per-layer draw
callbacks onto the scene's Environment.
"""

import config
from assets.plants import PLANT_SPRITES, POT_SPRITES


def register_plant_draws(scene):
    """Register a draw callback for each unique layer in scene.PLANT_SURFACES."""
    scene._plant_sprites = PLANT_SPRITES
    scene._pot_sprites   = POT_SPRITES
    seen = set()
    for surf in getattr(scene, 'PLANT_SURFACES', []):
        layer = surf['layer']
        if layer in seen:
            continue
        seen.add(layer)
        def make_cb(l):
            def cb(renderer, camera_x, parallax):
                draw_plants_layer(scene, renderer, camera_x, parallax, l)
            return cb
        scene.environment.add_custom_draw(layer, make_cb(layer))


def draw_plants_layer(scene, renderer, camera_x, parallax, layer):
    """Draw all pots and plants for one layer of one scene."""
    plant_sprites = getattr(scene, '_plant_sprites', None)
    pot_sprites   = getattr(scene, '_pot_sprites',   None)
    if plant_sprites is None or pot_sprites is None:
        return

    offset     = int(camera_x * parallax)
    scene_name = scene.SCENE_NAME

    for plant in scene.context.plants:
        if plant['scene'] != scene_name or plant['layer'] != layer:
            continue

        screen_x = plant['x'] - offset
        if screen_x + 30 < 0 or screen_x > config.DISPLAY_WIDTH:
            continue

        y_snap   = plant.get('y_snap', 63)
        pot_type = plant['pot']
        stage    = plant['stage']
        mirror   = plant.get('mirror', False)

        pot_h = 0
        if pot_type != 'ground':
            pot_spr = pot_sprites.get(pot_type)
            if pot_spr:
                pot_h = pot_spr['height']
                renderer.draw_sprite_obj(pot_spr, screen_x, y_snap - pot_h, mirror_h=mirror)

        if stage not in ('empty_pot', 'dead', 'dormant') and stage is not None:
            plant_spr = plant_sprites.get((plant['type'], stage))
            if plant_spr:
                renderer.draw_sprite_obj(
                    plant_spr,
                    screen_x,
                    y_snap - pot_h - plant_spr['height'],
                    mirror_h=mirror,
                )
