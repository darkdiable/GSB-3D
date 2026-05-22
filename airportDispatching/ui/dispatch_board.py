from panda3d.core import *
from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectGui import *
from config.settings import (
    STATUS_LABELS, STATUS_COLORS, STATUS_WAITING,
    STATUS_TAXIING, STATUS_TAKEOFF, STATUS_LANDING,
    STATUS_DEPARTED, STATUS_ARRIVED
)


class DispatchBoard:
    def __init__(self, base, dispatcher):
        self.base = base
        self.dispatcher = dispatcher
        self.board_frame = None
        self.flight_entries = {}
        self.selected_aircraft = None
        self.info_text = None
        self.highlight_frame = None

    def build(self):
        self._create_board_frame()
        self._create_title()
        self._create_flight_list()
        self._create_info_panel()
        self._create_controls_help()
        return self

    def _create_board_frame(self):
        self.board_frame = DirectFrame(
            frameColor=(0.05, 0.05, 0.1, 0.85),
            frameSize=(-0.65, 0.65, -0.9, 0.95),
            pos=(-1, 0, 0),
            relief=DGG.FLAT
        )

        border = DirectFrame(
            frameColor=(0.2, 0.4, 0.8, 0.8),
            frameSize=(-0.66, 0.66, -0.91, 0.96),
            pos=(-1, 0, 0),
            relief=DGG.FLAT
        )

    def _create_title(self):
        title_text = OnscreenText(
            text="机场调度板",
            pos=(-1, 0.85),
            scale=0.09,
            fg=(0.8, 0.9, 1.0, 1),
            align=TextNode.ACenter
        )

        subtitle = OnscreenText(
            text="AIRPORT DISPATCH BOARD",
            pos=(-1, 0.76),
            scale=0.04,
            fg=(0.5, 0.7, 0.9, 1),
            align=TextNode.ACenter
        )

        header_bg = DirectFrame(
            parent=self.board_frame,
            frameColor=(0.1, 0.2, 0.4, 0.9),
            frameSize=(-0.62, 0.62, 0.65, 0.73),
            pos=(0, 0, 0)
        )

        headers = ["航班号", "类型", "状态", "停机位"]
        positions = [-0.45, -0.15, 0.15, 0.45]
        for i, header in enumerate(headers):
            OnscreenText(
                text=header,
                pos=(-1 + positions[i], 0.68),
                scale=0.045,
                fg=(0.9, 0.95, 1.0, 1),
                align=TextNode.ACenter,
                parent=self.board_frame
            )

    def _create_flight_list(self):
        self.list_background = DirectFrame(
            parent=self.board_frame,
            frameColor=(0.02, 0.03, 0.08, 0.9),
            frameSize=(-0.62, 0.62, -0.85, 0.63),
            pos=(0, 0, 0)
        )

    def _create_info_panel(self):
        self.info_panel = DirectFrame(
            frameColor=(0.05, 0.05, 0.1, 0.9),
            frameSize=(-0.45, 0.45, -0.25, 0.15),
            pos=(0.7, 0, -0.6),
            relief=DGG.FLAT
        )

        info_border = DirectFrame(
            frameColor=(0.2, 0.4, 0.8, 0.6),
            frameSize=(-0.46, 0.46, -0.26, 0.16),
            pos=(0.7, 0, -0.6),
            relief=DGG.FLAT
        )

        OnscreenText(
            text="选中航班信息",
            pos=(0.7, 0.08),
            scale=0.05,
            fg=(0.8, 0.9, 1.0, 1),
            align=TextNode.ACenter
        )

        self.info_flight_number = OnscreenText(
            text="",
            pos=(0.7, -0.02),
            scale=0.07,
            fg=(1.0, 1.0, 0.6, 1),
            align=TextNode.ACenter
        )

        self.info_status = OnscreenText(
            text="",
            pos=(0.7, -0.1),
            scale=0.05,
            fg=(0.7, 0.9, 1.0, 1),
            align=TextNode.ACenter
        )

        self.info_gate = OnscreenText(
            text="",
            pos=(0.7, -0.18),
            scale=0.045,
            fg=(0.6, 0.8, 0.9, 1),
            align=TextNode.ACenter
        )

    def _create_controls_help(self):
        help_frame = DirectFrame(
            frameColor=(0.05, 0.05, 0.1, 0.8),
            frameSize=(-0.4, 0.4, -0.15, 0.1),
            pos=(0.7, 0, 0.7),
            relief=DGG.FLAT
        )

        OnscreenText(
            text="操作说明",
            pos=(0.7, 0.05),
            scale=0.045,
            fg=(0.8, 0.9, 1.0, 1),
            align=TextNode.ACenter
        )

        controls = [
            "鼠标点击飞机: 切换状态",
            "方向键: 旋转视角",
            "W/S: 缩放",
            "R: 重置视角",
            "空格: 暂停/继续"
        ]

        y_pos = -0.02
        for text in controls:
            OnscreenText(
                text=text,
                pos=(0.7, y_pos),
                scale=0.035,
                fg=(0.7, 0.8, 0.9, 1),
                align=TextNode.ALeft
            )
            y_pos -= 0.04

    def update_board(self, aircrafts):
        for flight_number in list(self.flight_entries.keys()):
            for item in self.flight_entries[flight_number]:
                if hasattr(item, 'destroy'):
                    item.destroy()
            del self.flight_entries[flight_number]

        if self.highlight_frame:
            self.highlight_frame.destroy()
            self.highlight_frame = None

        y_start = 0.58
        row_height = 0.06
        max_rows = 20

        for idx, aircraft in enumerate(aircrafts[:max_rows]):
            y_pos = y_start - idx * row_height

            is_selected = (self.selected_aircraft == aircraft)

            if is_selected:
                self.highlight_frame = DirectFrame(
                    parent=self.list_background,
                    frameColor=(0.3, 0.5, 0.9, 0.4),
                    frameSize=(-0.6, 0.6, y_pos - row_height / 2 + 0.01, y_pos + row_height / 2 - 0.01),
                    pos=(0, 0, 0)
                )

            flight_type = "出发" if aircraft.is_departure else "到达"
            status_label = STATUS_LABELS.get(aircraft.status, aircraft.status)
            status_color = STATUS_COLORS.get(aircraft.status, (1, 1, 1, 1))

            gate_text = str(aircraft.gate_id + 1) if aircraft.gate_id is not None else "-"

            positions = [-0.45, -0.15, 0.15, 0.45]
            texts = [aircraft.flight_number, flight_type, status_label, gate_text]
            colors = [(1, 1, 1, 1), (1, 0.6, 0.6, 1) if aircraft.is_departure else (0.6, 0.8, 1, 1), status_color, (0.9, 0.9, 0.7, 1)]

            entries = []
            for i, (text, pos_x, color) in enumerate(zip(texts, positions, colors)):
                entry = OnscreenText(
                    text=text,
                    pos=(-1 + pos_x, y_pos),
                    scale=0.04,
                    fg=color,
                    align=TextNode.ACenter,
                    parent=self.list_background
                )
                entries.append(entry)

            separator = LineSegs()
            separator.setColor(0.2, 0.3, 0.5, 0.5)
            separator.setThickness(1)
            separator.moveTo(-0.6, y_pos - row_height / 2, 0)
            separator.drawTo(0.6, y_pos - row_height / 2, 0)
            sep_node = separator.create()
            sep_np = self.list_background.attachNewNode(sep_node)
            entries.append(sep_np)

            self.flight_entries[aircraft.flight_number] = entries

    def select_aircraft(self, aircraft):
        self.selected_aircraft = aircraft
        if aircraft:
            self.info_flight_number.setText(aircraft.flight_number)
            status_label = STATUS_LABELS.get(aircraft.status, aircraft.status)
            self.info_status.setText(f"状态: {status_label}")
            gate_text = f"停机位: {aircraft.gate_id + 1}" if aircraft.gate_id is not None else "停机位: 无"
            self.info_gate.setText(gate_text)
        else:
            self.info_flight_number.setText("")
            self.info_status.setText("点击飞机选择")
            self.info_gate.setText("")

    def show_message(self, message, duration=2):
        if hasattr(self, 'message_text') and self.message_text:
            self.message_text.destroy()

        self.message_text = OnscreenText(
            text=message,
            pos=(0, -0.85),
            scale=0.06,
            fg=(1, 0.8, 0.4, 1),
            bg=(0, 0, 0, 0.7),
            align=TextNode.ACenter
        )

        def clear_message(task):
            if self.message_text:
                self.message_text.destroy()
                self.message_text = None
            return task.done

        self.base.taskMgr.doMethodLater(duration, clear_message, 'clear_msg')

    def update_status(self, aircraft):
        aircrafts = self.dispatcher.get_all_aircrafts()
        self.update_board(aircrafts)
        if self.selected_aircraft == aircraft:
            self.select_aircraft(aircraft)
