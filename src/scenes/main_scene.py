import random
import config
from scene import Scene
from entities.character import CharacterEntity
from menu import Menu, MenuItem
from plant_system import tick_plants
from plant_renderer import register_plant_draws
from gardening_ui import PlacementMode
from assets.icons import (TOYS_ICON, HEART_ICON, HEART_BUBBLE_ICON, HAND_ICON,
                          KIBBLE_ICON, TOY_ICONS, SNACK_ICONS, FISH_ICON,
                          CHICKEN_ICON, MEAL_ICON, TREES_ICON)
from assets.items import FOOD_BOWL, TREAT_PILE
from ui import draw_bubble


class MainScene(Scene):
    """Base class for main location scenes (inside, outside, etc.).

    Handles the shared pet interaction menu, character rendering, camera
    auto-panning, and the behavior lifecycle around scene enter/exit.

    Subclasses must set SCENE_NAME and implement setup_scene(). They may
    also override the on_* hooks for scene-specific behaviour:

      setup_scene  - create self.environment + self.character, place objects
      on_enter     - add custom draws, configure sky, etc.
      on_exit      - teardown sky, etc.
      on_update    - update sky/entities; must call self.character.update(dt)
      on_pre_draw  - any setup needed before environment.draw()
      on_post_draw - any drawing after the character (e.g. renderer.invert)
    """

    SCENE_NAME = None  # override in subclass
    ENTRY_X = 64      # character x position on scene entry (cached or fresh)

    def __init__(self, context, renderer, input):
        super().__init__(context, renderer, input)
        self.menu_active = False
        self.environment = None
        self.character = None
        self.menu = None
        self._placement = PlacementMode()

    def load(self):
        super().load()
        self.setup_scene()
        self.menu = Menu(self.renderer, self.input)

    def setup_scene(self):
        """Override to create self.environment, self.character, and place objects."""
        pass

    def unload(self):
        super().unload()

    def enter(self):
        if self.SCENE_NAME:
            self.context.last_main_scene = self.SCENE_NAME
        if self.character:
            self.character.x = self.ENTRY_X

        # Offset cats to opposite sides when a visit is active
        if self.context.visit is not None:
            if self.context.visit.get('role') == 'inviter':
                self.character.x = self.ENTRY_X - 20
            else:
                self.character.x = self.ENTRY_X + 20

        vm = getattr(self.context, 'visit_manager', None)
        if vm:
            vm.on_scene_enter(self)

        self.on_enter()

        if getattr(self, 'PLANT_SURFACES', None):
            register_plant_draws(self)

        # Handle pending plant move arriving at this scene.
        move = getattr(self.context, 'pending_gardening_move', None)
        if move and move.get('dest_scene') == self.SCENE_NAME:
            self.context.pending_gardening_move = None
            # TODO: activate placement mode for the moved plant (step 6)

        if self.character and not self.character.current_behavior.active:
            self.character.behavior_manager.resume_prior_behavior()

    def on_enter(self):
        """Override to configure sky, add custom draws, etc."""
        pass

    def exit(self):
        tick_plants(self.context)
        if self.character:
            self.character.behavior_manager.stop_current()
        self.environment.custom_draws.clear()
        vm = getattr(self.context, 'visit_manager', None)
        if vm:
            vm.on_scene_exit()
        self.on_exit()

    def on_exit(self):
        """Override for sky teardown, etc."""
        pass

    def update(self, dt):
        if self._placement.active:
            self._placement.update(dt)
        prev_x = self.character.x
        self.on_update(dt)
        if not (self.input.is_pressed('left') or self.input.is_pressed('right')):
            if int(prev_x) != int(self.character.x):
                margin = 32
                screen_x = int(self.character.x) - int(self.environment.camera_x)
                if screen_x < margin:
                    self.environment.set_camera(int(self.character.x) - margin)
                elif screen_x > config.DISPLAY_WIDTH - margin:
                    self.environment.set_camera(int(self.character.x) - (config.DISPLAY_WIDTH - margin))
        self._check_lightning_startled()

    # Behaviors that block lightning startled (don't interrupt deep sleep etc.)
    _NO_STARTLE_BEHAVIORS = frozenset(('sleeping', 'eating', 'being_groomed', 'training'))

    def _check_lightning_startled(self):
        """Trigger startled when lightning strikes, regardless of playdate state."""
        sky = getattr(self, 'sky', None)
        if not sky or not getattr(sky, 'lightning_just_started', False):
            return
        cb = self.character.current_behavior
        if cb and cb.NAME in self._NO_STARTLE_BEHAVIORS:
            return
        # Probability scales with inverse courage (same curve as can_trigger_startled)
        ctx = self.character.context
        p = 0.6 * (1 - ctx.courage / 100)
        if random.random() < p:
            print('[Scene] Lightning startled! p=%.2f courage=%.1f' % (p, ctx.courage))
            self.character.trigger('startled')

    def on_update(self, dt):
        """Override for sky/entity updates. Must call self.character.update(dt)."""
        self.character.update(dt)

    def draw(self):
        if self.menu_active:
            self.menu.draw()
            return
        self.on_pre_draw()
        self.environment.draw(self.renderer)
        camera_offset = int(self.environment.camera_x)

        vm = getattr(self.context, 'visit_manager', None)
        visitor_cat = vm.visitor_cat if vm else None

        # Inviter is always drawn in front (last). Visitor draws behind (first).
        inviter_is_us = (self.context.visit is None or
                         self.context.visit.get('role') == 'inviter')
        if inviter_is_us:
            if visitor_cat is not None:
                visitor_cat.draw(self.renderer, camera_offset=camera_offset)
            self.character.draw(self.renderer, mirror=self.character.mirror, camera_offset=camera_offset)
        else:
            self.character.draw(self.renderer, mirror=self.character.mirror, camera_offset=camera_offset)
            if visitor_cat is not None:
                visitor_cat.draw(self.renderer, camera_offset=camera_offset)

        # Draw visitor cat's speech bubble (vocalization exchange, greeting, sniff)
        if vm and vm.visitor_bubble is not None and visitor_cat is not None:
            icon, remaining, max_secs = vm.visitor_bubble
            progress = 1.0 - (remaining / max_secs) if max_secs > 0 else 0.0
            vis_x = int(visitor_cat.x) - camera_offset
            vis_y = int(visitor_cat.y)
            draw_bubble(self.renderer, icon, vis_x, vis_y, progress, visitor_cat.mirror)

        self.on_post_draw()

        if self._placement.active:
            self._placement.draw(self.renderer, self.environment)

    def on_pre_draw(self):
        """Override for any setup needed before environment.draw()."""
        pass

    def on_post_draw(self):
        """Override for any drawing after the character (e.g. renderer.invert)."""
        pass

    # ------------------------------------------------------------------

    def handle_input(self):
        if self._placement.active:
            return self._placement.handle_input(self.input, self.environment)

        if self.menu_active:
            result = self.menu.handle_input()
            if result == 'closed':
                self.menu_active = False
            elif result is not None:
                self.menu_active = False
                return self._handle_menu_action(result)
            return None

        if self.input.was_just_pressed('menu2'):
            self.menu_active = True
            self.menu.open(self._build_menu_items())
            return None

        dx, dy = self.input.get_direction()
        if dx != 0:
            self.environment.pan(dx * config.PAN_SPEED)

        return None

    def _build_menu_items(self):
        affection_items = [
            MenuItem("Pets", icon=HAND_ICON, action=("pets",)),
            MenuItem("Scratch", icon=HAND_ICON, action=("scratch",)),
            MenuItem("Kiss", icon=HEART_ICON, action=("kiss",)),
            MenuItem("Psst psst", icon=HEART_BUBBLE_ICON, action=("psst",)),
            MenuItem("Groom", icon=HAND_ICON, action=("groom",))
        ]

        food_stock = self.context.food_stock
        _meal_defs = (
            ("Chicken",  "chicken",  CHICKEN_ICON),
            ("Salmon",   "salmon",   FISH_ICON),
            ("Tuna",     "tuna",     FISH_ICON),
            ("Shrimp",   "shrimp",   FISH_ICON),
            ("Trout",    "trout",    FISH_ICON),
            ("Herring",  "herring",  FISH_ICON),
            ("Haddock",  "haddock",  FISH_ICON),
            ("Cod",      "cod",      FISH_ICON),
            ("Mackerel", "mackerel", FISH_ICON),
            ("Turkey",   "turkey",   CHICKEN_ICON),
            ("Beef",     "beef",     MEAL_ICON),
            ("Lamb",     "lamb",     MEAL_ICON),
            ("Liver",    "liver",    MEAL_ICON),
            ("Kibble",   "kibble",   KIBBLE_ICON),
        )
        meal_items = [
            MenuItem(f"{name} ({food_stock.get(key, 0)})", icon=icon, action=("meal", key))
            for name, key, icon in _meal_defs
            if food_stock.get(key, 0) > 0
        ]
        _snack_defs = (
            ("Treats",     "treats"),
            ("Chew Stick", "chew_stick"),
            ("Nugget",     "nugget"),
            ("Puree",      "puree"),
            ("Cream",      "cream"),
            ("Milk",       "milk"),
            ("Fish Bite",  "fish_bite"),
            ("Eggs",       "eggs"),
            ("Pumpkin",    "pumpkin"),
            ("Carrots",    "carrots"),
        )
        snack_items = [
            MenuItem(f"{name} ({food_stock.get(key, 0)})",
                     icon=SNACK_ICONS.get(name, KIBBLE_ICON),
                     action=("snack", key))
            for name, key in _snack_defs
            if food_stock.get(key, 0) > 0
        ]
        feed_items = []
        if meal_items:
            feed_items.append(MenuItem("Meals", icon=MEAL_ICON, submenu=meal_items))
        if snack_items:
            feed_items.append(MenuItem("Snacks", icon=KIBBLE_ICON, submenu=snack_items))
        feed_items.append(MenuItem("Store...", action=("go_store",)))

        toy_items = [
            MenuItem(toy["name"], icon=TOY_ICONS.get(toy["name"]), action=("toy", toy))
            for toy in self.context.inventory.get("toys", [])
        ]
        toy_items.append(MenuItem("Store...", action=("go_store",)))

        train_items = [
            MenuItem("Intelligence", icon=HAND_ICON, action=("train",)),
            MenuItem("Behavior", icon=HAND_ICON, action=("train",)),
            MenuItem("Fitness", icon=HAND_ICON, action=("train",)),
            MenuItem("Sociability", icon=HAND_ICON, action=("train",)),
        ]

        inv = self.context.inventory
        _pot_defs = (
            ("Small pot",   "small"),
            ("Medium pot",  "medium"),
            ("Large pot",   "large"),
            ("Planter box", "planter"),
        )
        place_pot_items = [
            MenuItem(f"{name} ({inv['pots'].get(key, 0)})", icon=TREES_ICON,
                     action=("gardening_place_pot", key))
            for name, key in _pot_defs
            if inv['pots'].get(key, 0) > 0
        ]

        _seed_defs = (
            ("Cat Grass",  "cat_grass"),
            ("Fern",       "fern"),
            ("Sunflower",  "sunflower"),
            ("Rose",       "rose"),
            ("Tulip",      "tulip"),
        )
        plant_seed_items = [
            MenuItem(f"{name} ({inv['seeds'].get(key, 0)})", icon=TREES_ICON,
                     action=("gardening_plant_seed", key))
            for name, key in _seed_defs
            if inv['seeds'].get(key, 0) > 0
        ]

        gardening_items = []
        if place_pot_items:
            gardening_items.append(MenuItem("Place Pot",  icon=TREES_ICON, submenu=place_pot_items))
        if plant_seed_items:
            gardening_items.append(MenuItem("Plant Seed", icon=TREES_ICON, submenu=plant_seed_items))
        gardening_items.append(MenuItem("Water", icon=TREES_ICON, action=("gardening_water",)))
        gardening_items.append(MenuItem("Tend",  icon=TREES_ICON, action=("gardening_tend",)))
        gardening_items.append(MenuItem("Reset",  icon=TREES_ICON, action=("gardening_reset",), confirm="Reset all plants?"))

        items = [
            MenuItem("Affection", icon=HEART_ICON, submenu=affection_items),
            MenuItem("Train", icon=HAND_ICON, submenu=train_items),
        ]
        items.append(MenuItem("Feed", icon=MEAL_ICON, submenu=feed_items))
        items.append(MenuItem("Play", icon=TOYS_ICON, submenu=toy_items))
        items.append(MenuItem("Gardening", icon=TREES_ICON, submenu=gardening_items))

        return items

    def _handle_menu_action(self, action):
        if not action:
            return

        action_type = action[0]

        if action_type == "meal":
            food_type = action[1]
            self.character.trigger('eating', food_sprite=FOOD_BOWL, food_type=food_type)
            self.context.food_stock[food_type] = max(0, self.context.food_stock.get(food_type, 0) - 1)
        elif action_type == "kiss":
            self.character.trigger('affection', variant='kiss')
        elif action_type == "pets":
            self.character.trigger('affection', variant='pets')
        elif action_type == "scratch":
            self.character.trigger('affection', variant='scratching')
        elif action_type == "psst":
            self.character.trigger('attention', variant='psst')
        elif action_type == "snack":
            snack_key = action[1]
            self.character.trigger('eating', food_sprite=TREAT_PILE, food_type=snack_key)
            self.context.food_stock[snack_key] = max(0, self.context.food_stock.get(snack_key, 0) - 1)
        elif action_type == "toy":
            self.character.trigger('playing', variant=action[1]['variant'])
        elif action_type == "groom":
            self.character.trigger('being_groomed')
        elif action_type == "train":
            self.character.trigger('training')
        elif action_type == "go_store":
            return ('change_scene', 'store')
        elif action_type == "gardening_place_pot":
            self._placement.enter(action[1], self)
        elif action_type == "gardening_plant_seed":
            # TODO step 6: enter seed-placement cursor mode
            print('[Gardening] plant_seed', action[1])
        elif action_type == "gardening_water":
            # TODO step 7: enter plant-selection mode → water selected plant
            print('[Gardening] water')
        elif action_type == "gardening_tend":
            # TODO step 7: enter plant-selection mode → show tend submenu
            print('[Gardening] tend')
        elif action_type == "gardening_reset":
            self.context.reset_plants()
