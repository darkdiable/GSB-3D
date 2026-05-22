import math
from panda3d.core import *


def create_box(width=1, height=1, depth=1):
    geom_node = _generate_box(width, height, depth)
    return NodePath(geom_node)


def create_sphere(radius=1, segments=16):
    geom_node = _generate_sphere(radius, segments)
    return NodePath(geom_node)


def create_cylinder(radius=1, height=2, segments=16):
    geom_node = _generate_cylinder(radius, height, segments)
    return NodePath(geom_node)


def _generate_box(width=1, height=1, depth=1):
    format = GeomVertexFormat.getV3n3c4()
    vdata = GeomVertexData('box', format, Geom.UHStatic)

    vertex = GeomVertexWriter(vdata, 'vertex')
    normal = GeomVertexWriter(vdata, 'normal')
    color = GeomVertexWriter(vdata, 'color')

    w, h, d = width / 2.0, height / 2.0, depth / 2.0

    vertices = [
        (-w, -h, -d), (w, -h, -d), (w, h, -d), (-w, h, -d),
        (w, -h, d), (-w, -h, d), (-w, h, d), (w, h, d),
        (-w, h, -d), (w, h, -d), (w, h, d), (-w, h, d),
        (-w, -h, d), (w, -h, d), (w, -h, -d), (-w, -h, -d),
        (w, -h, -d), (w, -h, d), (w, h, d), (w, h, -d),
        (-w, -h, d), (-w, -h, -d), (-w, h, -d), (-w, h, d),
    ]

    normals = [
        (0, 0, -1), (0, 0, -1), (0, 0, -1), (0, 0, -1),
        (0, 0, 1), (0, 0, 1), (0, 0, 1), (0, 0, 1),
        (0, 1, 0), (0, 1, 0), (0, 1, 0), (0, 1, 0),
        (0, -1, 0), (0, -1, 0), (0, -1, 0), (0, -1, 0),
        (1, 0, 0), (1, 0, 0), (1, 0, 0), (1, 0, 0),
        (-1, 0, 0), (-1, 0, 0), (-1, 0, 0), (-1, 0, 0),
    ]

    for i in range(24):
        vertex.addData3(*vertices[i])
        normal.addData3(*normals[i])
        color.addData4(1, 1, 1, 1)

    tris = GeomTriangles(Geom.UHStatic)
    for i in range(0, 24, 4):
        tris.addVertices(i, i + 1, i + 2)
        tris.addVertices(i, i + 2, i + 3)

    geom = Geom(vdata)
    geom.addPrimitive(tris)

    node = GeomNode('box')
    node.addGeom(geom)
    return node


def _generate_sphere(radius=1, segments=16):
    format = GeomVertexFormat.getV3n3c4()
    vdata = GeomVertexData('sphere', format, Geom.UHStatic)

    vertex = GeomVertexWriter(vdata, 'vertex')
    normal = GeomVertexWriter(vdata, 'normal')
    color = GeomVertexWriter(vdata, 'color')

    for lat in range(segments + 1):
        theta = math.pi * lat / segments
        sin_theta = math.sin(theta)
        cos_theta = math.cos(theta)

        for lon in range(segments + 1):
            phi = 2 * math.pi * lon / segments
            sin_phi = math.sin(phi)
            cos_phi = math.cos(phi)

            x = cos_phi * sin_theta
            y = sin_phi * sin_theta
            z = cos_theta

            vertex.addData3(x * radius, y * radius, z * radius)
            normal.addData3(x, y, z)
            color.addData4(1, 1, 1, 1)

    tris = GeomTriangles(Geom.UHStatic)
    for lat in range(segments):
        for lon in range(segments):
            first = lat * (segments + 1) + lon
            second = first + segments + 1

            tris.addVertices(first, second, first + 1)
            tris.addVertices(second, second + 1, first + 1)

    geom = Geom(vdata)
    geom.addPrimitive(tris)

    node = GeomNode('sphere')
    node.addGeom(geom)
    return node


def _generate_cylinder(radius=1, height=2, segments=16):
    format = GeomVertexFormat.getV3n3c4()
    vdata = GeomVertexData('cylinder', format, Geom.UHStatic)

    vertex = GeomVertexWriter(vdata, 'vertex')
    normal = GeomVertexWriter(vdata, 'normal')
    color = GeomVertexWriter(vdata, 'color')

    h = height / 2.0
    side_bottom = []
    side_top = []
    bottom_face = []
    top_face = []

    for i in range(segments):
        angle = 2 * math.pi * i / segments
        x = math.cos(angle)
        y = math.sin(angle)

        side_bottom.append(vdata.getNumRows())
        vertex.addData3(x * radius, y * radius, -h)
        normal.addData3(x, y, 0)
        color.addData4(1, 1, 1, 1)

        side_top.append(vdata.getNumRows())
        vertex.addData3(x * radius, y * radius, h)
        normal.addData3(x, y, 0)
        color.addData4(1, 1, 1, 1)

    center_bottom = vdata.getNumRows()
    vertex.addData3(0, 0, -h)
    normal.addData3(0, 0, -1)
    color.addData4(1, 1, 1, 1)

    center_top = vdata.getNumRows()
    vertex.addData3(0, 0, h)
    normal.addData3(0, 0, 1)
    color.addData4(1, 1, 1, 1)

    for i in range(segments):
        angle = 2 * math.pi * i / segments
        x = math.cos(angle)
        y = math.sin(angle)

        bottom_face.append(vdata.getNumRows())
        vertex.addData3(x * radius, y * radius, -h)
        normal.addData3(0, 0, -1)
        color.addData4(1, 1, 1, 1)

        top_face.append(vdata.getNumRows())
        vertex.addData3(x * radius, y * radius, h)
        normal.addData3(0, 0, 1)
        color.addData4(1, 1, 1, 1)

    tris = GeomTriangles(Geom.UHStatic)

    for i in range(segments):
        i1 = side_bottom[i]
        i2 = side_top[i]
        i3 = side_bottom[(i + 1) % segments]
        i4 = side_top[(i + 1) % segments]

        tris.addVertices(i1, i2, i3)
        tris.addVertices(i2, i4, i3)

    for i in range(segments):
        i1 = bottom_face[i]
        i2 = bottom_face[(i + 1) % segments]
        tris.addVertices(center_bottom, i2, i1)

    for i in range(segments):
        i1 = top_face[i]
        i2 = top_face[(i + 1) % segments]
        tris.addVertices(center_top, i1, i2)

    geom = Geom(vdata)
    geom.addPrimitive(tris)

    node = GeomNode('cylinder')
    node.addGeom(geom)
    return node
