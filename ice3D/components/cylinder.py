#!/usr/bin/env python3
"""
气缸组件
Cylinder Component - creates cylinder liners for all 4 cylinders
"""

import math
from vpython import cylinder, vector, color, extrusion, shapes, ring

from ice3D.config.settings import ENGINE_GEOMETRY, ENGINE_POSITION, COLORS


class Cylinder:
    def __init__(self, scene, cylinder_index):
        self.scene = scene
        self.geo = ENGINE_GEOMETRY
        self.pos = ENGINE_POSITION
        self.colors = COLORS
        self.index = cylinder_index
        
        self.x_offset = (cylinder_index - 1.5) * self.geo["cylinder_spacing"]
        self.cylinder_pos = vector(
            self.pos["center"].x + self.x_offset,
            self.pos["cylinder_y_offset"] + self.geo["cylinder_height"] / 2,
            self.pos["center"].z
        )
        
        self.outer_cylinder = None
        self.inner_cylinder = None
        self.cooling_fins = []
        self.components = []
        
        self._create_outer_cylinder()
        self._create_inner_cylinder()
        self._create_cooling_fins()
        self._create_head_gasket()
    
    def _create_outer_cylinder(self):
        self.outer_cylinder = cylinder(
            pos=vector(self.cylinder_pos.x, self.pos["cylinder_y_offset"], self.cylinder_pos.z),
            axis=vector(0, 1, 0),
            radius=self.geo["cylinder_radius"],
            length=self.geo["cylinder_height"],
            color=self.colors["cylinder"],
            opacity=0.7,
        )
        self.components.append(self.outer_cylinder)
    
    def _create_inner_cylinder(self):
        inner_radius = self.geo["cylinder_radius"] - self.geo["cylinder_wall_thickness"]
        self.inner_cylinder = cylinder(
            pos=vector(self.cylinder_pos.x, self.pos["cylinder_y_offset"], self.cylinder_pos.z),
            axis=vector(0, 1, 0),
            radius=inner_radius,
            length=self.geo["cylinder_height"],
            color=color.gray(0.2),
            opacity=0.3,
        )
        self.components.append(self.inner_cylinder)
    
    def _create_cooling_fins(self):
        fin_count = 6
        fin_spacing = self.geo["cylinder_height"] / (fin_count + 1)
        
        for i in range(fin_count):
            fin_y = self.pos["cylinder_y_offset"] + (i + 1) * fin_spacing
            fin = ring(
                pos=vector(self.cylinder_pos.x, fin_y, self.cylinder_pos.z),
                axis=vector(0, 1, 0),
                radius=self.geo["cylinder_radius"] + 0.15,
                thickness=0.12,
                color=color.gray(0.45),
            )
            self.cooling_fins.append(fin)
            self.components.append(fin)
    
    def _create_head_gasket(self):
        gasket = ring(
            pos=vector(
                self.cylinder_pos.x,
                self.pos["cylinder_y_offset"] + self.geo["cylinder_height"],
                self.cylinder_pos.z
            ),
            axis=vector(0, 1, 0),
            radius=self.geo["cylinder_radius"],
            thickness=0.08,
            color=color.gray(0.25),
        )
        self.components.append(gasket)
    
    def set_cutaway(self, cutaway):
        if cutaway:
            self.outer_cylinder.opacity = 0.2
            self.inner_cylinder.opacity = 0.1
            for fin in self.cooling_fins:
                fin.opacity = 0.3
        else:
            self.outer_cylinder.opacity = 0.7
            self.inner_cylinder.opacity = 0.3
            for fin in self.cooling_fins:
                fin.opacity = 1.0
    
    def toggle_visibility(self, visible):
        for comp in self.components:
            comp.visible = visible
    
    def get_position(self):
        return self.cylinder_pos
    
    def get_top_y(self):
        return self.pos["cylinder_y_offset"] + self.geo["cylinder_height"]
    
    def get_bottom_y(self):
        return self.pos["cylinder_y_offset"]
