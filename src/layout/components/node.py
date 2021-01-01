import src.util as util


class Node:
    def __init__(self, point):
        self.uuid = util.gen_uuid()
        self.point = point

    def to_string(self):
        return 'Node ' + self.uuid + ': ' + self.point.to_string()