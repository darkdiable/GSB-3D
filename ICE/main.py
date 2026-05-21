#!/usr/bin/env python3
"""
ICE - 4-Cylinder 4-Stroke Engine 3D Simulation
Main entry point for the engine simulation.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vpython import scene, rate, vector, color, box, label, local_light, distant_light

from ICE.engine.engine import FourCylinderEngine


def setup_scene():
    scene.title = "4缸4冲程发动机工作原理 3D模拟"
    scene.caption = "4-Cylinder 4-Stroke Engine 3D Simulation"
    scene.width = 1600
    scene.height = 900
    scene.background = color.gray(0.15)
    scene.autoscale = False
    scene.range = 18
    scene.forward = vector(0.3, -0.25, -1)
    scene.up = vector(0, 1, 0)
    scene.center = vector(0, 1, 0)

    local_light(pos=vector(0, 10, 0), color=color.white)
    distant_light(direction=vector(1, 0.5, 1), color=color.gray(0.6))
    distant_light(direction=vector(-1, -0.5, -1), color=color.gray(0.3))

    ground = box(
        pos=vector(0, -6, 0),
        length=40,
        width=20,
        height=0.3,
        color=color.gray(0.25)
    )

    return scene


def create_control_panel(engine):
    controls_text = (
        "控制说明 (Controls):\n"
        "  [空格]  暂停/继续 (Pause/Resume)\n"
        "  [↑]     加速 (Speed Up)\n"
        "  [↓]     减速 (Speed Down)\n"
        "  [L]     显示/隐藏标签 (Toggle Labels)\n"
        "  [E]     显示/隐藏特效 (Toggle Effects)\n"
        "  [R]     重置 (Reset)\n"
        "  [Q]     退出 (Quit)\n\n"
        "鼠标拖拽: 旋转视角 | 滚轮: 缩放"
    )

    control_lbl = label(
        pos=vector(-12, 8, 0),
        text=controls_text,
        color=color.white,
        background=color.gray(0.3),
        xoffset=-20,
        height=11,
        box=True,
        line=False,
        align="left"
    )

    return control_lbl


def handle_keypress(evt, engine):
    key = evt.key
    if key == ' ':
        running = engine.toggle_running()
        print(f"Engine {'running' if running else 'paused'}")
    elif key == 'up' or key == 'w':
        engine.increase_speed()
        print(f"Speed: {engine.speed_multiplier:.1f}x")
    elif key == 'down' or key == 's':
        engine.decrease_speed()
        print(f"Speed: {engine.speed_multiplier:.1f}x")
    elif key == 'l' or key == 'L':
        show = engine.toggle_labels()
        print(f"Labels {'shown' if show else 'hidden'}")
    elif key == 'e' or key == 'E':
        show = engine.toggle_effects()
        print(f"Effects {'shown' if show else 'hidden'}")
    elif key == 'r' or key == 'R':
        engine.reset()
        print("Engine reset")
    elif key == 'q' or key == 'Q':
        print("Quitting...")
        exit(0)


def main():
    print("=" * 60)
    print("ICE - 4-Cylinder 4-Stroke Engine 3D Simulation")
    print("=" * 60)
    print("\n正在初始化3D场景，请稍候...\n")

    scene = setup_scene()
    engine = FourCylinderEngine(scene)
    control_panel = create_control_panel(engine)

    scene.bind('keydown', lambda evt: handle_keypress(evt, engine))

    print("发动机模拟已启动！")
    print("请在浏览器中查看3D场景")
    print("=" * 60)

    try:
        while True:
            rate(60)
            engine.update()
    except KeyboardInterrupt:
        print("\n模拟已停止")
        sys.exit(0)


if __name__ == "__main__":
    main()
