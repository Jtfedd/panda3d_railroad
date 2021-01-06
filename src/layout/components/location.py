from src.geometry.point import Point


class Location:
    def track_uuid(self):
        return ''

    def get_pos(self):
        return Point(0, 0)

    def get_h(self):
        return 0

    def get_height(self):
        return 0

    def get_slope(self):
        return 0

    def get_offset(self, offset):
        return Location()
