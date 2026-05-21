import sys
import math
import time
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from panda3d.core import *
from config.settings import (
    WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE,
    CAMERA_DISTANCE, CAMERA_HEIGHT, CAMERA_FOLLOW_SPEED,
    ROAD_LENGTH, LANE_WIDTH
)
from road.road_builder import RoadBuilder
from vehicle.car import Car
from systems.speed_monitor import SpeedMonitor
from systems.lane_detection import LaneDetection
from systems.violation_detector import ViolationDetector
from ui.hud import HUD
from ui.notification import NotificationSystem
from utils.geometry_utils import create_sphere


class HighwaySimulation(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        self._setup_window()
        self._setup_lighting()
        self._setup_background()
        self._setup_camera()

        self.road_builder = RoadBuilder(self.render)
        self.road_builder.build()

        start_x = self.road_builder.get_lane_center_x(1)
        start_y = -ROAD_LENGTH / 2 + 50
        self.car = Car(self.render, start_x, start_y)

        self.speed_monitor = SpeedMonitor()
        self.lane_detection = LaneDetection(self.road_builder)
        self.violation_detector = ViolationDetector(self.speed_monitor, self.lane_detection)

        self.hud = HUD(self.aspect2d)
        self.notification_system = NotificationSystem(self.aspect2d)

        self._setup_controls()

        self.taskMgr.add(self.update_simulation, "update_simulation")
        self.taskMgr.add(self.update_camera, "update_camera")

        self.notification_system.show_custom_message(
            "欢迎使用3D高速行车模拟系统！",
            "info",
            4.0
        )

    def _setup_window(self):
        props = WindowProperties()
        props.setTitle(WINDOW_TITLE)
        props.setSize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.win.requestProperties(props)
        self.disableMouse()

    def _setup_lighting(self):
        ambient_light = AmbientLight('ambient_light')
        ambient_light.setColor(VBase4(0.4, 0.4, 0.45, 1))
        ambient_np = self.render.attachNewNode(ambient_light)
        self.render.setLight(ambient_np)

        directional_light = DirectionalLight('directional_light')
        directional_light.setColor(VBase4(0.9, 0.85, 0.75, 1))
        directional_light.setDirection(LVector3(0.5, -0.8, -1))
        directional_np = self.render.attachNewNode(directional_light)
        self.render.setLight(directional_np)

        self.render.setShaderAuto()

    def _setup_background(self):
        self.setBackgroundColor(0.4, 0.6, 0.9, 1)
        self._create_sky_dome()

    def _create_sky_dome(self):
        sky = create_sphere(self.render, 1, "sky_dome", 16)
        sky.setScale(800)
        sky.setP(90)
        sky.setBin('background', 1)
        sky.setDepthWrite(0)
        sky.setLightOff()

        sky_material = Material()
        sky_material.setDiffuse((0.5, 0.7, 0.95, 1))
        sky.setMaterial(sky_material)

    def _setup_camera(self):
        self.cam_distance = CAMERA_DISTANCE
        self.cam_height = CAMERA_HEIGHT
        self.cam_follow_speed = CAMERA_FOLLOW_SPEED
        self.camera_mode = 'third_person'

    def _setup_controls(self):
        self.accept('w', self.car.set_key, ['accelerate', True])
        self.accept('w-up', self.car.set_key, ['accelerate', False])
        self.accept('arrow_up', self.car.set_key, ['accelerate', True])
        self.accept('arrow_up-up', self.car.set_key, ['accelerate', False])

        self.accept('s', self.car.set_key, ['brake', True])
        self.accept('s-up', self.car.set_key, ['brake', False])
        self.accept('arrow_down', self.car.set_key, ['brake', True])
        self.accept('arrow_down-up', self.car.set_key, ['brake', False])

        self.accept('a', self.car.set_key, ['left', True])
        self.accept('a-up', self.car.set_key, ['left', False])
        self.accept('arrow_left', self.car.set_key, ['left', True])
        self.accept('arrow_left-up', self.car.set_key, ['left', False])

        self.accept('d', self.car.set_key, ['right', True])
        self.accept('d-up', self.car.set_key, ['right', False])
        self.accept('arrow_right', self.car.set_key, ['right', True])
        self.accept('arrow_right-up', self.car.set_key, ['right', False])

        self.accept('v', self.toggle_camera_mode)
        self.accept('r', self.reset_car)
        self.accept('escape', sys.exit)

    def toggle_camera_mode(self):
        if self.camera_mode == 'third_person':
            self.camera_mode = 'top_down'
        elif self.camera_mode == 'top_down':
            self.camera_mode = 'chase'
        else:
            self.camera_mode = 'third_person'

        self.notification_system.show_custom_message(
            f"切换到 {self._get_camera_mode_name()} 视角",
            "info",
            1.5
        )

    def _get_camera_mode_name(self) -> str:
        names = {
            'third_person': '第三人称',
            'top_down': '俯视',
            'chase': '追逐'
        }
        return names.get(self.camera_mode, '未知')

    def reset_car(self):
        start_x = self.road_builder.get_lane_center_x(1)
        start_y = -ROAD_LENGTH / 2 + 50
        self.car.x = start_x
        self.car.y = start_y
        self.car.speed = 0.0
        self.car.heading = 0.0
        self.speed_monitor.reset()
        self.notification_system.show_custom_message(
            "车辆已重置",
            "success",
            2.0
        )

    def update_simulation(self, task):
        dt = globalClock.getDt()
        current_time = time.time()

        self.car.update(dt)

        self.speed_monitor.update(self.car)
        self.lane_detection.update(self.car)
        self.violation_detector.update(current_time)

        self.hud.update(self.car, self.speed_monitor, self.lane_detection)
        self.notification_system.update(self.violation_detector, current_time)

        return Task.cont

    def update_camera(self, task):
        dt = globalClock.getDt()

        car_pos = self.car.get_position()
        car_heading = self.car.get_heading()
        heading_rad = math.radians(car_heading)

        if self.camera_mode == 'third_person':
            target_x = car_pos[0] - math.sin(heading_rad) * self.cam_distance
            target_y = car_pos[1] - math.cos(heading_rad) * self.cam_distance
            target_z = car_pos[2] + self.cam_height
        elif self.camera_mode == 'top_down':
            target_x = car_pos[0]
            target_y = car_pos[1] - 20
            target_z = 40
        elif self.camera_mode == 'chase':
            target_x = car_pos[0] - math.sin(heading_rad) * 6
            target_y = car_pos[1] - math.cos(heading_rad) * 6
            target_z = car_pos[2] + 2.5
        else:
            target_x = car_pos[0]
            target_y = car_pos[1] - self.cam_distance
            target_z = self.cam_height

        current_x, current_y, current_z = self.camera.getPos()
        lerp_factor = min(1, dt * self.cam_follow_speed)

        new_x = current_x + (target_x - current_x) * lerp_factor
        new_y = current_y + (target_y - current_y) * lerp_factor
        new_z = current_z + (target_z - current_z) * lerp_factor

        self.camera.setPos(new_x, new_y, new_z)

        look_at_x = car_pos[0] + math.sin(heading_rad) * 5
        look_at_y = car_pos[1] + math.cos(heading_rad) * 5
        look_at_z = car_pos[2] + 1

        self.camera.lookAt(look_at_x, look_at_y, look_at_z)

        return Task.cont

    def cleanup(self):
        self.hud.cleanup()
        self.notification_system.cleanup()


def main():
    app = HighwaySimulation()
    try:
        app.run()
    finally:
        app.cleanup()


if __name__ == "__main__":
    main()
