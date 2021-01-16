import math

from panda3d.core import Vec4, LineSegs

import src.constants as constants
from src.layout.components.straight import Straight
from src.geometry.point import Point
from src.layout.components.location import Location


class Curve(Straight):
    def __init__(self, center, radius, startAngle, endAngle, startNode, endNode):
        Straight.__init__(self, startNode, endNode)

        # In addition to the start node and end node, curves are defined by
        # a center point, a radius, a start angle, and an end angle.
        # - The start angle is always less than the end angle
        # - The arc of the curve is always swept counterclockwise
        # - The start angle is always between 0 and 2pi
        # - The end angle is always between the start angle and the start angle + 2pi
        self.center = center
        self.radius = radius
        self.startAngle = startAngle
        self.endAngle = endAngle

    def length(self) -> float:
        return (self.endAngle - self.startAngle) * self.radius

    def get_initial_location(self, node_id, rel_direction):
        direction = constants.DIRECTION_FORWARD
        angle = self.startAngle

        if node_id == self.startNode.uuid:
            if rel_direction == constants.DIRECTION_TOWARD_NODE:
                direction = constants.DIRECTION_REVERSE

        if node_id == self.endNode.uuid:
            if rel_direction == constants.DIRECTION_AWAY_FROM_NODE:
                direction = constants.DIRECTION_REVERSE
            angle = self.endAngle

        return CurveLocation(self, angle, direction)

    def get_offset(self, loc, offset):
        # Location must be from this track segment, otherwise it does not mean anything
        if self.uuid != loc.track_uuid():
            raise AssertionError(self.uuid + ' does not match provided ID ' + loc.track_uuid)

        offset_angle = offset / self.radius
        new_angle = loc.angle + offset_angle
        if loc.direction == constants.DIRECTION_REVERSE:
            new_angle = loc.angle - offset_angle

        if new_angle < self.startAngle:
            relative_dir = constants.DIRECTION_TOWARD_NODE
            remaining_angle = new_angle - self.startAngle

            if loc.direction == constants.DIRECTION_REVERSE:
                relative_dir = constants.DIRECTION_AWAY_FROM_NODE
                remaining_angle = self.startAngle - new_angle

            remaining_offset = remaining_angle * self.radius

            connecting_track = self.connections[self.startNode.uuid]
            new_track_loc = connecting_track.get_initial_location(self.startNode.uuid, relative_dir)
            return new_track_loc.get_offset(remaining_offset)

        if new_angle > self.endAngle:
            relative_dir = constants.DIRECTION_AWAY_FROM_NODE
            remaining_angle = new_angle - self.endAngle

            if loc.direction == constants.DIRECTION_REVERSE:
                relative_dir = constants.DIRECTION_TOWARD_NODE
                remaining_angle = self.endAngle - new_angle

            remaining_offset = remaining_angle * self.radius

            connecting_track = self.connections[self.endNode.uuid]
            new_track_loc = connecting_track.get_initial_location(self.endNode.uuid, relative_dir)
            return new_track_loc.get_offset(remaining_offset)

        return CurveLocation(self, new_angle, loc.direction)

    def get_geometry(self):
        segs = LineSegs()
        segs.setThickness(2.0)
        segs.setColor(Vec4(0, 1, 0, 1))
        segs.moveTo(self.startNode.point.x, self.startNode.point.y, self.startNode.height)

        for i in range(100):
            angle = self.startAngle + ((self.endAngle - self.startAngle) * (i / 100.0))
            x = self.center.x + (math.cos(angle) * self.radius)
            y = self.center.y + (math.sin(angle) * self.radius)
            height = self.startNode.height + ((self.endNode.height - self.startNode.height) * (i / 100.0))

            segs.drawTo(x, y, height)

        segs.drawTo(self.endNode.point.x, self.endNode.point.y, self.endNode.height)

        return segs.create(None)

    def to_string(self):
        string = 'Curve: ' + self.uuid + '\n'
        string += '  - center: ' + self.center.to_string() + '\n'
        string += '  - radius: ' + str(self.radius) + '\n'
        string += '  - startAngle: ' + str(self.startAngle) + '\n'
        string += '  - endAngle: ' + str(self.endAngle) + '\n'
        string += '  - start: ' + self.startNode.to_string() + '\n'
        string += '  - end:   ' + self.endNode.to_string() + '\n'
        string += '  - connections:\n'
        for node in self.connections:
            string += '    - ' + node + ': ' + self.connections[node].uuid + '\n'

        return string


class CurveLocation(Location):
    def __init__(self, track, angle, direction):
        self.track = track
        self.angle = angle
        self.direction = direction

    def track_uuid(self) -> str:
        return self.track.uuid

    def get_pos(self):
        x = self.track.center.x + (self.track.radius * math.cos(self.angle))
        y = self.track.center.y + (self.track.radius * math.sin(self.angle))
        return Point(x, y)

    def get_height(self):
        start_height = self.track.startNode.height
        end_height = self.track.endNode.height

        rel_angle = self.angle - self.track.startAngle
        total_angle = self.track.endAngle - self.track.startAngle

        return start_height + ((end_height - start_height) * (rel_angle / total_angle))

    def get_h(self):
        h = self.angle

        if self.direction == constants.DIRECTION_FORWARD:
            h += math.pi / 2
        else:
            h -= math.pi / 2

        return h

    def get_slope(self):
        dz = self.track.endNode.height - self.track.startNode.height
        slope = math.atan2(dz, self.track.length())

        if self.direction == constants.DIRECTION_REVERSE:
            slope = -slope

        return slope

    def get_offset(self, offset):
        return self.track.get_offset(self, offset)
