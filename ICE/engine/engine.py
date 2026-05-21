from vpython import vector, color, label, box

from ICE.utils.constants import (
    BASE_POSITION,
    NUM_CYLINDERS,
    DEGREES_PER_FRAME,
    VALVE_LIFT,
    CYLINDER_HEIGHT,
    CRANK_THROW,
    FIRING_ORDER,
    STROKES,
)
from ICE.components.cylinder import EngineBlock
from ICE.components.piston import PistonAssembly
from ICE.components.crankshaft import Crankshaft
from ICE.components.camshaft import Camshaft
from ICE.components.valves import Valves
from ICE.components.spark_plug import SparkPlug
from ICE.engine.four_stroke import FourStrokeCycle


class FourCylinderEngine:
    def __init__(self, scene):
        self.scene = scene
        self.base_pos = BASE_POSITION
        self.crank_angle = 0
        self.running = True
        self.speed_multiplier = 1.0
        self.show_labels = True
        self.show_effects = True

        self.engine_block = None
        self.piston_assembly = None
        self.crankshaft = None
        self.camshaft = None
        self.valves = None
        self.spark_plug = None
        self.four_stroke = None

        self.cylinder_labels = []
        self.stroke_info_labels = []
        self.info_panel = None

        self._build_engine()
        self._create_ui_elements()

    def _build_engine(self):
        self.engine_block = EngineBlock(self.base_pos)

        cylinder_x_positions = self.engine_block.get_cylinder_positions()
        cylinder_bottom_y = self.engine_block.get_cylinder_bottom_y()

        self.piston_assembly = PistonAssembly(
            self.base_pos,
            cylinder_bottom_y,
            cylinder_x_positions
        )

        self.crankshaft = Crankshaft(self.base_pos, cylinder_x_positions)
        self.camshaft = Camshaft(self.base_pos, cylinder_x_positions, cylinder_bottom_y)
        self.valves = Valves(self.base_pos, cylinder_x_positions, cylinder_bottom_y)
        self.spark_plug = SparkPlug(self.base_pos, cylinder_x_positions, cylinder_bottom_y)
        self.four_stroke = FourStrokeCycle()

    def _create_ui_elements(self):
        cylinder_x_positions = self.engine_block.get_cylinder_positions()
        cylinder_bottom_y = self.engine_block.get_cylinder_bottom_y()

        for i, x_pos in enumerate(cylinder_x_positions):
            lbl = label(
                pos=vector(x_pos, cylinder_bottom_y + CYLINDER_HEIGHT + 3.5, self.base_pos.z),
                text=f"缸 {i+1}\n(Cylinder {i+1})",
                yoffset=5,
                color=color.white,
                background=color.gray(0.3),
                height=11,
                box=True,
                line=True
            )
            self.cylinder_labels.append(lbl)

        stroke_panel_y = cylinder_bottom_y + CYLINDER_HEIGHT + 4.5

        for i, stroke in enumerate(STROKES):
            x_pos = self.base_pos.x - 6 + i * 4
            box(
                pos=vector(x_pos, stroke_panel_y, self.base_pos.z + 4),
                length=3.5,
                width=0.1,
                height=1.2,
                color=stroke["color"],
                opacity=0.7
            )
            lbl = label(
                pos=vector(x_pos, stroke_panel_y, self.base_pos.z + 4),
                text=f"{stroke['name']}\n{stroke['name_en']}",
                color=color.white,
                height=10,
                box=False,
                line=False
            )
            self.stroke_info_labels.append(lbl)

        self.info_panel = label(
            pos=vector(self.base_pos.x, cylinder_bottom_y - CRANK_THROW - 3, self.base_pos.z),
            text="",
            color=color.white,
            background=color.gray(0.2),
            height=12,
            box=True,
            line=False,
            yoffset=-10
        )

        firing_order_lbl = label(
            pos=vector(self.base_pos.x + 8, cylinder_bottom_y + CYLINDER_HEIGHT / 2, self.base_pos.z + 3),
            text=f"点火顺序: {' → '.join([str(i+1) for i in FIRING_ORDER])}\n(Firing Order)",
            color=color.yellow,
            background=color.gray(0.3),
            height=11,
            box=True,
            line=True,
            xoffset=20
        )
        self.cylinder_labels.append(firing_order_lbl)

    def update(self):
        if not self.running:
            return

        delta_angle = DEGREES_PER_FRAME * self.speed_multiplier
        self.crank_angle += delta_angle
        self.crank_angle = self.crank_angle % 720

        self.crankshaft.update(self.crank_angle)
        self.camshaft.update(self.crank_angle)

        for i in range(NUM_CYLINDERS):
            cyl_angle = self.crank_angle + i * 180
            self.piston_assembly.update(cyl_angle, i)

            intake_lift, exhaust_lift = self.four_stroke.get_valve_timing(i, self.crank_angle)
            self.valves.update_intake_valve(i, intake_lift * VALVE_LIFT)
            self.valves.update_exhaust_valve(i, exhaust_lift * VALVE_LIFT)

            piston_y = self.piston_assembly.get_piston_y(i)

            if self.show_effects:
                if self.four_stroke.is_intake_stroke(i, self.crank_angle):
                    self.spark_plug.hide_effects(i)
                    self.spark_plug.show_intake(i, 0.8)
                    self.spark_plug.update_intake_position(i, piston_y)

                elif self.four_stroke.should_spark(i, self.crank_angle):
                    self.spark_plug.hide_effects(i)
                    self.spark_plug.trigger_spark(i, 1.0)

                elif self.four_stroke.is_power_stroke(i, self.crank_angle):
                    stroke_progress = self.four_stroke.get_stroke_progress(i, self.crank_angle)
                    if stroke_progress < 0.6:
                        self.spark_plug.combustion_effects[i].visible = True
                        self.spark_plug.combustion_effects[i].opacity = 0.9 * (1 - stroke_progress)
                        self.spark_plug.update_combustion(i, piston_y)
                    else:
                        self.spark_plug.hide_effects(i)

                elif self.four_stroke.is_exhaust_stroke(i, self.crank_angle):
                    self.spark_plug.hide_effects(i)
                    self.spark_plug.show_exhaust(i, 0.7)
                    self.spark_plug.update_exhaust_position(i, piston_y)

                else:
                    self.spark_plug.hide_effects(i)
            else:
                self.spark_plug.hide_all_effects()

        self._update_info_panel()

    def _update_info_panel(self):
        info_text = "四缸四冲程发动机工作原理\n"
        info_text += "4-Cylinder 4-Stroke Engine Simulation\n\n"
        info_text += f"曲轴角度: {self.crank_angle:.1f}°\n"
        info_text += f"转速: {600 * self.speed_multiplier:.0f} RPM\n\n"
        info_text += "各缸工作状态:\n"

        all_strokes = self.four_stroke.get_all_cylinder_strokes(self.crank_angle)
        for stroke_info in all_strokes:
            cyl_num = stroke_info["cylinder"] + 1
            stroke_name = stroke_info["stroke_name"]
            progress = self.four_stroke.get_stroke_progress(stroke_info["cylinder"], self.crank_angle)
            info_text += f"  缸{cyl_num}: {stroke_name} ({progress*100:.0f}%)\n"

        self.info_panel.text = info_text

    def toggle_running(self):
        self.running = not self.running
        return self.running

    def set_speed(self, multiplier):
        self.speed_multiplier = max(0.1, min(5.0, multiplier))

    def increase_speed(self):
        self.set_speed(self.speed_multiplier + 0.2)

    def decrease_speed(self):
        self.set_speed(self.speed_multiplier - 0.2)

    def toggle_labels(self):
        self.show_labels = not self.show_labels
        self.engine_block.set_visibility(self.show_labels or True)
        if not self.show_labels:
            for lbl in self.cylinder_labels:
                lbl.visible = False
            for lbl in self.stroke_info_labels:
                lbl.visible = False
            self.info_panel.visible = False
        else:
            for lbl in self.cylinder_labels:
                lbl.visible = True
            for lbl in self.stroke_info_labels:
                lbl.visible = True
            self.info_panel.visible = True
        return self.show_labels

    def toggle_effects(self):
        self.show_effects = not self.show_effects
        return self.show_effects

    def reset(self):
        self.crank_angle = 0
        self.speed_multiplier = 1.0
        self.running = True
        self.spark_plug.hide_all_effects()
