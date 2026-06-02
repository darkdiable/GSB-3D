#!/usr/bin/env python3
"""
视觉效果组件
Visual Effects Component - combustion, airflow, and particle effects
"""

import math
import random
from vpython import sphere, vector, color, cylinder, box

from ice3D.config.settings import ENGINE_GEOMETRY, ENGINE_POSITION, COLORS


class CombustionEffect:
    def __init__(self, scene, cylinder_index):
        self.scene = scene
        self.geo = ENGINE_GEOMETRY
        self.pos = ENGINE_POSITION
        self.colors = COLORS
        self.index = cylinder_index
        
        self.x_offset = (cylinder_index - 1.5) * self.geo["cylinder_spacing"]
        self.chamber_y = self.pos["cylinder_y_offset"] + self.geo["cylinder_height"] - 0.5
        
        self.flames = []
        self.particles = []
        self.is_active = False
        self.intensity = 0
        
        self._create_flames()
    
    def _create_flames(self):
        for i in range(8):
            angle = i * math.pi / 4
            flame = sphere(
                pos=vector(
                    self.pos["center"].x + self.x_offset + 0.3 * math.cos(angle),
                    self.chamber_y,
                    self.pos["center"].z + 0.3 * math.sin(angle)
                ),
                radius=0.15,
                color=color.orange,
                emissive=True,
                visible=False,
            )
            self.flames.append(flame)
    
    def ignite(self, intensity=1.0):
        self.is_active = True
        self.intensity = intensity
        
        for i, flame in enumerate(self.flames):
            flame.visible = True
            flame.color = color.yellow if i % 2 == 0 else color.orange
            flame.radius = 0.1 + 0.1 * intensity * random.random()
    
    def extinguish(self):
        self.is_active = False
        self.intensity = 0
        
        for flame in self.flames:
            flame.visible = False
    
    def update(self, dt, piston_y):
        if not self.is_active:
            return
        
        for i, flame in enumerate(self.flames):
            angle = i * math.pi / 4 + dt * 5
            radius_variation = 0.05 * math.sin(dt * 20 + i)
            
            flame.pos.y = piston_y + 0.3 + 0.1 * random.random()
            flame.pos.x = self.pos["center"].x + self.x_offset + (0.2 + radius_variation) * math.cos(angle)
            flame.pos.z = self.pos["center"].z + (0.2 + radius_variation) * math.sin(angle)
            
            if self.intensity > 0.7:
                flame.color = color.white
            elif self.intensity > 0.4:
                flame.color = color.yellow
            else:
                flame.color = color.orange
        
        self.intensity = max(0, self.intensity - dt * 2)
        if self.intensity < 0.1:
            self.extinguish()
    
    def toggle_visibility(self, visible):
        for flame in self.flames:
            if self.is_active:
                flame.visible = visible


class AirFlowEffect:
    def __init__(self, scene, cylinder_index):
        self.scene = scene
        self.geo = ENGINE_GEOMETRY
        self.pos = ENGINE_POSITION
        self.colors = COLORS
        self.index = cylinder_index
        
        self.x_offset = (cylinder_index - 1.5) * self.geo["cylinder_spacing"]
        
        self.intake_particles = []
        self.exhaust_particles = []
        self.max_particles = 20
        
        self._create_particle_pool()
    
    def _create_particle_pool(self):
        for i in range(self.max_particles):
            particle = sphere(
                pos=vector(0, 0, 0),
                radius=0.08,
                color=self.colors["intake_air"],
                opacity=0.6,
                visible=False,
            )
            self.intake_particles.append(particle)
        
        for i in range(self.max_particles):
            particle = sphere(
                pos=vector(0, 0, 0),
                radius=0.08,
                color=self.colors["exhaust_gas"],
                opacity=0.5,
                visible=False,
            )
            self.exhaust_particles.append(particle)
    
    def spawn_intake_particle(self):
        for particle in self.intake_particles:
            if not particle.visible:
                particle.pos = vector(
                    self.pos["center"].x + self.x_offset + random.uniform(-0.3, 0.3),
                    self.pos["cylinder_y_offset"] + self.geo["cylinder_height"] + 1.5,
                    self.pos["center"].z + 0.6
                )
                particle.velocity = vector(
                    random.uniform(-0.1, 0.1),
                    -2 - random.random(),
                    random.uniform(-0.1, 0.1)
                )
                particle.visible = True
                particle.life = 1.0
                return particle
        return None
    
    def spawn_exhaust_particle(self, start_y):
        for particle in self.exhaust_particles:
            if not particle.visible:
                particle.pos = vector(
                    self.pos["center"].x + self.x_offset + random.uniform(-0.3, 0.3),
                    start_y,
                    self.pos["center"].z - 0.6
                )
                particle.velocity = vector(
                    random.uniform(-0.1, 0.1),
                    2 + random.random(),
                    random.uniform(-0.1, 0.1)
                )
                particle.visible = True
                particle.life = 1.0
                return particle
        return None
    
    def update(self, dt, is_intake, is_exhaust, piston_y):
        if is_intake and random.random() < 0.3:
            self.spawn_intake_particle()
        
        if is_exhaust and random.random() < 0.3:
            self.spawn_exhaust_particle(piston_y + 1)
        
        for particle in self.intake_particles:
            if particle.visible:
                particle.pos += particle.velocity * dt
                particle.life -= dt
                particle.opacity = particle.life * 0.6
                
                if particle.life <= 0 or particle.pos.y < self.pos["cylinder_y_offset"]:
                    particle.visible = False
        
        for particle in self.exhaust_particles:
            if particle.visible:
                particle.pos += particle.velocity * dt
                particle.life -= dt
                particle.opacity = particle.life * 0.5
                
                if particle.life <= 0 or particle.pos.y > self.pos["cylinder_y_offset"] + self.geo["cylinder_height"] + 3:
                    particle.visible = False
    
    def clear_all(self):
        for particle in self.intake_particles + self.exhaust_particles:
            particle.visible = False
    
    def toggle_visibility(self, visible):
        for particle in self.intake_particles + self.exhaust_particles:
            if particle.visible:
                particle.visible = visible
