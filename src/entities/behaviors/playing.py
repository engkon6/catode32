"""Playing behavior for energetic fun."""

import math
import random
from entities.behaviors.base import BaseBehavior
from ui import draw_bubble
from assets.items import YARN_BALL


# Variant configurations
VARIANTS = {
    "toy": {
        "bubble": "exclaim",
        "stats": {"playfulness": -8, "energy": -3, "focus": -1},
    },
    "throw_stick": {
        "bubble": "star",
        "stats": {"playfulness": -6, "energy": -5, "focus": -1},
    },
    "ball": {
        "stats": {"playfulness": -8, "energy": -4, "focus": -1},
        "passes": 4,  # number of half-passes (direction changes) before pouncing
    },
    "laser": {
        "stats": {"playfulness": -6, "energy": -3, "focus": -1},
    },
}

# Shared pounce constants (reusable across play variants)
POUNCE_SLIDE_SPEED = 28       # pixels per second during the leap slide
POUNCE_SLIDE_DURATION = 0.9   # seconds the slide lasts

# Ball variant constants
BALL_ROLL_SPEED = 25           # pixels per second
BALL_ROLL_RANGE = 28           # max horizontal offset left/right from cat center
BALL_Y_OFFSET = 8              # pixels above cat's y anchor
BALL_CATCH_DURATION = 1.5      # seconds of celebration after catching

# Laser variant constants
LASER_WOBBLE_AMPLITUDE = 8     # pixels of auto-oscillation around user-controlled position
LASER_WOBBLE_SPEED = 2.5       # radians per second for the wobble sine wave
LASER_USER_SPEED = 50          # pixels per second when player holds left/right
LASER_USER_RANGE = 45          # max offset from cat center for player-controlled position
LASER_Y_OFFSET = 1             # pixels above cat's y anchor
LASER_CATCH_DURATION = 1.5     # seconds of celebration after the final pounce
LASER_RECOVER_DURATION = 0.8   # seconds the cat sits happy between pounces
LASER_POUNCE_DELAY_MIN = 2.0   # minimum seconds before each pounce
LASER_POUNCE_DELAY_MAX = 5.0   # maximum seconds before each pounce
LASER_POUNCE_COUNT_MIN = 2     # fewest pounces per session
LASER_POUNCE_COUNT_MAX = 4     # most pounces per session
LASER_DOT_RADIUS = 2           # radius in pixels → 5×5 filled circle
LASER_LINE_TOP_Y = -64         # y coordinate of the off-screen line origin


def _compute_eye_frame(ball_offset_x, mirror):
    """Map ball horizontal offset from cat to eye frame index 0-4.

    For the CHAR_EYES_FRONT_LOOKAROUND sprite (non-mirrored):
      Frame 0 = looking right, Frame 2 = center, Frame 4 = looking left.
    When mirror=True the sprite is flipped, so we invert the mapping so the
    rendered gaze direction still follows the ball on screen.

    Args:
        ball_offset_x: Ball x minus cat x (positive = ball to the right).
        mirror: Whether the character sprite is currently mirrored.

    Returns:
        Integer frame index 0-4.
    """
    t = max(-1.0, min(1.0, ball_offset_x / BALL_ROLL_RANGE))
    # Non-mirrored: right(t=1)→frame 0, center→frame 2, left(t=-1)→frame 4
    # Mirrored: sprite is flipped, so invert t so gaze matches screen position
    if mirror:
        t = -t
    return max(0, min(4, round(2 - t * 2)))


