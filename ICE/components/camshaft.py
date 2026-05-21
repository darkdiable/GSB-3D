import math
from vpython import cylinder, box, vector, color, label

from ICE.utils.constants import (
    CAMSHAFT_RADIUS,
    CAMSHAFT_LENGTH,
    CAM_HEIGHT,
    CAM_RADIUS,
    NUM_CYLINDERS,
    CYLINDER_SPACING,
    CRANK_THROW,
    CYLINDER_HEIGHT,
    CYLINDER_HEAD_HEIGHT,
)
from ICE.utils.materials import STEEL, CAST_IRON, ENGINE_METAL


class Camshaft:
    def __init__(self, base_pos, cylinder_x_positions, cylinder_bottom_y):
        self.base_pos = base_pos
        self.cylinder_x_positions = cylinder_x_positions
        self.cylinder_bottom_y = cylinder_bottom_y
        self.shaft = None
        self.cams_intake = []
        self.cams_exhaust = []
        self.timing_gear = None
        self.chain = None
        self.labels = []
        self.current_angle = 0
        self._create_camshaft()
        self._add_labels()

    def _create_camshaft(self):
        head_top_y = self.cylinder_bottom_y + CYLINDER_HEIGHT + CYLINDER_HEAD_HEIGHT
        cam_y = head_top_y + 0.8
        start_x = self.base_pos.x - (NUM_CYLINDERS - 1) * CYLINDER_SPACING / 2 - 2

        self.shaft = cylinder(
            pos=vector(start_x, cam_y, self.base_pos.z + 0.5),
            axis=vector(CAMSHAFT_LENGTH, 0, 0),
            radius=CAMSHAFT_RADIUS,
            color=STEEL,
            shininess=0.7
        )

        for i in range(NUM_CYLINDERS):
            x_pos = self.cylinder_x_positions[i]
            cam_angle = i * 90

            intake_cam = cylinder(
                pos=vector(x_pos - 0.3, cam_y, self.base_pos.z + 0.5),
                axis=vector(0.6, 0, 0),
                radius=CAMSHAFT_RADIUS,
                color=CAST_IRON,
                shininess=0.5
            )

            intake_lobe = box(
                pos=vector(x_pos - 0.3, cam_y + CAM_HEIGHT / 2, self.base_pos.z + 0.5),
                length=0.6,
                width=CAM_RADIUS * 2,
                height=CAM_HEIGHT,
                color=CAST_IRON
            )
            intake_lobe.rotate(angle=math.radians(cam_angle), axis=vector(1, 0, 0), origin=intake_cam.pos)

            exhaust_cam = cylinder(
                pos=vector(x_pos + 0.3, cam_y, self.base_pos.z + 0.5),
                axis=vector(0.6, 0, 0),
                radius=CAMSHAFT_RADIUS,
                color=CAST_IRON,
                shininess=0.5
            )

            exhaust_lobe = box(
                pos=vector(x_pos + 0.3, cam_y + CAM_HEIGHT / 2, self.base_pos.z + 0.5),
                length=0.6,
                width=CAM_RADIUS * 2,
                height=CAM_HEIGHT,
                color=CAST_IRON
            )
            exhaust_lobe.rotate(angle=math.radians(cam_angle + 180), axis=vector(1, 0, 0), origin=exhaust_cam.pos)

            self.cams_intake.append({
                "index": i,
                "cam": intake_cam,
                "lobe": intake_lobe,
                "offset_angle": cam_angle
            })
            self.cams_exhaust.append({
                "index": i,
                "cam": exhaust_cam,
                "lobe": exhaust_lobe,
                "offset_angle": cam_angle + 180
            })

        gear_x = start_x + 0.5
        self.timing_gear = cylinder(
            pos=vector(gear_x, cam_y, self.base_pos.z + 0.5),
            axis=vector(0.5, 0, 0),
            radius=0.8,
            color=STEEL,
            shininess=0.6
        )

    def _add_labels(self):
        head_top_y = self.cylinder_bottom_y + CYLINDER_HEIGHT + CYLINDER_HEAD_HEIGHT
        cam_y = head_top_y + 0.8

        lbl_camshaft = label(
            pos=vector(
                self.base_pos.x,
                cam_y + 1,
                self.base_pos.z + 2
            ),
            text="凸轮轴\n(Camshaft)",
            xoffset=0,
            yoffset=20,
            color=color.white,
            background=STEEL,
            height=12,
            box=True,
            line=True
        )
        self.labels.append(lbl_camshaft)

    def update(self, crank_angle_deg):
        cam_angle_deg = (crank_angle_deg / 2) % 360
        self.current_angle = cam_angle_deg
        cam_angle_rad = math.radians(cam_angle_deg)

        for cam_data in self.cams_intake:
            offset_rad = math.radians(cam_data["offset_angle"])
            total_rad = cam_angle_rad + offset_rad
            lobe = cam_data["lobe"]
            cam_pos = cam_data["cam"].pos
            lobe.rotate(angle=0.01, axis=vector(1, 0, 0), origin=cam_pos)

        for cam_data in self.cams_exhaust:
            offset_rad = math.radians(cam_data["offset_angle"])
            total_rad = cam_angle_rad + offset_rad
            lobe = cam_data["lobe"]
            cam_pos = cam_data["cam"].pos
            lobe.rotate(angle=0.01, axis=vector(1, 0, 0), origin=cam_pos)

        self.timing_gear.rotate(angle=0.01, axis=vector(1, 0, 0), origin=self.timing_gear.pos)

    def get_intake_lift(self, cylinder_index):
        cam_data = self.cams_intake[cylinder_index]
        cam_angle_rad = math.radians((self.current_angle + cam_data["offset_angle"]) % 360)
        lift = max(0, math.sin(cam_angle_rad)) * CAM_HEIGHT
        return lift

    def get_exhaust_lift(self, cylinder_index):
        cam_data = self.cams_exhaust[cylinder_index]
        cam_angle_rad = math.radians((self.current_angle + cam_data["offset_angle"]) % 360)
        lift = max(0, math.sin(cam_angle_rad)) * CAM_HEIGHT
        return lift

    def set_visibility(self, visible=True):
        self.shaft.visible = visible
        for cam_data in self.cams_intake:
            cam_data["cam"].visible = visible
            cam_data["lobe"].visible = visible
        for cam_data in self.cams_exhaust:
            cam_data["cam"].visible = visible
            cam_data["lobe"].visible = visible
        self.timing_gear.visible = visible
        for lbl in self.labels:
            lbl.visible = visible
