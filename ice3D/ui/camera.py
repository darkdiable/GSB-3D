#!/usr/bin/env python3
"""
相机控制器
Camera Controller - handles camera movement and view controls
"""

import math
from vpython import vector, scene

from ice3D.config.settings import SCENE_CONFIG, ENGINE_GEOMETRY, ENGINE_POSITION

AUTO_ROTATE_SPEED = 0.3


class CameraController:
    def __init__(self, scene):
        self.scene = scene
        self.geo = ENGINE_GEOMETRY
        self.pos = ENGINE_POSITION
        
        self.default_range = SCENE_CONFIG["range"]
        self.default_center = SCENE_CONFIG["center"]
        
        self.current_focus = None
        self.auto_rotate = False
        self.rotation_angle = 0.0
    
    def toggle_auto_rotate(self):
        self.auto_rotate = not self.auto_rotate
        if self.auto_rotate:
            self.scene.userspin = False
            fwd = self.scene.forward
            self.rotation_angle = math.atan2(-fwd.x, -fwd.z)
        else:
            self.scene.userspin = True
        return self.auto_rotate
    
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
        self.auto_rotate = False
        self.rotation_angle = 0.0
        self.scene.userspin = True
    
    def update(self, dt=1/60):
        if self.current_focus is not None:
            x_offset = (self.current_focus - 1.5) * self.geo["cylinder_spacing"]
            target_center = vector(
                self.pos["center"].x + x_offset,
                self.pos["cylinder_y_offset"] + self.geo["cylinder_height"] / 2,
                self.pos["center"].z
            )
            
            self.scene.center = self.scene.center + 0.05 * (target_center - self.scene.center)
        
        if self.auto_rotate:
            self.rotation_angle += AUTO_ROTATE_SPEED * dt
            
            current_center = self.scene.center
            current_range = self.scene.range
            
            self.scene.forward = vector(
                math.sin(self.rotation_angle),
                -0.3,
                math.cos(self.rotation_angle)
            )
            
            self.scene.center = current_center
            self.scene.range = current_range
