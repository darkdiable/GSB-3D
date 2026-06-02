#!/usr/bin/env python3
"""
连杆组件
Connecting Rod Component - connects piston to crankshaft
"""

import math
from vpython import cylinder, vector, color, box, sphere, compound

from ice3D.config.settings import ENGINE_GEOMETRY, ENGINE_POSITION, COLORS


class ConnectingRod:
    def __init__(self, scene, cylinder_index):
        self.scene = scene
        self.geo = ENGINE_GEOMETRY
        self.pos = ENGINE_POSITION
        self.colors = COLORS
        self.index = cylinder_index
        
        self.x_offset = (cylinder_index - 1.5) * self.geo["cylinder_spacing"]
        self.rod_length = self.geo["connecting_rod_length"]
        
        self.big_end = None
        self.small_end = None
        self.rod_body = None
        self.components = []
        
        self.top_pos = vector(0, 0, 0)
        self.bottom_pos = vector(0, 0, 0)
        self.angle = 0
        
        self._create_rod()
    
    def _create_rod(self):
        start_y = self.pos["crankshaft_y"] + self.geo["stroke_length"] / 2
        end_y = start_y + self.rod_length
        
        self.top_pos = vector(
            self.pos["center"].x + self.x_offset,
            end_y,
            self.pos["center"].z
        )
        self.bottom_pos = vector(
            self.pos["center"].x + self.x_offset,
            start_y,
            self.pos["center"].z
        )
        
        rod_axis = self.top_pos - self.bottom_pos
        rod_length = rod_axis.mag
        
        self.rod_body = cylinder(
            pos=self.bottom_pos,
            axis=rod_axis,
            radius=0.18,
            length=rod_length - 0.6,
            color=self.colors["connecting_rod"],
        )
        self.components.append(self.rod_body)
        
        self.big_end = sphere(
            pos=self.bottom_pos,
            radius=self.geo["crank_pin_radius"] + 0.15,
            color=self.colors["connecting_rod"],
        )
        self.components.append(self.big_end)
        
        big_end_hole = sphere(
            pos=self.bottom_pos,
            radius=self.geo["crank_pin_radius"] + 0.02,
            color=color.gray(0.2),
        )
        self.components.append(big_end_hole)
        
        self.small_end = sphere(
            pos=self.top_pos,
            radius=self.geo["crank_pin_radius"] * 0.7 + 0.12,
            color=self.colors["connecting_rod"],
        )
        self.components.append(self.small_end)
        
        small_end_hole = sphere(
            pos=self.top_pos,
            radius=self.geo["crank_pin_radius"] * 0.6 + 0.02,
            color=color.gray(0.2),
        )
        self.components.append(small_end_hole)
    
    def update_position(self, crank_pin_pos, wrist_pin_pos):
        self.top_pos = vector(wrist_pin_pos.x, wrist_pin_pos.y, wrist_pin_pos.z)
        self.bottom_pos = vector(crank_pin_pos.x, crank_pin_pos.y, crank_pin_pos.z)
        
        rod_axis = self.top_pos - self.bottom_pos
        rod_length = rod_axis.mag
        
        if rod_length > 0:
            self.rod_body.pos = self.bottom_pos
            self.rod_body.axis = rod_axis.norm() * (rod_length - 0.6)
            
            self.big_end.pos = self.bottom_pos
            self.small_end.pos = self.top_pos
            
            for comp in self.components:
                if comp is not self.rod_body and comp is not self.big_end and comp is not self.small_end:
                    if comp.radius < self.geo["crank_pin_radius"] + 0.1:
                        comp.pos = self.bottom_pos
                    else:
                        comp.pos = self.top_pos
            
            self.angle = math.atan2(rod_axis.x, rod_axis.y)
    
    def toggle_visibility(self, visible):
        for comp in self.components:
            comp.visible = visible
