import config
from scenes.vacation_scene import VacationScene
from environment import Environment, LAYER_BACKGROUND, LAYER_MIDGROUND, LAYER_FOREGROUND
from entities.character import CharacterEntity
from sky import SkyRenderer
from assets.nature import BEACH_HILL, BEACH_MOUNTAIN, BEACH_TREES, WAVE_CHUNKS, WAVE_CHUNKS2

_WORLD_WIDTH = 234
_GROUND_Y    = 58

# Sprite dimensions
_HILL_W  = BEACH_HILL["width"]       # 36
_HILL_H  = BEACH_HILL["height"]      # 4
_MTN_W   = BEACH_MOUNTAIN["width"]
_MTN_H   = BEACH_MOUNTAIN["height"]
_TREE_W  = BEACH_TREES["width"]      # 16
_TREE_H  = BEACH_TREES["height"]     # 11
_WC_W    = WAVE_CHUNKS["width"]      # 8
_WC2_W   = WAVE_CHUNKS2["width"]     # 4

# Parallax factors (mirrors environment.py)
_BG_PARALLAX    = 0.3
_MG_PARALLAX    = 0.6
_FG_PARALLAX    = 1.0
_SHORE_PARALLAX = 1.5  # bottom of FG shore line moves faster than foreground

# World-x of the BEACH_HILL sprite (background parallax layer)
_HILL_WORLD_X = 54
_HILL_Y       = 38   # top of hill sprite

# Horizon lines
_WATER_HORIZON_Y = _HILL_Y + _HILL_H   # 1px below hill bottom
_SAND_HORIZON_Y  = _HILL_Y - 1         # 1px above hill top

# BEACH_MOUNTAIN on the background parallax layer
_MTN_WORLD_X = config.DISPLAY_WIDTH - _MTN_W + 31
_MTN_Y       = _HILL_Y - _MTN_H - 1

# BEACH_TREES on the background parallax layer, overlapping the hill
_TREES_WORLD_X = _HILL_WORLD_X + 14
_TREES_Y       = _HILL_Y - _TREE_H + 1

# Shore world-x: same as the hill left edge so lines are vertical at camera_x=0
_SHORE_WORLD_X = _HILL_WORLD_X

# Y extents for each shore line segment
_SHORE_BG_Y_TOP = _HILL_Y + _HILL_H   # 42 — bottom-left corner of hill
_SHORE_BG_Y_BOT = 48                   # meets MG line
_SHORE_MG_Y_BOT = 54                   # MG line ends here (meets FG line)
_SHORE_FG_Y_BOT = 63                   # FG line reaches screen bottom

# Sand texture — small pixel clusters pre-defined in world coordinates.
_SAND_MG_CLUSTERS = [
    (98, 44), (101, 46),
    (115, 41), (118, 43), (120, 41),
    (128, 48), (131, 50),
    (140, 43), (143, 45),
    (152, 50), (155, 48), (158, 51),
    (163, 45), (167, 40),
    (174, 39), (177, 42), (180, 40),
    (185, 47), (180, 43),
]

_SAND_FG_CLUSTERS = [
    (80, 55), (88, 57),
    (99, 60), (102, 62), (106, 60),
    (118, 53), (121, 55),
    (135, 58), (139, 60),
    (146, 62), (150, 60), (153, 63),
    (158, 55), (162, 57), (165, 55),
    (168, 60), (172, 58),
    (199, 54), (201, 56),
    (210, 58), (215, 60),
]

