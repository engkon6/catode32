"""pet_info.py - View and edit pet name; view pet info."""

from scene import Scene
from menu import Menu, MenuItem
from ui_keyboard import OnScreenKeyboard


class PetInfoScene(Scene):
    SCENE_NAME = 'pet_info'

    def __init__(self, context, renderer, input):
        super().__init__(context, renderer, input)
        self._menu    = Menu(renderer, input)
        self._editing = False
        self._kb_name = OnScreenKeyboard(renderer, input, charset='full', max_len=12)

    def load(self):
        super().load()

    def unload(self):
        super().unload()

    def enter(self):
        self._editing = False
        self._rebuild_menu()

    def exit(self):
        pass

    def update(self, dt):
        return None

    def draw(self):
        if self._editing:
            self._kb_name.draw()
        else:
            self._menu.draw()

    def handle_input(self):
        if self._editing:
            result = self._kb_name.handle_input()
            if result is not None:
                value = result.strip()
                if value:
                    self.context.pet_name = value
                self._editing = False
                self._rebuild_menu()
            return None

        result = self._menu.handle_input()
        if result == 'closed':
            return ('change_scene', 'last_main')
        if result is not None:
            self._kb_name.open('', self.context.pet_name or '')
            self._editing = True
        return None

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _rebuild_menu(self):
        days = self.context.environment.get('day_number', 0)
        days_str = str(min(days, 9999999))
        self._menu.open([
            MenuItem('Name: ' + (self.context.pet_name or '?'), action=('edit',)),
            MenuItem('Days: ' + days_str),
        ])
