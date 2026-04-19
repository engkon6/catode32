"""
Prowl - platformer minigame
Character controller: walk, jump, solid blocks, one-way platforms.
"""
from scene import Scene
from sprite_transform import mirror_sprite_h
from assets.minigame_character import (
    PLATFORMER_CAT_RUN,
    PLATFORMER_CAT_SIT,
    PLATFORMER_CAT_JUMP,
)

# Physics
GRAVITY   = 500    # px/s²
JUMP_VEL  = -185   # px/s (peak ~34px)
RUN_SPEED = 85     # px/s

# Cat logical hitbox (centered on self.x / self.feet_y)
CAT_HALF_W = 6     # half of 12px width
CAT_H      = 12    # height

# Terrain tile sizes
BLOCK_W = 8
BLOCK_H = 8
PLAT_H  = 4

# Hard floor safety fallback
GROUND_Y = 64

# Solid blocks: (x, y) — each BLOCK_W × BLOCK_H, collide from all sides
SOLID_BLOCKS = (
    # Bottom row
    (0,56),(8,56),(16,56),(24,56),(32,56),(40,56),(48,56),(56,56),
    (64,56),(72,56),(80,56),(88,56),(96,56),(104,56),(112,56),(120,56),
    # Elevated right group
    (56,36),(64,36),(72,36),(80,36),(88,36),(96,36),(104,36),(112,36),
)

# Platforms: (x, y, width) — PLAT_H tall, land on top only; jump through from below
PLATFORMS = (
    (8, 44, 32),   # Left side, 4 blocks wide
)

# Jump animation velocity thresholds
JUMP_PEAK_RANGE = 70

# Animation rates
IDLE_FPS = 6
RUN_FPS  = 10


def _precompute_frames(sprite):
    """Return (right_frames, left_frames) as lists of bytearrays."""
    w, h = sprite["width"], sprite["height"]
    right = [bytearray(f) for f in sprite["frames"]]
    left  = [mirror_sprite_h(f, w, h) for f in sprite["frames"]]
    return right, left


