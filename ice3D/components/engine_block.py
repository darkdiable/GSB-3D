#!/usr/bin/env python3
"""
发动机机体组件
Engine Block Component - creates the main engine block structure
"""

from vpython import box, vector, color, cylinder as vp_cylinder

from ice3D.config.settings import ENGINE_GEOMETRY, ENGINE_POSITION, COLORS


class EngineBlock:
    def __init__(self, scene):
        self.scene = scene
        self.geo = ENGINE_GEOMETRY
        self.pos = ENGINE_POSITION
        self.colors = COLORS
        
        self.block = None
        self.cylinder_head = None
        self.oil_pan = None
        self.components = []
        
        self._create_block()
        self._create_cylinder_head()
        self._create_oil_pan()
        self._create_support_structure()
    
    def _create_block(self):
        self.block = box(
            pos=vector(
                self.pos["center"].x,
                self.pos["crankshaft_y"] + self.geo["engine_block_height"] / 2 - self.geo["oil_pan_height"],
                self.pos["center"].z
            ),
            size=vector(
                self.geo["engine_block_width"],
                self.geo["engine_block_height"],
                self.geo["engine_block_depth"]
            ),
            color=self.colors["engine_block"],
            opacity=0.85,
        )
        self.components.append(self.block)
    
    def _create_cylinder_head(self):
        head_y = self.pos["cylinder_y_offset"] + self.geo["cylinder_height"] + self.geo["cylinder_head_height"] / 2
        self.cylinder_head = box(
            pos=vector(
                self.pos["center"].x,
                head_y,
                self.pos["center"].z
            ),
            size=vector(
                self.geo["engine_block_width"] - 1.0,
                self.geo["cylinder_head_height"],
                self.geo["engine_block_depth"] - 0.5
            ),
            color=self.colors["cylinder_head"],
        )
        self.components.append(self.cylinder_head)
        
        for i in range(4):
            x_offset = (i - 1.5) * self.geo["cylinder_spacing"]
            manifold = box(
                pos=vector(
                    self.pos["center"].x + x_offset,
                    head_y + self.geo["cylinder_head_height"] / 2 + 0.3,
                    self.pos["center"].z + 1.8
                ),
                size=vector(2.0, 0.6, 1.0),
                color=color.gray(0.35),
            )
            self.components.append(manifold)
            
            manifold_ex = box(
                pos=vector(
                    self.pos["center"].x + x_offset,
                    head_y + self.geo["cylinder_head_height"] / 2 + 0.3,
                    self.pos["center"].z - 1.8
                ),
                size=vector(2.0, 0.6, 1.0),
                color=color.gray(0.35),
            )
            self.components.append(manifold_ex)
    
    def _create_oil_pan(self):
        pan_y = self.pos["crankshaft_y"] - self.geo["oil_pan_height"] / 2
        self.oil_pan = box(
            pos=vector(
                self.pos["center"].x,
                pan_y,
                self.pos["center"].z
            ),
            size=vector(
                self.geo["engine_block_width"] - 0.5,
                self.geo["oil_pan_height"],
                self.geo["engine_block_depth"] - 0.5
            ),
            color=self.colors["oil_pan"],
        )
        self.components.append(self.oil_pan)
    
    def _create_support_structure(self):
        for i in range(5):
            x_pos = -self.geo["engine_block_width"] / 2 + i * self.geo["engine_block_width"] / 4
            support = box(
                pos=vector(
                    x_pos,
                    self.pos["crankshaft_y"] + self.geo["engine_block_height"] / 2 - self.geo["oil_pan_height"],
                    self.pos["center"].z + self.geo["engine_block_depth"] / 2 - 0.3
                ),
                size=vector(0.2, self.geo["engine_block_height"] - 0.5, 0.4),
                color=self.colors["engine_block"],
            )
            self.components.append(support)
            
            support2 = box(
                pos=vector(
                    x_pos,
                    self.pos["crankshaft_y"] + self.geo["engine_block_height"] / 2 - self.geo["oil_pan_height"],
                    self.pos["center"].z - self.geo["engine_block_depth"] / 2 + 0.3
                ),
                size=vector(0.2, self.geo["engine_block_height"] - 0.5, 0.4),
                color=self.colors["engine_block"],
            )
            self.components.append(support2)
    
    def set_opacity(self, opacity):
        for comp in self.components:
            if hasattr(comp, 'opacity'):
                comp.opacity = opacity
    
    def toggle_visibility(self, visible):
        for comp in self.components:
            comp.visible = visible
