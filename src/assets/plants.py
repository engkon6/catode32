"""assets/plants.py - Sprites for the plant system (pots and plants).

All plant and planter sprites live here.  They were previously spread across
assets/nature.py (PLANTER1, PLANT1-3, PLANT6) and assets/items.py
(PLANTER_SMALL_1).

PLANT_SPRITES maps (plant_type, stage) -> sprite dict.
POT_SPRITES   maps pot_type            -> sprite dict.

Wilted stages fall back to their base-stage sprite until dedicated wilted
art is available.  Dead plants render nothing (None) — a dead-stick sprite
will be added later.
"""

# ---------------------------------------------------------------------------
# Pot sprites
# ---------------------------------------------------------------------------

PLANTER1 = {
    "width": 13,
    "height": 9,
    "frames": [ b"\xff\xf8\xff\xf8\x40\x10\x40\x10\x20\x20\x20\x20\x10\x40\x1f\xc0\x3f\xe0" ],
    "fill_frames": [ b"\xff\xf8\xff\xf8\x7f\xf0\x7f\xf0\x3f\xe0\x3f\xe0\x1f\xc0\x1f\xc0\x3f\xe0" ]
}

PLANTER_SMALL_1 = {
    "width": 27,
    "height": 16,
    "frames": [
        b"\x00\x80\x10\x00\x05\x44\x2a\x00\x44\x8a\x95\x40\xb2\x44\x92\xa0\x4a\x54\x94\xc0\x0a\x6d\x15\x00\x05\x55\x25\x00\x05\x55\x26\x00\x05\x55\x26\x00\x05\x55\x26\x00\x00\x00\x00\x00\x1f\xff\xff\x80\x10\x00\x00\x80\x0f\xff\xff\x00\x0f\xff\xff\x00\x10\x00\x00\x80"
    ]
}

POT_SPRITES = {
    'small':   PLANTER1,        # 13x9  — small round pot
    'medium':  PLANTER1,        # stub — replace when medium pot sprite is ready
    'large':   PLANTER1,        # stub — replace when large pot sprite is ready
    'planter': PLANTER_SMALL_1, # 27x16 — wide planter box
}

# Height to add below a ground plant so it sits on the surface visually.
GROUND_PLANT_OFFSET = 0


# ---------------------------------------------------------------------------
# Plant sprites
# ---------------------------------------------------------------------------

PLANT3 = {
    "width": 9,
    "height": 7,
    "frames": [
        b"\x60\x00\xf0\x00\x70\x00\x38\x00\x08\x80\x09\x00\x09\x00"
    ]
}

PLANT1 = {
    "width": 14,
    "height": 17,
    "frames": [ b"\xc0\x00\xa0\x00\xd0\x70\x70\xb0\x31\x60\x09\xc0\x0a\x00\x04\x00\x64\x00\x54\x1c\x6a\x2c\x3a\x58\x06\x70\x02\x80\x03\x00\x02\x00\x02\x00" ]
}

PLANT2 = {
    "width": 19,
    "height": 10,
    "frames": [
        b"\x02\x10\x00\x01\x28\x00\x02\x90\x40\x41\x28\xa0\xa2\x91\x40\x51\x2a\x80\x2a\x91\x00\x19\x2a\x00\x05\x12\x00\x05\x12\x00"
    ]
}

PLANT6 = {
    "width": 20,
    "height": 23,
    "frames": [
        b"\x00\x10\x00\x00\x28\x00\x00\x10\x00\x02\x28\x00\x01\x10\x00\x02\xa8\x20\x01\x10\x50\x02\xa8\xa0\x01\x11\x40\x42\x92\x80\xa1\x15\x00\x51\x12\x00\x29\x15\x00\x19\x12\x00\x04\x92\x00\x04\x92\x00\x04\x92\x00\x04\x92\x00\x02\x92\x00\x02\x92\x00\x02\x92\x00\x02\x92\x00\x02\x92\x00"
    ]
}

# ---------------------------------------------------------------------------
# PLANT_SPRITES lookup: (plant_type, stage) -> sprite dict
# ---------------------------------------------------------------------------
# Stub assignments use existing sprites grouped by visual size.
# Replace individual entries as real sprites are delivered.
#
# Size guide for stubs:
#   seedling        → PLANT3  ( 9x 7) — tiny sprout
#   young           → PLANT3  ( 9x 7) — still small
#   growing         → PLANT1  (14x17) — mid-size leafy
#   mature          → PLANT2  (19x10) — spreading / bushy
#   thriving        → PLANT6  (20x23) — large statement plant
#   *_wilted        → same as base (no separate wilted art yet)
#   dead            → None    (draws nothing until dead-stick sprite added)
#   dormant         → None    (bare pot, no plant drawn)
#   empty_pot       → None    (just the pot rendered; no plant)

def _stage_sprite(base):
    if base == 'seedling': return PLANT3
    if base == 'young':    return PLANT3
    if base == 'growing':  return PLANT1
    if base == 'mature':   return PLANT2
    if base == 'thriving': return PLANT6
    return None


_TYPES = ('cat_grass', 'fern', 'tulip', 'rose', 'sunflower')
_BASES = ('seedling', 'young', 'growing', 'mature', 'thriving')

PLANT_SPRITES = {}

for _t in _TYPES:
    for _b in _BASES:
        _s = _stage_sprite(_b)
        PLANT_SPRITES[(_t, _b)]             = _s   # healthy
        PLANT_SPRITES[(_t, _b + '_wilted')] = _s   # wilted (same stub)

    PLANT_SPRITES[(_t, 'dead')]      = None
    PLANT_SPRITES[(_t, 'dormant')]   = None
    PLANT_SPRITES[(_t, 'empty_pot')] = None

del _t, _b, _s, _TYPES, _BASES