class PlayingBehavior(BaseBehavior):
    """Pet plays energetically.

    Default variants (toy / throw_stick) phases:
    1. excited  - Pet reacts with a speech bubble
    2. playing  - Active play animation
    3. tired    - Pet winds down

    Ball variant phases:
    1. watching  - Yarn ball rolls back and forth; cat tracks it with its eyes
    2. pouncing  - Cat leaps toward the stopped ball (pose + forward slide)
    3. catching  - Brief celebration after landing
    """

    NAME = "playing"

    def get_completion_bonus(self, context):
        bonus = dict(VARIANTS[self._variant].get("stats", {}))
        return self.apply_location_bonus(context, bonus)

    def apply_location_bonus(self, context, bonus):
        if context.last_main_scene in ('outside', 'treehouse', 'inside'):
            # Better play locations: reduce energy and playfulness costs by 25%
            for stat in ('energy', 'playfulness'):
                if stat in bonus:
                    bonus[stat] = bonus[stat] * 0.75
            bonus['fitness'] = bonus.get('fitness', 0) + 0.01
        return bonus

    def __init__(self, character):
        super().__init__(character)

        # Default variant timing
        self.excited_duration = random.uniform(1.0, 3.0)
        self.play_duration = random.uniform(5.0, 20.0)
        self.tired_duration = random.uniform(1.0, 10.0)

        # Active variant
        self._variant = "toy"
        self._bubble = None

        # Ball variant state
        self._ball_offset_x = 0.0   # horizontal offset from character.x (world coords)
        self._ball_rotation = 0.0   # current rotation in degrees
        self._ball_direction = 1    # 1 = rolling right, -1 = rolling left
        self._ball_passes_left = 4

        # Laser variant state
        self._laser_offset_x = 0.0    # current offset from character.x (wobble + user)
        self._laser_user_x = 0.0      # player-controlled base position
        self._laser_wobble_phase = 0.0 # phase of the auto-oscillation sine wave
        self._laser_pounce_timer = 0.0 # countdown to next pounce (set each watching phase)
        self._laser_pounces_total = 3  # total pounces this session (randomised at start)
        self._laser_pounces_done = 0   # pounces completed so far
        self._laser_line_x_top = 64    # fixed screen-space x for the off-screen line end

        # Shared pounce state
        self._pounce_direction = 1

        # Eye frame override — exposed as a property and read by CharacterEntity.draw()
        self._eye_frame_override = None

    @property
    def eye_frame_override(self):
        return self._eye_frame_override

    # ------------------------------------------------------------------
    # Scene helpers
    # ------------------------------------------------------------------

    def _get_scene_bounds(self):
        context = self._character.context
        x_min = getattr(context, 'scene_x_min', 10) + 15
        x_max = getattr(context, 'scene_x_max', 118) - 15
        return x_min, x_max

    # ------------------------------------------------------------------
    # Start / stop
    # ------------------------------------------------------------------

    def start(self, variant=None, on_complete=None):
        if self._active:
            return
        super().start(on_complete)
        self._variant = variant if variant in VARIANTS else "toy"
        self._eye_frame_override = None

        if self._variant == "ball":
            self._start_ball()
        elif self._variant == "laser":
            self._start_laser()
        else:
            config = VARIANTS[self._variant]
            self._bubble = config.get("bubble")
            self._phase = "excited"
            self._character.set_pose("sitting.side.happy")

    def _start_laser(self):
        """Initialise the laser variant state and enter the watching phase."""
        self._laser_user_x = 0.0
        self._laser_wobble_phase = 0.0
        self._laser_offset_x = 0.0
        self._laser_pounces_total = random.randint(LASER_POUNCE_COUNT_MIN, LASER_POUNCE_COUNT_MAX)
        self._laser_pounces_done = 0
        self._laser_pounce_timer = random.uniform(LASER_POUNCE_DELAY_MIN, LASER_POUNCE_DELAY_MAX)
        self._laser_line_x_top = random.randint(20, 108)
        self._eye_frame_override = _compute_eye_frame(
            self._laser_offset_x, self._character.mirror
        )
        self._phase = "watching"
        self._character.set_pose("playful.forward.wowed")

    def _start_ball(self):
        """Initialise the ball variant state and enter the watching phase."""
        config = VARIANTS["ball"]
        self._ball_passes_left = config.get("passes", 4)
        self._ball_offset_x = BALL_ROLL_RANGE   # start on the right side
        self._ball_rotation = 0.0
        self._ball_direction = -1               # roll left first
        self._eye_frame_override = _compute_eye_frame(
            self._ball_offset_x, self._character.mirror
        )
        self._phase = "watching"
        self._character.set_pose("playful.forward.wowed")

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------

    def update(self, dt):
        if not self._active:
            return
        self._phase_timer += dt

        if self._variant == "ball":
            self._update_ball(dt)
        elif self._variant == "laser":
            self._update_laser(dt)
        else:
            self._update_default(dt)

    # --- Default (toy / throw_stick) ---

    def _update_default(self, dt):
        if self._phase == "excited":
            if self._phase_timer >= self.excited_duration:
                self._phase = "playing"
                self._phase_timer = 0.0
                self._bubble = None
                self._character.set_pose("sitting_silly.side.happy")

        elif self._phase == "playing":
            self._progress = min(1.0, self._phase_timer / self.play_duration)
            if self._phase_timer >= self.play_duration:
                self._phase = "tired"
                self._phase_timer = 0.0
                self._character.set_pose("sitting.side.neutral")

        elif self._phase == "tired":
            if self._phase_timer >= self.tired_duration:
                self._character.play_bursts()
                self.stop(completed=True)

    # --- Ball variant ---

    def _update_ball(self, dt):
        if self._phase == "watching":
            self._update_ball_rolling(dt)
        elif self._phase == "pouncing":
            self._update_pounce(dt)
        elif self._phase == "catching":
            if self._phase_timer >= BALL_CATCH_DURATION:
                self._progress = 1.0
                self._character.play_bursts()
                self.stop(completed=True)

    def _update_ball_rolling(self, dt):
        """Advance the ball and update eye tracking each frame."""
        self._ball_offset_x += self._ball_direction * BALL_ROLL_SPEED * dt

        # Rotate proportional to distance rolled (d / r * 180/pi degrees)
        ball_radius = YARN_BALL["width"] / 2.0
        angle_delta = (self._ball_direction * BALL_ROLL_SPEED * dt
                       / ball_radius * (180.0 / math.pi))
        self._ball_rotation = (self._ball_rotation + angle_delta) % 360.0

        # Update eye tracking
        self._eye_frame_override = _compute_eye_frame(
            self._ball_offset_x, self._character.mirror
        )

        # Check if ball reached a boundary
        if self._ball_direction > 0 and self._ball_offset_x >= BALL_ROLL_RANGE:
            self._ball_offset_x = BALL_ROLL_RANGE
            self._ball_passes_left -= 1
            if self._ball_passes_left <= 0:
                self._begin_pounce()
            else:
                self._ball_direction = -1

        elif self._ball_direction < 0 and self._ball_offset_x <= -BALL_ROLL_RANGE:
            self._ball_offset_x = -BALL_ROLL_RANGE
            self._ball_passes_left -= 1
            if self._ball_passes_left <= 0:
                self._begin_pounce()
            else:
                self._ball_direction = 1

        # Track overall progress (watching counts as 0-90% to leave room for pounce)
        total = VARIANTS["ball"].get("passes", 4)
        done = total - self._ball_passes_left
        self._progress = min(0.9, done / total)

    # --- Laser variant ---

    def _update_laser(self, dt):
        if self._phase == "watching":
            self._update_laser_rolling(dt)
        elif self._phase == "pouncing":
            self._update_laser_pounce(dt)
        elif self._phase == "recovering":
            self._update_laser_recovering(dt)
        elif self._phase == "catching":
            if self._phase_timer >= LASER_CATCH_DURATION:
                self._progress = 1.0
                self._character.play_bursts()
                self.stop(completed=True)

    def _update_laser_rolling(self, dt):
        """Move the laser via D-pad + wobble and count down to the next pounce."""
        # Player controls the base position with left/right
        inp = getattr(self._character.context, 'input', None)
        if inp:
            if inp.is_pressed('left'):
                self._laser_user_x -= LASER_USER_SPEED * dt
            if inp.is_pressed('right'):
                self._laser_user_x += LASER_USER_SPEED * dt
            self._laser_user_x = max(-LASER_USER_RANGE, min(LASER_USER_RANGE, self._laser_user_x))

        # Auto-wobble oscillates around the user-controlled position
        self._laser_wobble_phase += LASER_WOBBLE_SPEED * dt
        self._laser_offset_x = (self._laser_user_x
                                 + LASER_WOBBLE_AMPLITUDE * math.sin(self._laser_wobble_phase))

        # Update eye tracking
        self._eye_frame_override = _compute_eye_frame(
            self._laser_offset_x, self._character.mirror
        )

        # Count down to pounce
        self._laser_pounce_timer -= dt
        if self._laser_pounce_timer <= 0:
            self._begin_laser_pounce()
            return

        self._progress = self._laser_pounces_done / self._laser_pounces_total

    def _begin_laser_pounce(self):
        """Start a pounce toward the current laser position."""
        self._laser_pounces_done += 1
        direction = 1 if self._laser_offset_x >= 0 else -1
        self._pounce_direction = direction
        self._character.mirror = direction > 0
        self._character.set_pose("leaning_forward.side.pounce")
        self._eye_frame_override = None
        self._phase = "pouncing"
        self._phase_timer = 0.0

    def _update_laser_pounce(self, dt):
        """Slide the cat toward the laser; keep the laser dot fixed on screen."""
        slide = self._pounce_direction * POUNCE_SLIDE_SPEED * dt
        self._character.x += slide
        # Compensate offset so the dot stays at the same screen position
        self._laser_offset_x -= slide

        if self._phase_timer >= POUNCE_SLIDE_DURATION:
            x_min, x_max = self._get_scene_bounds()
            self._character.x = max(x_min, min(x_max, self._character.x))
            self._phase = "recovering"
            self._phase_timer = 0.0
            self._character.set_pose("sitting_silly.side.happy")

    def _update_laser_recovering(self, dt):
        """Brief celebration pose after each pounce."""
        if self._phase_timer >= LASER_RECOVER_DURATION:
            if self._laser_pounces_done >= self._laser_pounces_total:
                self._phase = "catching"
                self._phase_timer = 0.0
            else:
                # Reset user position so the laser starts back near center
                self._laser_user_x = 0.0
                self._laser_pounce_timer = random.uniform(
                    LASER_POUNCE_DELAY_MIN, LASER_POUNCE_DELAY_MAX
                )
                self._eye_frame_override = _compute_eye_frame(
                    self._laser_offset_x, self._character.mirror
                )
                self._phase = "watching"
                self._phase_timer = 0.0
                self._character.set_pose("playful.forward.wowed")

    # ------------------------------------------------------------------
    # Shared pounce helpers — reusable for other play variants
    # ------------------------------------------------------------------

    def _begin_pounce(self, offset_x=None):
        """Transition into the pouncing phase (reusable for any play variant).

        Turns the cat to face the target's side, sets the pounce pose, and
        releases the eye-tracking override so the side-facing pose looks correct.

        Args:
            offset_x: Horizontal offset of the target from the cat. Defaults to
                       the ball's current offset when not provided.
        """
        if offset_x is None:
            offset_x = self._ball_offset_x
        self._pounce_direction = 1 if offset_x >= 0 else -1
        self._character.mirror = self._pounce_direction > 0
        self._character.set_pose("leaning_forward.side.pounce")
        self._eye_frame_override = None
        self._phase = "pouncing"
        self._phase_timer = 0.0

    def _update_pounce(self, dt):
        """Slide the cat forward during the pounce (reusable for any play variant)."""
        self._character.x += self._pounce_direction * POUNCE_SLIDE_SPEED * dt

        if self._phase_timer >= POUNCE_SLIDE_DURATION:
            x_min, x_max = self._get_scene_bounds()
            self._character.x = max(x_min, min(x_max, self._character.x))
            self._phase = "catching"
            self._phase_timer = 0.0
            self._character.set_pose("sitting_silly.side.happy")

    # ------------------------------------------------------------------
    # Draw
    # ------------------------------------------------------------------

    def draw(self, renderer, char_x, char_y, mirror=False):
        if not self._active:
            return

        if self._variant == "ball":
            self._draw_ball(renderer, char_x, char_y)
        elif self._variant == "laser":
            self._draw_laser(renderer, char_x, char_y)
        elif self._bubble and self._phase == "excited":
            progress = min(1.0, self._phase_timer / self.excited_duration)
            draw_bubble(renderer, self._bubble, char_x, char_y, progress, mirror)

    def _draw_ball(self, renderer, char_x, char_y):
        """Draw the rolling yarn ball (visible during watching and pouncing phases)."""
        if self._phase not in ("watching", "pouncing"):
            return

        hw = YARN_BALL["width"] // 2
        hh = YARN_BALL["height"] // 2
        # char_x is already the screen x (world x minus camera offset), so the
        # ball's screen x is simply char_x plus its offset from the cat.
        ball_x = char_x + int(self._ball_offset_x) - hw
        ball_y = char_y - BALL_Y_OFFSET - hh

        renderer.draw_sprite_obj(
            YARN_BALL,
            ball_x,
            ball_y,
            frame=0,
            rotate=int(self._ball_rotation),
        )

    def _draw_laser(self, renderer, char_x, char_y):
        """Draw the laser dot and beam line (always together while visible)."""
        if self._phase not in ("watching", "pouncing", "recovering"):
            return

        dot_x = char_x + int(self._laser_offset_x)
        dot_y = char_y - LASER_Y_OFFSET

        # Draw the beam line in all visible phases
        renderer.draw_line(
            self._laser_line_x_top, LASER_LINE_TOP_Y,
            dot_x, dot_y,
        )

        # Draw the 5×5 laser dot as a filled circle
        renderer.draw_circle(dot_x, dot_y, LASER_DOT_RADIUS, filled=True)
