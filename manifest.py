# Frozen module manifest for petpython firmware build.
#
# Files frozen here have their code stored in flash rather than heap.
# Import paths are relative to "src/" so assets/character.py -> assets.character
#
# What gets frozen:
#   - assets/* : large sprite/byte data. Loading these from the filesystem would
#     put tens of KB of bytecode + byte literals on the heap.
#   - The boot/baseline graph + scene_manager._PINNED_MODULES : modules loaded at
#     startup and never purged across scene transitions (see scene_manager.py).
#     Freezing them keeps their code (and string/bytes constants) in flash so the
#     ESP32-C3 heap stays available for runtime objects.
#
# What must stay on the filesystem:
#   - scenes/* except main_scene and vacation_scene : lazily imported per scene
#     and unloaded from sys.modules on transition (frozen modules cannot be
#     purged). main_scene/vacation_scene are pinned, so they are frozen.
#   - Lazy-loaded behavior modules (entities/behaviors/* except base+idle).
#   - Modules main.py explicitly discards after use: wifi_tracker, splash.
#   - The ESP-NOW game stack (espnow_handler/espnow_manager/visit_manager) and
#     other on-demand modules.

# Include the board's default manifest (asyncio, networking libs, etc.)
include("$(PORT_DIR)/boards/manifest.py")

import os as _os
_src = _os.environ["PETPYTHON_SRC"]

freeze(_src, (
    # ---- Asset data (always loaded, large byte literals) ----
    "assets/__init__.py",
    "assets/boot_img.py",
    "assets/character.py",
    "assets/effects.py",
    "assets/furniture.py",
    "assets/icons.py",
    "assets/items.py",
    "assets/minigame_assets.py",
    "assets/minigame_character.py",
    "assets/nature.py",
    "assets/platformer_levels.py",
    "assets/platformer_terrain.py",
    "assets/plants.py",
    "assets/store.py",

    # ---- Boot / baseline graph (imported at startup, never purged) ----
    "config.py",
    "input.py",
    "renderer.py",
    "context.py",
    "scene_manager.py",
    "main.py",
    "menu.py",
    "transitions.py",
    "ui.py",
    "framebuf.py",
    "sprite_transform.py",
    "weather_system.py",
    "time_system.py",
    "sleep_manager.py",
    "backup.py",
    "scene.py",

    # ---- Pinned modules (scene_manager._PINNED_MODULES, never purged) ----
    "sky.py",
    "environment.py",
    "clock.py",
    "behavior_manager.py",
    "plant_system.py",
    "plant_renderer.py",
    "gardening_ui.py",
    "scenes/main_scene.py",
    "scenes/vacation_scene.py",
    "entities/entity.py",
    "entities/character.py",
    "entities/behaviors/base.py",
    "entities/behaviors/idle.py",
))
