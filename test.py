import math

from direct.showbase.ShowBase import ShowBase
from direct.showbase.ShowBaseGlobal import globalClock
from panda3d.core import AmbientLight, DirectionalLight, Vec3, Vec4

from src.geometry.point import Point
from src.layout.components.node import Node
from src.layout.components.straight import Straight
from src.layout.components.curve import Curve
from src.layout.track import Track
from src.train.train import Train

class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        self.track = None
        self.train = None

        self.setup_lights()
        self.create_test_track()

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

        n0 = Node(p0, 0)
        n1 = Node(p1, 50)
        n2 = Node(p2, 10)
        n3 = Node(p3, 20)

        t0 = Curve(p4, 50, math.pi / 2, 3 * math.pi / 2, n0, n3)
        t1 = Straight(n0, n1)
        t2 = Curve(p5, 50, 3 * math.pi / 2, 5 * math.pi / 2, n2, n1)
        t3 = Straight(n2, n3)

        nodes = [n0, n1, n2, n3]
        tracks = [t0, t1, t2, t3]

        self.track = Track(nodes, tracks)
        self.track.render(self.render)

        self.train = Train(self.track, t0.uuid, self)

        self.taskMgr.add(self.update_task, "main_update_loop")

    def update_task(self, task):
        dt = globalClock.getDt()

        self.train.update(task.time, dt)

        return task.cont


app = MyApp()
app.run()
