import math


class Point:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def distance(self, other) -> float:
        # Distance formula
        return math.sqrt(((self.x-other.x)**2)+((self.y-other.y)**2))

    def to_string(self) -> str:
        return '(' + str(self.x) + ', ' + str(self.y) + ')'
