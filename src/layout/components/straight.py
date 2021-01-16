import math
from typing import Dict, List

from panda3d.core import Vec4, LineSegs

import src.util as util
from src.constants import Direction, RelativeDirection
from src.geometry.point import Point
from src.layout.components.location import Location
from src.layout.components.node import Node


class Straight:
    uuid: str

    startNode: Node
    endNode: Node

    connections: Dict[str, ]

    def __init__(self, startNode: Node, endNode: Node):
        self.uuid = util.gen_uuid()
        self.connections = {}

        # Straight tracks are defined by two points
        self.startNode = startNode
        self.endNode = endNode

    def length(self) -> float:
        return self.startNode.point.distance(self.endNode.point)

    def add_connection(self, node_id: str, track):
        self.connections[node_id] = track

    def get_nodes(self) -> List[str]:
        return [self.startNode.uuid, self.endNode.uuid]

    def get_initial_location(self, node_id: str, rel_direction: RelativeDirection) -> Location:
        direction = Direction.FORWARD
        t = 0

        if node_id == self.startNode.uuid:
            if rel_direction == RelativeDirection.TOWARD:
                direction = Direction.REVERSE
        else:
            if rel_direction == RelativeDirection.AWAY:
                direction = Direction.REVERSE
            t = self.length()

        return StraightLocation(self, t, direction)

    def get_offset(self, loc: Location, offset: float) -> Location:
        # Location must be from this track segment, otherwise it does not mean anything
        if self.uuid != loc.track_uuid():
            raise AssertionError(self.uuid + ' does not match provided ID ' + loc.track_uuid())

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
            return new_track_loc.get_offset(remaining_offset)

        if new_t > length:
            relative_dir = constants.DIRECTION_AWAY_FROM_NODE
            remaining_offset = new_t - length

            if loc.direction == constants.DIRECTION_REVERSE:
                relative_dir = constants.DIRECTION_TOWARD_NODE
                remaining_offset = length - new_t

            connecting_track = self.connections[self.endNode.uuid]
            new_track_loc = connecting_track.get_initial_location(self.endNode.uuid, relative_dir)
            return new_track_loc.get_offset(remaining_offset)

        return StraightLocation(self, new_t, loc.direction)

    def get_geometry(self):
        segs = LineSegs()
        segs.setThickness(2.0)
        segs.setColor(Vec4(0, 1, 0, 1))
        segs.moveTo(self.startNode.point.x, self.startNode.point.y, self.startNode.height)
        segs.drawTo(self.endNode.point.x, self.endNode.point.y, self.endNode.height)
        return segs.create(None)

    def to_string(self):
        string = 'Straight: ' + self.uuid + '\n'
        string += '  - start: ' + self.startNode.to_string() + '\n'
        string += '  - end:   ' + self.endNode.to_string() + '\n'
        string += '  - connections:\n'
        for node in self.connections:
            string += '    - ' + node + ': ' + self.connections[node].uuid + '\n'

        return string


class StraightLocation(Location):
    def __init__(self, track, t, direction):
        self.track = track
        self.t = t
        self.direction = direction

    def track_uuid(self):
        return self.track.uuid

    def get_pos(self):
        percent = self.t / self.track.length()

        start_x = self.track.startNode.point.x
        start_y = self.track.startNode.point.y

        end_x = self.track.endNode.point.x
        end_y = self.track.endNode.point.y

        x = start_x + ((end_x - start_x) * percent)
        y = start_y + ((end_y - start_y) * percent)
        return Point(x, y)

    def get_height(self):
        percent = self.t / self.track.length()

        start_height = self.track.startNode.height
        end_height = self.track.endNode.height

        return start_height + ((end_height - start_height) * percent)

    def get_h(self):
        y = self.track.endNode.point.y - self.track.startNode.point.y
        x = self.track.endNode.point.x - self.track.startNode.point.x
        angle = math.atan2(y, x)

        if self.direction == constants.DIRECTION_REVERSE:
            angle += math.pi

        return angle

    def get_slope(self):
        dz = self.track.endNode.height - self.track.startNode.height
        slope = math.atan2(dz, self.track.length())

        if self.direction == constants.DIRECTION_REVERSE:
            slope = -slope

        return slope

    def get_offset(self, offset):
        return self.track.get_offset(self, offset)
