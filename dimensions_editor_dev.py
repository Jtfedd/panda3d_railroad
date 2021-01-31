from direct.showbase.ShowBase import ShowBase

from src.constants.colors import EDITOR_BACKGROUND
from src.editor.grid import Grid


class TestApp:
    def __init__(self, panda_base):
        self.base = panda_base

        self.base.setBackgroundColor(EDITOR_BACKGROUND)

        self.grid = Grid(self.base, 50, 50)


base = ShowBase()
app = TestApp(base)
base.run()
