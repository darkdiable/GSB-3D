#!/usr/bin/env python3
"""
部件标注模块
Labels Module - creates labels for engine components and strokes
"""

from vpython import label, vector, color

from ice3D.config.settings import (
    ENGINE_GEOMETRY,
    ENGINE_POSITION,
    COLORS,
    LABEL_CONFIG,
    STROKES,
    FIRING_ORDER,
)


class ComponentLabels:
    def __init__(self, scene, engine):
        self.scene = scene
        self.engine = engine
        self.geo = ENGINE_GEOMETRY
        self.pos = ENGINE_POSITION
        self.colors = COLORS
        self.label_config = LABEL_CONFIG
        
        self.labels = {}
        self.cylinder_stroke_labels = []
        
        self._create_component_labels()
        self._create_stroke_labels()
    
    def _create_component_labels(self):
        label_defs = [
            {
                "key": "engine_block",
                "text": "气缸体\nCylinder Block",
                "pos": vector(7.5, -1, 0),
                "xoffset": 50,
                "yoffset": 0,
                "color": COLORS["engine_block"],
            },
            {
                "key": "cylinder_head",
                "text": "气缸盖\nCylinder Head",
                "pos": vector(7.5, 9.5, 0),
                "xoffset": 50,
                "yoffset": 0,
                "color": COLORS["cylinder_head"],
            },
            {
                "key": "cylinder_1",
                "text": "气缸1\nCylinder 1",
                "pos": vector(-4.5, 6, 0),
                "xoffset": -50,
                "yoffset": 20,
                "color": COLORS["cylinder"],
            },
            {
                "key": "cylinder_4",
                "text": "气缸4\nCylinder 4",
                "pos": vector(4.5, 6, 0),
                "xoffset": 50,
                "yoffset": 20,
                "color": COLORS["cylinder"],
            },
            {
                "key": "piston",
                "text": "活塞\nPiston",
                "pos": vector(-4.5, 4.5, 0),
                "xoffset": -50,
                "yoffset": -20,
                "color": COLORS["piston"],
            },
            {
                "key": "connecting_rod",
                "text": "连杆\nConnecting Rod",
                "pos": vector(0, 0, 0),
                "xoffset": 0,
                "yoffset": 30,
                "color": COLORS["connecting_rod"],
            },
            {
                "key": "crankshaft",
                "text": "曲轴\nCrankshaft",
                "pos": vector(0, -2.5, 0),
                "xoffset": 0,
                "yoffset": -40,
                "color": COLORS["crankshaft"],
            },
            {
                "key": "intake_valve",
                "text": "进气门\nIntake Valve",
                "pos": vector(-1.5, 9, 1.2),
                "xoffset": 40,
                "yoffset": 20,
                "color": COLORS["intake_valve"],
            },
            {
                "key": "exhaust_valve",
                "text": "排气门\nExhaust Valve",
                "pos": vector(-1.5, 9, -1.2),
                "xoffset": 40,
                "yoffset": -20,
                "color": COLORS["exhaust_valve"],
            },
            {
                "key": "spark_plug",
                "text": "火花塞\nSpark Plug",
                "pos": vector(0, 9, 0),
                "xoffset": -40,
                "yoffset": 30,
                "color": COLORS["spark_plug"],
            },
            {
                "key": "oil_pan",
                "text": "油底壳\nOil Pan",
                "pos": vector(7.5, -4, 0),
                "xoffset": 50,
                "yoffset": 0,
                "color": COLORS["oil_pan"],
            },
            {
                "key": "camshaft",
                "text": "进气歧管\nIntake Manifold",
                "pos": vector(0, 10.5, 1.8),
                "xoffset": 0,
                "yoffset": 30,
                "color": color.gray(0.4),
            },
        ]
        
        for ld in label_defs:
            lbl = label(
                pos=ld["pos"],
                text=ld["text"],
                xoffset=ld["xoffset"],
                yoffset=ld["yoffset"],
                color=self.colors["label_text"],
                background=self.colors["label_background"],
                linecolor=ld["color"],
                height=self.label_config["height"],
                box=self.label_config["box"],
                line=self.label_config["line"],
                font=self.label_config["font"],
            )
            self.labels[ld["key"]] = lbl
    
    def _create_stroke_labels(self):
        for i in range(4):
            x_offset = (i - 1.5) * self.geo["cylinder_spacing"]
            
            stroke_label = label(
                pos=vector(
                    self.pos["center"].x + x_offset,
                    self.pos["cylinder_y_offset"] + self.geo["cylinder_height"] + 2,
                    self.pos["center"].z
                ),
                text="",
                xoffset=0,
                yoffset=20,
                color=self.colors["label_text"],
                background=self.colors["label_background"],
                linecolor=color.white,
                height=self.label_config["height"],
                box=True,
                line=True,
                font=self.label_config["font"],
            )
            self.cylinder_stroke_labels.append(stroke_label)
    
    def update(self):
        for i, stroke_label in enumerate(self.cylinder_stroke_labels):
            stroke, cycle_angle = self.engine.get_cylinder_stroke_info(i)
            stroke_progress = (cycle_angle - stroke["angle_start"]) / 180.0
            
            stroke_label.text = (
                f"气缸{i+1} | Cylinder {i+1}\n"
                f"{stroke['name']}\n"
                f"{stroke['name_en']}\n"
                f"{stroke_progress*100:.0f}%"
            )
            stroke_label.linecolor = stroke["color"]
            
            if self.engine.focus_cylinder is not None:
                x_offset = (self.engine.focus_cylinder - 1.5) * self.geo["cylinder_spacing"]
                stroke_label.pos.x = self.pos["center"].x + x_offset
                stroke_label.visible = (i == self.engine.focus_cylinder)
            else:
                x_offset = (i - 1.5) * self.geo["cylinder_spacing"]
                stroke_label.pos.x = self.pos["center"].x + x_offset
                stroke_label.visible = self.engine.show_labels
        
        for key, lbl in self.labels.items():
            lbl.visible = self.engine.show_labels
    
    def toggle_visibility(self, visible):
        for lbl in self.labels.values():
            lbl.visible = visible
        for lbl in self.cylinder_stroke_labels:
            lbl.visible = visible
