import math
from vpython import vector, rate


class CameraController:
    def __init__(self, scene):
        self.scene = scene
        self.scene.userspin = False
        self.scene.userpan = False
        self.scene.userzoom = False

        self.is_rotating = False
        self.is_panning = False
        self.last_mouse_pos = None

        self.rotate_sensitivity = 0.008
        self.pan_sensitivity = 0.015
        self.zoom_sensitivity = 1.02

        self.initial_forward = vector(scene.forward.x, scene.forward.y, scene.forward.z)
        self.initial_center = vector(scene.center.x, scene.center.y, scene.center.z)
        self.initial_range = scene.range

    def update(self):
        mouse = self.scene.mouse

        if mouse.press:
            if mouse.button == 'left':
                self.is_rotating = True
                self.is_panning = False
                self.last_mouse_pos = vector(mouse.pos.x, mouse.pos.y, 0)
            elif mouse.button in ('right', 'middle'):
                self.is_rotating = False
                self.is_panning = True
                self.last_mouse_pos = vector(mouse.pos.x, mouse.pos.y, 0)

        if mouse.release:
            self.is_rotating = False
            self.is_panning = False
            self.last_mouse_pos = None

        if self.is_rotating and self.last_mouse_pos is not None:
            dx = mouse.pos.x - self.last_mouse_pos.x
            dy = mouse.pos.y - self.last_mouse_pos.y
            self._rotate(dx, dy)
            self.last_mouse_pos = vector(mouse.pos.x, mouse.pos.y, 0)

        if self.is_panning and self.last_mouse_pos is not None:
            dx = mouse.pos.x - self.last_mouse_pos.x
            dy = mouse.pos.y - self.last_mouse_pos.y
            self._pan(dx, dy)
            self.last_mouse_pos = vector(mouse.pos.x, mouse.pos.y, 0)

        if hasattr(mouse, 'wheel') and mouse.wheel != 0:
            if mouse.wheel > 0:
                self.scene.range /= self.zoom_sensitivity
            else:
                self.scene.range *= self.zoom_sensitivity

    def _rotate(self, dx, dy):
        yaw = -dx * self.rotate_sensitivity
        pitch = dy * self.rotate_sensitivity

        forward = self.scene.forward
        up = vector(0, 1, 0)
        right = forward.cross(up)

        if right.mag < 1e-6:
            right = vector(1, 0, 0)
        right = right.norm()

        new_forward = self._rotate_vector(forward, yaw, up)
        new_right = self._rotate_vector(right, yaw, up)

        new_forward = self._rotate_vector(new_forward, pitch, new_right)

        max_pitch = 0.95
        if abs(new_forward.dot(up)) > max_pitch:
            new_forward = forward

        self.scene.forward = new_forward

    def _pan(self, dx, dy):
        forward = self.scene.forward
        up = vector(0, 1, 0)
        right = forward.cross(up)

        if right.mag < 1e-6:
            right = vector(1, 0, 0)
        right = right.norm()

        pan_scale = self.scene.range * self.pan_sensitivity
        offset = (right * (-dx) + up * dy) * pan_scale
        self.scene.center += offset

    @staticmethod
    def _rotate_vector(v, angle, axis):
        c = math.cos(angle)
        s = math.sin(angle)
        k = axis.norm()
        return v * c + k.cross(v) * s + k * k.dot(v) * (1 - c)
