import math
from vpython import vector


class CameraController:
    def __init__(self, scene):
        self.scene = scene
        self.scene.userspin = True
        self.scene.userpan = True
        self.scene.userzoom = True

        self.initial_forward = vector(scene.forward.x, scene.forward.y, scene.forward.z)
        self.initial_center = vector(scene.center.x, scene.center.y, scene.center.z)
        self.initial_range = scene.range

    def update(self):
        pass

    def reset(self):
        self.scene.forward = self.initial_forward
        self.scene.center = self.initial_center
        self.scene.range = self.initial_range
