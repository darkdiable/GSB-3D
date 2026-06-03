import math
from panda3d.core import (
    GeomVertexData, GeomVertexFormat, GeomVertexWriter,
    Geom, GeomTriangles, GeomNode, NodePath, LVector3f
)
from config.settings import Config


class Highway:
    def __init__(self, render):
        self.render = render
        self.road_segments = []
        self.line_segments = []
        self.grass_segments = []
        self.env_segments = []

    def _make_quad(self, name, v0, v1, v2, v3, color):
        vdata = GeomVertexData(name, GeomVertexFormat.getV3c4(), Geom.UHStatic)
        vertex = GeomVertexWriter(vdata, 'vertex')
        color_writer = GeomVertexWriter(vdata, 'color')
        for v in [v0, v1, v2, v3]:
            vertex.addData3f(*v)
            color_writer.addData4f(*color)
        prim = GeomTriangles(Geom.UHStatic)
        prim.addVertices(0, 1, 2)
        prim.addVertices(0, 2, 3)
        geom = Geom(vdata)
        geom.addPrimitive(prim)
        node = GeomNode(name)
        node.addGeom(geom)
        np = NodePath(node)
        np.setLightOff()
        return np

    def create_road_segment(self, segment_start, segment_end):
        road_half_width = (Config.LANE_WIDTH * Config.LANE_COUNT) / 2
        shoulder_width = 1.5
        total_half_width = road_half_width + shoulder_width

        parent = NodePath('road_seg')

        road = self._make_quad('road',
            (segment_start, -total_half_width, 0.0),
            (segment_end,   -total_half_width, 0.0),
            (segment_end,    total_half_width, 0.0),
            (segment_start,  total_half_width, 0.0),
            (0.15, 0.15, 0.15, 1))
        road.reparentTo(parent)

        surface = self._make_quad('road_surface',
            (segment_start, -road_half_width, 0.01),
            (segment_end,   -road_half_width, 0.01),
            (segment_end,    road_half_width, 0.01),
            (segment_start,  road_half_width, 0.01),
            Config.ROAD_COLOR)
        surface.reparentTo(parent)

        shoulder_color_l = (0.6, 0.6, 0.5, 1)
        shoulder_color_r = (0.6, 0.6, 0.5, 1)
        shoulder_l = self._make_quad('shoulder_l',
            (segment_start, -total_half_width, 0.005),
            (segment_end,   -total_half_width, 0.005),
            (segment_end,   -road_half_width,  0.005),
            (segment_start, -road_half_width,  0.005),
            shoulder_color_l)
        shoulder_l.reparentTo(parent)

        shoulder_r = self._make_quad('shoulder_r',
            (segment_start, road_half_width,  0.005),
            (segment_end,   road_half_width,  0.005),
            (segment_end,   total_half_width, 0.005),
            (segment_start, total_half_width, 0.005),
            shoulder_color_r)
        shoulder_r.reparentTo(parent)

        return parent

    def create_line_segment(self, segment_start, segment_end, y_pos, is_dashed=False, color=None):
        if color is None:
            color = Config.LINE_COLOR
        line_half_width = Config.LINE_WIDTH / 2

        parent = NodePath('line_seg')

        if is_dashed:
            dash_length = 4.0
            gap_length = 4.0
            current_pos = segment_start
            while current_pos < segment_end:
                dash_end = min(current_pos + dash_length, segment_end)
                dash = self._make_quad('dash',
                    (current_pos, y_pos - line_half_width, 0.02),
                    (dash_end,   y_pos - line_half_width, 0.02),
                    (dash_end,   y_pos + line_half_width, 0.02),
                    (current_pos, y_pos + line_half_width, 0.02),
                    color)
                dash.reparentTo(parent)
                current_pos += dash_length + gap_length
        else:
            line = self._make_quad('solid_line',
                (segment_start, y_pos - line_half_width, 0.02),
                (segment_end,   y_pos - line_half_width, 0.02),
                (segment_end,   y_pos + line_half_width, 0.02),
                (segment_start, y_pos + line_half_width, 0.02),
                color)
            line.reparentTo(parent)

        return parent

    def create_grass_segment(self, segment_start, segment_end):
        road_half_width = (Config.LANE_WIDTH * Config.LANE_COUNT) / 2
        shoulder_width = 1.5
        grass_extent = 80.0

        parent = NodePath('grass_seg')

        grass_l = self._make_quad('grass_l',
            (segment_start, -(road_half_width + shoulder_width + grass_extent), -0.05),
            (segment_end,   -(road_half_width + shoulder_width + grass_extent), -0.05),
            (segment_end,   -(road_half_width + shoulder_width),               -0.05),
            (segment_start, -(road_half_width + shoulder_width),               -0.05),
            Config.GRASS_COLOR)
        grass_l.reparentTo(parent)

        grass_r = self._make_quad('grass_r',
            (segment_start, (road_half_width + shoulder_width),               -0.05),
            (segment_end,   (road_half_width + shoulder_width),               -0.05),
            (segment_end,   (road_half_width + shoulder_width + grass_extent), -0.05),
            (segment_start, (road_half_width + shoulder_width + grass_extent), -0.05),
            Config.GRASS_COLOR)
        grass_r.reparentTo(parent)

        return parent

    def create_guardrail(self, segment_start, segment_end, y_pos):
        post_interval = 10.0
        post_height = 0.8
        post_width = 0.15
        rail_height = 0.1
        rail_width = 0.3
        rail_z = 0.4

        parent = NodePath('guardrail')

        rail = self._make_quad('rail_top',
            (segment_start, y_pos - rail_width / 2, rail_z + rail_height / 2),
            (segment_end,   y_pos - rail_width / 2, rail_z + rail_height / 2),
            (segment_end,   y_pos + rail_width / 2, rail_z + rail_height / 2),
            (segment_start, y_pos + rail_width / 2, rail_z + rail_height / 2),
            (0.7, 0.7, 0.7, 1))
        rail.reparentTo(parent)

        rail_front = self._make_quad('rail_front',
            (segment_start, y_pos - rail_width / 2, rail_z - rail_height / 2),
            (segment_end,   y_pos - rail_width / 2, rail_z - rail_height / 2),
            (segment_end,   y_pos - rail_width / 2, rail_z + rail_height / 2),
            (segment_start, y_pos - rail_width / 2, rail_z + rail_height / 2),
            (0.8, 0.8, 0.8, 1))
        rail_front.reparentTo(parent)

        pos = segment_start
        while pos < segment_end:
            post = self._make_box(f'post_{pos}',
                (pos, y_pos, post_height / 2),
                (post_width, post_width, post_height),
                (0.5, 0.5, 0.5, 1))
            post.reparentTo(parent)
            pos += post_interval

        return parent

    def _make_box(self, name, center, size, color):
        cx, cy, cz = center
        sx, sy, sz = size
        vdata = GeomVertexData(name, GeomVertexFormat.getV3c4(), Geom.UHStatic)
        vertex = GeomVertexWriter(vdata, 'vertex')
        color_writer = GeomVertexWriter(vdata, 'color')

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

    def create_tree(self, x, y):
        parent = NodePath('tree')
        trunk = self._make_box('trunk', (x, y, 1.5), (0.3, 0.3, 3.0), (0.4, 0.25, 0.1, 1))
        trunk.reparentTo(parent)
        foliage = self._make_box('foliage', (x, y, 4.0), (2.0, 2.0, 2.5), (0.1, 0.5, 0.1, 1))
        foliage.reparentTo(parent)
        foliage2 = self._make_box('foliage2', (x, y, 5.5), (1.2, 1.2, 1.5), (0.15, 0.6, 0.15, 1))
        foliage2.reparentTo(parent)
        return parent

    def create_distance_marker(self, x, y, km):
        parent = NodePath('marker')
        pole = self._make_box('pole', (x, y, 1.0), (0.1, 0.1, 2.0), (0.6, 0.6, 0.6, 1))
        pole.reparentTo(parent)
        sign = self._make_box('sign', (x, y, 2.3), (0.8, 0.05, 0.6), (0.1, 0.4, 0.8, 1))
        sign.reparentTo(parent)
        return parent

    def create_building(self, x, y, width, depth, height, color):
        parent = NodePath('building')
        bld = self._make_box('bld', (x + width/2, y + depth/2, height/2),
                             (width, depth, height), color)
        bld.reparentTo(parent)
        return parent

    def build(self):
        segment_length = 200
        num_segments = int(Config.ROAD_LENGTH // segment_length) + 1

        road_half_width = (Config.LANE_WIDTH * Config.LANE_COUNT) / 2
        shoulder_width = 1.5
        guardrail_y_offset = road_half_width + shoulder_width * 0.5

        for i in range(num_segments):
            start = i * segment_length
            end = (i + 1) * segment_length

            road_segment = self.create_road_segment(start, end)
            road_segment.reparentTo(self.render)
            self.road_segments.append(road_segment)

            grass_segment = self.create_grass_segment(start, end)
            grass_segment.reparentTo(self.render)
            self.grass_segments.append(grass_segment)

            edge_color = (1.0, 1.0, 1.0, 1)
            lane_color = (1.0, 1.0, 1.0, 1)

            for lane in range(Config.LANE_COUNT + 1):
                y_pos = -road_half_width + lane * Config.LANE_WIDTH
                is_dashed = 0 < lane < Config.LANE_COUNT
                color = edge_color if not is_dashed else lane_color
                line_segment = self.create_line_segment(start, end, y_pos, is_dashed, color)
                line_segment.reparentTo(self.render)
                self.line_segments.append(line_segment)

            guardrail_l = self.create_guardrail(start, end, -(road_half_width + shoulder_width))
            guardrail_l.reparentTo(self.render)
            self.env_segments.append(guardrail_l)

            guardrail_r = self.create_guardrail(start, end, (road_half_width + shoulder_width))
            guardrail_r.reparentTo(self.render)
            self.env_segments.append(guardrail_r)

        tree_distance = road_half_width + shoulder_width + 8.0
        for x in range(0, int(Config.ROAD_LENGTH), 25):
            offset = 12.5 if (x // 25) % 2 == 0 else 0
            tree_l = self.create_tree(x + offset, -tree_distance)
            tree_l.reparentTo(self.render)
            self.env_segments.append(tree_l)

            tree_r = self.create_tree(x, tree_distance)
            tree_r.reparentTo(self.render)
            self.env_segments.append(tree_r)

        for x in range(0, int(Config.ROAD_LENGTH), 100):
            marker_l = self.create_distance_marker(x, -(road_half_width + shoulder_width + 2.0), x // 1000)
            marker_l.reparentTo(self.render)
            self.env_segments.append(marker_l)

        building_distance = road_half_width + shoulder_width + 40.0
        building_colors = [
            (0.6, 0.55, 0.5, 1),
            (0.5, 0.5, 0.55, 1),
            (0.55, 0.5, 0.45, 1),
            (0.65, 0.6, 0.55, 1),
        ]
        for x in range(0, int(Config.ROAD_LENGTH), 60):
            color = building_colors[(x // 60) % len(building_colors)]
            height = 6.0 + (x * 7 % 13)
            width = 10.0 + (x * 3 % 8)
            depth = 8.0 + (x * 5 % 6)

            bld_l = self.create_building(x, -building_distance - depth / 2, width, depth, height, color)
            bld_l.reparentTo(self.render)
            self.env_segments.append(bld_l)

            bld_r = self.create_building(x + 30, building_distance + depth / 2, width, depth, height * 0.8, color)
            bld_r.reparentTo(self.render)
            self.env_segments.append(bld_r)

    def get_lane_center(self, lane_index):
        road_half_width = (Config.LANE_WIDTH * Config.LANE_COUNT) / 2
        return -road_half_width + (lane_index + 0.5) * Config.LANE_WIDTH

    def get_road_bounds(self):
        road_half_width = (Config.LANE_WIDTH * Config.LANE_COUNT) / 2
        return (-road_half_width, road_half_width)

    def get_lane_lines(self):
        road_half_width = (Config.LANE_WIDTH * Config.LANE_COUNT) / 2
        lines = []
        for lane in range(Config.LANE_COUNT + 1):
            lines.append(-road_half_width + lane * Config.LANE_WIDTH)
        return lines
