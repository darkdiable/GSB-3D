import math
from vpython import vector


class CameraController:
    def __init__(self, scene):
        self.scene = scene
        self.scene.userspin = False
        self.scene.userpan = False
        self.scene.userzoom = False

        self.active_button = None
        self.prev_x = 0
        self.prev_y = 0

        self.rotate_sensitivity = 0.005
        self.pan_sensitivity = 0.002
        self.zoom_sensitivity = 1.05

        self.scene.bind('mousedown', self._on_mousedown)
        self.scene.bind('mousemove', self._on_mousemove)
        self.scene.bind('mouseup', self._on_mouseup)

    def _on_mousedown(self, evt):
        self.active_button = evt.button
        self.prev_x = evt.pos.x
        self.prev_y = evt.pos.y

    def _on_mousemove(self, evt):
        if self.active_button is None:
            return

        dx = evt.pos.x - self.prev_x
        dy = evt.pos.y - self.prev_y

        if self.active_button == 'left':
            self._rotate(dx, dy)
        elif self.active_button in ('right', 'middle'):
            self._pan(dx, dy)

        self.prev_x = evt.pos.x
        self.prev_y = evt.pos.y

    def _on_mouseup(self, evt):
        self.active_button = None

    def handle_scroll(self, delta):
        if delta > 0:
            self.scene.range /= self.zoom_sensitivity
        elif delta < 0:
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
