from enum import Enum

MIN_TURN_RADIUS = 21


class Direction(Enum):
    FORWARD = 1
    REVERSE = 2


class RelativeDirection(Enum):
    TOWARD = 1
    AWAY = 2