class PlatformerScene(Scene):

    def enter(self):
        # Precompute mirrored frames once — no per-frame allocation
        self._run_r,  self._run_l  = _precompute_frames(PLATFORMER_CAT_RUN)
        self._sit_r,  self._sit_l  = _precompute_frames(PLATFORMER_CAT_SIT)
        self._jump_r, self._jump_l = _precompute_frames(PLATFORMER_CAT_JUMP)

        # self.x = center x of hitbox; self.feet_y = bottom of hitbox
        self.x = 20.0
        self.feet_y = 56.0    # on top of bottom block row
        self.vx = 0.0
        self.vy = 0.0
        self.on_ground = True
        self.just_landed = False
        self.facing_right = True

        self._on_platform   = -1  # index of platform cat stands on (-1 = solid/none)
        self._drop_platform = -1  # index of platform being dropped through (-1 = none)

        self.anim_timer = 0.0
        self.anim_frame = 0

    def exit(self):
        self._run_r = self._run_l = None
        self._sit_r = self._sit_l = None
        self._jump_r = self._jump_l = None

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------

    def update(self, dt):
        self.just_landed = False

        # Detect walking off an edge: if nothing is beneath feet, start falling
        if self.on_ground and not self._is_supported():
            self.on_ground = False
            self._on_platform = -1

        # Horizontal movement + collision
        self.x += self.vx * dt
        if self.x < CAT_HALF_W:
            self.x = float(CAT_HALF_W)
        elif self.x > 128 - CAT_HALF_W:
            self.x = float(128 - CAT_HALF_W)
        self._resolve_x()

        # Vertical physics + collision (only while airborne)
        if not self.on_ground:
            self.vy += GRAVITY * dt
            prev_feet = self.feet_y
            self.feet_y += self.vy * dt
            self._resolve_y(prev_feet)

        # Clear drop-through flag once cat's feet are below the platform
        if self._drop_platform >= 0:
            _, py, _ = PLATFORMS[self._drop_platform]
            if self.feet_y > py + PLAT_H:
                self._drop_platform = -1

        # Advance ground animation
        if self.on_ground:
            fps = RUN_FPS if abs(self.vx) > 1 else IDLE_FPS
            self.anim_timer += dt
            if self.anim_timer >= 1.0 / fps:
                self.anim_timer -= 1.0 / fps
                n = (len(PLATFORMER_CAT_RUN["frames"]) if abs(self.vx) > 1
                     else len(PLATFORMER_CAT_SIT["frames"]))
                self.anim_frame = (self.anim_frame + 1) % n

    def _is_supported(self):
        """True if there is solid ground or a platform directly under the cat's feet."""
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
        """Push cat out of solid blocks horizontally."""
        cl = int(self.x) - CAT_HALF_W
        cr = int(self.x) + CAT_HALF_W
        ct = int(self.feet_y) - CAT_H
        cb = int(self.feet_y)

        for bx, by in SOLID_BLOCKS:
            br = bx + BLOCK_W
            bb = by + BLOCK_H
            if ct >= bb or cb <= by:   # no vertical overlap
                continue
            if cl >= br or cr <= bx:   # no horizontal overlap
                continue
            # Push cat to whichever side it came from
            if self.vx > 0:
                self.x = float(bx - CAT_HALF_W)
            elif self.vx < 0:
                self.x = float(br + CAT_HALF_W)
            else:
                # Stationary but inside a block — resolve to nearest edge
                if cr - bx < br - cl:
                    self.x = float(bx - CAT_HALF_W)
                else:
                    self.x = float(br + CAT_HALF_W)
            self.vx = 0.0
            # Recalculate bounds for subsequent blocks in this pass
            cl = int(self.x) - CAT_HALF_W
            cr = int(self.x) + CAT_HALF_W

    def _resolve_y(self, prev_feet):
        """Resolve vertical collisions against solid blocks and platforms."""
        cl = int(self.x) - CAT_HALF_W
        cr = int(self.x) + CAT_HALF_W

        if self.vy >= 0:  # descending
            # Solid block tops
            for bx, by in SOLID_BLOCKS:
                if cl >= bx + BLOCK_W or cr <= bx:
                    continue
                if prev_feet <= by <= self.feet_y:
                    self.feet_y = float(by)
                    self.vy = 0.0
                    self.on_ground = True
                    self._on_platform = -1
                    self.just_landed = True
                    return

            # Platform tops (one-way; skipped when dropping through)
            for i, (px, py, pw) in enumerate(PLATFORMS):
                if i == self._drop_platform:
                    continue
                if cl >= px + pw or cr <= px:
                    continue
                if prev_feet <= py <= self.feet_y:
                    self.feet_y = float(py)
                    self.vy = 0.0
                    self.on_ground = True
                    self._on_platform = i
                    self.just_landed = True
                    return

            # Hard floor fallback
            if self.feet_y >= GROUND_Y:
                self.feet_y = float(GROUND_Y)
                self.vy = 0.0
                self.on_ground = True
                self._on_platform = -1
                self.just_landed = True

        else:  # ascending — check solid block ceilings
            prev_head = prev_feet - CAT_H
            curr_head = self.feet_y - CAT_H
            for bx, by in SOLID_BLOCKS:
                bb = by + BLOCK_H
                if cl >= bx + BLOCK_W or cr <= bx:
                    continue
                if prev_head >= bb > curr_head:
                    self.feet_y = float(bb + CAT_H)
                    self.vy = 0.0
                    break

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
            self.on_ground = False
            self._on_platform = -1
            self.anim_frame = 0
            self.anim_timer = 0.0

        # Drop through platform on down press
        if (self.input.was_just_pressed('down')
                and self.on_ground
                and self._on_platform >= 0):
            self._drop_platform = self._on_platform
            self._on_platform = -1
            self.on_ground = False
            self.vy = 20.0   # small nudge to begin descent
            self.anim_frame = 0
            self.anim_timer = 0.0

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
        # Terrain
        for bx, by in SOLID_BLOCKS:
            self.renderer.draw_rect(bx, by, BLOCK_W, BLOCK_H, filled=True, color=1)

        for px, py, pw in PLATFORMS:
            self.renderer.draw_rect(px, py, pw, PLAT_H, filled=True, color=1)

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

        data = frames_r[frame] if self.facing_right else frames_l[frame]
        draw_x = int(self.x) - sprite["width"] // 2
        draw_y = int(self.feet_y) - sprite["height"]

        self.renderer.draw_sprite(data, sprite["width"], sprite["height"], draw_x, draw_y)
