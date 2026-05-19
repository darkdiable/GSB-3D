from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from panda3d.core import *
from direct.gui.OnscreenText import OnscreenText
import math
import sys
from random import random

class SolarSystem(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        self.disableMouse()
        self.camera.setPos(0, -80, 40)
        self.camera.lookAt(0, 0, 0)

        self.setBackgroundColor(0, 0, 0.05)

        self.setup_lighting()
        self.create_skybox()
        self.create_sun()
        self.create_planets()
        self.setup_controls()

        self.cam_distance = 80
        self.cam_angle_h = 0
        self.cam_angle_v = 25
        self.cam_target = LVector3(0, 0, 0)

        self.taskMgr.add(self.update_solar_system, "update_solar_system")
        self.taskMgr.add(self.update_camera, "update_camera")

        self.add_instructions()

    def setup_lighting(self):
        sun_light = PointLight('sun_light')
        sun_light.setColor(VBase4(1, 1, 0.9, 1))
        sun_light.setAttenuation(Point3(0, 0, 0.0001))
        self.sun_light_np = self.render.attachNewNode(sun_light)
        self.sun_light_np.setPos(0, 0, 0)
        self.render.setLight(self.sun_light_np)

        ambient_light = AmbientLight('ambient_light')
        ambient_light.setColor(VBase4(0.15, 0.15, 0.2, 1))
        ambient_np = self.render.attachNewNode(ambient_light)
        self.render.setLight(ambient_np)

    def create_skybox(self):
        skybox = loader.loadModel("models/box")
        skybox.reparentTo(self.render)
        skybox.setScale(500)
        skybox.setBin('background', 1)
        skybox.setDepthWrite(0)
        skybox.setLightOff()
        
        tex = Texture()
        tex.setupCubeMap()
        
        for i in range(6):
            face_img = PNMImage(256, 256, 3)
            face_img.fill(0, 0, 0)
            for _ in range(100):
                x = int(random() * 256)
                y = int(random() * 256)
                brightness = 0.3 + random() * 0.7
                face_img.setXel(x, y, brightness, brightness, brightness)
            tex.load(face_img, i)
        
        ts = TextureStage('ts')
        skybox.setTexture(ts, tex)

        stars = self.render.attachNewNode('stars')
        for i in range(500):
            theta = 2 * math.pi * random()
            phi = math.acos(2 * random() - 1)
            r = 150 + random() * 50
            x = r * math.sin(phi) * math.cos(theta)
            y = r * math.sin(phi) * math.sin(theta)
            z = r * math.cos(phi)
            
            star = loader.loadModel("models/sphere")
            star.reparentTo(stars)
            star.setPos(x, y, z)
            star.setScale(0.2 + random() * 0.3)
            star.setLightOff()
            star.setColor(1, 1, 1, 1)

    def create_sun(self):
        self.sun = self.render.attachNewNode('sun')
        self.sun.setPos(0, 0, 0)

        sun_sphere = loader.loadModel("models/sphere")
        sun_sphere.reparentTo(self.sun)
        sun_sphere.setScale(5)

        sun_material = Material()
        sun_material.setEmission((1, 0.9, 0.3, 1))
        sun_material.setShininess(10)
        sun_sphere.setMaterial(sun_material)
        sun_sphere.setLightOff()

        sun_glow = loader.loadModel("models/sphere")
        sun_glow.reparentTo(self.sun)
        sun_glow.setScale(6)
        sun_glow.setColor(1, 0.8, 0.2, 0.3)
        sun_glow.setTransparency(TransparencyAttrib.MAlpha)
        sun_glow.setLightOff()
        sun_glow.setDepthWrite(False)

        self.add_label(self.sun, "Sun", (1, 1, 0.5, 1), 8)

    def create_planets(self):
        self.planets = []
        self.orbits = []
        
        planets_data = [
            {"name": "Mercury", "radius": 1.2, "orbit_radius": 12, "orbit_speed": 4.74, 
             "rotation_speed": 0.03, "color": (0.7, 0.7, 0.7, 1), "start_angle": 0.0},
            {"name": "Venus", "radius": 1.8, "orbit_radius": 17, "orbit_speed": 3.50,
             "rotation_speed": 0.005, "color": (1.0, 0.6, 0.2, 1), "start_angle": 0.8},
            {"name": "Earth", "radius": 2.0, "orbit_radius": 23, "orbit_speed": 2.98,
             "rotation_speed": 0.1, "color": (0.2, 0.4, 1.0, 1), "start_angle": 1.6},
            {"name": "Mars", "radius": 1.5, "orbit_radius": 29, "orbit_speed": 2.41,
             "rotation_speed": 0.09, "color": (1.0, 0.3, 0.2, 1), "start_angle": 2.4},
            {"name": "Jupiter", "radius": 4.0, "orbit_radius": 38, "orbit_speed": 1.31,
             "rotation_speed": 0.2, "color": (1.0, 0.7, 0.4, 1), "start_angle": 3.2},
            {"name": "Saturn", "radius": 3.5, "orbit_radius": 47, "orbit_speed": 0.97,
             "rotation_speed": 0.18, "color": (1.0, 0.9, 0.6, 1), "start_angle": 4.0},
            {"name": "Uranus", "radius": 2.8, "orbit_radius": 56, "orbit_speed": 0.68,
             "rotation_speed": 0.15, "color": (0.5, 1.0, 1.0, 1), "start_angle": 4.8},
            {"name": "Neptune", "radius": 2.7, "orbit_radius": 65, "orbit_speed": 0.54,
             "rotation_speed": 0.16, "color": (0.3, 0.5, 1.0, 1), "start_angle": 5.6}
        ]

        for data in planets_data:
            self.create_orbit(data["orbit_radius"])

            orbit_node = self.render.attachNewNode(f'orbit_{data["name"]}')
            orbit_node.setPos(0, 0, 0)

            planet_node = orbit_node.attachNewNode(f'planet_{data["name"]}')
            planet_node.setPos(data["orbit_radius"], 0, 0)
            planet_node.setHpr(math.degrees(data["start_angle"]), 0, 0)

            sphere = loader.loadModel("models/sphere")
            sphere.reparentTo(planet_node)
            sphere.setScale(data["radius"])

            material = Material()
            material.setDiffuse(data["color"])
            material.setSpecular((0.2, 0.2, 0.2, 1))
            material.setShininess(20)
            sphere.setMaterial(material)

            self.add_label(planet_node, data["name"], data["color"], data["radius"] * 1.5 + 1)

            if data["name"] == "Saturn":
                self.create_saturn_rings(planet_node, data["radius"])

            self.planets.append({
                "node": planet_node,
                "orbit": orbit_node,
                "data": data,
                "angle": data["start_angle"]
            })

    def create_orbit(self, radius):
        orbit = self.render.attachNewNode(f'orbit_line_{radius}')
        
        segments = 64
        lines = LineSegs()
        lines.setColor(0.4, 0.4, 0.5, 0.6)
        lines.setThickness(1)
        
        for i in range(segments + 1):
            angle = 2 * math.pi * i / segments
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            if i == 0:
                lines.moveTo(x, y, 0)
            else:
                lines.drawTo(x, y, 0)
        
        node = lines.create()
        orbit.attachNewNode(node)
        self.orbits.append(orbit)

    def create_saturn_rings(self, parent, planet_radius):
        ring_node = parent.attachNewNode('saturn_rings')
        
        outer_radius = planet_radius * 2.2
        inner_radius = planet_radius * 1.3
        
        ring = loader.loadModel("models/torus")
        if ring:
            ring.reparentTo(ring_node)
            ring.setScale(outer_radius, outer_radius, 0.2)
            ring.setP(75)
            
            material = Material()
            material.setDiffuse((0.8, 0.75, 0.6, 0.8))
            material.setTransparency(TransparencyAttrib.MAlpha)
            ring.setMaterial(material)
        else:
            segments = 48
            lines = LineSegs()
            lines.setColor(0.8, 0.75, 0.6, 0.7)
            lines.setThickness(2)
            
            for i in range(segments + 1):
                angle = 2 * math.pi * i / segments
                x = outer_radius * math.cos(angle)
                z = outer_radius * math.sin(angle) * 0.3
                if i == 0:
                    lines.moveTo(x, 0, z)
                else:
                    lines.drawTo(x, 0, z)
            
            node = lines.create()
            ring_node.attachNewNode(node)

    def add_label(self, parent, text, color, offset):
        label = OnscreenText(
            text=text,
            pos=(0, 0),
            fg=color,
            bg=(0, 0, 0, 0.5),
            align=TextNode.ACenter,
            scale=0.05,
            mayChange=False,
            parent=parent
        )
        label.setBillboardPointEye()
        label.setPos(0, 0, offset)
        label.setDepthWrite(False)

    def setup_controls(self):
        self.key_map = {
            'rotate_left': False,
            'rotate_right': False,
            'rotate_up': False,
            'rotate_down': False,
            'zoom_in': False,
            'zoom_out': False,
            'speed_up': False,
            'speed_down': False
        }

        self.time_scale = 1.0

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
        self.accept('+', self.set_key, ['speed_up', True])
        self.accept('-', self.set_key, ['speed_down', True])
        self.accept('=', self.set_key, ['speed_up', True])
        self.accept('_', self.set_key, ['speed_down', True])
        self.accept('escape', sys.exit)

    def set_key(self, key, value):
        self.key_map[key] = value

    def update_solar_system(self, task):
        dt = globalClock.getDt() * self.time_scale

        for planet_info in self.planets:
            data = planet_info["data"]
            planet_info["angle"] += data["orbit_speed"] * 0.01 * dt
            
            angle = planet_info["angle"]
            x = data["orbit_radius"] * math.cos(angle)
            y = data["orbit_radius"] * math.sin(angle)
            planet_info["node"].setPos(x, y, 0)
            planet_info["node"].setH(planet_info["node"].getH() + data["rotation_speed"] * 60 * dt)

        self.sun.setH(self.sun.getH() + 5 * dt)

        if self.key_map['speed_up']:
            self.time_scale = min(self.time_scale * 1.02, 10)
            self.key_map['speed_up'] = False
        if self.key_map['speed_down']:
            self.time_scale = max(self.time_scale * 0.98, 0.1)
            self.key_map['speed_down'] = False

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
            self.cam_distance = max(self.cam_distance - 30 * dt, 10)
        if self.key_map['zoom_out']:
            self.cam_distance = min(self.cam_distance + 30 * dt, 200)

        h_rad = math.radians(self.cam_angle_h)
        v_rad = math.radians(self.cam_angle_v)
        
        cam_x = self.cam_distance * math.cos(v_rad) * math.sin(h_rad)
        cam_y = -self.cam_distance * math.cos(v_rad) * math.cos(h_rad)
        cam_z = self.cam_distance * math.sin(v_rad)
        
        self.camera.setPos(self.cam_target.getX() + cam_x,
                          self.cam_target.getY() + cam_y,
                          self.cam_target.getZ() + cam_z)
        self.camera.lookAt(self.cam_target)

        return Task.cont

    def add_instructions(self):
        instructions = [
            "Controls:",
            "Arrow Keys: Rotate Camera",
            "W/S: Zoom In/Out",
            "+/-: Speed Up/Down",
            "ESC: Exit"
        ]
        
        y_pos = 0.85
        for text in instructions:
            OnscreenText(
                text=text,
                pos=(-0.9, y_pos),
                fg=(1, 1, 1, 0.8),
                align=TextNode.ALeft,
                scale=0.04
            )
            y_pos -= 0.05

if __name__ == "__main__":
    app = SolarSystem()
    app.run()
