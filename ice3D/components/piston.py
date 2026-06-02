#!/usr/bin/env python3
"""
活塞组件
Piston Component - creates piston with rings and wrist pin
"""

import math
from vpython import cylinder, vector, color, ring, sphere, box

from ice3D.config.settings import ENGINE_GEOMETRY, ENGINE_POSITION, COLORS


class Piston:
    def __init__(self, scene, cylinder_index):
        self.scene = scene
        self.geo = ENGINE_GEOMETRY
        self.pos = ENGINE_POSITION
        self.colors = COLORS
        self.index = cylinder_index
        
        self.x_offset = (cylinder_index - 1.5) * self.geo["cylinder_spacing"]
        self.base_y = self.pos["cylinder_y_offset"] + self.geo["stroke_length"] / 2 + self.geo["piston_height"] / 2
        self.current_y = self.base_y
        
        self.piston_body = None
        self.piston_rings = []
        self.wrist_pin = None
        self.components = []
        
        self._create_piston_body()
        self._create_piston_rings()
        self._create_wrist_pin()
    
    def _create_piston_body(self):
        self.piston_body = cylinder(
            pos=vector(
                self.pos["center"].x + self.x_offset,
                self.current_y - self.geo["piston_height"] / 2,
                self.pos["center"].z
            ),
            axis=vector(0, 1, 0),
            radius=self.geo["piston_radius"],
            length=self.geo["piston_height"],
            color=self.colors["piston"],
        )
        self.components.append(self.piston_body)
        
        piston_crown = cylinder(
            pos=vector(
                self.pos["center"].x + self.x_offset,
                self.current_y + self.geo["piston_height"] / 2 - 0.05,
                self.pos["center"].z
            ),
            axis=vector(0, 1, 0),
            radius=self.geo["piston_radius"] - 0.02,
            length=0.1,
            color=color.gray(0.55),
        )
        self.components.append(piston_crown)
    
    def _create_piston_rings(self):
        ring_positions = [0.2, 0.5, 0.8]
        
        for i, rel_pos in enumerate(ring_positions):
            ring_y = self.current_y + self.geo["piston_height"] / 2 - rel_pos * self.geo["piston_height"]
            piston_ring = ring(
                pos=vector(
                    self.pos["center"].x + self.x_offset,
                    ring_y,
                    self.pos["center"].z
                ),
                axis=vector(0, 1, 0),
                radius=self.geo["piston_radius"] + 0.01,
                thickness=0.04,
                color=color.gray(0.3),
            )
            self.piston_rings.append(piston_ring)
            self.components.append(piston_ring)
    
    def _create_wrist_pin(self):
        self.wrist_pin = cylinder(
            pos=vector(
                self.pos["center"].x + self.x_offset,
                self.current_y - self.geo["piston_height"] / 4,
                self.pos["center"].z
            ),
            axis=vector(0, 0, 1),
            radius=self.geo["crank_pin_radius"] * 0.6,
            length=self.geo["piston_radius"] * 1.5,
            color=color.gray(0.45),
        )
        self.components.append(self.wrist_pin)
    
    def update_position(self, y_position):
        dy = y_position - self.current_y
        self.current_y = y_position
        
        for comp in self.components:
            comp.pos.y += dy
    
    def get_position(self):
        return vector(
            self.pos["center"].x + self.x_offset,
            self.current_y,
            self.pos["center"].z
        )
    
    def get_wrist_pin_position(self):
        return vector(
            self.pos["center"].x + self.x_offset,
            self.current_y - self.geo["piston_height"] / 4,
            self.pos["center"].z
        )
    
    def toggle_visibility(self, visible):
        for comp in self.components:
            comp.visible = visible
    
    def set_opacity(self, opacity):
        for comp in self.components:
            if hasattr(comp, 'opacity'):
                comp.opacity = opacity
