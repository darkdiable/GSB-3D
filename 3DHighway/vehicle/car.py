from panda3d.core import *
from direct.showbase.ShowBase import ShowBase
import math
from config.settings import (
    CAR_WIDTH, CAR_LENGTH, CAR_HEIGHT, CAR_MAX_SPEED,
    CAR_ACCELERATION, CAR_BRAKE, CAR_TURN_SPEED, CAR_FRICTION,
    SPEED_CONVERSION, ROAD_WIDTH, ROAD_LENGTH
)


class Car:
    def __init__(self, render: NodePath, loader: Loader, start_x: float = 0, start_y: float = 0):
        self.render = render
        self.loader = loader
        self.car_root = self.render.attachNewNode("car_root")

        self.x = start_x
        self.y = start_y
        self.z = 0.5
        self.heading = 0.0
        self.speed = 0.0

        self.max_speed = CAR_MAX_SPEED / SPEED_CONVERSION
        self.acceleration = CAR_ACCELERATION
        self.brake = CAR_BRAKE
        self.turn_speed = CAR_TURN_SPEED
        self.friction = CAR_FRICTION

        self.key_map = {
            'accelerate': False,
            'brake': False,
            'left': False,
            'right': False
        }

        self._build_car_model()
        self._update_position()

    def _build_car_model(self):
        body = self.loader.loadModel("models/box")
        body.reparentTo(self.car_root)
        body.setScale(CAR_LENGTH / 2, CAR_WIDTH / 2, CAR_HEIGHT / 2)
        body.setPos(0, 0, CAR_HEIGHT / 2)

        body_material = Material()
        body_material.setDiffuse((0.8, 0.1, 0.1, 1))
        body_material.setSpecular((0.5, 0.5, 0.5, 1))
        body_material.setShininess(50)
        body.setMaterial(body_material)

        cabin = self.loader.loadModel("models/box")
        cabin.reparentTo(self.car_root)
        cabin.setScale(CAR_LENGTH * 0.4, CAR_WIDTH * 0.85, CAR_HEIGHT * 0.5)
        cabin.setPos(-CAR_LENGTH * 0.1, 0, CAR_HEIGHT * 0.75)

        cabin_material = Material()
        cabin_material.setDiffuse((0.1, 0.1, 0.2, 0.9))
        cabin_material.setTransparency(TransparencyAttrib.MAlpha)
        cabin.setMaterial(cabin_material)

        wheel_radius = 0.35
        wheel_width = 0.2
        wheel_positions = [
            (CAR_LENGTH * 0.35, CAR_WIDTH * 0.55, wheel_radius),
            (CAR_LENGTH * 0.35, -CAR_WIDTH * 0.55, wheel_radius),
            (-CAR_LENGTH * 0.35, CAR_WIDTH * 0.55, wheel_radius),
            (-CAR_LENGTH * 0.35, -CAR_WIDTH * 0.55, wheel_radius)
        ]

        self.wheels = []
        for i, (wx, wy, wz) in enumerate(wheel_positions):
            wheel = self.loader.loadModel("models/torus")
            if wheel:
                wheel.reparentTo(self.car_root)
                wheel.setScale(wheel_radius, wheel_radius, wheel_width)
                wheel.setPos(wx, wy, wz)
                wheel.setP(90)

                wheel_material = Material()
                wheel_material.setDiffuse((0.05, 0.05, 0.05, 1))
                wheel.setMaterial(wheel_material)

                self.wheels.append(wheel)

        headlight_data = [
            (CAR_LENGTH * 0.48, CAR_WIDTH * 0.35, CAR_HEIGHT * 0.4),
            (CAR_LENGTH * 0.48, -CAR_WIDTH * 0.35, CAR_HEIGHT * 0.4)
        ]

        for hx, hy, hz in headlight_data:
            headlight = self.loader.loadModel("models/sphere")
            headlight.reparentTo(self.car_root)
            headlight.setScale(0.15)
            headlight.setPos(hx, hy, hz)

            hl_material = Material()
            hl_material.setDiffuse((1, 1, 0.8, 1))
            hl_material.setEmission((1, 1, 0.6, 1))
            headlight.setMaterial(hl_material)

        taillight_data = [
            (-CAR_LENGTH * 0.48, CAR_WIDTH * 0.35, CAR_HEIGHT * 0.4),
            (-CAR_LENGTH * 0.48, -CAR_WIDTH * 0.35, CAR_HEIGHT * 0.4)
        ]

        for tx, ty, tz in taillight_data:
            taillight = self.loader.loadModel("models/sphere")
            taillight.reparentTo(self.car_root)
            taillight.setScale(0.12)
            taillight.setPos(tx, ty, tz)

            tl_material = Material()
            tl_material.setDiffuse((1, 0.1, 0.1, 1))
            tl_material.setEmission((0.8, 0, 0, 1))
            taillight.setMaterial(tl_material)

    def set_key(self, key: str, value: bool):
        if key in self.key_map:
            self.key_map[key] = value

    def update(self, dt: float):
        if self.key_map['accelerate']:
            self.speed += self.acceleration * dt
        if self.key_map['brake']:
            self.speed -= self.brake * dt

        self.speed *= self.friction
        self.speed = max(-self.max_speed * 0.3, min(self.speed, self.max_speed))

        if abs(self.speed) > 0.1:
            turn_factor = 1.0 if self.speed > 0 else -1.0
            if self.key_map['left']:
                self.heading += self.turn_speed * dt * turn_factor
            if self.key_map['right']:
                self.heading -= self.turn_speed * dt * turn_factor

        heading_rad = math.radians(self.heading)
        self.x += math.sin(heading_rad) * self.speed * dt
        self.y += math.cos(heading_rad) * self.speed * dt

        half_road = ROAD_WIDTH / 2
        self.x = max(-half_road - 2.0, min(self.x, half_road + 2.0))

        road_end = ROAD_LENGTH / 2
        if self.y > road_end:
            self.y = -road_end
        elif self.y < -road_end:
            self.y = road_end

        self._update_position()
        self._update_wheels(dt)

    def _update_position(self):
        self.car_root.setPos(self.x, self.y, self.z)
        self.car_root.setH(self.heading)

    def _update_wheels(self, dt: float):
        wheel_radius = 0.35
        rotation_speed = (self.speed * dt) / wheel_radius
        rotation_deg = math.degrees(rotation_speed)

        for wheel in self.wheels:
            wheel.setR(wheel.getR() + rotation_deg)

    def get_speed_kmh(self) -> float:
        return abs(self.speed) * SPEED_CONVERSION

    def get_position(self) -> tuple:
        return (self.x, self.y, self.z)

    def get_heading(self) -> float:
        return self.heading

    def get_bounds(self) -> tuple:
        half_width = CAR_WIDTH / 2
        heading_rad = math.radians(self.heading)

        corners = [
            (-CAR_LENGTH / 2, -half_width),
            (CAR_LENGTH / 2, -half_width),
            (CAR_LENGTH / 2, half_width),
            (-CAR_LENGTH / 2, half_width)
        ]

        world_corners = []
        for cx, cy in corners:
            wx = self.x + cx * math.sin(heading_rad) + cy * math.cos(heading_rad)
            wy = self.y + cx * math.cos(heading_rad) - cy * math.sin(heading_rad)
            world_corners.append((wx, wy))

        x_coords = [c[0] for c in world_corners]
        y_coords = [c[1] for c in world_corners]

        return (min(x_coords), max(x_coords), min(y_coords), max(y_coords))

    def get_left_bound(self) -> float:
        half_width = CAR_WIDTH / 2
        heading_rad = math.radians(self.heading)
        offset = half_width * math.cos(heading_rad)
        return self.x - offset

    def get_right_bound(self) -> float:
        half_width = CAR_WIDTH / 2
        heading_rad = math.radians(self.heading)
        offset = half_width * math.cos(heading_rad)
        return self.x + offset

    def get_node_path(self) -> NodePath:
        return self.car_root
