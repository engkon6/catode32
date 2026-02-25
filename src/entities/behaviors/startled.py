"""Startled behavior - sudden fright reaction."""

import random
from entities.behaviors.base import BaseBehavior


class StartledBehavior(BaseBehavior):
    """Pet is suddenly startled by something.

    Triggered randomly, with lower courage and resilience making it
    more likely. After the shock wears off, the pet either retreats
    to idle or goes to investigate, depending on courage and curiosity.

    Phases:
    1. startled - Frozen in shock (5-10 seconds)
    2. recovering - Brief wind-down before transitioning
    """

    NAME = "startled"

    PRIORITY = 35

    @classmethod
    def can_trigger(cls, context):
        # Base ~8% chance per idle cycle, reduced by courage and resilience
        p = 0.08 * (1 - context.courage / 200) * (1 - context.resilience / 200)
        return random.random() < p

    STAT_EFFECTS = {"energy": -1.0, "comfort": -1.5, "curiosity": 0.5}
    COMPLETION_BONUS = {"curiosity": 5, "comfort": -5, "energy": -5}

    def __init__(self, character):
        super().__init__(character)

        self.startled_duration = random.uniform(5.0, 10.0)
        self.recover_duration = 1.0

    def start(self, on_complete=None):
        if self._active:
            return
        super().start(on_complete)
        self.startled_duration = random.uniform(5.0, 10.0)
        self._phase = "startled"
        self._character.set_pose("sitting.forward.shocked")

    def update(self, dt):
        if not self._active:
            return

        self._phase_timer += dt

        if self._phase == "startled":
            self._progress = min(1.0, self._phase_timer / self.startled_duration)
            if self._phase_timer >= self.startled_duration:
                self._phase = "recovering"
                self._phase_timer = 0.0
                self._character.set_pose("sitting.forward.neutral")

        elif self._phase == "recovering":
            if self._phase_timer >= self.recover_duration:
                self.stop(completed=True)

    def next(self, context):
        # Higher courage and curiosity both push toward investigating
        p_investigate = (context.curiosity + context.courage) / 200.0
        if random.random() < p_investigate:
            from entities.behaviors.investigating import InvestigatingBehavior
            return InvestigatingBehavior
        return None  # -> idle