# ------------------------------------------------------------------
# Wave chunk definitions
# (y_pos, phase_frac)  — phase_frac is 0.0–1.0 of total cycle duration,
#   used by _make_wave_states to spread chunks across the full wave cycle.
# BG layer + first 4 MG rows → WAVE_CHUNKS2 (4px wide, 1px tall, 4 frames)
# Remaining MG + FG        → WAVE_CHUNKS  (8px wide, 3px tall, 8 frames)
# ------------------------------------------------------------------
_BG_WAVE_CHUNKS = [      # y in [42, 48]; WAVE_CHUNKS2 (1.5s cycle — step 0.25 ≈ crest_dur/cycle)
    (44, 0.23),
    (46, 0.37),
]
_MG_WAVE_SMALL = [       # y in [48, 52]; WAVE_CHUNKS2
    (48, 0.13),
    (50, 0.25),
]
_MG_WAVE_LARGE = [       # y in [52, 54]; WAVE_CHUNKS
    (52, 0.42),
]
_FG_WAVE_CHUNKS = [      # y in [54, 63]; WAVE_CHUNKS (1.9s cycle — step 0.21 ≈ crest_dur/cycle)
    (54, 0.54),
    (57, 0.61),
    (60, 0.72),
]

# ------------------------------------------------------------------
# Shimmer definitions — individual pixels in open water that drift
# left or right and vanish. BG and MG layers only.
# (world_x, y, phase_frac, direction, dark_pause, max_drift)
#   dark_pause: seconds between appearances (varies → different cycle lengths)
#   max_drift:  pixels of travel before despawning (varies → different distances)
# ------------------------------------------------------------------
_BG_SHIMMERS = [
    ( 8, 44, 0.000,  1, 1.0, 2),
    (22, 44, 0.125, -1, 1.6, 3),
    (35, 46, 0.250,  1, 0.8, 4),
    (12, 47, 0.375, -1, 1.3, 2),
    (28, 48, 0.500,  1, 1.8, 3),
    (18, 45, 0.625, -1, 0.7, 4),
    (42, 46, 0.750,  1, 1.1, 2),
    ( 5, 44, 0.875, -1, 1.5, 3),
]

_MG_SHIMMERS = [
    (10, 49, 0.000,  1, 1.2, 3),
    (24, 51, 0.143, -1, 0.8, 2),
    (38, 49, 0.286,  1, 1.6, 4),
    (16, 52, 0.429, -1, 1.0, 3),
    (30, 54, 0.571,  1, 0.7, 2),
    ( 7, 55, 0.714, -1, 1.4, 4),
    (44, 58, 0.857,  1, 1.0, 3),
]

# Wave animation timing
_WAVE_FRAME_INTERVAL   = 0.10  # seconds per frame during incoming
_WAVE_CREST_DURATION   = 0.40  # seconds to hold at shore before receding
_WAVE_RECEDE_DURATION  = 0.70  # seconds to drift back to water

# Pixels each wave group travels from water to shoreline (frame 0 → last frame).
# Smaller/further-away groups travel less to sell the depth.
_WAVE_TRAVEL_BG    = 4   # background WAVE_CHUNKS2
_WAVE_TRAVEL_MG_SM = 6   # midground WAVE_CHUNKS2
_WAVE_TRAVEL_MG_LG = 8   # midground WAVE_CHUNKS
_WAVE_TRAVEL_FG    = 12  # foreground WAVE_CHUNKS

# Shimmer timing — dark_pause and max_drift are now per-shimmer so each
# has a unique cycle length and travel distance and they never re-sync.
_SHIMMER_STEP_DURATION = 0.18  # seconds per pixel of drift (shared)

# State machine values — waves are ALWAYS drawn, no invisible state
_WS_INCOMING = 0
_WS_CREST    = 1
_WS_RECEDING = 2

# State list indices
_WI_STATE = 0
_WI_FRAME = 1
_WI_TIMER = 2

# Shimmer states and state list indices
_SS_DARK  = 0
_SS_LIT   = 1
_SDI_STATE = 0
_SDI_STEPS = 1
_SDI_TIMER = 2


def _make_wave_states(chunks, num_frames):
    last_frame = num_frames - 1
    incoming_dur = num_frames * _WAVE_FRAME_INTERVAL
    total_cycle = incoming_dur + _WAVE_CREST_DURATION + _WAVE_RECEDE_DURATION
    states = []
    for (_, phase_frac) in chunks:
        offset = phase_frac * total_cycle
        if offset < incoming_dur:
            frame = int(offset / _WAVE_FRAME_INTERVAL)
            timer = _WAVE_FRAME_INTERVAL - (offset % _WAVE_FRAME_INTERVAL)
            states.append([_WS_INCOMING, frame, timer])
        elif offset < incoming_dur + _WAVE_CREST_DURATION:
            timer = _WAVE_CREST_DURATION - (offset - incoming_dur)
            states.append([_WS_CREST, last_frame, timer])
        else:
            timer = _WAVE_RECEDE_DURATION - (offset - incoming_dur - _WAVE_CREST_DURATION)
            states.append([_WS_RECEDING, last_frame, timer])
    return states


