import math
from collections import defaultdict

from direct.showbase.ShowBase import ShowBase
from direct.showbase.ShowBaseGlobal import globalClock
from panda3d.core import AmbientLight, DirectionalLight, Vec3, Vec4, LineSegs

import src.util as util
import src.constants as constants


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def distance_to(self, other):
        # Distance formula
        return math.sqrt(((self.x-other.x)**2)+((self.y-other.y)**2))

    def to_string(self):
        return '(' + str(self.x) + ', ' + str(self.y) + ')'


class Node:
    # A node is a connection between two tracks
    def __init__(self, point):
        self.uuid = util.gen_uuid()
        self.point = point

    def to_string(self):
        return 'Node ' + self.uuid + ': ' + self.point.to_string()


class Straight:
    def __init__(self, startNode, endNode):
        self.uuid = util.gen_uuid()
        self.connections = {}

        # Straight tracks are defined by two points
        self.startNode = startNode
        self.endNode = endNode

    def length(self):
        return self.startNode.point.distance_to(self.endNode.point)

    def track_angle(self):
        y = self.endNode.point.y - self.startNode.point.y
        x = self.endNode.point.x - self.startNode.point.x
        return math.atan2(y, x)

    def add_connection(self, node_id, track):
        self.connections[node_id] = track

    def get_nodes(self):
        return [self.startNode.uuid, self.endNode.uuid]

    def get_initial_location(self, node_id, rel_direction):
        if node_id == self.startNode.uuid:
            direction = constants.DIRECTION_FORWARD
            if rel_direction == constants.DIRECTION_TOWARD_NODE:
                direction = constants.DIRECTION_REVERSE

            heading_angle = self.track_angle()
            if direction == constants.DIRECTION_REVERSE:
                heading_angle += math.pi
            
            return StraightLocation(self.uuid, self.startNode.point, heading_angle, 0, direction)

        if node_id == self.endNode.uuid:
            direction = constants.DIRECTION_REVERSE
            if rel_direction == constants.DIRECTION_TOWARD_NODE:
                direction = constants.DIRECTION_FORWARD

            heading_angle = self.track_angle()
            if direction == constants.DIRECTION_REVERSE:
                heading_angle += math.pi

            return StraightLocation(self.uuid, self.endNode.point, heading_angle, self.length(), direction)

        raise AssertionError(self.uuid + ' does not start or end with the node ' + node_id)

    def get_updated_location(self, loc, offset):
        # Location must be from this track segment, otherwise it does not mean anything
        if self.uuid != loc.track_uuid:
            raise AssertionError(self.uuid + ' does not match provided ID ' + loc.track_uuid)

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
            return connecting_track.get_updated_location(new_track_loc, remaining_offset)

        if new_t > length:
            relative_dir = constants.DIRECTION_AWAY_FROM_NODE
            remaining_offset = new_t - length

            if loc.direction == constants.DIRECTION_REVERSE:
                relative_dir = constants.DIRECTION_TOWARD_NODE
                remaining_offset = length - new_t

            connecting_track = self.connections[self.endNode.uuid]
            new_track_loc = connecting_track.get_initial_location(self.endNode.uuid, relative_dir)
            return connecting_track.get_updated_location(new_track_loc, remaining_offset)

        new_percent = 0 if new_t == 0 else new_t / length

        x = self.startNode.point.x + ((self.endNode.point.x - self.startNode.point.x) * new_percent)
        y = self.startNode.point.y + ((self.endNode.point.y - self.startNode.point.y) * new_percent)
        new_pos = Point(x, y)

        heading_angle = self.track_angle()
        if loc.direction == constants.DIRECTION_REVERSE:
            heading_angle += math.pi

        return StraightLocation(self.uuid, new_pos, heading_angle, new_t, loc.direction)

    def get_geometry(self):
        segs = LineSegs()
        segs.setThickness(2.0)
        segs.setColor(Vec4(0, 1, 0, 1))
        segs.moveTo(self.startNode.point.x, self.startNode.point.y, 0)
        segs.drawTo(self.endNode.point.x, self.endNode.point.y, 0)
        return segs.create(None)

    def to_string(self):
        string = 'Straight: ' + self.uuid + '\n'
        string += '  - start: ' + self.startNode.to_string() + '\n'
        string += '  - end:   ' + self.endNode.to_string() + '\n'
        string += '  - connections:\n'
        for node in self.connections:
            string += '    - ' + node + ': ' + self.connections[node].uuid + '\n'

        return string


class StraightLocation:
    def __init__(self, track_uuid, pos, heading, t, direction):
        self.track_uuid = track_uuid
        self.pos = pos
        self.heading = heading
        self.t = t
        self.direction = direction


