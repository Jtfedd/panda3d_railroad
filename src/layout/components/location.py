from __future__ import annotations

from src.geometry.point import Point


class Location:
    def track_uuid(self) -> str:
        return ''

    def get_pos(self) -> Point:
        return Point(0, 0)

    def get_h(self) -> float:
        return 0

    def get_height(self) -> float:
        return 0

    def get_slope(self) -> float:
        return 0

    def get_offset(self, offset: float) -> Location:
        return Location()
