"""
Prowl - platformer minigame
Character controller: walk, jump, solid blocks, one-way platforms, camera scrolling.
"""
from scene import Scene
from sprite_transform import mirror_sprite_h
from assets.minigame_character import (
    PLATFORMER_CAT_RUN,
    PLATFORMER_CAT_SIT,
    PLATFORMER_CAT_JUMP,
)

# Physics
GRAVITY   = 500
JUMP_VEL  = -185
RUN_SPEED = 85

# Cat logical hitbox (centered on self.x / self.feet_y)
CAT_HALF_W = 6
CAT_H      = 12

# Terrain tile sizes
BLOCK_W = 8
BLOCK_H = 8
PLAT_H  = 4

# World dimensions
WORLD_W  = 400
GROUND_Y = 64   # hard-floor fallback; also == world bottom

# Camera scroll thresholds (screen pixels)
LEFT_SCROLL_PX  = 57   # ~45% of 128
RIGHT_SCROLL_PX = 83   # ~65% of 128
TOP_SCROLL_PX   = 22   # ~35% of 64
BOT_SCROLL_PX   = 42   # ~65% of 64

# Camera speed and bounds
CAM_LERP  = 5.0    # lerp factor (higher = snappier follow)
CAM_X_MIN = 0
CAM_X_MAX = WORLD_W - 128   # 272
CAM_Y_MIN = -128             # max upward scroll
CAM_Y_MAX = 0                # floor stays at screen bottom; never scroll down past start

# Animation
IDLE_FPS       = 6
RUN_FPS        = 10
JUMP_PEAK_RANGE = 70


def _make_level():
    """Build and return (solid_blocks, platforms) for the test level."""
    solid = []

    # Full-width bottom row
    x = 0
    while x < WORLD_W:
        solid.append((x, 56))
        x += BLOCK_W

    # Elevated solid group A — right of start
    for i in range(8):
        solid.append((56 + i * BLOCK_W, 20))

    # Elevated solid group B — further right
    for i in range(6):
        solid.append((240 + i * BLOCK_W, 28))

    platforms = (
        (8,   28, 32),   # Left side, near start (moved up 16px)
        (148, 36, 32),   # Mid-level
        (192, 20, 32),   # Mid-high
        (244,  4, 24),   # Near top of screen
        (272, -16, 32),  # Above screen top — requires scrolling up to reach
        (320, 36, 32),   # Far right
    )

    return tuple(solid), platforms


# Build once at import time; freed when scene module is unloaded
SOLID_BLOCKS, PLATFORMS = _make_level()


def _precompute_frames(sprite):
    """Return (right_frames, left_frames) as lists of bytearrays."""
    w, h = sprite["width"], sprite["height"]
    right = [bytearray(f) for f in sprite["frames"]]
    left  = [mirror_sprite_h(f, w, h) for f in sprite["frames"]]
    return right, left