class Curve(Straight):
    def __init__(self, center, radius, startAngle, endAngle, startNode, endNode):
        Straight.__init__(self, startNode, endNode)

        # In addition to the start node and end node, curves are defined by
        # a center point, a radius, a start angle, and an end angle.
        # - The start angle is always less than the end angle
        # - The arc of the curve is always swept counterclockwise
        # - The start angle is always between 0 and 2pi
        # - The end angle is always between the start angle and the start angle + 2pi
        self.center = center
        self.radius = radius
        self.startAngle = startAngle
        self.endAngle = endAngle

    def length(self):
        return (self.endAngle - self.startAngle) * self.radius

    def get_initial_location(self, node_id, rel_direction):
        if node_id == self.startNode.uuid:
            direction = constants.DIRECTION_FORWARD
            if rel_direction == constants.DIRECTION_TOWARD_NODE:
                direction = constants.DIRECTION_REVERSE

            heading_angle = self.startAngle
            if direction == constants.DIRECTION_FORWARD:
                heading_angle += math.pi/2
            else:
                heading_angle -= math.pi/2

            return CurveLocation(self.uuid, self.startNode.point, heading_angle, self.startAngle, direction)

        if node_id == self.endNode.uuid:
            direction = constants.DIRECTION_REVERSE
            if rel_direction == constants.DIRECTION_TOWARD_NODE:
                direction = constants.DIRECTION_FORWARD

            heading_angle = self.endAngle
            if direction == constants.DIRECTION_FORWARD:
                heading_angle += math.pi / 2
            else:
                heading_angle -= math.pi / 2

            return CurveLocation(self.uuid, self.endNode.point, heading_angle, self.endAngle, direction)

        raise AssertionError(self.uuid + ' does not start or end with the node ' + node_id)

    def get_updated_location(self, loc, offset):
        # Location must be from this track segment, otherwise it does not mean anything
        if self.uuid != loc.track_uuid:
            raise AssertionError(self.uuid + ' does not match provided ID ' + loc.track_uuid)

        offset_angle = offset / self.radius
        new_angle = loc.angle + offset_angle
        if loc.direction == constants.DIRECTION_REVERSE:
            new_angle = loc.angle + offset_angle

        if new_angle < self.startAngle:
            relative_dir = constants.DIRECTION_TOWARD_NODE
            remaining_angle = new_angle - self.startAngle

            if loc.direction == constants.DIRECTION_REVERSE:
                relative_dir = constants.DIRECTION_AWAY_FROM_NODE
                remaining_angle = self.startAngle - new_angle

            remaining_offset = remaining_angle * self.radius

            connecting_track = self.connections[self.startNode.uuid]
            new_track_loc = connecting_track.get_initial_location(self.startNode.uuid, relative_dir)
            return connecting_track.get_updated_location(new_track_loc, remaining_offset)

        if new_angle > self.endAngle:
            relative_dir = constants.DIRECTION_AWAY_FROM_NODE
            remaining_angle = new_angle - self.endAngle

            if loc.direction == constants.DIRECTION_REVERSE:
                relative_dir = constants.DIRECTION_TOWARD_NODE
                remaining_angle = self.endAngle - new_angle

            remaining_offset = remaining_angle * self.radius

            connecting_track = self.connections[self.endNode.uuid]
            new_track_loc = connecting_track.get_initial_location(self.endNode.uuid, relative_dir)
            return connecting_track.get_updated_location(new_track_loc, remaining_offset)

        x = self.center.x + (self.radius * math.cos(new_angle))
        y = self.center.y + (self.radius * math.sin(new_angle))
        new_pos = Point(x, y)

        heading_angle = new_angle
        if loc.direction == constants.DIRECTION_FORWARD:
            heading_angle += math.pi/2
        else:
            heading_angle -= math.pi/2

        return CurveLocation(self.uuid, new_pos, heading_angle, new_angle, loc.direction)

    def get_geometry(self):
        segs = LineSegs()
        segs.setThickness(2.0)
        segs.setColor(Vec4(0, 1, 0, 1))
        segs.moveTo(self.startNode.point.x, self.startNode.point.y, 0)

        for i in range(100):
            angle = self.startAngle + ((self.endAngle - self.startAngle) * (i / 100.0))
            x = self.center.x + (math.cos(angle) * self.radius)
            y = self.center.y + (math.sin(angle) * self.radius)

            segs.drawTo(x, y, 0)

        segs.drawTo(self.endNode.point.x, self.endNode.point.y, 0)

        return segs.create(None)

    def to_string(self):
        string = 'Curve: ' + self.uuid + '\n'
        string += '  - center: ' + self.center.to_string() + '\n'
        string += '  - radius: ' + str(self.radius) + '\n'
        string += '  - startAngle: ' + str(self.startAngle) + '\n'
        string += '  - endAngle: ' + str(self.endAngle) + '\n'
        string += '  - start: ' + self.startNode.to_string() + '\n'
        string += '  - end:   ' + self.endNode.to_string() + '\n'
        string += '  - connections:\n'
        for node in self.connections:
            string += '    - ' + node + ': ' + self.connections[node].uuid + '\n'

        return string


