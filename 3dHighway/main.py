import sys
import os
import math

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from direct.showbase.ShowBase import ShowBase
from panda3d.core import (
    Vec3, Vec4, loadPrcFileData, WindowProperties,
    DirectionalLight, AmbientLight, NodePath,
    GeomVertexData, GeomVertexFormat, GeomVertexWriter,
    Geom, GeomTriangles, GeomNode, Fog
)
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

        self.setup_lighting()
        self.setup_sky()
        self.setup_fog()

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

    def setup_lighting(self):
        alight = AmbientLight('ambient_light')
        alight.setColor(Vec4(0.5, 0.5, 0.55, 1))
        alnp = self.render.attachNewNode(alight)
        self.render.setLight(alnp)

        dlight = DirectionalLight('directional_light')
        dlight.setColor(Vec4(0.8, 0.8, 0.75, 1))
        dlnp = self.render.attachNewNode(dlight)
        dlnp.setHpr(-45, -60, 0)
        self.render.setLight(dlnp)

        dlight2 = DirectionalLight('fill_light')
        dlight2.setColor(Vec4(0.3, 0.3, 0.35, 1))
        dl2np = self.render.attachNewNode(dlight2)
        dl2np.setHpr(135, -30, 0)
        self.render.setLight(dl2np)

    def setup_sky(self):
        sky = NodePath('sky')

        sky_radius = 500.0
        segments = 32
        rings = 16

        vdata = GeomVertexData('sky', GeomVertexFormat.getV3c4(), Geom.UHStatic)
        vertex = GeomVertexWriter(vdata, 'vertex')
        color_writer = GeomVertexWriter(vdata, 'color')

        for j in range(rings + 1):
            phi = math.pi * j / rings
            for i in range(segments + 1):
                theta = 2.0 * math.pi * i / segments

                x = sky_radius * math.sin(phi) * math.cos(theta)
                y = sky_radius * math.sin(phi) * math.sin(theta)
                z = sky_radius * math.cos(phi)

                vertex.addData3f(x, y, z)

                t = j / rings
                if z > 0:
                    r = 0.4 + 0.1 * (1 - t)
                    g = 0.55 + 0.2 * (1 - t)
                    b = 0.85 + 0.1 * (1 - t)
                else:
                    r = 0.6 + 0.15 * (1 - t)
                    g = 0.65 + 0.1 * (1 - t)
                    b = 0.75 + 0.05 * (1 - t)

                horizon = abs(z / sky_radius)
                if horizon < 0.3:
                    blend = 1.0 - horizon / 0.3
                    r = r * (1 - blend * 0.3) + 0.9 * blend * 0.3
                    g = g * (1 - blend * 0.2) + 0.8 * blend * 0.2
                    b = b * (1 - blend * 0.1) + 0.7 * blend * 0.1

                color_writer.addData4f(r, g, b, 1)

        prim = GeomTriangles(Geom.UHStatic)
        for j in range(rings):
            for i in range(segments):
                p0 = j * (segments + 1) + i
                p1 = p0 + 1
                p2 = (j + 1) * (segments + 1) + i
                p3 = p2 + 1

                prim.addVertices(p0, p2, p1)
                prim.addVertices(p1, p2, p3)

        geom = Geom(vdata)
        geom.addPrimitive(prim)
        node = GeomNode('sky')
        node.addGeom(geom)
        sky_np = NodePath(node)
        sky_np.setLightOff()
        sky_np.setTwoSided(True)
        sky_np.reparentTo(self.render)

        self.sky_node = sky_np

    def setup_fog(self):
        fog = Fog('distance_fog')
        fog.setColor(*Config.FOG_COLOR[:3])
        fog.setLinearRange(200, 800)
        self.render.setFog(fog)

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

        if hasattr(self, 'sky_node'):
            self.sky_node.setPos(target_pos.getX(), target_pos.getY(), 0)

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
        print("Vehicle reset")

    def exit(self):
        print("\n=== Simulation End ===")
        print(f"Total violations: {self.violation_detector.get_violation_count()}")
        print(f"Speeding: {self.violation_detector.get_speeding_count()}")
        print(f"Lane crossing: {self.violation_detector.get_lane_crossing_count()}")
        print(f"Max speed: {self.speed_monitor.get_max_speed():.1f} km/h")

        self.hud.cleanup()
        self.keyboard_controller.cleanup()
        self.userExit()


def main():
    app = HighwaySimulationApp()
    app.run()


if __name__ == '__main__':
    main()
