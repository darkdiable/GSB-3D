import math
from vpython import cylinder, box, vector, color, label, compound

from ICE.utils.constants import (
    CRANKSHAFT_RADIUS,
    CRANKSHAFT_LENGTH,
    CRANK_PIN_RADIUS,
    CRANK_THROW,
    NUM_CYLINDERS,
    CYLINDER_SPACING,
    FIRING_ORDER,
)
from ICE.utils.materials import STEEL, ENGINE_METAL, CAST_IRON


class Crankshaft:
    def __init__(self, base_pos, cylinder_x_positions):
        self.base_pos = base_pos
        self.cylinder_x_positions = cylinder_x_positions
        self.shaft = None
        self.crank_pins = []
        self.crank_webs = []
        self.flywheel = None
        self.pulleys = []
        self.labels = []
        self.current_angle = 0
        self._create_crankshaft()
        self._add_labels()

    def _create_crankshaft(self):
        start_x = self.base_pos.x - (NUM_CYLINDERS - 1) * CYLINDER_SPACING / 2 - 2
        end_x = start_x + CRANKSHAFT_LENGTH

        self.shaft = cylinder(
            pos=vector(start_x, self.base_pos.y, self.base_pos.z),
            axis=vector(CRANKSHAFT_LENGTH, 0, 0),
            radius=CRANKSHAFT_RADIUS,
            color=STEEL,
            shininess=0.7
        )

        for i in range(NUM_CYLINDERS):
            x_pos = self.cylinder_x_positions[i]
            crank_angle = i * 180

            web1 = box(
                pos=vector(x_pos - 0.8, self.base_pos.y, self.base_pos.z),
                length=0.3,
                width=CRANK_THROW * 2 + 0.5,
                height=CRANKSHAFT_RADIUS * 2 + 0.3,
                color=STEEL
            )
            web2 = box(
                pos=vector(x_pos + 0.8, self.base_pos.y, self.base_pos.z),
                length=0.3,
                width=CRANK_THROW * 2 + 0.5,
                height=CRANKSHAFT_RADIUS * 2 + 0.3,
                color=STEEL
            )

            crank_pin = cylinder(
                pos=vector(x_pos - 0.8, self.base_pos.y - CRANK_THROW, self.base_pos.z),
                axis=vector(1.6, 0, 0),
                radius=CRANK_PIN_RADIUS,
                color=CAST_IRON,
                shininess=0.6
            )

            self.crank_webs.extend([web1, web2])
            self.crank_pins.append({
                "index": i,
                "pin": crank_pin,
                "webs": [web1, web2],
                "offset_angle": crank_angle
            })

        flywheel_x = end_x - 0.5
        self.flywheel = cylinder(
            pos=vector(flywheel_x, self.base_pos.y, self.base_pos.z),
            axis=vector(0.6, 0, 0),
            radius=2.0,
            color=CAST_IRON,
            shininess=0.4
        )

        pulley_x = start_x + 0.5
        pulley = cylinder(
            pos=vector(pulley_x, self.base_pos.y, self.base_pos.z),
            axis=vector(0.8, 0, 0),
            radius=1.0,
            color=ENGINE_METAL,
            shininess=0.5
        )
        self.pulleys.append(pulley)

    def _add_labels(self):
        lbl_crankshaft = label(
            pos=vector(
                self.base_pos.x,
                self.base_pos.y - CRANK_THROW - 1,
                self.base_pos.z + 2
            ),
            text="曲轴\n(Crankshaft)",
            xoffset=0,
            yoffset=-20,
            color=color.white,
            background=STEEL,
            height=12,
            box=True,
            line=True
        )
        self.labels.append(lbl_crankshaft)

        lbl_flywheel = label(
            pos=vector(
                self.flywheel.pos.x + self.flywheel.axis.x / 2 + 0.5,
                self.base_pos.y,
                self.base_pos.z + 2
            ),
            text="飞轮\n(Flywheel)",
            xoffset=20,
            yoffset=0,
            color=color.white,
            background=CAST_IRON,
            height=12,
            box=True,
            line=True
        )
        self.labels.append(lbl_flywheel)

    def update(self, crank_angle_deg):
        self.current_angle = crank_angle_deg
        crank_angle_rad = math.radians(crank_angle_deg)

        for pin_data in self.crank_pins:
            offset_rad = math.radians(pin_data["offset_angle"])
            total_rad = crank_angle_rad + offset_rad

            pin_y = self.base_pos.y - CRANK_THROW * math.cos(total_rad)
            pin_z = self.base_pos.z + CRANK_THROW * math.sin(total_rad)
            pin_data["pin"].pos.y = pin_y
            pin_data["pin"].pos.z = pin_z

            for web in pin_data["webs"]:
                center = web.pos
                web.rotate(angle=0.02, axis=vector(1, 0, 0), origin=center)
                web.pos = center

        self.flywheel.rotate(angle=0.02, axis=vector(1, 0, 0), origin=self.flywheel.pos)
        for pulley in self.pulleys:
            pulley.rotate(angle=0.02, axis=vector(1, 0, 0), origin=pulley.pos)

    def get_crank_pin_position(self, cylinder_index):
        pin_data = self.crank_pins[cylinder_index]
        return pin_data["pin"].pos

    def set_visibility(self, visible=True):
        self.shaft.visible = visible
        for pin_data in self.crank_pins:
            pin_data["pin"].visible = visible
            for web in pin_data["webs"]:
                web.visible = visible
        self.flywheel.visible = visible
        for pulley in self.pulleys:
            pulley.visible = visible
        for lbl in self.labels:
            lbl.visible = visible
