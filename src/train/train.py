import math

from src.geometry.point import Point
from src.layout.components.curve import CurveLocation

import src.constants as constants


class TrainCar:
    def __init__(self, base, track, initial_loc):
        self.base = base
        self.track = track

        self.loc = initial_loc

        self.wheel_offset = 1.5
        self.wheel_dist = 5

        front_wheel_loc = self.track.get_updated_location(self.loc, -self.wheel_offset)
        back_wheel_loc = self.track.get_updated_location(front_wheel_loc, -self.wheel_dist)

        self.front_wheels = TrainWheels(self.base, front_wheel_loc, False)
        self.back_wheels = TrainWheels(self.base, back_wheel_loc, True)

        self.model = self.base.loader.loadModel("assets/models/simple_car.glb")
        self.model.reparentTo(self.base.render)
        self.position_model()

    def length(self):
        return 2 * self.wheel_offset + self.wheel_dist

    def update(self, new_loc):
        self.loc = new_loc

        front_wheel_loc = self.track.get_updated_location(self.loc, -self.wheel_offset)
        back_wheel_loc = self.track.get_updated_location(front_wheel_loc, -self.wheel_dist)

        self.front_wheels.update_loc(front_wheel_loc)
        self.back_wheels.update_loc(back_wheel_loc)

        self.position_model()

    def position_model(self):
        x = (self.front_wheels.loc.pos.x + self.back_wheels.loc.pos.x) / 2
        y = (self.front_wheels.loc.pos.y + self.back_wheels.loc.pos.y) / 2
        z = (self.front_wheels.loc.height + self.back_wheels.loc.height) / 2

        self.model.setPos(x, y, 1 + z)

        dx = self.back_wheels.loc.pos.x - self.front_wheels.loc.pos.x
        dy = self.back_wheels.loc.pos.y - self.front_wheels.loc.pos.y
        angle = math.atan2(dy, dx)

        self.model.setH(math.degrees(angle))

        dz = self.back_wheels.loc.height - self.front_wheels.loc.height
        slope = math.atan2(dz, self.wheel_dist)

        self.model.setR(math.degrees(-slope))


class TrainWheels:
    def __init__(self, base, initial_loc, is_reverse):
        self.base = base
        self.loc = initial_loc
        self.is_reverse = is_reverse

        self.model = self.base.loader.loadModel("assets/models/simple_wheelset.glb")
        self.model.reparentTo(self.base.render)
        self.position_model()

    def position_model(self):
        self.model.setPos(self.loc.pos.x, self.loc.pos.y, self.loc.height)

        h = self.loc.heading
        slope = self.loc.slope
        if self.is_reverse:
            h += math.pi
            slope = -slope

        self.model.setH(math.degrees(h))
        self.model.setR(math.degrees(-slope))

    def update_loc(self, new_loc):
        self.loc = new_loc
        self.position_model()


class Train:
    def __init__(self, track, start_uuid, base):
        self.base = base
        self.track = track

        self.loc = CurveLocation(start_uuid, Point(-50, 0), math.pi/2, 0, 0, math.pi, constants.DIRECTION_REVERSE)
        self.speed = 10

        self.length = 15

        self.cars = []
        for i in range(self.length):
            car = TrainCar(self.base, self.track, self.loc)
            self.cars.append(car)

    def update(self, time, dt):
        offset = self.speed * dt
        self.loc = self.track.get_updated_location(self.loc, offset)

        loc = self.loc
        for i in range(self.length):
            self.cars[i].update(loc)
            loc = self.track.get_updated_location(loc, -self.cars[i].length())
