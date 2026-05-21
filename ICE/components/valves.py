from vpython import cylinder, box, vector, color, label

from ICE.utils.constants import (
    VALVE_RADIUS,
    VALVE_STEM_LENGTH,
    VALVE_HEAD_RADIUS,
    VALVE_LIFT,
    NUM_CYLINDERS,
    CYLINDER_HEIGHT,
    CYLINDER_HEAD_HEIGHT,
    CRANK_THROW,
)
from ICE.utils.materials import STEEL, ENGINE_METAL


class Valves:
    def __init__(self, base_pos, cylinder_x_positions, cylinder_bottom_y):
        self.base_pos = base_pos
        self.cylinder_x_positions = cylinder_x_positions
        self.cylinder_bottom_y = cylinder_bottom_y
        self.intake_valves = []
        self.exhaust_valves = []
        self.valve_springs = []
        self.labels = []
        self._create_valves()
        self._add_labels()

    def _create_valves(self):
        head_bottom_y = self.cylinder_bottom_y + CYLINDER_HEIGHT
        head_top_y = head_bottom_y + CYLINDER_HEAD_HEIGHT

        for i, x_pos in enumerate(self.cylinder_x_positions):
            intake_x = x_pos - 0.5
            exhaust_x = x_pos + 0.5

            intake_stem = cylinder(
                pos=vector(intake_x, head_bottom_y, self.base_pos.z - 0.3),
                axis=vector(0, VALVE_STEM_LENGTH, 0),
                radius=VALVE_RADIUS,
                color=STEEL,
                shininess=0.7
            )

            intake_head = cylinder(
                pos=vector(intake_x, head_bottom_y - 0.1, self.base_pos.z - 0.3),
                axis=vector(0, 0.2, 0),
                radius=VALVE_HEAD_RADIUS,
                color=STEEL,
                shininess=0.7
            )

            intake_spring = cylinder(
                pos=vector(intake_x, head_top_y - 0.5, self.base_pos.z - 0.3),
                axis=vector(0, 0.6, 0),
                radius=0.25,
                color=ENGINE_METAL,
                opacity=0.7
            )

            exhaust_stem = cylinder(
                pos=vector(exhaust_x, head_bottom_y, self.base_pos.z + 0.3),
                axis=vector(0, VALVE_STEM_LENGTH, 0),
                radius=VALVE_RADIUS,
                color=STEEL,
                shininess=0.7
            )

            exhaust_head = cylinder(
                pos=vector(exhaust_x, head_bottom_y - 0.1, self.base_pos.z + 0.3),
                axis=vector(0, 0.2, 0),
                radius=VALVE_HEAD_RADIUS,
                color=STEEL,
                shininess=0.7
            )

            exhaust_spring = cylinder(
                pos=vector(exhaust_x, head_top_y - 0.5, self.base_pos.z + 0.3),
                axis=vector(0, 0.6, 0),
                radius=0.25,
                color=ENGINE_METAL,
                opacity=0.7
            )

            self.intake_valves.append({
                "index": i,
                "stem": intake_stem,
                "head": intake_head,
                "spring": intake_spring,
                "base_y": head_bottom_y,
                "current_lift": 0
            })

            self.exhaust_valves.append({
                "index": i,
                "stem": exhaust_stem,
                "head": exhaust_head,
                "spring": exhaust_spring,
                "base_y": head_bottom_y,
                "current_lift": 0
            })

    def _add_labels(self):
        head_bottom_y = self.cylinder_bottom_y + CYLINDER_HEIGHT
        x_pos = self.cylinder_x_positions[0]

        lbl_intake = label(
            pos=vector(x_pos - 0.5, head_bottom_y - 0.5, self.base_pos.z - 1.5),
            text="进气门\n(Intake Valve)",
            xoffset=-30,
            yoffset=-10,
            color=color.blue,
            background=color.gray(0.3),
            height=11,
            box=True,
            line=True
        )
        self.labels.append(lbl_intake)

        lbl_exhaust = label(
            pos=vector(x_pos + 0.5, head_bottom_y - 0.5, self.base_pos.z + 1.5),
            text="排气门\n(Exhaust Valve)",
            xoffset=30,
            yoffset=-10,
            color=color.green,
            background=color.gray(0.3),
            height=11,
            box=True,
            line=True
        )
        self.labels.append(lbl_exhaust)

    def update_intake_valve(self, cylinder_index, lift):
        valve_data = self.intake_valves[cylinder_index]
        lift = min(lift, VALVE_LIFT)
        valve_data["current_lift"] = lift

        valve_data["stem"].pos.y = valve_data["base_y"] + lift
        valve_data["head"].pos.y = valve_data["base_y"] - 0.1 + lift

    def update_exhaust_valve(self, cylinder_index, lift):
        valve_data = self.exhaust_valves[cylinder_index]
        lift = min(lift, VALVE_LIFT)
        valve_data["current_lift"] = lift

        valve_data["stem"].pos.y = valve_data["base_y"] + lift
        valve_data["head"].pos.y = valve_data["base_y"] - 0.1 + lift

    def is_intake_open(self, cylinder_index):
        return self.intake_valves[cylinder_index]["current_lift"] > 0.05

    def is_exhaust_open(self, cylinder_index):
        return self.exhaust_valves[cylinder_index]["current_lift"] > 0.05

    def set_visibility(self, visible=True):
        for valve_data in self.intake_valves:
            valve_data["stem"].visible = visible
            valve_data["head"].visible = visible
            valve_data["spring"].visible = visible
        for valve_data in self.exhaust_valves:
            valve_data["stem"].visible = visible
            valve_data["head"].visible = visible
            valve_data["spring"].visible = visible
        for lbl in self.labels:
            lbl.visible = visible
