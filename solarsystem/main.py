#!/usr/bin/env python3
"""
3D Solar System Simulation
Main entry point for the solar system simulation.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vpython import scene, rate, vector, color

from solarsystem.solar_system import SolarSystem
from solarsystem.camera import CameraController


def setup_scene():
    scene.title = "3D太阳系模拟"
    scene.caption = "3D Solar System Simulation"
    scene.width = 1600
    scene.height = 900
    scene.background = color.black
    scene.autoscale = False
    scene.range = 45
    scene.forward = vector(0, -0.3, -1)
    scene.up = vector(0, 1, 0)
    scene.center = vector(0, 0, 0)
    scene.userzoom = False
    scene.userspin = False
    scene.userpan = False

    return scene


def handle_keypress(evt, solar_system):
    key = evt.key
    if key == ' ':
        running = solar_system.toggle_running()
        print(f"Simulation {'running' if running else 'paused'}")
    elif key == 'up' or key == 'w':
        solar_system.increase_speed()
        print(f"Speed: {solar_system.speed_multiplier:.1f}x")
    elif key == 'down' or key == 's':
        solar_system.decrease_speed()
        print(f"Speed: {solar_system.speed_multiplier:.1f}x")
    elif key == 'o' or key == 'O':
        show = solar_system.toggle_orbits()
        print(f"Orbits {'shown' if show else 'hidden'}")
    elif key == 'l' or key == 'L':
        show = solar_system.toggle_labels()
        print(f"Labels {'shown' if show else 'hidden'}")
    elif key == 'r' or key == 'R':
        show = solar_system.toggle_rings()
        print(f"Rings {'shown' if show else 'hidden'}")
    elif key == 's' and evt.ctrl:
        pass
    elif key == 'S':
        show = solar_system.toggle_stars()
        print(f"Stars {'shown' if show else 'hidden'}")
    elif key == '0':
        solar_system.reset()
        print("Simulation reset")
    elif key == 'q' or key == 'Q':
        print("Quitting...")
        exit(0)


def main():
    print("=" * 60)
    print("3D Solar System Simulation")
    print("3D太阳系模拟")
    print("=" * 60)
    print("\n正在初始化3D场景，请稍候...\n")

    scene = setup_scene()
    solar_system = SolarSystem(scene)
    camera = CameraController(scene)

    scene.bind('keydown', lambda evt: handle_keypress(evt, solar_system))

    def on_scroll(evt):
        if hasattr(evt, 'delta') and evt.delta:
            camera.handle_scroll(evt.delta)
        elif hasattr(evt, 'event') and 'wheel' in str(evt.event).lower():
            camera.handle_scroll(-1)

    scene.bind('scroll', on_scroll)

    print("太阳系模拟已启动！")
    print("请在浏览器中查看3D场景")
    print("=" * 60)

    try:
        while True:
            rate(60)
            dt = 1 / 60
            solar_system.update(dt)
    except KeyboardInterrupt:
        print("\n模拟已停止")
        sys.exit(0)


if __name__ == "__main__":
    main()
