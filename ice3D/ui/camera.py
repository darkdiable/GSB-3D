#!/usr/bin/env python3
"""
相机控制器
Camera Controller - handles camera movement and view controls
"""

from vpython import vector, scene

from ice3D.config.settings import SCENE_CONFIG, ENGINE_GEOMETRY, ENGINE_POSITION


class CameraController:
    def __init__(self, scene):
        self.scene = scene
        self.geo = ENGINE_GEOMETRY
        self.pos = ENGINE_POSITION
        
        self.default_range = SCENE_CONFIG["range"]
        self.default_center = SCENE_CONFIG["center"]
        
        self.current_focus = None
    
    def focus_on_cylinder(self, cylinder_index):
        if cylinder_index is None:
            self.current_focus = None
            self.reset()
        else:
            self.current_focus = cylinder_index
            x_offset = (cylinder_index - 1.5) * self.geo["cylinder_spacing"]
            
            target_center = vector(
                self.pos["center"].x + x_offset,
                self.pos["cylinder_y_offset"] + self.geo["cylinder_height"] / 2,
                self.pos["center"].z
            )
            
            self.scene.center = target_center
            self.scene.range = 10
    
    def reset(self):
        self.current_focus = None
        self.scene.center = self.default_center
        self.scene.range = self.default_range
    
    def update(self):
        if self.current_focus is not None:
            x_offset = (self.current_focus - 1.5) * self.geo["cylinder_spacing"]
            target_center = vector(
                self.pos["center"].x + x_offset,
                self.pos["cylinder_y_offset"] + self.geo["cylinder_height"] / 2,
                self.pos["center"].z
            )
            
            self.scene.center = self.scene.center + 0.05 * (target_center - self.scene.center)
