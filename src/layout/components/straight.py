import math

from panda3d.core import Vec4, LineSegs

import src.util as util
import src.constants as constants
from src.geometry.point import Point


class Straight:
    def __init__(self, startNode, endNode):
        self.uuid = util.gen_uuid()
        self.connections = {}

        # Straight tracks are defined by two points
        self.startNode = startNode
        self.endNode = endNode

    def length(self):
        return self.startNode.point.distance(self.endNode.point)

    def track_angle(self):
        y = self.endNode.point.y - self.startNode.point.y
        x = self.endNode.point.x - self.startNode.point.x
        return math.atan2(y, x)

    def add_connection(self, node_id, track):
        self.connections[node_id] = track

    def get_nodes(self):
        return [self.startNode.uuid, self.endNode.uuid]

    def get_initial_location(self, node_id, rel_direction):
        if node_id == self.startNode.uuid:
            direction = constants.DIRECTION_FORWARD
            if rel_direction == constants.DIRECTION_TOWARD_NODE:
                direction = constants.DIRECTION_REVERSE

            heading_angle = self.track_angle()
            if direction == constants.DIRECTION_REVERSE:
                heading_angle += math.pi

            return StraightLocation(self.uuid, self.startNode.point, heading_angle, 0, direction)

        if node_id == self.endNode.uuid:
            direction = constants.DIRECTION_REVERSE
            if rel_direction == constants.DIRECTION_TOWARD_NODE:
                direction = constants.DIRECTION_FORWARD

            heading_angle = self.track_angle()
            if direction == constants.DIRECTION_REVERSE:
                heading_angle += math.pi

            return StraightLocation(self.uuid, self.endNode.point, heading_angle, self.length(), direction)

        raise AssertionError(self.uuid + ' does not start or end with the node ' + node_id)

    def get_updated_location(self, loc, offset):
        # Location must be from this track segment, otherwise it does not mean anything
        if self.uuid != loc.track_uuid:
            raise AssertionError(self.uuid + ' does not match provided ID ' + loc.track_uuid)

        length = self.length()

        new_t = loc.t + offset
        if loc.direction == constants.DIRECTION_REVERSE:
            new_t = loc.t - offset

        if new_t < 0:
            relative_dir = constants.DIRECTION_TOWARD_NODE
            remaining_offset = new_t

            if loc.direction == constants.DIRECTION_REVERSE:
                relative_dir = constants.DIRECTION_AWAY_FROM_NODE
                remaining_offset = offset - loc.t

            connecting_track = self.connections[self.startNode.uuid]
            new_track_loc = connecting_track.get_initial_location(self.startNode.uuid, relative_dir)
            return connecting_track.get_updated_location(new_track_loc, remaining_offset)

        if new_t > length:
            relative_dir = constants.DIRECTION_AWAY_FROM_NODE
            remaining_offset = new_t - length

            if loc.direction == constants.DIRECTION_REVERSE:
                relative_dir = constants.DIRECTION_TOWARD_NODE
                remaining_offset = length - new_t

            connecting_track = self.connections[self.endNode.uuid]
            new_track_loc = connecting_track.get_initial_location(self.endNode.uuid, relative_dir)
            return connecting_track.get_updated_location(new_track_loc, remaining_offset)

        new_percent = 0 if new_t == 0 else new_t / length

        x = self.startNode.point.x + ((self.endNode.point.x - self.startNode.point.x) * new_percent)
        y = self.startNode.point.y + ((self.endNode.point.y - self.startNode.point.y) * new_percent)
        new_pos = Point(x, y)

        heading_angle = self.track_angle()
        if loc.direction == constants.DIRECTION_REVERSE:
            heading_angle += math.pi

        return StraightLocation(self.uuid, new_pos, heading_angle, new_t, loc.direction)

    def get_geometry(self):
        segs = LineSegs()
        segs.setThickness(2.0)
        segs.setColor(Vec4(0, 1, 0, 1))
        segs.moveTo(self.startNode.point.x, self.startNode.point.y, 0)
        segs.drawTo(self.endNode.point.x, self.endNode.point.y, 0)
        return segs.create(None)

    def to_string(self):
        string = 'Straight: ' + self.uuid + '\n'
        string += '  - start: ' + self.startNode.to_string() + '\n'
        string += '  - end:   ' + self.endNode.to_string() + '\n'
        string += '  - connections:\n'
        for node in self.connections:
            string += '    - ' + node + ': ' + self.connections[node].uuid + '\n'

        return string


class StraightLocation:
    def __init__(self, track_uuid, pos, heading, t, direction):
        self.track_uuid = track_uuid
        self.pos = pos
        self.heading = heading
        self.t = t
        self.direction = direction