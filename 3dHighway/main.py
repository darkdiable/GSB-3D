import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from direct.showbase.ShowBase import ShowBase
from panda3d.core import Vec3, loadPrcFileData, WindowProperties
from config.settings import Config

from road.highway import Highway
from models.vehicle_model import VehicleModel
from vehicle.vehicle_controller import VehicleController
from monitoring.speed_monitor import SpeedMonitor, ViolationDetector
from ui.hud import HUD
from controllers.keyboard_controller import KeyboardController


class HighwaySimulationApp(ShowBase):
    def __init__(self):
        loadPrcFileData('', f'win-size {Config.WINDOW_WIDTH} {Config.WINDOW_HEIGHT}')
        loadPrcFileData('', 'window-title ' + Config.WINDOW_TITLE)
        loadPrcFileData('', 'show-frame-rate-meter #t')
        loadPrcFileData('', 'sync-video #f')
        
        super().__init__()
        
        self.game_time = 0.0
        self.last_violation_time = 0.0
        
        self.setBackgroundColor(*Config.SKY_COLOR)
        
        self.highway = Highway(self.render)
        self.highway.build()
        
        self.vehicle_model = VehicleModel(self.render)
        self.vehicle_node = self.vehicle_model.build()
        
        self.vehicle_controller = VehicleController(self.vehicle_node, self.highway)
        self.vehicle_controller.reset()
        
        self.speed_monitor = SpeedMonitor(self.vehicle_controller)
        self.violation_detector = ViolationDetector(self.vehicle_controller, self.speed_monitor)
        
        self.hud = HUD(self)
        self.hud.build()
        
        self.keyboard_controller = KeyboardController(self, self.vehicle_controller, self)
        
        self.setup_camera()
        
        self.taskMgr.add(self.update, 'update_task')
    
    def setup_camera(self):
        self.disableMouse()
        self.camera.setPos(0, -10, 5)
        self.camera.lookAt(0, 0, 0)
    
    def update_camera(self, dt):
        target_pos = self.vehicle_controller.get_position()
        heading = self.vehicle_controller.get_heading()
        
        cam_x = target_pos.getX() - Config.CAMERA_DISTANCE
        cam_y = target_pos.getY()
        cam_z = Config.CAMERA_HEIGHT
        
        current_pos = self.camera.getPos()
        new_x = current_pos.getX() + (cam_x - current_pos.getX()) * Config.CAMERA_FOLLOW_SPEED * dt
        new_y = current_pos.getY() + (cam_y - current_pos.getY()) * Config.CAMERA_FOLLOW_SPEED * dt
        new_z = current_pos.getZ() + (cam_z - current_pos.getZ()) * Config.CAMERA_FOLLOW_SPEED * dt
        
        self.camera.setPos(new_x, new_y, new_z)
        self.camera.lookAt(target_pos.getX(), target_pos.getY(), Config.VEHICLE_HEIGHT)
    
    def update(self, task):
        dt = globalClock.getDt()
        self.game_time += dt
        
        self.vehicle_controller.update(dt)
        
        self.speed_monitor.update(dt)
        
        violations = self.violation_detector.update(self.game_time, dt)
        
        if violations['speeding'] or violations['lane_crossing']:
            recent_violation = self.violation_detector.get_recent_violation()
            if recent_violation and (self.game_time - self.last_violation_time) > 0.5:
                self.hud.show_violation(recent_violation['message'])
                self.last_violation_time = self.game_time
        
        self.update_camera(dt)
        
        self.hud.update_speed(self.speed_monitor.get_current_speed())
        self.hud.update_lane(self.vehicle_controller.get_current_lane())
        self.hud.update_violation_count(
            self.violation_detector.get_violation_count(),
            self.violation_detector.get_speeding_count(),
            self.violation_detector.get_lane_crossing_count()
        )
        self.hud.update(dt)
        
        return task.cont
    
    def reset(self):
        self.vehicle_controller.reset()
        self.violation_detector.reset()
        self.speed_monitor.reset_max_speed()
        self.game_time = 0.0
        print("车辆已重置")
    
    def exit(self):
        print("\n=== 模拟结束 ===")
        print(f"总违章次数: {self.violation_detector.get_violation_count()}")
        print(f"超速违章: {self.violation_detector.get_speeding_count()}")
        print(f"压线违章: {self.violation_detector.get_lane_crossing_count()}")
        print(f"最高车速: {self.speed_monitor.get_max_speed():.1f} km/h")
        
        self.hud.cleanup()
        self.keyboard_controller.cleanup()
        self.userExit()


def main():
    app = HighwaySimulationApp()
    app.run()


if __name__ == '__main__':
    main()
