import src.util as util


class Node:
    def __init__(self, point, height):
        self.uuid = util.gen_uuid()
        self.point = point
        self.height = height

    def to_string(self):
        return 'Node ' + self.uuid + ': ' + self.point.to_string()