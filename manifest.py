# Frozen module manifest for petpython firmware build.
#
# Files frozen here have their bytecode stored in flash rather than heap.
# Frozen modules CANNOT be unloaded from sys.modules, so only freeze
# modules that are always needed.
#
# Strategy:
#   - Freeze: assets, core engine (renderer, environment, sky, ui, etc.)
#   - Keep on filesystem: scenes, behaviors (lazy-loaded/unloaded)

include("$(PORT_DIR)/boards/manifest.py")

import os as _os
_src = _os.environ["PETPYTHON_SRC"]

freeze(_src, (
    # --- Assets (always needed, heavy sprite data) ---
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

    # --- Core engine (loaded at startup, never unloaded) ---
    "config.py",
    "context.py",
    "input.py",
    "main.py",
    "menu.py",
    "scene.py",
    "scene_manager.py",
    "renderer.py",
    "sprite_transform.py",
    "transitions.py",
    "ui.py",
    "ui_keyboard.py",
    "splash.py",
    "settings.py",
    "reset_context.py",
    "backup.py",
    "clock.py",
    "environment.py",
    "sky.py",
    "weather_system.py",
    "time_system.py",
    "temperature_system.py",
    "sleep_manager.py",
    "plant_system.py",
    "plant_renderer.py",
    "gardening_ui.py",
    "visit_manager.py",
    "espnow_handler.py",
    "espnow_manager.py",
    "wifi_tracker.py",
    "framebuf.py",
    "sh1106.py",
    "ssd1306.py",
))