def _shore_x_at_y(y, camera_x):
    """Return the screen-x of the shore centre line at a given screen-y."""
    if y <= _SHORE_BG_Y_BOT:
        t = (y - _SHORE_BG_Y_TOP) / (_SHORE_BG_Y_BOT - _SHORE_BG_Y_TOP)
        x0 = _SHORE_WORLD_X - int(camera_x * _BG_PARALLAX)
        x1 = _SHORE_WORLD_X - int(camera_x * _MG_PARALLAX)
    elif y <= _SHORE_MG_Y_BOT:
        t = (y - _SHORE_BG_Y_BOT) / (_SHORE_MG_Y_BOT - _SHORE_BG_Y_BOT)
        x0 = _SHORE_WORLD_X - int(camera_x * _MG_PARALLAX)
        x1 = _SHORE_WORLD_X - int(camera_x * _FG_PARALLAX)
    else:
        t = (y - _SHORE_MG_Y_BOT) / (_SHORE_FG_Y_BOT - _SHORE_MG_Y_BOT)
        x0 = _SHORE_WORLD_X - int(camera_x * _FG_PARALLAX)
        x1 = _SHORE_WORLD_X - int(camera_x * _SHORE_PARALLAX)
    return int(x0 + t * (x1 - x0))


def _tick_wave_group(dt, chunks, states, num_frames):
    last_frame = num_frames - 1
    for i in range(len(chunks)):
        st = states[i]
        st[_WI_TIMER] -= dt
        if st[_WI_TIMER] > 0:
            continue
        if st[_WI_STATE] == _WS_INCOMING:
            st[_WI_FRAME] += 1
            if st[_WI_FRAME] >= num_frames:
                st[_WI_FRAME] = last_frame
                st[_WI_STATE] = _WS_CREST
                st[_WI_TIMER] += _WAVE_CREST_DURATION
            else:
                st[_WI_TIMER] += _WAVE_FRAME_INTERVAL
        elif st[_WI_STATE] == _WS_CREST:
            st[_WI_STATE] = _WS_RECEDING
            st[_WI_TIMER] += _WAVE_RECEDE_DURATION
        else:  # RECEDING — drift back to water, then restart
            st[_WI_FRAME] = 0
            st[_WI_STATE] = _WS_INCOMING
            st[_WI_TIMER] += _WAVE_FRAME_INTERVAL


def _draw_wave_group(renderer, camera_x, chunks, states, sprite, sprite_w, num_frames, travel_px):
    half_w = sprite_w // 2
    last_frame = num_frames - 1
    for i in range(len(chunks)):
        st = states[i]
        y = chunks[i][0]
        shore_x = _shore_x_at_y(y, camera_x) - half_w
        if st[_WI_STATE] == _WS_INCOMING:
            travel = travel_px * st[_WI_FRAME] // last_frame
        elif st[_WI_STATE] == _WS_CREST:
            travel = travel_px
        else:
            progress = st[_WI_TIMER] / _WAVE_RECEDE_DURATION
            travel = int(travel_px * progress)
        sx = shore_x - (travel_px - travel)
        renderer.draw_sprite_obj(sprite, sx, y, frame=st[_WI_FRAME])


def _make_shimmer_states(shimmers):
    states = []
    for (_, _, phase_frac, _, dark_pause, max_drift) in shimmers:
        total_cycle = dark_pause + max_drift * _SHIMMER_STEP_DURATION
        offset = phase_frac * total_cycle
        if offset < dark_pause:
            states.append([_SS_DARK, 0, dark_pause - offset])
        else:
            into_lit = offset - dark_pause
            step = min(int(into_lit / _SHIMMER_STEP_DURATION), max_drift - 1)
            remaining = _SHIMMER_STEP_DURATION - into_lit % _SHIMMER_STEP_DURATION
            states.append([_SS_LIT, step, remaining])
    return states


