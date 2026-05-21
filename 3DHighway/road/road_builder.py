from panda3d.core import *
from direct.showbase.ShowBase import ShowBase
import math
from config.settings import (
    ROAD_LENGTH, ROAD_WIDTH, LANE_COUNT, LANE_WIDTH,
    LINE_WIDTH, LINE_LENGTH, LINE_GAP
)


class RoadBuilder:
    def __init__(self, render: NodePath, loader: Loader):
        self.render = render
        self.loader = loader
        self.road_root = self.render.attachNewNode("road_root")
        self.road_segments = []
        self.lane_lines = []
        self.edge_lines = []

    def build(self):
        self._create_road_surface()
        self._create_lane_lines()
        self._create_edge_lines()
        self._create_shoulders()
        self._create_environment()
        return self.road_root

    def _create_road_surface(self):
        road_segments = int(ROAD_LENGTH / 100) + 1
        segment_length = ROAD_LENGTH / road_segments

        for i in range(road_segments):
            segment = self.loader.loadModel("models/box")
            segment.reparentTo(self.road_root)
            segment.setScale(ROAD_WIDTH / 2, segment_length / 2, 0.1)
            segment.setPos(0, i * segment_length - ROAD_LENGTH / 2 + segment_length / 2, -0.1)

            material = Material()
            material.setDiffuse((0.15, 0.15, 0.15, 1))
            material.setSpecular((0.05, 0.05, 0.05, 1))
            material.setShininess(5)
            segment.setMaterial(material)

            self.road_segments.append(segment)

    def _create_lane_lines(self):
        segments = int(ROAD_LENGTH / (LINE_LENGTH + LINE_GAP))
        half_road = ROAD_WIDTH / 2

        for lane_idx in range(1, LANE_COUNT):
            lane_x = -half_road + lane_idx * LANE_WIDTH

            for i in range(segments):
                line = self.loader.loadModel("models/box")
                line.reparentTo(self.road_root)
                line.setScale(LINE_WIDTH / 2, LINE_LENGTH / 2, 0.01)
                line.setPos(
                    lane_x,
                    -ROAD_LENGTH / 2 + i * (LINE_LENGTH + LINE_GAP) + LINE_LENGTH / 2,
                    0.005
                )

                material = Material()
                material.setDiffuse((1, 1, 1, 1))
                material.setEmission((0.8, 0.8, 0.8, 1))
                line.setMaterial(material)

                self.lane_lines.append(line)

    def _create_edge_lines(self):
        half_road = ROAD_WIDTH / 2
        edge_offsets = [-half_road + LINE_WIDTH / 2, half_road - LINE_WIDTH / 2]

        for x in edge_offsets:
            line = self.loader.loadModel("models/box")
            line.reparentTo(self.road_root)
            line.setScale(LINE_WIDTH / 2, ROAD_LENGTH / 2, 0.01)
            line.setPos(x, 0, 0.005)

            material = Material()
            material.setDiffuse((1, 1, 0.8, 1))
            material.setEmission((0.9, 0.9, 0.7, 1))
            line.setMaterial(material)

            self.edge_lines.append(line)

    def _create_shoulders(self):
        half_road = ROAD_WIDTH / 2
        shoulder_width = 2.0

        shoulder_data = [
            (-half_road - shoulder_width / 2, shoulder_width, (0.3, 0.3, 0.3, 1)),
            (half_road + shoulder_width / 2, shoulder_width, (0.3, 0.3, 0.3, 1))
        ]

        for x, width, color in shoulder_data:
            shoulder = self.loader.loadModel("models/box")
            shoulder.reparentTo(self.road_root)
            shoulder.setScale(width / 2, ROAD_LENGTH / 2, 0.05)
            shoulder.setPos(x, 0, -0.05)

            material = Material()
            material.setDiffuse(color)
            shoulder.setMaterial(material)

    def _create_environment(self):
        self._create_grass()
        self._create_guardrails()
        self._create_distant_trees()

    def _create_grass(self):
        grass_width = 50.0
        half_road = ROAD_WIDTH / 2

        grass_data = [
            (-half_road - 2.0 - grass_width / 2, grass_width),
            (half_road + 2.0 + grass_width / 2, grass_width)
        ]

        for x, width in grass_data:
            grass = self.loader.loadModel("models/box")
            grass.reparentTo(self.road_root)
            grass.setScale(width / 2, ROAD_LENGTH / 2, 0.1)
            grass.setPos(x, 0, -0.15)

            material = Material()
            material.setDiffuse((0.2, 0.5, 0.2, 1))
            grass.setMaterial(material)

    def _create_guardrails(self):
        half_road = ROAD_WIDTH / 2
        post_spacing = 10.0
        post_count = int(ROAD_LENGTH / post_spacing) + 1

        for side in [-1, 1]:
            x = half_road + 1.0 if side == 1 else -half_road - 1.0

            for i in range(post_count):
                post = self.loader.loadModel("models/box")
                post.reparentTo(self.road_root)
                post.setScale(0.15, 0.15, 0.6)
                post.setPos(side * x, -ROAD_LENGTH / 2 + i * post_spacing, 0.5)

                material = Material()
                material.setDiffuse((0.4, 0.4, 0.4, 1))
                post.setMaterial(material)

            for i in range(3):
                rail = self.loader.loadModel("models/box")
                rail.reparentTo(self.road_root)
                rail.setScale(0.1, ROAD_LENGTH / 2, 0.1)
                rail.setPos(side * x, 0, 0.3 + i * 0.25)

                material = Material()
                material.setDiffuse((0.5, 0.5, 0.5, 1))
                rail.setMaterial(material)

    def _create_distant_trees(self):
        import random
        half_road = ROAD_WIDTH / 2
        tree_count = 100

        for i in range(tree_count):
            side = 1 if random.random() > 0.5 else -1
            x = half_road + 5.0 + random.random() * 30.0
            y = -ROAD_LENGTH / 2 + random.random() * ROAD_LENGTH
            height = 2.0 + random.random() * 3.0

            trunk = self.loader.loadModel("models/box")
            trunk.reparentTo(self.road_root)
            trunk.setScale(0.3, 0.3, height / 2)
            trunk.setPos(side * x, y, height / 2)

            trunk_material = Material()
            trunk_material.setDiffuse((0.4, 0.25, 0.1, 1))
            trunk.setMaterial(trunk_material)

            crown = self.loader.loadModel("models/sphere")
            crown.reparentTo(self.road_root)
            crown.setScale(1.0 + random.random() * 0.5)
            crown.setPos(side * x, y, height + 0.5)

            crown_material = Material()
            green = 0.3 + random.random() * 0.3
            crown_material.setDiffuse((0.1, green, 0.1, 1))
            crown.setMaterial(crown_material)

    def get_lane_center_x(self, lane_index: int) -> float:
        half_road = ROAD_WIDTH / 2
        return -half_road + LANE_WIDTH / 2 + lane_index * LANE_WIDTH

    def get_lane_bounds(self, lane_index: int) -> tuple:
        half_road = ROAD_WIDTH / 2
        left = -half_road + lane_index * LANE_WIDTH
        right = left + LANE_WIDTH
        return (left, right)

    def get_all_lane_bounds(self) -> list:
        bounds = []
        for i in range(LANE_COUNT):
            bounds.append(self.get_lane_bounds(i))
        return bounds
