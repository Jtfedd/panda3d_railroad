from panda3d.core import LineSegs

from src.constants.colors import *


class Grid:
    def __init__(self, base, width, height):
        self.base = base

        # Width and height should be integer number of feet
        self.width = width
        self.height = height

        self.root = None
        self.generate()

    def generate(self):
        if self.root is not None:
            self.cleanup()

        self.root = self.base.render.attachNewNode('editor_grid')


        # Draw border
        segs = LineSegs()
        segs.setThickness(4.0)
        segs.setColor(EDITOR_DARK)

        segs.moveTo(0, 0, 0)
        segs.drawTo(12*self.width, 0, 0)
        segs.drawTo(12*self.width, 12*self.height, 0)
        segs.drawTo(0, 12*self.height, 0)
        segs.drawTo(0, 0, 0)

        self.root.attachNewNode(segs.create(None))

        # Draw 1-foot lines
        segs = LineSegs()
        segs.setThickness(2.0)
        segs.setColor(EDITOR_MEDIUM)

        for i in range(1, self.width):
            segs.moveTo(12 * i, 0, 0)
            segs.drawTo(12 * i, 12*self.height, 0)
        for i in range(1, self.height):
            segs.moveTo(0, 12 * i, 0)
            segs.drawTo(12 * self.width, 12 * i, 0)

        self.root.attachNewNode(segs.create(None))

        # Draw inch lines
        segs = LineSegs()
        segs.setThickness(1.0)
        segs.setColor(EDITOR_LIGHT)

        for i in range(1, 12*self.width):
            if i % 12 == 0:
                continue
            segs.moveTo(i, 0, 0)
            segs.drawTo(i, 12 * self.height, 0)
        for i in range(1, 12*self.height):
            if i % 12 == 0:
                continue
            segs.moveTo(0, i, 0)
            segs.drawTo(12 * self.width, i, 0)

        self.root.attachNewNode(segs.create(None))

    def update_size(self, newWidth, newHeight):
        self.width = newWidth
        self.height = newHeight

        self.generate()

    def cleanup(self):
        self.root.removeNode()
