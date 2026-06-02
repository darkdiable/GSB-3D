#!/usr/bin/env python3
"""
四缸四冲程发动机核心逻辑
4-Cylinder 4-Stroke Engine Core Logic
"""

import math
from vpython import vector, color, local_light, distant_light

from ice3D.config.settings import (
    ENGINE_GEOMETRY,
    ENGINE_POSITION,
    STROKES,
    CYLINDER_PHASE_OFFSETS,
    FIRING_ORDER,
    ANIMATION_CONFIG,
    COLORS,
)
from ice3D.components.engine_block import EngineBlock
from ice3D.components.cylinder import Cylinder
from ice3D.components.piston import Piston
from ice3D.components.connecting_rod import ConnectingRod
from ice3D.components.crankshaft import Crankshaft
from ice3D.components.valves import Valve, SparkPlug
from ice3D.components.visual_effects import CombustionEffect, AirFlowEffect


class CylinderUnit:
    def __init__(self, scene, cylinder_index):
        self.scene = scene
        self.index = cylinder_index
        self.geo = ENGINE_GEOMETRY
        self.pos = ENGINE_POSITION
        self.phase_offset = math.radians(CYLINDER_PHASE_OFFSETS[cylinder_index])
        
        self.cylinder = Cylinder(scene, cylinder_index)
        self.piston = Piston(scene, cylinder_index)
        self.connecting_rod = ConnectingRod(scene, cylinder_index)
        self.intake_valve = Valve(scene, cylinder_index, "intake")
        self.exhaust_valve = Valve(scene, cylinder_index, "exhaust")
        self.spark_plug = SparkPlug(scene, cylinder_index)
        self.combustion = CombustionEffect(scene, cylinder_index)
        self.airflow = AirFlowEffect(scene, cylinder_index)
        
        self.current_stroke = 0
        self.cycle_angle = 0
        self.ignition_occurred = False
    
    def get_piston_y_from_crank_angle(self, crank_angle):
        stroke = self.geo["stroke_length"] / 2
        rod_length = self.geo["connecting_rod_length"]
        
        effective_angle = crank_angle + self.phase_offset
        
        piston_y_from_crank = stroke * math.cos(effective_angle)
        rod_angle = math.asin((stroke / rod_length) * math.sin(effective_angle))
        piston_y_from_rod = rod_length * math.cos(rod_angle)
        
        total_piston_y = piston_y_from_crank + piston_y_from_rod
        
        base_y = self.pos["crankshaft_y"] + rod_length
        return base_y - (stroke + rod_length - total_piston_y) + self.geo["piston_height"] / 2
    
    def get_current_stroke(self, crank_angle):
        effective_angle = (math.degrees(crank_angle) + CYLINDER_PHASE_OFFSETS[self.index]) % 720
        
        for stroke in STROKES:
            if stroke["angle_start"] <= effective_angle < stroke["angle_end"]:
                return stroke, effective_angle
        
        return STROKES[0], effective_angle
    
    def update(self, dt, crank_angle, crankshaft):
        piston_y = self.get_piston_y_from_crank_angle(crank_angle)
        self.piston.update_position(piston_y)
        
        crank_pin_pos = crankshaft.get_crank_pin_position(self.index)
        wrist_pin_pos = self.piston.get_wrist_pin_position()
        self.connecting_rod.update_position(crank_pin_pos, wrist_pin_pos)
        
        stroke, cycle_angle = self.get_current_stroke(crank_angle)
        self.current_stroke = stroke["id"]
        self.cycle_angle = cycle_angle
        
        self._update_valves(stroke, cycle_angle)
        self._update_ignition(stroke, cycle_angle)
        self._update_visual_effects(dt, stroke, piston_y)
    
    def _update_valves(self, stroke, cycle_angle):
        stroke_progress = (cycle_angle - stroke["angle_start"]) / 180.0
        
        intake_lift = 0
        exhaust_lift = 0
        
        if stroke["intake_valve_open"]:
            if stroke_progress < 0.1:
                intake_lift = stroke_progress / 0.1
            elif stroke_progress > 0.9:
                intake_lift = (1 - stroke_progress) / 0.1
            else:
                intake_lift = 1.0
        elif stroke["id"] == 0 and stroke_progress < 0.05:
            intake_lift = 1 - stroke_progress / 0.05
        elif stroke["id"] == 3 and stroke_progress > 0.95:
            intake_lift = (stroke_progress - 0.95) / 0.05
        
        if stroke["exhaust_valve_open"]:
            if stroke_progress < 0.1:
                exhaust_lift = stroke_progress / 0.1
            elif stroke_progress > 0.9:
                exhaust_lift = (1 - stroke_progress) / 0.1
            else:
                exhaust_lift = 1.0
        elif stroke["id"] == 2 and stroke_progress > 0.9:
            exhaust_lift = (stroke_progress - 0.9) / 0.1
        elif stroke["id"] == 3 and stroke_progress < 0.05:
            exhaust_lift = 1 - stroke_progress / 0.05
        
        self.intake_valve.set_lift(intake_lift)
        self.exhaust_valve.set_lift(exhaust_lift)
    
    def _update_ignition(self, stroke, cycle_angle):
        if stroke["id"] == 1:
            stroke_progress = (cycle_angle - stroke["angle_start"]) / 180.0
            if stroke_progress > 0.9 and not self.ignition_occurred:
                self.ignition_occurred = True
                self.spark_plug.set_spark_visible(True)
                self.combustion.ignite(intensity=1.0)
            elif stroke_progress <= 0.9:
                self.ignition_occurred = False
                self.spark_plug.set_spark_visible(False)
        else:
            self.ignition_occurred = False
            self.spark_plug.set_spark_visible(False)
    
    def _update_visual_effects(self, dt, stroke, piston_y):
        self.combustion.update(dt, piston_y)
        
        is_intake = stroke["intake_valve_open"]
        is_exhaust = stroke["exhaust_valve_open"]
        
        self.airflow.update(dt, is_intake, is_exhaust, piston_y)
    
    def set_cutaway(self, cutaway):
        self.cylinder.set_cutaway(cutaway)
    
    def toggle_visibility(self, visible):
        self.cylinder.toggle_visibility(visible)
        self.piston.toggle_visibility(visible)
        self.connecting_rod.toggle_visibility(visible)
        self.intake_valve.toggle_visibility(visible)
        self.exhaust_valve.toggle_visibility(visible)
        self.spark_plug.toggle_visibility(visible)
        self.combustion.toggle_visibility(visible)
        self.airflow.toggle_visibility(visible)


