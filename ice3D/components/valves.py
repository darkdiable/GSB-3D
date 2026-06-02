#!/usr/bin/env python3
"""
气门组件
Valve Component - intake and exhaust valves with actuation
"""

import math
from vpython import cylinder, vector, color, sphere

from ice3D.config.settings import ENGINE_GEOMETRY, ENGINE_POSITION, COLORS


class Valve:
    def __init__(self, scene, cylinder_index, valve_type):
        self.scene = scene
        self.geo = ENGINE_GEOMETRY
        self.pos = ENGINE_POSITION
        self.colors = COLORS
        self.index = cylinder_index
        self.valve_type = valve_type
        
        self.x_offset = (cylinder_index - 1.5) * self.geo["cylinder_spacing"]
        self.z_offset = 0.6 if valve_type == "intake" else -0.6
        
        self.head_y = self.pos["cylinder_y_offset"] + self.geo["cylinder_height"] + self.geo["cylinder_head_height"] / 2
        
        self.valve_stem = None
        self.valve_head = None
        self.valve_spring = None
        self.components = []
        
        self.base_y = self.head_y - self.geo["cylinder_head_height"] / 2 + 0.1
        self.current_lift = 0
        self.max_lift = self.geo["valve_lift"]
        
        self._create_valve()
    
    def _create_valve(self):
        valve_color = self.colors["intake_valve"] if self.valve_type == "intake" else self.colors["exhaust_valve"]
        
        self.valve_stem = cylinder(
            pos=vector(
                self.pos["center"].x + self.x_offset,
                self.base_y,
                self.pos["center"].z + self.z_offset
            ),
            axis=vector(0, 1, 0),
            radius=self.geo["valve_stem_radius"],
            length=self.geo["valve_length"],
            color=valve_color,
        )
        self.components.append(self.valve_stem)
        
        self.valve_head = sphere(
            pos=vector(
                self.pos["center"].x + self.x_offset,
                self.base_y - 0.05,
                self.pos["center"].z + self.z_offset
            ),
            radius=self.geo["valve_radius"],
            color=valve_color,
        )
        self.components.append(self.valve_head)
        
        spring_coils = 6
        for i in range(spring_coils):
            spring_y = self.base_y + self.geo["valve_length"] - 0.3 - i * 0.1
            spring_ring = cylinder(
                pos=vector(
                    self.pos["center"].x + self.x_offset,
                    spring_y,
                    self.pos["center"].z + self.z_offset
                ),
                axis=vector(0, 1, 0),
                radius=self.geo["valve_radius"],
                length=0.02,
                color=self.colors["crankshaft"],
                opacity=0.7,
            )
            self.components.append(spring_ring)
    
    def set_lift(self, lift_amount):
        lift_amount = max(0, min(1, lift_amount))
        dy = lift_amount * self.max_lift - self.current_lift
        
        if abs(dy) > 0.001:
            self.current_lift = lift_amount * self.max_lift
            
            for comp in self.components:
                comp.pos.y += dy
    
    def open(self, lift=1.0):
        self.set_lift(lift)
    
    def close(self):
        self.set_lift(0)
    
    def toggle_visibility(self, visible):
        for comp in self.components:
            comp.visible = visible
    
    def get_position(self):
        return vector(
            self.pos["center"].x + self.x_offset,
            self.base_y + self.current_lift,
            self.pos["center"].z + self.z_offset
        )


class SparkPlug:
    def __init__(self, scene, cylinder_index):
        self.scene = scene
        self.geo = ENGINE_GEOMETRY
        self.pos = ENGINE_POSITION
        self.colors = COLORS
        self.index = cylinder_index
        
        self.x_offset = (cylinder_index - 1.5) * self.geo["cylinder_spacing"]
        
        self.head_y = self.pos["cylinder_y_offset"] + self.geo["cylinder_height"] + self.geo["cylinder_head_height"] / 2
        
        self.plug_body = None
        self.electrode = None
        self.spark = None
        self.components = []
        
        self._create_spark_plug()
    
    def _create_spark_plug(self):
        self.plug_body = cylinder(
            pos=vector(
                self.pos["center"].x + self.x_offset,
                self.head_y - self.geo["cylinder_head_height"] / 2,
                self.pos["center"].z
            ),
            axis=vector(0, 1, 0),
            radius=self.geo["spark_plug_radius"],
            length=self.geo["spark_plug_length"],
            color=self.colors["spark_plug"],
        )
        self.components.append(self.plug_body)
        
        hex_nut = cylinder(
            pos=vector(
                self.pos["center"].x + self.x_offset,
                self.head_y,
                self.pos["center"].z
            ),
            axis=vector(0, 1, 0),
            radius=self.geo["spark_plug_radius"] + 0.1,
            length=0.2,
            color=color.gray(0.4),
        )
        self.components.append(hex_nut)
        
        self.electrode = cylinder(
            pos=vector(
                self.pos["center"].x + self.x_offset,
                self.head_y - self.geo["cylinder_head_height"] / 2 - 0.1,
                self.pos["center"].z
            ),
            axis=vector(0, -1, 0),
            radius=0.04,
            length=0.15,
            color=color.gray(0.3),
        )
        self.components.append(self.electrode)
        
        self.spark = sphere(
            pos=vector(
                self.pos["center"].x + self.x_offset,
                self.head_y - self.geo["cylinder_head_height"] / 2 - 0.2,
                self.pos["center"].z
            ),
            radius=0.1,
            color=color.yellow,
            emissive=True,
            visible=False,
        )
        self.components.append(self.spark)
    
    def ignite(self, duration=0.1):
        self.spark.visible = True
        self.spark.radius = 0.15
        self.spark.color = color.white
        
        def fade_spark():
            import time
            time.sleep(duration)
            if self.spark.visible:
                self.spark.radius = 0.1
                self.spark.color = color.yellow
                self.spark.visible = False
        
        return fade_spark
    
    def set_spark_visible(self, visible):
        self.spark.visible = visible
        if visible:
            self.spark.radius = 0.15 + 0.1 * math.sin(math.pi * 2 * 10)
            self.spark.color = color.orange
    
    def toggle_visibility(self, visible):
        for comp in self.components:
            if comp is not self.spark:
                comp.visible = visible
