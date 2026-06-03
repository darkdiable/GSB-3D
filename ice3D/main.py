#!/usr/bin/env python3
"""
四缸四冲程发动机三维模拟主程序
Main entry point for the 4-cylinder 4-stroke engine 3D simulation.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vpython import scene, rate, vector, color

from ice3D.config.settings import SCENE_CONFIG, ANIMATION_CONFIG
from ice3D.engine.four_stroke_engine import FourStrokeEngine
from ice3D.ui.labels import ComponentLabels
from ice3D.ui.control_panel import ControlPanel
from ice3D.ui.camera import CameraController


def setup_scene():
    scene.title = SCENE_CONFIG["title"]
    scene.width = SCENE_CONFIG["width"]
    scene.height = SCENE_CONFIG["height"]
    scene.background = SCENE_CONFIG["background"]
    scene.autoscale = False
    scene.range = SCENE_CONFIG["range"]
    scene.center = SCENE_CONFIG["center"]
    scene.up = SCENE_CONFIG["up"]
    scene.userspin = True
    scene.userzoom = True
    scene.userpan = True
    
    return scene


def handle_keypress(evt, engine, camera, app_state):
    key = evt.key
    
    if key == ' ':
        running = engine.toggle_running()
        print(f"Simulation {'running' if running else 'paused'}")
    
    elif key == 'up' or key == 'w' or key == 'W':
        engine.increase_speed()
        print(f"Speed: {engine.speed_multiplier:.1f}x")
    
    elif key == 'down' or key == 's' or key == 'S':
        engine.decrease_speed()
        print(f"Speed: {engine.speed_multiplier:.1f}x")
    
    elif key == 'l' or key == 'L':
        show = engine.toggle_labels()
        print(f"Labels {'shown' if show else 'hidden'}")
    
    elif key == 'x' or key == 'X':
        cutaway = engine.toggle_cutaway()
        print(f"Cutaway view: {'enabled' if cutaway else 'disabled'}")
    
    elif key == 'r' or key == 'R':
        rotating = camera.toggle_auto_rotate()
        print(f"Auto rotate: {'enabled' if rotating else 'disabled'}")
    
    elif key in ['1', '2', '3', '4']:
        cylinder_index = int(key) - 1
        if engine.focus_cylinder == cylinder_index:
            engine.focus_on_cylinder(None)
            camera.focus_on_cylinder(None)
            print(f"Showing all cylinders")
        else:
            engine.focus_on_cylinder(cylinder_index)
            camera.focus_on_cylinder(cylinder_index)
            print(f"Focusing on cylinder {cylinder_index + 1}")
    
    elif key == '0':
        engine.reset()
        camera.reset()
        print("Simulation reset")
    
    elif key == 'q' or key == 'Q':
        print("\nQuitting...")
        app_state["should_exit"] = True


def main():
    print("=" * 70)
    print("  四缸四冲程发动机三维模拟系统")
    print("  4-Cylinder 4-Stroke Engine 3D Simulation")
    print("=" * 70)
    print()
    print("正在初始化3D场景，请稍候...")
    print("Initializing 3D scene, please wait...")
    print()
    
    scene = setup_scene()
    
    print("正在创建发动机模型...")
    print("Creating engine model...")
    engine = FourStrokeEngine(scene)
    
    print("正在创建标注系统...")
    print("Creating labeling system...")
    labels = ComponentLabels(scene, engine)
    
    print("正在创建控制面板...")
    print("Creating control panel...")
    control_panel = ControlPanel(scene, engine)
    
    print("正在初始化相机控制器...")
    print("Initializing camera controller...")
    camera = CameraController(scene)
    
    app_state = {"should_exit": False}
    
    print()
    print("绑定键盘事件...")
    print("Binding keyboard events...")
    scene.bind('keydown', lambda evt: handle_keypress(evt, engine, camera, app_state))
    
    print()
    print("=" * 70)
    print("模拟已启动！请在浏览器中查看3D场景")
    print("Simulation started! Please view the 3D scene in your browser")
    print("=" * 70)
    print()
    print("按键提示 (Key Tips):")
    print("  [空格] 暂停/继续 | [↑/↓] 加速/减速 | [L] 标签 | [X] 剖视图")
    print("  [R] 自动旋转 | [1-4] 聚焦气缸 | [0] 重置 | [Q] 退出")
    print()
    
    fps = ANIMATION_CONFIG["fps"]
    
    try:
        while True:
            rate(fps)
            dt = 1.0 / fps
            
            if app_state["should_exit"]:
                print()
                print("=" * 70)
                print("模拟已停止")
                print("Simulation stopped")
                print("=" * 70)
                sys.exit(0)
            
            engine.update(dt)
            labels.update()
            control_panel.update()
            camera.update(dt)
    
    except KeyboardInterrupt:
        print()
        print("=" * 70)
        print("模拟已停止")
        print("Simulation stopped")
        print("=" * 70)
        sys.exit(0)


if __name__ == "__main__":
    main()