class CurveLocation:
    def __init__(self, track_uuid, pos, heading, angle, direction):
        self.track_uuid = track_uuid
        self.pos = pos
        self.heading = heading
        self.angle = angle
        self.direction = direction


class Track:
    def __init__(self, nodes, tracks):
        self.nodes = {}
        self.tracks = {}

        tracks_by_node = defaultdict(lambda: [])

        for node in nodes:
            self.nodes[node.uuid] = node

        for track in tracks:
            self.tracks[track.uuid] = track

            for node in track.get_nodes():
                tracks_by_node[node].append(track)

        for node in tracks_by_node:
            if node not in self.nodes:
                raise AssertionError(node + ' not found in provided nodes')
            if len(tracks_by_node[node]) != 2:
                print('Warning: node has ' + str(len(tracks_by_node[node])) + ' connections')

            for track in tracks_by_node[node]:
                for other_track in tracks_by_node[node]:
                    if track.uuid == other_track.uuid:
                        continue

                    track.add_connection(node, other_track)

    def get_updated_location(self, loc, offset):
        return self.tracks[loc.track_uuid].get_updated_location(loc, offset)

    def to_string(self):
        string = 'Track\n'
        string += '--- NODES ---\n\n'

        for n in self.nodes.values():
            string += n.to_string() + '\n'

        string += '\n--- TRACKS --- \n\n'

        for t in self.tracks.values():
            string += t.to_string()

        return string

    def render(self, render):
        for track in self.tracks.values():
            geom = track.get_geometry()
            render.attachNewNode(geom)


class Train:
    def __init__(self, track, start_uuid, base):
        self.base = base
        self.track = track

        self.loc = CurveLocation(start_uuid, Point(-50, 0), 3*math.pi/2, math.pi, constants.DIRECTION_FORWARD)
        self.speed = 20

        self.length = 10

        self.cubes = []
        for i in range(self.length):
            model = self.base.loader.loadModel("assets/arrow.glb")
            model.reparentTo(self.base.render)
            model.setPos(self.loc.pos.x, self.loc.pos.y, 0)
            self.cubes.append(model)

    def update(self, time, dt):
        speed = 20 * math.sin(time / 10)

        offset = speed * dt
        self.loc = self.track.get_updated_location(self.loc, offset)

        loc = self.loc
        for i in range(self.length):
            loc = self.track.get_updated_location(loc, -10)
            self.cubes[i].setPos(loc.pos.x, loc.pos.y, 0)
            self.cubes[i].setH(math.degrees(loc.heading))


class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        self.track = None
        self.train = None

        self.setup_lights()
        self.create_test_track()

    def render_cube(self):
        cube = self.loader.loadModel("assets/cube.glb")
        cube.reparentTo(self.render)

    def setup_lights(self):
        alight = AmbientLight('ambientLight')
        alight.setColor(Vec4(0.5, 0.5, 0.5, 1))
        alight_np = self.render.attachNewNode(alight)

        dir_light = DirectionalLight('directionalLight')
        dir_light.setDirection(Vec3(1, 1.2, -1.5))
        dir_light.setColor(Vec4(0.7, 0.7, 0.7, 1))
        dir_light_np = self.render.attachNewNode(dir_light)

        dir_light_2 = DirectionalLight('directionalLight2')
        dir_light_2.setDirection(Vec3(-.5, -.3, -.2))
        dir_light_2.setColor(Vec4(0.3, 0.3, 0.3, 1))
        dir_light_np_2 = self.render.attachNewNode(dir_light_2)

        self.render.clearLight()
        self.render.setLight(alight_np)
        self.render.setLight(dir_light_np)
        self.render.setLight(dir_light_np_2)

    def create_test_track(self):
        p0 = Point(0, 50)
        p1 = Point(100, 50)
        p2 = Point(100, -50)
        p3 = Point(0, -50)
        p4 = Point(0, 0)
        p5 = Point(100, 0)

        n0 = Node(p0)
        n1 = Node(p1)
        n2 = Node(p2)
        n3 = Node(p3)

        t0 = Curve(p4, 50, math.pi / 2, 3 * math.pi / 2, n0, n3)
        t1 = Straight(n0, n1)
        t2 = Curve(p5, 50, 3 * math.pi / 2, 5 * math.pi / 2, n2, n1)
        t3 = Straight(n2, n3)

        nodes = [n0, n1, n2, n3]
        tracks = [t0, t1, t2, t3]

        self.track = Track(nodes, tracks)
        # print(track.to_string())
        self.track.render(self.render)

        self.train = Train(self.track, t0.uuid, self)

        self.taskMgr.add(self.update_task, "main_update_loop")

    def update_task(self, task):
        dt = globalClock.getDt()

        self.train.update(task.time, dt)

        return task.cont


app = MyApp()
app.run()
