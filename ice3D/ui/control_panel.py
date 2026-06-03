#!/usr/bin/env python3
"""
控制面板模块
Control Panel Module - creates UI panels for engine info and controls
"""

from vpython import label, vector, color

from ice3D.config.settings import (
    COLORS,
    CONTROLS,
    STROKES,
    FIRING_ORDER,
)


class ControlPanel:
    def __init__(self, scene, engine):
        self.scene = scene
        self.engine = engine
        self.colors = COLORS
        
        self.info_panel = None
        self.control_panel = None
        self.stroke_legend = None
        
        self._create_info_panel()
        self._create_control_panel()
        self._create_stroke_legend()
    
    def _create_info_panel(self):
        self.info_panel = label(
            pos=vector(-15, 12, 0),
            text="",
            color=color.cyan,
            background=color.gray(0.2),
            xoffset=-20,
            height=11,
            box=True,
            line=False,
            align="left",
            font="sans",
        )
    
    def _create_control_panel(self):
        controls_text = "控制说明 (Controls):\n"
        controls_text += "-" * 30 + "\n"
        
        key_map = {
            "space": "空格",
            "up": "↑",
            "down": "↓",
            "l": "L",
            "x": "X",
            "r": "R",
            "1-4": "1-4",
            "0": "0",
            "q": "Q",
        }
        
        for key, desc in CONTROLS.items():
            display_key = key_map.get(key, key)
            controls_text += f"  [{display_key}]  {desc}\n"
        
        controls_text += "\n鼠标操作:\n"
        controls_text += "  左键拖拽: 旋转视角\n"
        controls_text += "  右键拖拽: 平移\n"
        controls_text += "  滚轮: 缩放"
        
        self.control_panel = label(
            pos=vector(-15, -12, 0),
            text=controls_text,
            color=color.white,
            background=color.gray(0.2),
            xoffset=-20,
            height=10,
            box=True,
            line=False,
            align="left",
            font="sans",
        )
    
    def _create_stroke_legend(self):
        legend_text = "四冲程说明 (Four Strokes):\n"
        legend_text += "-" * 35 + "\n"
        
        for stroke in STROKES:
            color_indicator = "■"
            legend_text += f"  {color_indicator} {stroke['name']} ({stroke['name_en']}):\n"
            legend_text += f"     {stroke['description']}\n"
        
        legend_text += "\n点火顺序 (Firing Order): 1 → 3 → 4 → 2\n"
        
        self.stroke_legend = label(
            pos=vector(15, 12, 0),
            text=legend_text,
            color=color.white,
            background=color.gray(0.2),
            xoffset=20,
            height=10,
            box=True,
            line=False,
            align="left",
            font="sans",
        )
    
    def update(self):
        rpm = self.engine.get_rpm()
        stroke_info = []
        
        for i in range(4):
            stroke, cycle_angle = self.engine.get_cylinder_stroke_info(i)
            stroke_progress = (cycle_angle - stroke["angle_start"]) / 180.0
            
            is_firing = ""
            if FIRING_ORDER[self.engine.get_cylinder_stroke(i)] == i:
                if stroke["id"] == 2 and stroke_progress > 0.1 and stroke_progress < 0.3:
                    is_firing = " 🔥"
            
            stroke_info.append(
                f"  气缸{i+1}: {stroke['name']} ({stroke_progress*100:3.0f}%){is_firing}"
            )
        
        crank_angle_deg = (self.engine.crank_angle * 180 / 3.14159) % 720
        
        info_text = "发动机实时数据\n"
        info_text += "Engine Real-time Data\n"
        info_text += "=" * 30 + "\n\n"
        info_text += f"运行状态: {'▶ 运行中' if self.engine.running else '⏸ 已暂停'}\n"
        info_text += f"模拟速度: {self.engine.speed_multiplier:.1f}x\n"
        info_text += f"转速 (RPM): {rpm:.0f}\n"
        info_text += f"曲轴转角: {crank_angle_deg:.0f}° / 720°\n"
        info_text += f"剖视图: {'开启' if self.engine.cutaway_mode else '关闭'}\n"
        
        if self.engine.focus_cylinder is not None:
            info_text += f"聚焦气缸: {self.engine.focus_cylinder + 1}\n"
        else:
            info_text += "聚焦气缸: 全部\n"
        
        info_text += "\n各气缸状态:\n"
        for si in stroke_info:
            info_text += si + "\n"
        
        info_text += "\n点火顺序: "
        firing_order_display = []
        for idx in FIRING_ORDER:
            firing_order_display.append(f"{idx + 1}")
        info_text += " → ".join(firing_order_display) + "\n"
        
        current_firing_cylinder = int((crank_angle_deg // 180) % 4)
        actual_cylinder = FIRING_ORDER[current_firing_cylinder] + 1
        info_text += f"当前做功: 气缸 {actual_cylinder}\n"
        
        self.info_panel.text = info_text
    
    def toggle_visibility(self, visible):
        self.info_panel.visible = visible
        self.control_panel.visible = visible
        self.stroke_legend.visible = visible