class PlatformerScene(Scene):

    def enter(self):
        # Precompute mirrored frames — no per-frame allocation
        self._run_r,  self._run_l  = _precompute_frames(PLATFORMER_CAT_RUN)
        self._sit_r,  self._sit_l  = _precompute_frames(PLATFORMER_CAT_SIT)
        self._jump_r, self._jump_l = _precompute_frames(PLATFORMER_CAT_JUMP)

        # self.x = hitbox centre x;  self.feet_y = hitbox bottom
        self.x        = 20.0
        self.feet_y   = 56.0
        self.vx       = 0.0
        self.vy       = 0.0
        self.on_ground    = True
        self.just_landed  = False
        self.facing_right = True

        self._on_platform   = -1  # platform index cat stands on  (-1 = solid/none)
        self._drop_platform = -1  # platform index being dropped through

        self.anim_timer = 0.0
        self.anim_frame = 0

        # Camera: world coord of top-left of screen
        # camera_y=0 → floor (y=56) sits near the bottom of the screen
        self.camera_x      = 0.0
        self.camera_y      = 0.0
        self.target_cam_x  = 0.0
        self.target_cam_y  = 0.0

    def exit(self):
        self._run_r = self._run_l = None
        self._sit_r = self._sit_l = None
        self._jump_r = self._jump_l = None

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------

    def update(self, dt):
        self.just_landed = False

        # Walk-off-edge detection: if nothing beneath feet, start falling
        if self.on_ground and not self._is_supported():
            self.on_ground    = False
            self._on_platform = -1

        # Horizontal movement + collision
        self.x += self.vx * dt
        if self.x < CAT_HALF_W:
            self.x = float(CAT_HALF_W)
        elif self.x > WORLD_W - CAT_HALF_W:
            self.x = float(WORLD_W - CAT_HALF_W)
        self._resolve_x()

        # Vertical physics + collision
        if not self.on_ground:
            self.vy += GRAVITY * dt
            prev_feet = self.feet_y
            self.feet_y += self.vy * dt
            self._resolve_y(prev_feet)

        # Clear drop-through once fully below the platform
        if self._drop_platform >= 0:
            _, py, _ = PLATFORMS[self._drop_platform]
            if self.feet_y > py + PLAT_H:
                self._drop_platform = -1

        # Ground animation
        if self.on_ground:
            fps = RUN_FPS if abs(self.vx) > 1 else IDLE_FPS
            self.anim_timer += dt
            if self.anim_timer >= 1.0 / fps:
                self.anim_timer -= 1.0 / fps
                n = (len(PLATFORMER_CAT_RUN["frames"]) if abs(self.vx) > 1
                     else len(PLATFORMER_CAT_SIT["frames"]))
                self.anim_frame = (self.anim_frame + 1) % n

        self._update_camera(dt)

    def _is_supported(self):
        fy = int(self.feet_y)
        cl = int(self.x) - CAT_HALF_W
        cr = int(self.x) + CAT_HALF_W

        for bx, by in SOLID_BLOCKS:
            if by == fy and cl < bx + BLOCK_W and cr > bx:
                return True

        if self._on_platform >= 0:
            px, py, pw = PLATFORMS[self._on_platform]
            if py == fy and cl < px + pw and cr > px:
                return True

        return fy >= GROUND_Y

    def _resolve_x(self):
        cl = int(self.x) - CAT_HALF_W
        cr = int(self.x) + CAT_HALF_W
        ct = int(self.feet_y) - CAT_H
        cb = int(self.feet_y)

        for bx, by in SOLID_BLOCKS:
            br = bx + BLOCK_W
            bb = by + BLOCK_H
            if ct >= bb or cb <= by:
                continue
            if cl >= br or cr <= bx:
                continue
            if self.vx > 0:
                self.x = float(bx - CAT_HALF_W)
            elif self.vx < 0:
                self.x = float(br + CAT_HALF_W)
            else:
                if cr - bx < br - cl:
                    self.x = float(bx - CAT_HALF_W)
                else:
                    self.x = float(br + CAT_HALF_W)
            self.vx = 0.0
            cl = int(self.x) - CAT_HALF_W
            cr = int(self.x) + CAT_HALF_W

    def _resolve_y(self, prev_feet):
        cl = int(self.x) - CAT_HALF_W
        cr = int(self.x) + CAT_HALF_W

        if self.vy >= 0:  # descending
            for bx, by in SOLID_BLOCKS:
                if cl >= bx + BLOCK_W or cr <= bx:
                    continue
                if prev_feet <= by <= self.feet_y:
                    self.feet_y   = float(by)
                    self.vy       = 0.0
                    self.on_ground    = True
                    self._on_platform = -1
                    self.just_landed  = True
                    return

            for i, (px, py, pw) in enumerate(PLATFORMS):
                if i == self._drop_platform:
                    continue
                if cl >= px + pw or cr <= px:
                    continue
                if prev_feet <= py <= self.feet_y:
                    self.feet_y   = float(py)
                    self.vy       = 0.0
                    self.on_ground    = True
                    self._on_platform = i
                    self.just_landed  = True
                    return

            if self.feet_y >= GROUND_Y:
                self.feet_y   = float(GROUND_Y)
                self.vy       = 0.0
                self.on_ground    = True
                self._on_platform = -1
                self.just_landed  = True

        else:  # ascending — solid block ceilings only
            prev_head = prev_feet - CAT_H
            curr_head = self.feet_y - CAT_H
            for bx, by in SOLID_BLOCKS:
                bb = by + BLOCK_H
                if cl >= bx + BLOCK_W or cr <= bx:
                    continue
                if prev_head >= bb > curr_head:
                    self.feet_y = float(bb + CAT_H)
                    self.vy     = 0.0
                    break

    def _update_camera(self, dt):
        cat_sx = self.x      - self.camera_x
        cat_sy = self.feet_y - self.camera_y

        # Horizontal: direction-aware deadband
        if self.facing_right and cat_sx > RIGHT_SCROLL_PX:
            self.target_cam_x = self.x - RIGHT_SCROLL_PX
        elif not self.facing_right and cat_sx < LEFT_SCROLL_PX:
            self.target_cam_x = self.x - LEFT_SCROLL_PX

        # Vertical: scroll up when cat is high; drift back to 0 when grounded
        if cat_sy < TOP_SCROLL_PX:
            self.target_cam_y = self.feet_y - TOP_SCROLL_PX
        elif cat_sy > BOT_SCROLL_PX:
            self.target_cam_y = self.feet_y - BOT_SCROLL_PX

        # Clamp targets to world bounds
        if self.target_cam_x < CAM_X_MIN:
            self.target_cam_x = float(CAM_X_MIN)
        elif self.target_cam_x > CAM_X_MAX:
            self.target_cam_x = float(CAM_X_MAX)
        if self.target_cam_y < CAM_Y_MIN:
            self.target_cam_y = float(CAM_Y_MIN)
        elif self.target_cam_y > CAM_Y_MAX:
            self.target_cam_y = float(CAM_Y_MAX)

        # Smooth lerp toward target
        self.camera_x += (self.target_cam_x - self.camera_x) * CAM_LERP * dt
        self.camera_y += (self.target_cam_y - self.camera_y) * CAM_LERP * dt

    # ------------------------------------------------------------------
    # Input
    # ------------------------------------------------------------------

    def handle_input(self):
        moving = False

        if self.input.is_pressed('left'):
            self.vx = -RUN_SPEED
            self.facing_right = False
            moving = True
        elif self.input.is_pressed('right'):
            self.vx = RUN_SPEED
            self.facing_right = True
            moving = True
        else:
            self.vx = 0.0

        if not moving and self.on_ground:
            if self.anim_frame >= len(PLATFORMER_CAT_SIT["frames"]):
                self.anim_frame = 0

        if self.input.was_just_pressed('a') and self.on_ground and not self.just_landed:
            self.vy = JUMP_VEL
            self.on_ground    = False
            self._on_platform = -1
            self.anim_frame   = 0
            self.anim_timer   = 0.0

        if (self.input.was_just_pressed('down')
                and self.on_ground
                and self._on_platform >= 0):
            self._drop_platform = self._on_platform
            self._on_platform   = -1
            self.on_ground      = False
            self.vy             = 20.0
            self.anim_frame     = 0
            self.anim_timer     = 0.0

    # ------------------------------------------------------------------
    # Draw
    # ------------------------------------------------------------------

    def _jump_frame(self):
        if self.vy < -JUMP_PEAK_RANGE:
            return 0   # rising
        if self.vy <= JUMP_PEAK_RANGE:
            return 1   # near peak
        return 2       # falling

    def draw(self):
        cam_x = int(self.camera_x)
        cam_y = int(self.camera_y)

        # Terrain — cull anything fully off-screen
        for bx, by in SOLID_BLOCKS:
            sx = bx - cam_x
            sy = by - cam_y
            if -BLOCK_W < sx < 128 and -BLOCK_H < sy < 64:
                self.renderer.draw_rect(sx, sy, BLOCK_W, BLOCK_H, filled=True, color=1)

        for px, py, pw in PLATFORMS:
            sx = px - cam_x
            sy = py - cam_y
            if -pw < sx < 128 and -PLAT_H < sy < 64:
                self.renderer.draw_rect(sx, sy, pw, PLAT_H, filled=True, color=1)

        # Cat sprite
        if not self.on_ground or self.just_landed:
            frames_r, frames_l = self._jump_r, self._jump_l
            sprite = PLATFORMER_CAT_JUMP
            frame = self._jump_frame() if not self.on_ground else 2
        elif abs(self.vx) > 1:
            frames_r, frames_l = self._run_r, self._run_l
            sprite = PLATFORMER_CAT_RUN
            frame = self.anim_frame % len(frames_r)
        else:
            frames_r, frames_l = self._sit_r, self._sit_l
            sprite = PLATFORMER_CAT_SIT
            frame = self.anim_frame % len(frames_r)

        data  = frames_r[frame] if self.facing_right else frames_l[frame]
        draw_x = int(self.x) - sprite["width"] // 2 - cam_x
        draw_y = int(self.feet_y) - sprite["height"] - cam_y

        self.renderer.draw_sprite(data, sprite["width"], sprite["height"], draw_x, draw_y)
