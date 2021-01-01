import math


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def distance(self, other):
        # Distance formula
        return math.sqrt(((self.x-other.x)**2)+((self.y-other.y)**2))

    def to_string(self):
        return '(' + str(self.x) + ', ' + str(self.y) + ')'
