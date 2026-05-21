from panda3d.core import *
import math


def create_box(parent: NodePath, width: float, height: float, depth: float, name: str = "box") -> NodePath:
    node = GeomNode(name)

    format = GeomVertexFormat.getV3n3cpt2()
    vdata = GeomVertexData(name, format, Geom.UHStatic)

    vertex = GeomVertexWriter(vdata, 'vertex')
    normal = GeomVertexWriter(vdata, 'normal')
    color = GeomVertexWriter(vdata, 'color')
    texcoord = GeomVertexWriter(vdata, 'texcoord')

    w, h, d = width / 2, height / 2, depth / 2

    vertices = [
        (-w, -h, d), (w, -h, d), (w, h, d), (-w, h, d),
        (w, -h, -d), (-w, -h, -d), (-w, h, -d), (w, h, -d),
        (-w, h, d), (w, h, d), (w, h, -d), (-w, h, -d),
        (-w, -h, -d), (w, -h, -d), (w, -h, d), (-w, -h, d),
        (w, -h, d), (w, -h, -d), (w, h, -d), (w, h, d),
        (-w, -h, -d), (-w, -h, d), (-w, h, d), (-w, h, -d)
    ]

    normals = [
        (0, 0, 1), (0, 0, 1), (0, 0, 1), (0, 0, 1),
        (0, 0, -1), (0, 0, -1), (0, 0, -1), (0, 0, -1),
        (0, 1, 0), (0, 1, 0), (0, 1, 0), (0, 1, 0),
        (0, -1, 0), (0, -1, 0), (0, -1, 0), (0, -1, 0),
        (1, 0, 0), (1, 0, 0), (1, 0, 0), (1, 0, 0),
        (-1, 0, 0), (-1, 0, 0), (-1, 0, 0), (-1, 0, 0)
    ]

    for i in range(24):
        vertex.addData3f(*vertices[i])
        normal.addData3f(*normals[i])
        color.addData4f(1, 1, 1, 1)
        texcoord.addData2f(0, 0)

    tris = GeomTriangles(Geom.UHStatic)
    for i in range(0, 24, 4):
        tris.addVertices(i, i + 1, i + 2)
        tris.addVertices(i, i + 2, i + 3)
        tris.closePrimitive()

    geom = Geom(vdata)
    geom.addPrimitive(tris)
    node.addGeom(geom)

    np = parent.attachNewNode(node)
    return np


def create_sphere(parent: NodePath, radius: float, name: str = "sphere", segments: int = 16) -> NodePath:
    node = GeomNode(name)

    format = GeomVertexFormat.getV3n3cpt2()
    vdata = GeomVertexData(name, format, Geom.UHStatic)

    vertex = GeomVertexWriter(vdata, 'vertex')
    normal = GeomVertexWriter(vdata, 'normal')
    color = GeomVertexWriter(vdata, 'color')
    texcoord = GeomVertexWriter(vdata, 'texcoord')

    for lat in range(segments + 1):
        theta = lat * math.pi / segments
        sin_theta = math.sin(theta)
        cos_theta = math.cos(theta)

        for lon in range(segments + 1):
            phi = lon * 2 * math.pi / segments
            sin_phi = math.sin(phi)
            cos_phi = math.cos(phi)

            x = cos_phi * sin_theta
            y = cos_theta
            z = sin_phi * sin_theta

            vertex.addData3f(radius * x, radius * y, radius * z)
            normal.addData3f(x, y, z)
            color.addData4f(1, 1, 1, 1)
            texcoord.addData2f(lon / segments, lat / segments)

    tris = GeomTriangles(Geom.UHStatic)
    for lat in range(segments):
        for lon in range(segments):
            first = lat * (segments + 1) + lon
            second = first + segments + 1

            tris.addVertices(first, second, first + 1)
            tris.addVertices(second, second + 1, first + 1)
            tris.closePrimitive()

    geom = Geom(vdata)
    geom.addPrimitive(tris)
    node.addGeom(geom)

    np = parent.attachNewNode(node)
    return np


def create_torus(parent: NodePath, outer_radius: float, inner_radius: float, name: str = "torus", segments: int = 24) -> NodePath:
    node = GeomNode(name)

    format = GeomVertexFormat.getV3n3cpt2()
    vdata = GeomVertexData(name, format, Geom.UHStatic)

    vertex = GeomVertexWriter(vdata, 'vertex')
    normal = GeomVertexWriter(vdata, 'normal')
    color = GeomVertexWriter(vdata, 'color')
    texcoord = GeomVertexWriter(vdata, 'texcoord')

    for i in range(segments + 1):
        u = i * 2 * math.pi / segments
        cos_u = math.cos(u)
        sin_u = math.sin(u)

        for j in range(segments + 1):
            v = j * 2 * math.pi / segments
            cos_v = math.cos(v)
            sin_v = math.sin(v)

            r = outer_radius + inner_radius * cos_v

            x = r * cos_u
            y = r * sin_u
            z = inner_radius * sin_v

            nx = cos_v * cos_u
            ny = cos_v * sin_u
            nz = sin_v

            vertex.addData3f(x, y, z)
            normal.addData3f(nx, ny, nz)
            color.addData4f(1, 1, 1, 1)
            texcoord.addData2f(i / segments, j / segments)

    tris = GeomTriangles(Geom.UHStatic)
    for i in range(segments):
        for j in range(segments):
            first = i * (segments + 1) + j
            second = first + segments + 1

            tris.addVertices(first, second, first + 1)
            tris.addVertices(second, second + 1, first + 1)
            tris.closePrimitive()

    geom = Geom(vdata)
    geom.addPrimitive(tris)
    node.addGeom(geom)

    np = parent.attachNewNode(node)
    return np


class GeometryLoader:
    def __init__(self, render: NodePath):
        self.render = render
        self._temp_node = render.attachNewNode("temp_geom")

    def load_box(self) -> NodePath:
        return create_box(self._temp_node, 2, 2, 2, "box")

    def load_sphere(self) -> NodePath:
        return create_sphere(self._temp_node, 1, "sphere")

    def load_torus(self) -> NodePath:
        return create_torus(self._temp_node, 1, 0.3, "torus")
