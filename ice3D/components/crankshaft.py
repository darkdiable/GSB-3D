#!/usr/bin/env python3
"""
曲轴组件
Crankshaft Component - rotating shaft with crank pins for all 4 cylinders
"""

import math
from vpython import cylinder, vector, color, box, sphere

from ice3D.config.settings import ENGINE_GEOMETRY, ENGINE_POSITION, COLORS


class Crankshaft:
    def __init__(self, scene):
        self.scene = scene
        self.geo = ENGINE_GEOMETRY
        self.pos = ENGINE_POSITION
        self.colors = COLORS
        
        self.main_shaft = None
        self.crank_pins = []
        self.crank_webs = []
        self.counterweights = []
        self.components = []
        
        self.rotation_angle = 0
        self.stroke = self.geo["stroke_length"] / 2
        
        self._create_main_shaft()
        self._create_crank_pins()
        self._create_crank_webs()
        self._create_counterweights()
    
    def _create_main_shaft(self):
        total_length = self.geo["engine_block_width"] + 2.0
        
        self.main_shaft = cylinder(
            pos=vector(
                -total_length / 2,
                self.pos["crankshaft_y"],
                self.pos["center"].z
            ),
            axis=vector(1, 0, 0),
            radius=self.geo["crankshaft_radius"],
            length=total_length,
            color=self.colors["crankshaft"],
        )
        self.components.append(self.main_shaft)
        
        pulley = cylinder(
            pos=vector(
                -total_length / 2 - 0.3,
                self.pos["crankshaft_y"],
                self.pos["center"].z
            ),
            axis=vector(1, 0, 0),
            radius=self.geo["crankshaft_radius"] + 0.5,
            length=0.4,
            color=color.gray(0.35),
        )
        self.components.append(pulley)
        
        flywheel = cylinder(
            pos=vector(
                total_length / 2 - 0.1,
                self.pos["crankshaft_y"],
                self.pos["center"].z
            ),
            axis=vector(1, 0, 0),
            radius=self.geo["crankshaft_radius"] + 1.0,
            length=0.3,
            color=color.gray(0.3),
        )
        self.components.append(flywheel)
    
    def _create_crank_pins(self):
        phase_offsets = [0, math.pi, math.pi, 0]
        
        for i in range(4):
            x_offset = (i - 1.5) * self.geo["cylinder_spacing"]
            phase = phase_offsets[i]
            
            crank_pin = cylinder(
                pos=vector(
                    self.pos["center"].x + x_offset - self.geo["crank_web_thickness"] / 2,
                    self.pos["crankshaft_y"] + self.stroke * math.cos(phase),
                    self.pos["center"].z + self.stroke * math.sin(phase)
                ),
                axis=vector(1, 0, 0),
                radius=self.geo["crank_pin_radius"],
                length=self.geo["crank_web_thickness"],
                color=color.gray(0.5),
            )
            self.crank_pins.append(crank_pin)
            self.components.append(crank_pin)
    
    def _create_crank_webs(self):
        for i in range(4):
            x_offset = (i - 1.5) * self.geo["cylinder_spacing"]
            
            web1 = box(
                pos=vector(
                    self.pos["center"].x + x_offset - self.geo["crank_web_thickness"] - 0.1,
                    self.pos["crankshaft_y"],
                    self.pos["center"].z
                ),
                size=vector(0.15, self.stroke * 2 + 0.5, self.geo["engine_block_depth"] - 1.5),
                color=self.colors["crankshaft"],
            )
            self.crank_webs.append(web1)
            self.components.append(web1)
            
            web2 = box(
                pos=vector(
                    self.pos["center"].x + x_offset + self.geo["crank_web_thickness"] + 0.1,
                    self.pos["crankshaft_y"],
                    self.pos["center"].z
                ),
                size=vector(0.15, self.stroke * 2 + 0.5, self.geo["engine_block_depth"] - 1.5),
                color=self.colors["crankshaft"],
            )
            self.crank_webs.append(web2)
            self.components.append(web2)
    
    def _create_counterweights(self):
        for i in range(4):
            x_offset = (i - 1.5) * self.geo["cylinder_spacing"]
            
            cw1 = box(
                pos=vector(
                    self.pos["center"].x + x_offset - self.geo["crank_web_thickness"] - 0.1,
                    self.pos["crankshaft_y"] - self.stroke / 2,
                    self.pos["center"].z
                ),
                size=vector(0.2, self.stroke * 0.9, self.geo["engine_block_depth"] - 1.8),
                color=color.gray(0.5),
            )
            self.counterweights.append(cw1)
            self.components.append(cw1)
            
            cw2 = box(
                pos=vector(
                    self.pos["center"].x + x_offset + self.geo["crank_web_thickness"] + 0.1,
                    self.pos["crankshaft_y"] - self.stroke / 2,
                    self.pos["center"].z
                ),
                size=vector(0.2, self.stroke * 0.9, self.geo["engine_block_depth"] - 1.8),
                color=color.gray(0.5),
            )
            self.counterweights.append(cw2)
            self.components.append(cw2)
    
    def update_rotation(self, angle_rad):
        self.rotation_angle = angle_rad
        phase_offsets = [0, math.pi, math.pi, 0]
        
        for i, (crank_pin, phase) in enumerate(zip(self.crank_pins, phase_offsets)):
            x_offset = (i - 1.5) * self.geo["cylinder_spacing"]
            effective_angle = angle_rad + phase
            
            crank_pin.pos.y = self.pos["crankshaft_y"] + self.stroke * math.cos(effective_angle)
            crank_pin.pos.z = self.pos["center"].z + self.stroke * math.sin(effective_angle)
        
        for i, (web1, web2) in enumerate(zip(self.crank_webs[::2], self.crank_webs[1::2])):
            phase = phase_offsets[i]
            effective_angle = angle_rad + phase
            
            web1.rotate(angle=0.02, axis=vector(1, 0, 0), origin=vector(web1.pos.x, self.pos["crankshaft_y"], self.pos["center"].z))
            web2.rotate(angle=0.02, axis=vector(1, 0, 0), origin=vector(web2.pos.x, self.pos["crankshaft_y"], self.pos["center"].z))
        
        for i, (cw1, cw2) in enumerate(zip(self.counterweights[::2], self.counterweights[1::2])):
            phase = phase_offsets[i]
            effective_angle = angle_rad + phase
            
            cw1.rotate(angle=0.02, axis=vector(1, 0, 0), origin=vector(cw1.pos.x, self.pos["crankshaft_y"], self.pos["center"].z))
            cw2.rotate(angle=0.02, axis=vector(1, 0, 0), origin=vector(cw2.pos.x, self.pos["crankshaft_y"], self.pos["center"].z))
        
        self.main_shaft.rotate(angle=0.02, axis=vector(1, 0, 0), origin=vector(0, self.pos["crankshaft_y"], self.pos["center"].z))
    
    def get_crank_pin_position(self, cylinder_index):
        phase_offsets = [0, math.pi, math.pi, 0]
        x_offset = (cylinder_index - 1.5) * self.geo["cylinder_spacing"]
        effective_angle = self.rotation_angle + phase_offsets[cylinder_index]
        
        return vector(
            self.pos["center"].x + x_offset,
            self.pos["crankshaft_y"] + self.stroke * math.cos(effective_angle),
            self.pos["center"].z + self.stroke * math.sin(effective_angle)
        )
    
    def toggle_visibility(self, visible):
        for comp in self.components:
            comp.visible = visible
