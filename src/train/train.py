import math

from src.geometry.point import Point
from src.layout.components.curve import CurveLocation

import src.constants as constants


class Train:
    def __init__(self, track, start_uuid, base):
        self.base = base
        self.track = track

        self.loc = CurveLocation(start_uuid, Point(-50, 0), math.pi/2, math.pi, constants.DIRECTION_REVERSE)
        self.speed = 20

        self.length = 10

        self.cubes = []
        for i in range(self.length):
            model = self.base.loader.loadModel("assets/models/arrow.glb")
            model.reparentTo(self.base.render)
            model.setPos(self.loc.pos.x, self.loc.pos.y, 0)
            self.cubes.append(model)

    def update(self, time, dt):
        speed = 20 * math.sin(time / 10)

        offset = speed * dt
        self.loc = self.track.get_updated_location(self.loc, offset)

        loc = self.loc
        for i in range(self.length):
            loc = self.track.get_updated_location(loc, -10)
            self.cubes[i].setPos(loc.pos.x, loc.pos.y, 0)
            self.cubes[i].setH(math.degrees(loc.heading))
