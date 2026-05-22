import math
from panda3d.core import *
from direct.gui.OnscreenText import OnscreenText
from config.settings import (
    TAXI_SPEED, FLIGHT_SPEED, TAKEOFF_SPEED, LANDING_SPEED,
    STATUS_WAITING, STATUS_TAXIING, STATUS_TAKEOFF, STATUS_LANDING,
    STATUS_DEPARTED, STATUS_ARRIVED, STATUS_COLORS
)
from utils.helpers import (
    generate_flight_number, lerp_vector, distance,
    get_angle_to_point, lerp
)


class Aircraft:
    def __init__(self, flight_number=None, is_departure=True):
        self.flight_number = flight_number or generate_flight_number()
        self.is_departure = is_departure
        self.status = STATUS_WAITING
        self.node = None
        self.body_node = None
        self.label_node = None
        self.target_point = None
        self.path_points = []
        self.current_path_index = 0
        self.gate_id = None
        self.animation_progress = 0
        self.takeoff_altitude = 0
        self.landing_altitude = 0
        self.rotation_speed = 120

    def create_model(self, render, loader, start_pos, start_hpr=(0, 0, 0)):
        self.node = render.attachNewNode(f'aircraft_{self.flight_number}')
        self.node.setPos(start_pos)
        self.node.setHpr(*start_hpr)

        self.body_node = self.node.attachNewNode('body')

        fuselage = loader.loadModel("models/box")
        fuselage.reparentTo(self.body_node)
        fuselage.setScale(1.2, 4, 0.8)
        fuselage.setPos(0, 0, 0.8)

        fuselage_material = Material()
        fuselage_color = (0.95, 0.95, 0.95, 1)
        fuselage_material.setDiffuse(fuselage_color)
        fuselage_material.setSpecular((0.3, 0.3, 0.3, 1))
        fuselage_material.setShininess(50)
        fuselage.setMaterial(fuselage_material)

        nose = loader.loadModel("models/sphere")
        nose.reparentTo(self.body_node)
        nose.setScale(1.2, 1.5, 0.8)
        nose.setPos(0, 2.5, 0.8)
        nose.setMaterial(fuselage_material)

        tail = loader.loadModel("models/box")
        tail.reparentTo(self.body_node)
        tail.setScale(0.8, 0.2, 2)
        tail.setPos(0, -1.8, 1.8)

        tail_material = Material()
        tail_color = (0.8, 0.2, 0.2, 1) if self.is_departure else (0.2, 0.4, 0.8, 1)
        tail_material.setDiffuse(tail_color)
        tail.setMaterial(tail_material)

        vertical_tail = loader.loadModel("models/box")
        vertical_tail.reparentTo(self.body_node)
        vertical_tail.setScale(0.15, 1.2, 1.8)
        vertical_tail.setPos(0, -1.8, 2.2)
        vertical_tail.setMaterial(tail_material)

        wing = loader.loadModel("models/box")
        wing.reparentTo(self.body_node)
        wing.setScale(5, 0.8, 0.15)
        wing.setPos(0, -0.5, 0.8)
        wing.setMaterial(fuselage_material)

        rear_wing = loader.loadModel("models/box")
        rear_wing.reparentTo(self.body_node)
        rear_wing.setScale(1.8, 0.4, 0.15)
        rear_wing.setPos(0, -2, 1.3)
        rear_wing.setMaterial(fuselage_material)

        engine1 = loader.loadModel("models/cylinder")
        engine1.reparentTo(self.body_node)
        engine1.setScale(0.4, 0.4, 1)
        engine1.setPos(1.8, -0.3, 0.5)
        engine1.setP(90)

        engine2 = loader.loadModel("models/cylinder")
        engine2.reparentTo(self.body_node)
        engine2.setScale(0.4, 0.4, 1)
        engine2.setPos(-1.8, -0.3, 0.5)
        engine2.setP(90)

        engine_material = Material()
        engine_material.setDiffuse((0.3, 0.3, 0.3, 1))
        engine1.setMaterial(engine_material)
        engine2.setMaterial(engine_material)

        cockpit = loader.loadModel("models/sphere")
        cockpit.reparentTo(self.body_node)
        cockpit.setScale(0.7, 0.9, 0.6)
        cockpit.setPos(0, 1.5, 1.1)

        cockpit_material = Material()
        cockpit_material.setDiffuse((0.3, 0.5, 0.7, 1))
        cockpit_material.setTransparency(TransparencyAttrib.MAlpha)
        cockpit.setMaterial(cockpit_material)

        self._create_label(loader)
        return self

    def _create_label(self, loader):
        label_text = TextNode(f'label_{self.flight_number}')
        label_text.setText(self.flight_number)
        label_text.setAlign(TextNode.ACenter)
        label_text.setTextColor(1, 1, 1, 1)

        bg = TextNode(f'label_bg_{self.flight_number}')
        bg.setText(self.flight_number)
        bg.setAlign(TextNode.ACenter)
        bg.setTextColor(0, 0, 0, 0.7)

        bg_node = self.node.attachNewNode(bg)
        bg_node.setPos(0, 0, 3.5)
        bg_node.setScale(0.82)
        bg_node.setBillboardPointEye()
        bg_node.setDepthWrite(False)

        self.label_node = self.node.attachNewNode(label_text)
        self.label_node.setPos(0, 0, 3.5)
        self.label_node.setScale(0.8)
        self.label_node.setBillboardPointEye()
        self.label_node.setDepthWrite(False)

        status_text = TextNode(f'status_{self.flight_number}')
        status_text.setText('等待')
        status_text.setAlign(TextNode.ACenter)
        status_text.setTextColor(1, 1, 0.4, 1)

        self.status_label_node = self.node.attachNewNode(status_text)
        self.status_label_node.setPos(0, 0, 4.3)
        self.status_label_node.setScale(0.5)
        self.status_label_node.setBillboardPointEye()
        self.status_label_node.setDepthWrite(False)

    def set_status(self, status):
        self.status = status
        if self.status_label_node:
            status_text = self.status_label_node.node()
            from config.settings import STATUS_LABELS
            status_text.setText(STATUS_LABELS.get(status, status))
            color = STATUS_COLORS.get(status, (1, 1, 1, 1))
            status_text.setTextColor(*color)

    def set_path(self, points):
        self.path_points = points
        self.current_path_index = 0
        self.animation_progress = 0
        if points:
            self.target_point = points[0]

    def update(self, dt):
        if self.status == STATUS_DEPARTED or self.status == STATUS_ARRIVED:
            return False

        if not self.path_points or self.current_path_index >= len(self.path_points):
            return True

        current_pos = self.node.getPos()
        target = self.path_points[self.current_path_index]
        dist = distance(current_pos, target)

        speed = self._get_speed()

        if dist < 0.5:
            self.current_path_index += 1
            if self.current_path_index >= len(self.path_points):
                self._on_path_complete()
                return True
            self.target_point = self.path_points[self.current_path_index]
            return True

        move_amount = min(speed * dt, dist)
        direction = target - current_pos
        direction.normalize()
        new_pos = current_pos + direction * move_amount

        if self.status == STATUS_TAKEOFF:
            total_takeoff_dist = distance(self.path_points[0], self.path_points[-1])
            progress = 1 - (dist / max(total_takeoff_dist, 1))
            new_pos.setZ(min(progress * 15, target.getZ()))
        elif self.status == STATUS_LANDING:
            total_landing_dist = distance(self.path_points[0], self.path_points[-1])
            progress = 1 - (dist / max(total_landing_dist, 1))
            start_z = self.path_points[0].getZ()
            end_z = self.path_points[-1].getZ()
            new_pos.setZ(lerp(start_z, end_z, progress))

        self.node.setPos(new_pos)

        target_h = get_angle_to_point(current_pos, target)
        current_h = self.node.getH()
        h_diff = target_h - current_h
        while h_diff > 180:
            h_diff -= 360
        while h_diff < -180:
            h_diff += 360

        max_rotate = self.rotation_speed * dt
        if abs(h_diff) > max_rotate:
            h_diff = max_rotate if h_diff > 0 else -max_rotate
        self.node.setH(current_h + h_diff)

        if self.status == STATUS_TAKEOFF:
            pitch = min(15, (self.node.getZ() / 15) * 15)
            self.node.setP(pitch)
        elif self.status == STATUS_LANDING:
            pitch = -3 if self.node.getZ() > 2 else 0
            self.node.setP(pitch)
        else:
            self.node.setP(0)

        return True

    def _get_speed(self):
        if self.status == STATUS_TAXIING:
            return TAXI_SPEED
        elif self.status == STATUS_TAKEOFF:
            return TAKEOFF_SPEED
        elif self.status == STATUS_LANDING:
            return LANDING_SPEED
        elif self.status == STATUS_WAITING:
            return 0
        return TAXI_SPEED

    def _on_path_complete(self):
        if self.status == STATUS_TAKEOFF:
            self.set_status(STATUS_DEPARTED)
            self.node.hide()
        elif self.status == STATUS_LANDING:
            self.set_status(STATUS_WAITING)

    def destroy(self):
        if self.node:
            self.node.removeNode()

    def get_position(self):
        return self.node.getPos() if self.node else None