class FourStrokeEngine:
    def __init__(self, scene):
        self.scene = scene
        self.geo = ENGINE_GEOMETRY
        self.pos = ENGINE_POSITION
        self.anim_config = ANIMATION_CONFIG
        self.colors = COLORS
        
        self.running = True
        self.speed_multiplier = self.anim_config["default_speed"]
        self.crank_angle = 0
        self.show_labels = True
        self.cutaway_mode = False
        self.focus_cylinder = None
        
        self.engine_block = None
        self.crankshaft = None
        self.cylinder_units = []
        
        self._create_lighting()
        self._create_engine_block()
        self._create_crankshaft()
        self._create_cylinders()
    
    def _create_lighting(self):
        local_light(pos=vector(0, 5, 5), color=color.white)
        distant_light(direction=vector(1, 0.5, 1), color=color.gray(0.4))
        distant_light(direction=vector(-1, -0.5, -1), color=color.gray(0.2))
    
    def _create_engine_block(self):
        self.engine_block = EngineBlock(self.scene)
    
    def _create_crankshaft(self):
        self.crankshaft = Crankshaft(self.scene)
    
    def _create_cylinders(self):
        for i in range(4):
            cylinder_unit = CylinderUnit(self.scene, i)
            self.cylinder_units.append(cylinder_unit)
    
    def update(self, dt):
        if not self.running:
            return
        
        adjusted_dt = dt * self.anim_config["crankshaft_speed"] * self.speed_multiplier
        self.crank_angle += adjusted_dt
        
        if self.crank_angle >= 4 * math.pi:
            self.crank_angle -= 4 * math.pi
        
        self.crankshaft.update_rotation(self.crank_angle)
        
        for cylinder_unit in self.cylinder_units:
            cylinder_unit.update(dt, self.crank_angle, self.crankshaft)
    
    def get_cylinder_stroke(self, cylinder_index):
        if 0 <= cylinder_index < len(self.cylinder_units):
            return self.cylinder_units[cylinder_index].current_stroke
        return 0
    
    def get_cylinder_stroke_info(self, cylinder_index):
        if 0 <= cylinder_index < len(self.cylinder_units):
            unit = self.cylinder_units[cylinder_index]
            return STROKES[unit.current_stroke], unit.cycle_angle
        return STROKES[0], 0
    
    def toggle_running(self):
        self.running = not self.running
        return self.running
    
    def set_speed(self, multiplier):
        self.speed_multiplier = max(
            self.anim_config["min_speed"],
            min(self.anim_config["max_speed"], multiplier)
        )
    
    def increase_speed(self):
        self.set_speed(self.speed_multiplier + self.anim_config["speed_step"])
    
    def decrease_speed(self):
        self.set_speed(self.speed_multiplier - self.anim_config["speed_step"])
    
    def toggle_labels(self):
        self.show_labels = not self.show_labels
        return self.show_labels
    
    def toggle_cutaway(self):
        self.cutaway_mode = not self.cutaway_mode
        for unit in self.cylinder_units:
            unit.set_cutaway(self.cutaway_mode)
        if self.cutaway_mode:
            self.engine_block.set_opacity(0.3)
        else:
            self.engine_block.set_opacity(0.85)
        return self.cutaway_mode
    
    def focus_on_cylinder(self, cylinder_index):
        if cylinder_index is None:
            self.focus_cylinder = None
            for unit in self.cylinder_units:
                unit.toggle_visibility(True)
        else:
            self.focus_cylinder = cylinder_index
            for i, unit in enumerate(self.cylinder_units):
                unit.toggle_visibility(i == cylinder_index)
    
    def reset(self):
        self.crank_angle = 0
        self.running = True
        self.speed_multiplier = self.anim_config["default_speed"]
        self.cutaway_mode = False
        self.focus_cylinder = None
        self.show_labels = True
        
        for unit in self.cylinder_units:
            unit.toggle_visibility(True)
            unit.set_cutaway(False)
            unit.airflow.clear_all()
            unit.combustion.extinguish()
        
        self.engine_block.set_opacity(0.85)
    
    def get_rpm(self):
        if not self.running:
            return 0
        rotations_per_second = (self.anim_config["crankshaft_speed"] * self.speed_multiplier) / (2 * math.pi)
        return rotations_per_second * 60
    
    def get_firing_order(self):
        return [FIRING_ORDER.index(i) + 1 for i in range(4)]
