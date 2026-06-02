import random
import math
from vpython import sphere, label, vector, color, local_light, distant_light

from solarsystem.constants import (
    SUN_DATA,
    PLANET_DATA,
    SIMULATION_SPEED,
    STAR_COUNT,
    STAR_DISTANCE,
)
from solarsystem.planet import Planet


class SolarSystem:
    def __init__(self, scene):
        self.scene = scene
        self.sun_pos = vector(0, 0, 0)
        self.speed_multiplier = 1.0
        self.running = True
        self.show_orbits = True
        self.show_labels = True
        self.show_rings = True
        self.show_stars = True

        self.sun = None
        self.sun_label = None
        self.planets = []
        self.stars = []
        self.info_panel = None
        self.control_panel = None

        self._create_sun()
        self._create_planets()
        self._create_stars()
        self._create_lighting()
        self._create_ui_elements()

    def _create_sun(self):
        self.sun = sphere(
            pos=self.sun_pos,
            radius=SUN_DATA["radius"],
            color=SUN_DATA["color"],
            emissive=True,
            make_trail=False,
        )

        self.sun_label = label(
            pos=self.sun_pos,
            text=f"{SUN_DATA['name']}\n{SUN_DATA['name_en']}",
            yoffset=SUN_DATA["radius"] + 1,
            xoffset=10,
            color=color.yellow,
            background=color.gray(0.3),
            height=12,
            box=True,
            line=True,
            linecolor=color.yellow,
        )

    def _create_planets(self):
        for planet_data in PLANET_DATA:
            planet = Planet(planet_data, self.sun_pos)
            self.planets.append(planet)

    def _create_stars(self):
        for _ in range(STAR_COUNT):
            theta = random.uniform(0, 2 * math.pi)
            phi = random.uniform(0, math.pi)
            r = STAR_DISTANCE + random.uniform(-5, 5)

            x = r * math.sin(phi) * math.cos(theta)
            y = r * math.sin(phi) * math.sin(theta)
            z = r * math.cos(phi)

            star = sphere(
                pos=vector(x, y, z),
                radius=random.uniform(0.05, 0.15),
                color=color.white,
                emissive=True,
                opacity=random.uniform(0.5, 1.0),
            )
            self.stars.append(star)

    def _create_lighting(self):
        local_light(pos=self.sun_pos, color=color.white)
        distant_light(direction=vector(1, 0.5, 1), color=color.gray(0.3))
        distant_light(direction=vector(-1, -0.5, -1), color=color.gray(0.2))

    def _create_ui_elements(self):
        controls_text = (
            "控制说明 (Controls):\n"
            "  [空格]  暂停/继续 (Pause/Resume)\n"
            "  [↑]     加速 (Speed Up)\n"
            "  [↓]     减速 (Speed Down)\n"
            "  [O]     显示/隐藏轨道 (Toggle Orbits)\n"
            "  [L]     显示/隐藏标签 (Toggle Labels)\n"
            "  [R]     显示/隐藏行星环 (Toggle Rings)\n"
            "  [S]     显示/隐藏星空 (Toggle Stars)\n"
            "  [0]     重置 (Reset)\n"
            "  [Q]     退出 (Quit)\n\n"
            "鼠标左键拖拽: 旋转视角 | 右键拖拽: 平移 | 滚轮: 缩放"
        )

        self.control_panel = label(
            pos=vector(-35, 25, 0),
            text=controls_text,
            color=color.white,
            background=color.gray(0.3),
            xoffset=-20,
            height=10,
            box=True,
            line=False,
            align="left",
        )

        self.info_panel = label(
            pos=vector(30, 25, 0),
            text="",
            color=color.cyan,
            background=color.gray(0.3),
            xoffset=20,
            height=10,
            box=True,
            line=False,
            align="left",
        )

    def update(self, dt):
        if not self.running:
            return

        adjusted_dt = dt * SIMULATION_SPEED * self.speed_multiplier
        self.sun.rotate(angle=0.01 * adjusted_dt, axis=vector(0, 1, 0))

        for planet in self.planets:
            planet.update(dt, self.speed_multiplier)

        self._update_info_panel()

    def _update_info_panel(self):
        info_text = "太阳系 3D 模拟\n"
        info_text += "Solar System 3D Simulation\n\n"
        info_text += f"运行状态: {'运行中' if self.running else '已暂停'}\n"
        info_text += f"模拟速度: {self.speed_multiplier:.1f}x\n\n"
        info_text += "天体数据 (相对地球):\n"
        info_text += f"  行星数量: {len(self.planets)}\n"
        info_text += f"  显示轨道: {'是' if self.show_orbits else '否'}\n"
        info_text += f"  显示标签: {'是' if self.show_labels else '否'}\n\n"
        info_text += "行星公转周期:\n"

        for planet in self.planets:
            period_years = planet.orbit_period / 365.25
            info_text += f"  {planet.name}: {period_years:.2f} 年\n"

        self.info_panel.text = info_text

    def toggle_running(self):
        self.running = not self.running
        return self.running

    def set_speed(self, multiplier):
        self.speed_multiplier = max(0.1, min(10.0, multiplier))

    def increase_speed(self):
        self.set_speed(self.speed_multiplier + 0.5)

    def decrease_speed(self):
        self.set_speed(self.speed_multiplier - 0.5)

    def toggle_orbits(self):
        self.show_orbits = not self.show_orbits
        for planet in self.planets:
            planet.toggle_orbit(self.show_orbits)
        return self.show_orbits

    def toggle_labels(self):
        self.show_labels = not self.show_labels
        self.sun_label.visible = self.show_labels
        for planet in self.planets:
            planet.toggle_label(self.show_labels)
        return self.show_labels

    def toggle_rings(self):
        self.show_rings = not self.show_rings
        for planet in self.planets:
            planet.toggle_ring(self.show_rings)
        return self.show_rings

    def toggle_stars(self):
        self.show_stars = not self.show_stars
        for star in self.stars:
            star.visible = self.show_stars
        return self.show_stars

    def reset(self):
        self.speed_multiplier = 1.0
        self.running = True
        for planet in self.planets:
            planet.angle = 0
            planet.rotation_angle = 0
