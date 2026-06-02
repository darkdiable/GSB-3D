#!/usr/bin/env python3
"""
ice3D 配置文件
Configuration settings for the 4-cylinder 4-stroke engine simulation.
"""

from vpython import vector, color

# ==================== 场景配置 ====================
SCENE_CONFIG = {
    "title": "四缸四冲程发动机三维模拟 | 4-Cylinder 4-Stroke Engine Simulation",
    "width": 1600,
    "height": 900,
    "background": color.gray(0.1),
    "range": 20,
    "forward": vector(0, -0.3, -1),
    "up": vector(0, 1, 0),
    "center": vector(0, 0, 0),
}

# ==================== 动画配置 ====================
ANIMATION_CONFIG = {
    "fps": 60,
    "default_speed": 1.0,
    "min_speed": 0.1,
    "max_speed": 5.0,
    "speed_step": 0.3,
    "crankshaft_speed": 2.0,
}

# ==================== 发动机几何参数 ====================
ENGINE_GEOMETRY = {
    "cylinder_spacing": 3.0,
    "cylinder_radius": 1.2,
    "cylinder_height": 6.0,
    "cylinder_wall_thickness": 0.15,
    
    "piston_radius": 1.05,
    "piston_height": 1.5,
    
    "stroke_length": 3.0,
    "connecting_rod_length": 4.5,
    
    "crankshaft_radius": 0.4,
    "crank_pin_radius": 0.25,
    "crank_web_thickness": 0.3,
    
    "cylinder_head_height": 1.0,
    
    "valve_radius": 0.25,
    "valve_stem_radius": 0.08,
    "valve_length": 1.5,
    "valve_lift": 0.4,
    
    "camshaft_radius": 0.2,
    "cam_lobe_height": 0.3,
    
    "spark_plug_radius": 0.15,
    "spark_plug_length": 0.8,
    
    "engine_block_width": 14.0,
    "engine_block_height": 5.0,
    "engine_block_depth": 5.0,
    
    "oil_pan_height": 1.5,
}

# ==================== 发动机位置 ====================
ENGINE_POSITION = {
    "center": vector(0, 0, 0),
    "cylinder_y_offset": 3.0,
    "crankshaft_y": -2.5,
}

# ==================== 四冲程定义 ====================
STROKES = [
    {
        "id": 0,
        "name": "进气冲程",
        "name_en": "Intake Stroke",
        "description": "进气门开启，活塞下行，吸入油气混合气",
        "description_en": "Intake valve opens, piston moves down, drawing in air-fuel mixture",
        "angle_start": 0,
        "angle_end": 180,
        "piston_direction": -1,
        "intake_valve_open": True,
        "exhaust_valve_open": False,
        "color": color.blue,
    },
    {
        "id": 1,
        "name": "压缩冲程",
        "name_en": "Compression Stroke",
        "description": "气门关闭，活塞上行，压缩油气混合气",
        "description_en": "Valves closed, piston moves up, compressing air-fuel mixture",
        "angle_start": 180,
        "angle_end": 360,
        "piston_direction": 1,
        "intake_valve_open": False,
        "exhaust_valve_open": False,
        "color": color.orange,
    },
    {
        "id": 2,
        "name": "做功冲程",
        "name_en": "Power Stroke",
        "description": "火花塞点火，气体膨胀推动活塞下行",
        "description_en": "Spark plug fires, expanding gases push piston down",
        "angle_start": 360,
        "angle_end": 540,
        "piston_direction": -1,
        "intake_valve_open": False,
        "exhaust_valve_open": False,
        "color": color.red,
    },
    {
        "id": 3,
        "name": "排气冲程",
        "name_en": "Exhaust Stroke",
        "description": "排气门开启，活塞上行，排出废气",
        "description_en": "Exhaust valve opens, piston moves up, pushing out exhaust gases",
        "angle_start": 540,
        "angle_end": 720,
        "piston_direction": 1,
        "intake_valve_open": False,
        "exhaust_valve_open": True,
        "color": color.gray(0.5),
    },
]

# ==================== 四缸点火顺序 (1-3-4-2) ====================
FIRING_ORDER = [0, 2, 3, 1]
CYLINDER_PHASE_OFFSETS = [0, 360, 180, 540]

# ==================== 颜色配置 ====================
COLORS = {
    "engine_block": color.gray(0.4),
    "cylinder": color.gray(0.5),
    "cylinder_head": color.gray(0.3),
    "piston": color.gray(0.7),
    "connecting_rod": color.gray(0.6),
    "crankshaft": color.gray(0.55),
    "intake_valve": color.cyan,
    "exhaust_valve": color.magenta,
    "camshaft": color.gray(0.45),
    "spark_plug": color.yellow,
    "oil_pan": color.gray(0.35),
    "combustion": color.red,
    "intake_air": color.blue,
    "exhaust_gas": color.gray(0.6),
    "label_text": color.white,
    "label_background": color.gray(0.2),
    "highlight": color.yellow,
}

# ==================== 标注配置 ====================
LABEL_CONFIG = {
    "height": 12,
    "box": True,
    "line": True,
    "font": "sans",
}

# ==================== 控制说明 ====================
CONTROLS = {
    "space": "暂停/继续 (Pause/Resume)",
    "up": "加速 (Speed Up)",
    "down": "减速 (Speed Down)",
    "l": "显示/隐藏标签 (Toggle Labels)",
    "x": "显示/隐藏剖视图 (Toggle Cutaway)",
    "1-4": "聚焦单个气缸 (Focus on Cylinder 1-4)",
    "0": "重置视角 (Reset View)",
    "q": "退出 (Quit)",
}
