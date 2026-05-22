import sys
import os
import math

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from panda3d.core import *
from direct.gui.OnscreenText import OnscreenText

from config.settings import (
    CAMERA_DISTANCE, CAMERA_ANGLE_H, CAMERA_ANGLE_V,
    STATUS_WAITING, STATUS_TAXIING, STATUS_TAKEOFF, STATUS_LANDING,
    STATUS_LABELS
)
from airport.airport_builder import AirportBuilder
from systems.dispatcher import Dispatcher
from ui.dispatch_board import DispatchBoard


class AirportDispatchingApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        ShowBase.base = self

        self.disableMouse()
        self.setBackgroundColor(0.4, 0.6, 0.9, 1)

        self.cam_distance = CAMERA_DISTANCE
        self.cam_angle_h = CAMERA_ANGLE_H
        self.cam_angle_v = CAMERA_ANGLE_V
        self.cam_target = LVector3(0, 0, 0)
        self.paused = False

        self.setup_lighting()
        self.setup_controls()

        self.airport = AirportBuilder(self.render, self.loader).build()

        self.picker = CollisionTraverser()
        self.pq = CollisionHandlerQueue()
        self._setup_ground_collision()
        self.accept('mouse1', self.on_mouse_click)
        self.dispatcher = Dispatcher(self.render, self.loader, self.airport)

        self.dispatch_board = DispatchBoard(self, self.dispatcher).build()
        self.dispatcher.on_status_change = self.dispatch_board.update_status

        self.dispatcher.create_initial_aircrafts(count=4)
        self.dispatch_board.update_board(self.dispatcher.get_all_aircrafts())
        self.dispatch_board.select_aircraft(None)

        self.taskMgr.add(self.update, "update")
        self.taskMgr.add(self.update_camera, "update_camera")

        self.add_title()

    def setup_lighting(self):
        directional_light = DirectionalLight('directional_light')
        directional_light.setColor(VBase4(1.0, 0.95, 0.85, 1))
        directional_light.setDirection(LVector3(-1, -1, -2))
        dl_np = self.render.attachNewNode(directional_light)
        self.render.setLight(dl_np)

        ambient_light = AmbientLight('ambient_light')
        ambient_light.setColor(VBase4(0.4, 0.45, 0.5, 1))
        ambient_np = self.render.attachNewNode(ambient_light)
        self.render.setLight(ambient_np)

        fill_light = DirectionalLight('fill_light')
        fill_light.setColor(VBase4(0.3, 0.35, 0.4, 1))
        fill_light.setDirection(LVector3(1, 0.5, -1))
        fl_np = self.render.attachNewNode(fill_light)
        self.render.setLight(fl_np)

        self.render.setShaderAuto()

    def setup_controls(self):
        self.key_map = {
            'rotate_left': False,
            'rotate_right': False,
            'rotate_up': False,
            'rotate_down': False,
            'zoom_in': False,
            'zoom_out': False,
        }

        self.accept('arrow_left', self.set_key, ['rotate_left', True])
        self.accept('arrow_left-up', self.set_key, ['rotate_left', False])
        self.accept('arrow_right', self.set_key, ['rotate_right', True])
        self.accept('arrow_right-up', self.set_key, ['rotate_right', False])
        self.accept('arrow_up', self.set_key, ['rotate_up', True])
        self.accept('arrow_up-up', self.set_key, ['rotate_up', False])
        self.accept('arrow_down', self.set_key, ['rotate_down', True])
        self.accept('arrow_down-up', self.set_key, ['rotate_down', False])
        self.accept('w', self.set_key, ['zoom_in', True])
        self.accept('w-up', self.set_key, ['zoom_in', False])
        self.accept('s', self.set_key, ['zoom_out', True])
        self.accept('s-up', self.set_key, ['zoom_out', False])

        self.accept('r', self.reset_camera)
        self.accept('space', self.toggle_pause)
        self.accept('escape', sys.exit)

    def _setup_ground_collision(self):
        ground_plane = CollisionPlane(Plane(Vec3(0, 0, 1), Point3(0, 0, 0)))
        ground_node = CollisionNode('ground_plane')
        ground_node.addSolid(ground_plane)
        ground_node.setIntoCollideMask(BitMask32.bit(1))
        self.ground_np = self.render.attachNewNode(ground_node)

        self.picker_ray = CollisionRay()
        picker_node = CollisionNode('mouseRay')
        picker_node.addSolid(self.picker_ray)
        picker_node.setFromCollideMask(BitMask32.bit(1))
        picker_node.setIntoCollideMask(BitMask32.allOff())
        self.picker_np = self.camera.attachNewNode(picker_node)
        self.picker.addCollider(self.picker_np, self.pq)

    def set_key(self, key, value):
        self.key_map[key] = value

    def reset_camera(self):
        self.cam_distance = CAMERA_DISTANCE
        self.cam_angle_h = CAMERA_ANGLE_H
        self.cam_angle_v = CAMERA_ANGLE_V
        self.cam_target = LVector3(0, 0, 0)

    def toggle_pause(self):
        self.paused = not self.paused
        status = "已暂停" if self.paused else "已继续"
        self.dispatch_board.show_message(f"调度系统{status}")

    def on_mouse_click(self):
        if self.mouseWatcherNode.hasMouse():
            mpos = self.mouseWatcherNode.getMouse()

            self.picker_ray.setFromLens(self.camNode, mpos.getX(), mpos.getY())
            self.picker.traverse(self.render)

            if self.pq.getNumEntries() > 0:
                self.pq.sortEntries()
                entry = self.pq.getEntry(0)
                hit_pos = entry.getSurfacePoint(self.render)

                aircraft = self.dispatcher.get_aircraft_at_position(hit_pos)
                if aircraft:
                    self.handle_aircraft_click(aircraft)
                else:
                    self.dispatch_board.select_aircraft(None)
                    self.dispatch_board.update_board(self.dispatcher.get_all_aircrafts())

    def handle_aircraft_click(self, aircraft):
        self.dispatch_board.select_aircraft(aircraft)

        if aircraft.status == STATUS_TAKEOFF or aircraft.status == STATUS_LANDING:
            self.dispatch_board.show_message(
                f"航班 {aircraft.flight_number} 正在{STATUS_LABELS.get(aircraft.status, '')}中，无法切换"
            )
            self.dispatch_board.update_board(self.dispatcher.get_all_aircrafts())
            return

        result = self.dispatcher.toggle_aircraft_status(aircraft)

        messages = {
            'takeoff_requested': f"航班 {aircraft.flight_number} 请求起飞",
            'landing_requested': f"航班 {aircraft.flight_number} 请求降落",
            'request_failed': f"跑道繁忙或无可用停机位，请稍后再试",
            'paused': f"航班 {aircraft.flight_number} 已暂停，返回等待状态",
            'cannot_toggle_in_flight': f"航班正在飞行中，无法切换",
        }

        msg = messages.get(result, "")
        if msg:
            self.dispatch_board.show_message(msg)

        self.dispatch_board.update_board(self.dispatcher.get_all_aircrafts())

    def update(self, task):
        if not self.paused:
            dt = globalClock.getDt()
            self.dispatcher.update(dt)

            aircrafts = self.dispatcher.get_all_aircrafts()
            if len(self.dispatch_board.flight_entries) != len(aircrafts):
                self.dispatch_board.update_board(aircrafts)

        return Task.cont

    def update_camera(self, task):
        dt = globalClock.getDt()

        if self.key_map['rotate_left']:
            self.cam_angle_h -= 60 * dt
        if self.key_map['rotate_right']:
            self.cam_angle_h += 60 * dt
        if self.key_map['rotate_up']:
            self.cam_angle_v = min(self.cam_angle_v + 40 * dt, 85)
        if self.key_map['rotate_down']:
            self.cam_angle_v = max(self.cam_angle_v - 40 * dt, -85)
        if self.key_map['zoom_in']:
            self.cam_distance = max(self.cam_distance - 25 * dt, 20)
        if self.key_map['zoom_out']:
            self.cam_distance = min(self.cam_distance + 25 * dt, 150)

        h_rad = math.radians(self.cam_angle_h)
        v_rad = math.radians(self.cam_angle_v)

        cam_x = self.cam_distance * math.cos(v_rad) * math.sin(h_rad)
        cam_y = -self.cam_distance * math.cos(v_rad) * math.cos(h_rad)
        cam_z = self.cam_distance * math.sin(v_rad)

        self.camera.setPos(
            self.cam_target.getX() + cam_x,
            self.cam_target.getY() + cam_y,
            self.cam_target.getZ() + cam_z
        )
        self.camera.lookAt(self.cam_target)

        return Task.cont

    def add_title(self):
        title = OnscreenText(
            text="3D 机场航班调度模拟系统",
            pos=(0, 0.92),
            fg=(0.95, 0.95, 1.0, 1),
            bg=(0.1, 0.15, 0.3, 0.8),
            align=TextNode.ACenter,
            scale=0.07
        )

        status_title = OnscreenText(
            text="跑道状态: " + ("空闲" if not self.dispatcher.runway_busy else "使用中"),
            pos=(0, 0.85),
            fg=(0.6, 1.0, 0.6, 1) if not self.dispatcher.runway_busy else (1.0, 0.6, 0.6, 1),
            align=TextNode.ACenter,
            scale=0.045
        )

        self.status_title = status_title

        def update_runway_status(task):
            if hasattr(self, 'status_title') and self.status_title:
                is_busy = self.dispatcher.runway_busy
                self.status_title.setText(
                    "跑道状态: " + ("空闲" if not is_busy else "使用中")
                )
                self.status_title.setFg(
                    (0.6, 1.0, 0.6, 1) if not is_busy else (1.0, 0.6, 0.6, 1)
                )
            return task.cont

        self.taskMgr.add(update_runway_status, 'update_runway_status')


if __name__ == "__main__":
    app = AirportDispatchingApp()
    app.run()
