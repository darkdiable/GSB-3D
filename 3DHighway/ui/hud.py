from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectGui import *
from panda3d.core import *
from config.settings import SPEED_LIMIT, SPEED_UNIT, LANE_COUNT
from systems.speed_monitor import SpeedMonitor
from systems.lane_detection import LaneDetection
from vehicle.car import Car


class HUD:
    def __init__(self, aspect2d: NodePath):
        self.aspect2d = aspect2d
        self.elements = {}

        self._create_speed_display()
        self._create_lane_display()
        self._create_speed_limit_display()
        self._create_status_indicators()

    def _create_speed_display(self):
        speed_frame = DirectFrame(
            parent=self.aspect2d,
            pos=(-0.85, 0, -0.7),
            frameSize=(-0.15, 0.15, -0.12, 0.12),
            frameColor=(0, 0, 0, 0.7),
            relief=DGG.FLAT
        )
        self.elements['speed_frame'] = speed_frame

        speed_label = OnscreenText(
            text="车速",
            parent=speed_frame,
            pos=(0, 0.07),
            fg=(1, 1, 1, 0.9),
            align=TextNode.ACenter,
            scale=0.05
        )
        self.elements['speed_label'] = speed_label

        speed_value = OnscreenText(
            text="0",
            parent=speed_frame,
            pos=(0, -0.02),
            fg=(0, 1, 0, 1),
            align=TextNode.ACenter,
            scale=0.1,
            font=self._get_font()
        )
        self.elements['speed_value'] = speed_value

        speed_unit = OnscreenText(
            text=SPEED_UNIT,
            parent=speed_frame,
            pos=(0, -0.09),
            fg=(0.8, 0.8, 0.8, 0.9),
            align=TextNode.ACenter,
            scale=0.035
        )
        self.elements['speed_unit'] = speed_unit

    def _create_speed_limit_display(self):
        limit_frame = DirectFrame(
            parent=self.aspect2d,
            pos=(-0.6, 0, -0.7),
            frameSize=(-0.1, 0.1, -0.1, 0.1),
            frameColor=(1, 1, 1, 0.9),
            relief=DGG.RIDGE,
            borderWidth=(0.02, 0.02)
        )
        self.elements['limit_frame'] = limit_frame

        inner_circle = DirectFrame(
            parent=limit_frame,
            pos=(0, 0, 0),
            frameSize=(-0.07, 0.07, -0.07, 0.07),
            frameColor=(1, 1, 1, 1),
            relief=DGG.RIDGE
        )
        self.elements['limit_circle'] = inner_circle

        limit_value = OnscreenText(
            text=str(int(SPEED_LIMIT)),
            parent=inner_circle,
            pos=(0, -0.025),
            fg=(0, 0, 0, 1),
            align=TextNode.ACenter,
            scale=0.07,
            font=self._get_font()
        )
        self.elements['limit_value'] = limit_value

    def _create_lane_display(self):
        lane_frame = DirectFrame(
            parent=self.aspect2d,
            pos=(0.85, 0, -0.7),
            frameSize=(-0.15, 0.15, -0.12, 0.12),
            frameColor=(0, 0, 0, 0.7),
            relief=DGG.FLAT
        )
        self.elements['lane_frame'] = lane_frame

        lane_label = OnscreenText(
            text="当前车道",
            parent=lane_frame,
            pos=(0, 0.07),
            fg=(1, 1, 1, 0.9),
            align=TextNode.ACenter,
            scale=0.045
        )
        self.elements['lane_label'] = lane_label

        lane_indicator = self._create_lane_indicator(lane_frame)
        self.elements['lane_indicator'] = lane_indicator

        lane_value = OnscreenText(
            text="2 / " + str(LANE_COUNT),
            parent=lane_frame,
            pos=(0, -0.07),
            fg=(0.3, 0.6, 1, 1),
            align=TextNode.ACenter,
            scale=0.05
        )
        self.elements['lane_value'] = lane_value

    def _create_lane_indicator(self, parent):
        indicator_root = parent.attachNewNode("lane_indicator")
        indicator_root.setPos(0, 0, 0)
        indicator_root.setScale(0.08)

        lane_width = 0.8
        lane_spacing = 0.15
        line_width = 0.1

        for i in range(LANE_COUNT + 1):
            x = -((LANE_COUNT / 2) * (lane_width + lane_spacing)) + i * (lane_width + lane_spacing)

            if i == 0 or i == LANE_COUNT:
                line_card = CardMaker(f"edge_line_{i}")
                line_card.setFrame(x - line_width / 2, x + line_width / 2, -0.8, 0.8)
                line_card.setColor(1, 1, 0.8, 1)
                line_node = indicator_root.attachNewNode(line_card.generate())
                line_node.setTransparency(TransparencyAttrib.MAlpha)
            else:
                for j in range(4):
                    y_start = -0.8 + j * 0.45
                    line_card = CardMaker(f"lane_line_{i}_{j}")
                    line_card.setFrame(x - line_width / 2, x + line_width / 2, y_start, y_start + 0.2)
                    line_card.setColor(1, 1, 1, 1)
                    line_node = indicator_root.attachNewNode(line_card.generate())
                    line_node.setTransparency(TransparencyAttrib.MAlpha)

        for i in range(LANE_COUNT):
            x = -((LANE_COUNT / 2) * (lane_width + lane_spacing)) + (i + 0.5) * (lane_width + lane_spacing)

            lane_bg_card = CardMaker(f"lane_bg_{i}")
            lane_bg_card.setFrame(x - lane_width / 2, x + lane_width / 2, -0.8, 0.8)
            lane_bg_card.setColor(0.2, 0.2, 0.2, 0.8)
            lane_bg_node = indicator_root.attachNewNode(lane_bg_card.generate())
            lane_bg_node.setTransparency(TransparencyAttrib.MAlpha)

        car_card = CardMaker("car_indicator")
        car_card.setFrame(-0.3, 0.3, -0.4, 0.4)
        car_card.setColor(1, 0, 0, 1)
        car_node = indicator_root.attachNewNode(car_card.generate())
        car_node.setTransparency(TransparencyAttrib.MAlpha)
        car_node.setScale(0.6, 1, 0.8)
        self.elements['car_indicator'] = car_node

        return indicator_root

    def _create_status_indicators(self):
        status_frame = DirectFrame(
            parent=self.aspect2d,
            pos=(0, 0, 0.8),
            frameSize=(-0.5, 0.5, -0.05, 0.08),
            frameColor=(0, 0, 0, 0.5),
            relief=DGG.FLAT
        )
        self.elements['status_frame'] = status_frame

        title_text = OnscreenText(
            text="3D 高速行车模拟系统",
            parent=status_frame,
            pos=(0, 0.02),
            fg=(1, 0.8, 0.2, 1),
            align=TextNode.ACenter,
            scale=0.055
        )
        self.elements['title_text'] = title_text

        instructions = [
            "W/↑: 加速  |  S/↓: 刹车  |  A/←: 左转  |  D/→: 右转  |  ESC: 退出"
        ]

        y_pos = -0.75
        for text in instructions:
            instruction_text = OnscreenText(
                text=text,
                parent=self.aspect2d,
                pos=(0, y_pos),
                fg=(0.9, 0.9, 0.9, 0.9),
                align=TextNode.ACenter,
                scale=0.04
            )
            self.elements[f'instruction_{y_pos}'] = instruction_text
            y_pos -= 0.04

        stats_frame = DirectFrame(
            parent=self.aspect2d,
            pos=(-0.85, 0, 0.7),
            frameSize=(-0.18, 0.18, -0.1, 0.1),
            frameColor=(0, 0, 0, 0.6),
            relief=DGG.FLAT
        )
        self.elements['stats_frame'] = stats_frame

        self.elements['avg_speed_label'] = OnscreenText(
            text="平均速度: 0 km/h",
            parent=stats_frame,
            pos=(0, 0.04),
            fg=(0.8, 0.8, 0.8, 1),
            align=TextNode.ACenter,
            scale=0.035
        )

        self.elements['max_speed_label'] = OnscreenText(
            text="最高速度: 0 km/h",
            parent=stats_frame,
            pos=(0, -0.04),
            fg=(0.8, 0.8, 0.8, 1),
            align=TextNode.ACenter,
            scale=0.035
        )

    def _get_font(self):
        font = loader.loadFont("models/arial.ttf") if loader.loadFont("models/arial.ttf") else None
        return font

    def update(self, car: Car, speed_monitor: SpeedMonitor, lane_detection: LaneDetection):
        current_speed = speed_monitor.get_current_speed()
        speed_color = self._get_speed_color(current_speed)

        if 'speed_value' in self.elements:
            self.elements['speed_value'].setText(f"{current_speed:.0f}")
            self.elements['speed_value'].setFg(speed_color)

        if 'lane_value' in self.elements:
            current_lane = lane_detection.get_current_lane()
            self.elements['lane_value'].setText(f"{current_lane + 1} / {LANE_COUNT}")

        if 'car_indicator' in self.elements:
            current_lane = lane_detection.get_current_lane()
            lane_width = 0.8
            lane_spacing = 0.15
            x_pos = -((LANE_COUNT / 2) * (lane_width + lane_spacing)) + (current_lane + 0.5) * (lane_width + lane_spacing)
            self.elements['car_indicator'].setX(x_pos)

            offset = lane_detection.get_lane_center_offset(car.get_position()[0])
            offset_scale = offset / 2.0
            self.elements['car_indicator'].setX(x_pos + offset_scale)

        if 'avg_speed_label' in self.elements:
            avg_speed = speed_monitor.get_average_speed()
            self.elements['avg_speed_label'].setText(f"平均速度: {avg_speed:.1f} km/h")

        if 'max_speed_label' in self.elements:
            max_speed = speed_monitor.get_max_speed_recorded()
            self.elements['max_speed_label'].setText(f"最高速度: {max_speed:.1f} km/h")

    def _get_speed_color(self, speed: float) -> tuple:
        if speed > SPEED_LIMIT + 30:
            return (1, 0, 0, 1)
        elif speed > SPEED_LIMIT + 10:
            return (1, 0.5, 0, 1)
        elif speed > SPEED_LIMIT:
            return (1, 1, 0, 1)
        elif speed > SPEED_LIMIT * 0.8:
            return (0, 1, 1, 1)
        else:
            return (0, 1, 0, 1)

    def cleanup(self):
        for element in self.elements.values():
            if hasattr(element, 'destroy'):
                element.destroy()
            else:
                element.removeNode()
        self.elements.clear()
