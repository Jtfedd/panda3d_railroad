import math


class Vector:
    def __init__(self, dx, dy):
        self.dx = dx
        self.dy = dy

    @classmethod
    def from_points(cls, p1, p2):
        return cls(p2.x - p1.x, p2.y - p1.y)

    def magnitude(self):
        return math.sqrt((self.dx**2)+(self.dy**2))

    def angle(self):
        return math.atan2(self.dy, self.dx)

    def dot(self, other):
        return self.dx * other.dx + self.dy * other.dy

    def cross(self, other):
        return self.dx * other.dy - self.dy * other.dx
