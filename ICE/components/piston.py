import math
from vpython import cylinder, box, vector, color, label, compound

from ICE.utils.constants import (
    PISTON_RADIUS,
    PISTON_HEIGHT,
    CYLINDER_RADIUS,
    CONNECTING_ROD_LENGTH,
    CRANK_THROW,
    NUM_CYLINDERS,
    CYLINDER_SPACING,
)
from ICE.utils.materials import ALUMINUM, STEEL, ENGINE_METAL


class PistonAssembly:
    def __init__(self, base_pos, cylinder_bottom_y, cylinder_x_positions):
        self.base_pos = base_pos
        self.cylinder_bottom_y = cylinder_bottom_y
        self.cylinder_x_positions = cylinder_x_positions
        self.pistons = []
        self.connecting_rods = []
        self.wrist_pins = []
        self.labels = []
        self._create_pistons()
        self._add_labels()

    def _create_pistons(self):
        for i, x_pos in enumerate(self.cylinder_x_positions):
            piston_cyl = cylinder(
                pos=vector(x_pos, self.cylinder_bottom_y + 0.5, self.base_pos.z),
                axis=vector(0, PISTON_HEIGHT, 0),
                radius=PISTON_RADIUS,
                color=ALUMINUM,
                shininess=0.5
            )

            ring1 = cylinder(
                pos=vector(x_pos, self.cylinder_bottom_y + 0.7, self.base_pos.z),
                axis=vector(0, 0.05, 0),
                radius=PISTON_RADIUS + 0.02,
                color=STEEL
            )
            ring2 = cylinder(
                pos=vector(x_pos, self.cylinder_bottom_y + 0.95, self.base_pos.z),
                axis=vector(0, 0.05, 0),
                radius=PISTON_RADIUS + 0.02,
                color=STEEL
            )
            ring3 = cylinder(
                pos=vector(x_pos, self.cylinder_bottom_y + 1.2, self.base_pos.z),
                axis=vector(0, 0.05, 0),
                radius=PISTON_RADIUS + 0.02,
                color=ENGINE_METAL
            )

            wrist_pin = cylinder(
                pos=vector(x_pos, self.cylinder_bottom_y + PISTON_HEIGHT / 2 + 0.5, self.base_pos.z),
                axis=vector(0, 0, 0.8),
                radius=0.12,
                color=STEEL
            )

            rod_top_pos = vector(x_pos, self.cylinder_bottom_y + PISTON_HEIGHT / 2 + 0.5, self.base_pos.z)
            rod_bottom_pos = vector(x_pos, self.cylinder_bottom_y - CRANK_THROW, self.base_pos.z)

            rod = box(
                pos=(rod_top_pos + rod_bottom_pos) / 2,
                length=0.3,
                width=0.5,
                height=CONNECTING_ROD_LENGTH,
                color=STEEL,
                shininess=0.6
            )
            rod.rotate(angle=0, axis=vector(1, 0, 0))

            self.pistons.append({
                "index": i,
                "x_pos": x_pos,
                "piston": piston_cyl,
                "rings": [ring1, ring2, ring3],
                "rod": rod,
                "wrist_pin": wrist_pin,
                "current_angle": i * 180
            })

    def _add_labels(self):
        x_pos = self.cylinder_x_positions[0]
        y_pos = self.cylinder_bottom_y + PISTON_HEIGHT / 2 + 1

        lbl_piston = label(
            pos=vector(x_pos, y_pos, self.base_pos.z + CYLINDER_RADIUS + 1),
            text="活塞\n(Piston)",
            xoffset=30,
            yoffset=10,
            color=color.white,
            background=ALUMINUM,
            height=12,
            box=True,
            line=True
        )
        self.labels.append(lbl_piston)

        lbl_rod = label(
            pos=vector(x_pos, y_pos - 1.5, self.base_pos.z + CYLINDER_RADIUS + 1),
            text="连杆\n(Connecting Rod)",
            xoffset=30,
            yoffset=0,
            color=color.white,
            background=STEEL,
            height=12,
            box=True,
            line=True
        )
        self.labels.append(lbl_rod)

    def update(self, crank_angle_deg, cylinder_index):
        crank_angle_rad = math.radians(crank_angle_deg)
        piston_data = self.pistons[cylinder_index]

        piston_y = (
            self.cylinder_bottom_y + PISTON_HEIGHT / 2
            + CRANK_THROW * (1 - math.cos(crank_angle_rad))
            + CONNECTING_ROD_LENGTH * (
                1 - math.sqrt(1 - (CRANK_THROW / CONNECTING_ROD_LENGTH) ** 2 * math.sin(crank_angle_rad) ** 2)
            )
        )

        y_offset = piston_y - (self.cylinder_bottom_y + PISTON_HEIGHT / 2)

        piston_data["piston"].pos.y = self.cylinder_bottom_y + 0.5 + y_offset
        piston_data["piston"].axis = vector(0, PISTON_HEIGHT, 0)

        for ring in piston_data["rings"]:
            ring.pos.y = ring.pos.y + y_offset if ring.pos.y < 100 else self.cylinder_bottom_y + 0.7 + y_offset

        ring_heights = [0.7, 0.95, 1.2]
        for idx, ring in enumerate(piston_data["rings"]):
            ring.pos.y = self.cylinder_bottom_y + ring_heights[idx] + y_offset
            ring.axis = vector(0, 0.05, 0)

        piston_data["wrist_pin"].pos.y = self.cylinder_bottom_y + PISTON_HEIGHT / 2 + 0.5 + y_offset

        crank_pin_y = self.base_pos.y - CRANK_THROW * math.cos(crank_angle_rad)
        crank_pin_z = self.base_pos.z + CRANK_THROW * math.sin(crank_angle_rad)
        crank_pin_pos = vector(piston_data["x_pos"], crank_pin_y, crank_pin_z)

        rod_top_pos = vector(
            piston_data["x_pos"],
            self.cylinder_bottom_y + PISTON_HEIGHT / 2 + 0.5 + y_offset,
            self.base_pos.z
        )

        rod_center = (rod_top_pos + crank_pin_pos) / 2
        piston_data["rod"].pos = rod_center

        rod_axis = crank_pin_pos - rod_top_pos
        rod_length = rod_axis.mag
        piston_data["rod"].height = rod_length

        rod_axis = rod_axis.norm()
        up = vector(0, 1, 0)
        piston_data["rod"].axis = rod_axis
        if abs(rod_axis.dot(up)) > 0.99:
            piston_data["rod"].up = vector(1, 0, 0)
        else:
            piston_data["rod"].up = up

        angle = math.atan2(rod_axis.z, rod_axis.y)
        piston_data["rod"].rotate(angle=angle - piston_data.get("last_angle", 0), axis=vector(1, 0, 0))
        piston_data["last_angle"] = angle

        return y_offset

    def get_piston_y(self, cylinder_index):
        return self.pistons[cylinder_index]["piston"].pos.y

    def set_visibility(self, visible=True):
        for piston_data in self.pistons:
            piston_data["piston"].visible = visible
            for ring in piston_data["rings"]:
                ring.visible = visible
            piston_data["rod"].visible = visible
            piston_data["wrist_pin"].visible = visible
        for lbl in self.labels:
            lbl.visible = visible
