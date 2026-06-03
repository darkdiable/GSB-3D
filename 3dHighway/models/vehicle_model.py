from panda3d.core import (
    GeomVertexData, GeomVertexFormat, GeomVertexWriter,
    Geom, GeomTriangles, GeomNode, NodePath, Vec3
)
from config.settings import Config
import math


class VehicleModel:
    def __init__(self, render):
        self.render = render
        self.vehicle_node = None
        self.body_color = (0.8, 0.15, 0.15, 1)
        self.window_color = (0.3, 0.55, 0.8, 1)
        self.wheel_color = (0.1, 0.1, 0.1, 1)
        self.headlight_color = (1.0, 1.0, 0.8, 1)
        self.taillight_color = (1.0, 0.0, 0.0, 1)

    def _make_box(self, name, center, size, color):
        vdata = GeomVertexData(name, GeomVertexFormat.getV3c4(), Geom.UHStatic)
        vertex = GeomVertexWriter(vdata, 'vertex')
        color_writer = GeomVertexWriter(vdata, 'color')

        cx, cy, cz = center
        sx, sy, sz = size

        verts = [
            (cx - sx/2, cy - sy/2, cz - sz/2),
            (cx + sx/2, cy - sy/2, cz - sz/2),
            (cx + sx/2, cy + sy/2, cz - sz/2),
            (cx - sx/2, cy + sy/2, cz - sz/2),
            (cx - sx/2, cy - sy/2, cz + sz/2),
            (cx + sx/2, cy - sy/2, cz + sz/2),
            (cx + sx/2, cy + sy/2, cz + sz/2),
            (cx - sx/2, cy + sy/2, cz + sz/2),
        ]
        for v in verts:
            vertex.addData3f(*v)
            color_writer.addData4f(*color)

        prim = GeomTriangles(Geom.UHStatic)
        faces = [
            (0, 2, 1), (0, 3, 2),
            (4, 5, 6), (4, 6, 7),
            (0, 5, 4), (0, 1, 5),
            (2, 7, 6), (2, 3, 7),
            (0, 4, 7), (0, 7, 3),
            (1, 6, 5), (1, 2, 6),
        ]
        for f in faces:
            prim.addVertices(*f)

        geom = Geom(vdata)
        geom.addPrimitive(prim)
        node = GeomNode(name)
        node.addGeom(geom)
        np = NodePath(node)
        np.setLightOff()
        return np

    def create_wheel(self, center, radius, width, color):
        cx, cy, cz = center
        segments = 16
        parent = NodePath('wheel')

        vdata = GeomVertexData('wheel_cyl', GeomVertexFormat.getV3c4(), Geom.UHStatic)
        vertex = GeomVertexWriter(vdata, 'vertex')
        color_writer = GeomVertexWriter(vdata, 'color')

        for i in range(segments):
            a1 = (i / segments) * math.pi * 2
            a2 = ((i + 1) / segments) * math.pi * 2
            cos1, sin1 = math.cos(a1), math.sin(a1)
            cos2, sin2 = math.cos(a2), math.sin(a2)

            vertex.addData3f(cx, cy - width/2, cz)
            color_writer.addData4f(*color)
            vertex.addData3f(cx + radius * cos1, cy - width/2, cz + radius * sin1)
            color_writer.addData4f(*color)
            vertex.addData3f(cx + radius * cos2, cy - width/2, cz + radius * sin2)
            color_writer.addData4f(*color)

            vertex.addData3f(cx, cy + width/2, cz)
            color_writer.addData4f(*color)
            vertex.addData3f(cx + radius * cos2, cy + width/2, cz + radius * sin2)
            color_writer.addData4f(*color)
            vertex.addData3f(cx + radius * cos1, cy + width/2, cz + radius * sin1)
            color_writer.addData4f(*color)

            vertex.addData3f(cx + radius * cos1, cy - width/2, cz + radius * sin1)
            color_writer.addData4f(*color)
            vertex.addData3f(cx + radius * cos2, cy - width/2, cz + radius * sin2)
            color_writer.addData4f(*color)
            vertex.addData3f(cx + radius * cos2, cy + width/2, cz + radius * sin2)
            color_writer.addData4f(*color)

            vertex.addData3f(cx + radius * cos2, cy + width/2, cz + radius * sin2)
            color_writer.addData4f(*color)
            vertex.addData3f(cx + radius * cos1, cy + width/2, cz + radius * sin1)
            color_writer.addData4f(*color)
            vertex.addData3f(cx + radius * cos1, cy - width/2, cz + radius * sin1)
            color_writer.addData4f(*color)

        prim = GeomTriangles(Geom.UHStatic)
        for i in range(segments * 4):
            prim.addVertices(i * 3, i * 3 + 1, i * 3 + 2)

        geom = Geom(vdata)
        geom.addPrimitive(prim)
        node = GeomNode('wheel_cyl')
        node.addGeom(geom)
        wheel_np = NodePath(node)
        wheel_np.setLightOff()
        wheel_np.reparentTo(parent)

        return parent

    def create_simple_car(self):
        car_root = NodePath('car')

        body = self._make_box('body',
            (0, 0, Config.VEHICLE_HEIGHT / 2),
            (Config.VEHICLE_LENGTH, Config.VEHICLE_WIDTH, Config.VEHICLE_HEIGHT),
            self.body_color)
        body.reparentTo(car_root)

        cabin = self._make_box('cabin',
            (Config.VEHICLE_LENGTH * 0.1, 0, Config.VEHICLE_HEIGHT * 1.25),
            (Config.VEHICLE_LENGTH * 0.5, Config.VEHICLE_WIDTH * 0.88, Config.VEHICLE_HEIGHT * 0.5),
            self.window_color)
        cabin.reparentTo(car_root)

        roof = self._make_box('roof',
            (Config.VEHICLE_LENGTH * 0.05, 0, Config.VEHICLE_HEIGHT * 1.55),
            (Config.VEHICLE_LENGTH * 0.45, Config.VEHICLE_WIDTH * 0.85, Config.VEHICLE_HEIGHT * 0.08),
            self.body_color)
        roof.reparentTo(car_root)

        hood = self._make_box('hood',
            (Config.VEHICLE_LENGTH * 0.35, 0, Config.VEHICLE_HEIGHT * 0.85),
            (Config.VEHICLE_LENGTH * 0.25, Config.VEHICLE_WIDTH * 0.95, Config.VEHICLE_HEIGHT * 0.15),
            self.body_color)
        hood.reparentTo(car_root)

        trunk = self._make_box('trunk',
            (-Config.VEHICLE_LENGTH * 0.35, 0, Config.VEHICLE_HEIGHT * 0.85),
            (Config.VEHICLE_LENGTH * 0.25, Config.VEHICLE_WIDTH * 0.95, Config.VEHICLE_HEIGHT * 0.15),
            self.body_color)
        trunk.reparentTo(car_root)

        hl_x = Config.VEHICLE_LENGTH / 2
        hl_y = Config.VEHICLE_WIDTH * 0.35
        headlight_l = self._make_box('headlight_l',
            (hl_x, hl_y, Config.VEHICLE_HEIGHT * 0.55),
            (0.05, 0.15, 0.12),
            self.headlight_color)
        headlight_l.reparentTo(car_root)

        headlight_r = self._make_box('headlight_r',
            (hl_x, -hl_y, Config.VEHICLE_HEIGHT * 0.55),
            (0.05, 0.15, 0.12),
            self.headlight_color)
        headlight_r.reparentTo(car_root)

        tl_x = -Config.VEHICLE_LENGTH / 2
        tl_y = Config.VEHICLE_WIDTH * 0.35
        taillight_l = self._make_box('taillight_l',
            (tl_x, tl_y, Config.VEHICLE_HEIGHT * 0.55),
            (0.05, 0.15, 0.12),
            self.taillight_color)
        taillight_l.reparentTo(car_root)

        taillight_r = self._make_box('taillight_r',
            (tl_x, -tl_y, Config.VEHICLE_HEIGHT * 0.55),
            (0.05, 0.15, 0.12),
            self.taillight_color)
        taillight_r.reparentTo(car_root)

        wheel_radius = 0.35
        wheel_width = 0.2

        wheel_positions = [
            (Config.VEHICLE_LENGTH * 0.32, -Config.VEHICLE_WIDTH * 0.55, wheel_radius),
            (Config.VEHICLE_LENGTH * 0.32, Config.VEHICLE_WIDTH * 0.55, wheel_radius),
            (-Config.VEHICLE_LENGTH * 0.32, -Config.VEHICLE_WIDTH * 0.55, wheel_radius),
            (-Config.VEHICLE_LENGTH * 0.32, Config.VEHICLE_WIDTH * 0.55, wheel_radius),
        ]

        for pos in wheel_positions:
            wheel = self.create_wheel(pos, wheel_radius, wheel_width, self.wheel_color)
            wheel.reparentTo(car_root)

        return car_root

    def build(self):
        self.vehicle_node = self.create_simple_car()
        self.vehicle_node.reparentTo(self.render)
        return self.vehicle_node
