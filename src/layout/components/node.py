import src.util as util

from src.geometry.point import Point


class Node:
    uuid: str

    point: Point
    height: float

    def __init__(self, point: Point, height: float):
        self.uuid = util.gen_uuid()
        self.point = point
        self.height = height

    def to_string(self) -> str:
        return 'Node ' + self.uuid + ': ' + self.point.to_string()