def _tick_shimmers(dt, shimmers, states):
    for i in range(len(states)):
        st = states[i]
        dark_pause = shimmers[i][4]
        max_drift  = shimmers[i][5]
        st[_SDI_TIMER] -= dt
        if st[_SDI_TIMER] > 0:
            continue
        if st[_SDI_STATE] == _SS_DARK:
            st[_SDI_STATE] = _SS_LIT
            st[_SDI_STEPS] = 0
            st[_SDI_TIMER] += _SHIMMER_STEP_DURATION
        else:
            st[_SDI_STEPS] += 1
            if st[_SDI_STEPS] >= max_drift:
                st[_SDI_STATE] = _SS_DARK
                st[_SDI_STEPS] = 0
                st[_SDI_TIMER] += dark_pause
            else:
                st[_SDI_TIMER] += _SHIMMER_STEP_DURATION


def _draw_shimmers(renderer, camera_x, parallax, shimmers, states):
    sw = config.DISPLAY_WIDTH
    offset = int(camera_x * parallax)
    for i in range(len(shimmers)):
        st = states[i]
        if st[_SDI_STATE] == _SS_DARK:
            continue
        wx, wy, _, direction, _, _ = shimmers[i]
        sx = wx + st[_SDI_STEPS] * direction - offset
        if 0 <= sx < sw:
            renderer.draw_pixel(sx, wy)


