import math
from vpython import sphere, ring, label, vector, color

from solarsystem.constants import (
    EARTH_ORBIT_PERIOD,
    ORBIT_LINE_THICKNESS,
)


class Planet:
    def __init__(self, planet_data, sun_pos=vector(0, 0, 0)):
        self.name = planet_data["name"]
        self.name_en = planet_data["name_en"]
        self.radius = planet_data["radius"]
        self.orbit_radius = planet_data["orbit_radius"]
        self.orbit_period = planet_data["orbit_period"]
        self.rotation_period = planet_data["rotation_period"]
        self.color = planet_data["color"]
        self.has_ring = planet_data["has_ring"]
        self.sun_pos = sun_pos

        self.angle = 0
        self.rotation_angle = 0
        self.sphere = None
        self.orbit_line = None
        self.ring = None
        self.label = None

        self._create_sphere()
        self._create_orbit_line()
        if self.has_ring:
            self._create_ring(planet_data)
        self._create_label()

    def _create_sphere(self):
        self.sphere = sphere(
            pos=self._calculate_position(),
            radius=self.radius,
            color=self.color,
            make_trail=False,
        )

    def _create_orbit_line(self):
        self.orbit_line = ring(
            pos=self.sun_pos,
            axis=vector(0, 1, 0),
            radius=self.orbit_radius,
            thickness=ORBIT_LINE_THICKNESS,
            color=color.gray(0.4),
            opacity=0.5,
        )

    def _create_ring(self, planet_data):
        self.ring = ring(
            pos=self.sphere.pos,
            axis=vector(0, 1, 0),
            radius=planet_data["ring_outer"],
            thickness=planet_data["ring_outer"] - planet_data["ring_inner"],
            color=planet_data["ring_color"],
            opacity=0.7,
        )

    def _create_label(self):
        self.label = label(
            pos=self.sphere.pos,
            text=f"{self.name}\n{self.name_en}",
            yoffset=self.radius + 0.5,
            xoffset=10,
            color=color.white,
            background=color.gray(0.3),
            height=10,
            box=True,
            line=True,
            linecolor=color.gray(0.6),
        )

    def _calculate_position(self):
        x = self.sun_pos.x + self.orbit_radius * math.cos(self.angle)
        z = self.sun_pos.z + self.orbit_radius * math.sin(self.angle)
        return vector(x, self.sun_pos.y, z)

    def update(self, dt, speed_multiplier):
        orbit_speed = (2 * math.pi) / (self.orbit_period / EARTH_ORBIT_PERIOD)
        self.angle += orbit_speed * dt * speed_multiplier

        rotation_speed = (2 * math.pi) / (self.rotation_period / EARTH_ORBIT_PERIOD)
        self.rotation_angle += rotation_speed * dt * speed_multiplier

        new_pos = self._calculate_position()
        self.sphere.pos = new_pos
        self.sphere.rotate(angle=rotation_speed * dt * speed_multiplier, axis=vector(0, 1, 0))

        if self.ring is not None:
            self.ring.pos = new_pos
            self.ring.rotate(angle=rotation_speed * dt * speed_multiplier * 0.1, axis=vector(0, 1, 0))

        self.label.pos = new_pos

    def toggle_orbit(self, visible):
        self.orbit_line.visible = visible

    def toggle_label(self, visible):
        self.label.visible = visible

    def toggle_ring(self, visible):
        if self.ring is not None:
            self.ring.visible = visible
