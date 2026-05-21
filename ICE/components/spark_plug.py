import math
from vpython import cylinder, sphere, vector, color, label

from ICE.utils.constants import (
    SPARK_PLUG_LENGTH,
    SPARK_PLUG_RADIUS,
    NUM_CYLINDERS,
    CYLINDER_HEIGHT,
    CYLINDER_HEAD_HEIGHT,
    CYLINDER_RADIUS,
)
from ICE.utils.materials import STEEL, COPPER, ENGINE_METAL, EXPLOSION, FUEL, INTAKE_AIR, EXHAUST


class SparkPlug:
    def __init__(self, base_pos, cylinder_x_positions, cylinder_bottom_y):
        self.base_pos = base_pos
        self.cylinder_x_positions = cylinder_x_positions
        self.cylinder_bottom_y = cylinder_bottom_y
        self.spark_plugs = []
        self.sparks = []
        self.combustion_effects = []
        self.intake_effects = []
        self.exhaust_effects = []
        self.labels = []
        self._create_spark_plugs()
        self._add_labels()

    def _create_spark_plugs(self):
        head_bottom_y = self.cylinder_bottom_y + CYLINDER_HEIGHT
        head_top_y = head_bottom_y + CYLINDER_HEAD_HEIGHT

        for i, x_pos in enumerate(self.cylinder_x_positions):
            plug_body = cylinder(
                pos=vector(x_pos, head_top_y - SPARK_PLUG_LENGTH / 2, self.base_pos.z),
                axis=vector(0, SPARK_PLUG_LENGTH, 0),
                radius=SPARK_PLUG_RADIUS,
                color=STEEL,
                shininess=0.6
            )

            plug_tip = cylinder(
                pos=vector(x_pos, head_bottom_y + 0.2, self.base_pos.z),
                axis=vector(0, 0.4, 0),
                radius=SPARK_PLUG_RADIUS * 0.6,
                color=COPPER,
                shininess=0.8
            )

            electrode = cylinder(
                pos=vector(x_pos, head_bottom_y + 0.05, self.base_pos.z),
                axis=vector(0, 0.15, 0),
                radius=SPARK_PLUG_RADIUS * 0.3,
                color=STEEL
            )

            spark = sphere(
                pos=vector(x_pos, head_bottom_y, self.base_pos.z),
                radius=0.1,
                color=EXPLOSION,
                emissive=True,
                visible=False
            )

            combustion = sphere(
                pos=vector(x_pos, head_bottom_y - 0.3, self.base_pos.z),
                radius=0.5,
                color=EXPLOSION,
                emissive=True,
                opacity=0.8,
                visible=False
            )

            intake_cloud = sphere(
                pos=vector(x_pos, head_bottom_y - 0.5, self.base_pos.z - 0.3),
                radius=0.3,
                color=INTAKE_AIR,
                opacity=0.6,
                visible=False
            )

            exhaust_cloud = sphere(
                pos=vector(x_pos, head_bottom_y - 0.5, self.base_pos.z + 0.3),
                radius=0.3,
                color=EXHAUST,
                opacity=0.6,
                visible=False
            )

            self.spark_plugs.append({
                "index": i,
                "body": plug_body,
                "tip": plug_tip,
                "electrode": electrode,
                "x_pos": x_pos
            })
            self.sparks.append(spark)
            self.combustion_effects.append(combustion)
            self.intake_effects.append(intake_cloud)
            self.exhaust_effects.append(exhaust_cloud)

    def _add_labels(self):
        head_bottom_y = self.cylinder_bottom_y + CYLINDER_HEIGHT
        head_top_y = head_bottom_y + CYLINDER_HEAD_HEIGHT
        x_pos = self.cylinder_x_positions[0]

        lbl_spark = label(
            pos=vector(x_pos + 1, head_top_y - 0.3, self.base_pos.z + 1),
            text="火花塞\n(Spark Plug)",
            xoffset=30,
            yoffset=0,
            color=color.white,
            background=COPPER,
            height=12,
            box=True,
            line=True
        )
        self.labels.append(lbl_spark)

    def trigger_spark(self, cylinder_index, intensity=1.0):
        spark = self.sparks[cylinder_index]
        spark.visible = True
        spark.radius = 0.15 * intensity

        combustion = self.combustion_effects[cylinder_index]
        combustion.visible = True
        combustion.radius = 0.8 * intensity
        combustion.opacity = 0.9 * intensity

    def show_intake(self, cylinder_index, intensity=1.0):
        effect = self.intake_effects[cylinder_index]
        effect.visible = True
        effect.opacity = 0.6 * intensity
        effect.pos.y = effect.pos.y

    def show_exhaust(self, cylinder_index, intensity=1.0):
        effect = self.exhaust_effects[cylinder_index]
        effect.visible = True
        effect.opacity = 0.6 * intensity

    def hide_effects(self, cylinder_index):
        self.sparks[cylinder_index].visible = False
        self.combustion_effects[cylinder_index].visible = False
        self.intake_effects[cylinder_index].visible = False
        self.exhaust_effects[cylinder_index].visible = False

    def hide_all_effects(self):
        for i in range(NUM_CYLINDERS):
            self.hide_effects(i)

    def update_combustion(self, cylinder_index, piston_y):
        combustion = self.combustion_effects[cylinder_index]
        if combustion.visible:
            combustion.pos.y = (self.cylinder_bottom_y + CYLINDER_HEIGHT + piston_y) / 2

    def update_intake_position(self, cylinder_index, piston_y):
        effect = self.intake_effects[cylinder_index]
        if effect.visible:
            base_y = (self.cylinder_bottom_y + CYLINDER_HEIGHT + piston_y) / 2
            effect.pos.y = base_y
            effect.pos.z = self.base_pos.z - 0.3

    def update_exhaust_position(self, cylinder_index, piston_y):
        effect = self.exhaust_effects[cylinder_index]
        if effect.visible:
            base_y = (self.cylinder_bottom_y + CYLINDER_HEIGHT + piston_y) / 2
            effect.pos.y = base_y
            effect.pos.z = self.base_pos.z + 0.3

    def set_visibility(self, visible=True):
        for plug_data in self.spark_plugs:
            plug_data["body"].visible = visible
            plug_data["tip"].visible = visible
            plug_data["electrode"].visible = visible
        if not visible:
            self.hide_all_effects()
        for lbl in self.labels:
            lbl.visible = visible