class VacationBeachScene(VacationScene):
    SCENE_NAME     = 'vacation_beach'
    ENTRY_X        = 110
    ENJOY_DURATION = 750.0
    GRACE_DURATION = 120.0
    STAT_ACCRUAL   = {'serenity': 8.0, 'fulfillment': 8.0}

    def __init__(self, context, renderer, input):
        super().__init__(context, renderer, input)
        self.sky = SkyRenderer()
        self._bg_wave_st   = _make_wave_states(_BG_WAVE_CHUNKS, 4)
        self._mg_small_st  = _make_wave_states(_MG_WAVE_SMALL,  4)
        self._mg_large_st  = _make_wave_states(_MG_WAVE_LARGE,  8)
        self._fg_wave_st   = _make_wave_states(_FG_WAVE_CHUNKS, 8)
        self._bg_shimmer_st = _make_shimmer_states(_BG_SHIMMERS)
        self._mg_shimmer_st = _make_shimmer_states(_MG_SHIMMERS)

    def setup_scene(self):
        self.environment = Environment(world_width=_WORLD_WIDTH)
        self.context.scene_x_min = 100
        self.context.scene_x_max = _WORLD_WIDTH - 10
        self.character = CharacterEntity(self.ENTRY_X, _GROUND_Y, context=self.context)

    def on_enter(self):
        env_settings = getattr(self.context, 'environment', {})
        sky_settings = dict(env_settings)
        sky_settings['weather'] = 'Clear'
        self.sky.configure(
            sky_settings,
            world_width=self.environment.world_width,
            seed=self.context.pet_seed
        )
        self.sky._render_rect = (0, 0, config.DISPLAY_WIDTH, _SAND_HORIZON_Y - 1)
        self.sky.add_to_environment(self.environment, LAYER_BACKGROUND)
        self.environment.add_custom_draw(LAYER_BACKGROUND, self._draw_background)
        self.environment.add_custom_draw(LAYER_MIDGROUND, self._draw_midground)
        self.environment.add_custom_draw(LAYER_FOREGROUND, self._draw_foreground)

    def on_exit(self):
        self.sky.remove_from_environment(self.environment, LAYER_BACKGROUND)

    def on_update(self, dt):
        env = self.context.environment
        self.sky.set_time(env.get('time_hours', 12), env.get('time_minutes', 0))
        self.sky.update(dt)
        self.character.update(dt)
        self.environment.update(dt)
        _tick_wave_group(dt, _BG_WAVE_CHUNKS,  self._bg_wave_st,  4)
        _tick_wave_group(dt, _MG_WAVE_SMALL,   self._mg_small_st, 4)
        _tick_wave_group(dt, _MG_WAVE_LARGE,   self._mg_large_st, 8)
        _tick_wave_group(dt, _FG_WAVE_CHUNKS,  self._fg_wave_st,  8)
        _tick_shimmers(dt, _BG_SHIMMERS, self._bg_shimmer_st)
        _tick_shimmers(dt, _MG_SHIMMERS, self._mg_shimmer_st)
        self._tick_vacation(dt)

    # ------------------------------------------------------------------
    # Draw passes
    # ------------------------------------------------------------------

    def _draw_background(self, renderer, camera_x, parallax):
        offset = int(camera_x * parallax)
        sw = config.DISPLAY_WIDTH
        hill_sx = _HILL_WORLD_X - offset

        # Water horizon: left edge to left side of hill
        water_right = max(0, min(sw, hill_sx))
        if water_right > 0:
            renderer.draw_line(0, _WATER_HORIZON_Y, water_right - 1, _WATER_HORIZON_Y, color=1)

        # Sand horizon: right side of hill to right edge
        sand_left = max(0, min(sw, hill_sx + _HILL_W))
        if sand_left < sw:
            renderer.draw_line(sand_left, _SAND_HORIZON_Y, sw - 1, _SAND_HORIZON_Y, color=1)

        # Hill, mountain, trees
        if hill_sx + _HILL_W >= 0 and hill_sx < sw:
            renderer.draw_sprite_obj(BEACH_HILL, hill_sx, _HILL_Y)

        mtn_sx = _MTN_WORLD_X - offset
        if mtn_sx + _MTN_W >= 0 and mtn_sx < sw:
            renderer.draw_sprite_obj(BEACH_MOUNTAIN, mtn_sx, _MTN_Y)

        tree_sx = _TREES_WORLD_X - offset
        if tree_sx + _TREE_W >= 0 and tree_sx < sw:
            renderer.draw_sprite_obj(BEACH_TREES, tree_sx, _TREES_Y)

        _draw_shimmers(renderer, camera_x, parallax, _BG_SHIMMERS, self._bg_shimmer_st)
        _draw_wave_group(renderer, camera_x, _BG_WAVE_CHUNKS,
                         self._bg_wave_st, WAVE_CHUNKS2, _WC2_W, 4, _WAVE_TRAVEL_BG)

    def _draw_midground(self, renderer, camera_x, parallax):
        offset = int(camera_x * parallax)
        sw = config.DISPLAY_WIDTH

        # Sand texture clusters
        for wx, wy in _SAND_MG_CLUSTERS:
            sx = wx - offset
            if 0 <= sx < sw:
                renderer.draw_pixel(sx, wy)

        _draw_shimmers(renderer, camera_x, parallax, _MG_SHIMMERS, self._mg_shimmer_st)
        _draw_wave_group(renderer, camera_x, _MG_WAVE_SMALL,
                         self._mg_small_st, WAVE_CHUNKS2, _WC2_W, 4, _WAVE_TRAVEL_MG_SM)
        _draw_wave_group(renderer, camera_x, _MG_WAVE_LARGE,
                         self._mg_large_st, WAVE_CHUNKS,  _WC_W,  8, _WAVE_TRAVEL_MG_LG)

    def _draw_foreground(self, renderer, camera_x, parallax):
        offset = int(camera_x * parallax)
        sw = config.DISPLAY_WIDTH

        # Sand texture clusters
        for wx, wy in _SAND_FG_CLUSTERS:
            sx = wx - offset
            if 0 <= sx < sw:
                renderer.draw_pixel(sx, wy)

        _draw_wave_group(renderer, camera_x, _FG_WAVE_CHUNKS,
                         self._fg_wave_st, WAVE_CHUNKS, _WC_W, 8, _WAVE_TRAVEL_FG)
