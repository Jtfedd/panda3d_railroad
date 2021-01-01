import math

from panda3d.core import Vec4, LineSegs

import src.constants as constants
from src.layout.components.straight import Straight
from src.geometry.point import Point


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

    def length(self):
        return (self.endAngle - self.startAngle) * self.radius

    def get_initial_location(self, node_id, rel_direction):
        if node_id == self.startNode.uuid:
            direction = constants.DIRECTION_FORWARD
            if rel_direction == constants.DIRECTION_TOWARD_NODE:
                direction = constants.DIRECTION_REVERSE

            heading_angle = self.startAngle
            if direction == constants.DIRECTION_FORWARD:
                heading_angle += math.pi/2
            else:
                heading_angle -= math.pi/2

            return CurveLocation(self.uuid, self.startNode.point, heading_angle, self.startNode.height, self.get_slope(direction), self.startAngle, direction)

        if node_id == self.endNode.uuid:
            direction = constants.DIRECTION_REVERSE
            if rel_direction == constants.DIRECTION_TOWARD_NODE:
                direction = constants.DIRECTION_FORWARD

            heading_angle = self.endAngle
            if direction == constants.DIRECTION_FORWARD:
                heading_angle += math.pi / 2
            else:
                heading_angle -= math.pi / 2

            return CurveLocation(self.uuid, self.endNode.point, heading_angle, self.endNode.height, self.get_slope(direction), self.endAngle, direction)

        raise AssertionError(self.uuid + ' does not start or end with the node ' + node_id)

    def get_updated_location(self, loc, offset):
        # Location must be from this track segment, otherwise it does not mean anything
        if self.uuid != loc.track_uuid:
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
            return connecting_track.get_updated_location(new_track_loc, remaining_offset)

        if new_angle > self.endAngle:
            relative_dir = constants.DIRECTION_AWAY_FROM_NODE
            remaining_angle = new_angle - self.endAngle

            if loc.direction == constants.DIRECTION_REVERSE:
                relative_dir = constants.DIRECTION_TOWARD_NODE
                remaining_angle = self.endAngle - new_angle

            remaining_offset = remaining_angle * self.radius

            connecting_track = self.connections[self.endNode.uuid]
            new_track_loc = connecting_track.get_initial_location(self.endNode.uuid, relative_dir)
            return connecting_track.get_updated_location(new_track_loc, remaining_offset)

        x = self.center.x + (self.radius * math.cos(new_angle))
        y = self.center.y + (self.radius * math.sin(new_angle))
        z = self.startNode.height + ((self.endNode.height - self.startNode.height) * ((new_angle - self.startAngle) / (self.endAngle - self.startAngle)))
        new_pos = Point(x, y)

        heading_angle = new_angle
        if loc.direction == constants.DIRECTION_FORWARD:
            heading_angle += math.pi/2
        else:
            heading_angle -= math.pi/2

        return CurveLocation(self.uuid, new_pos, heading_angle, z, self.get_slope(loc.direction), new_angle, loc.direction)

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


class CurveLocation:
    def __init__(self, track_uuid, pos, heading, height, slope, angle, direction):
        self.track_uuid = track_uuid
        self.pos = pos
        self.heading = heading
        self.height = height
        self.slope = slope
        self.angle = angle
        self.direction = direction
