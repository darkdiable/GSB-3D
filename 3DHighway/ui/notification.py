from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectGui import *
from panda3d.core import *
import time
from config.settings import NOTIFICATION_DURATION
from systems.violation_detector import ViolationDetector, Violation


class NotificationSystem:
    def __init__(self, aspect2d: NodePath):
        self.aspect2d = aspect2d
        self.active_notifications = []
        self.notification_history = []
        self.max_notifications = 5
        self.notification_y_start = 0.6
        self.notification_y_spacing = 0.12

    def update(self, violation_detector: ViolationDetector, current_time: float = None):
        if current_time is None:
            current_time = time.time()

        active_violations = violation_detector.get_active_violations()

        for violation in active_violations:
            if not self._is_violation_displayed(violation):
                self._create_notification(violation)

        self._update_notifications(current_time)
        self._refresh_notification_positions()

    def _is_violation_displayed(self, violation: Violation) -> bool:
        for notif in self.active_notifications:
            if notif['violation'] == violation:
                return True
        return False

    def _create_notification(self, violation: Violation):
        color = self._get_severity_color(violation.severity)
        icon = self._get_severity_icon(violation.severity)

        frame_width = 0.8
        frame_height = 0.1

        frame = DirectFrame(
            parent=self.aspect2d,
            pos=(0, 0, self.notification_y_start),
            frameSize=(-frame_width / 2, frame_width / 2, -frame_height / 2, frame_height / 2),
            frameColor=(color[0], color[1], color[2], 0.85),
            relief=DGG.RIDGE,
            borderWidth=(0.01, 0.01)
        )

        icon_text = OnscreenText(
            text=icon,
            parent=frame,
            pos=(-frame_width / 2 + 0.06, -0.025),
            fg=(1, 1, 1, 1),
            align=TextNode.ALeft,
            scale=0.07
        )

        message_text = OnscreenText(
            text=violation.message,
            parent=frame,
            pos=(-frame_width / 2 + 0.14, -0.025),
            fg=(1, 1, 1, 1),
            align=TextNode.ALeft,
            scale=0.045
        )

        bar_full_width = frame_width - 0.04
        bar_left = -frame_width / 2 + 0.02

        timer_bg_card = CardMaker("timer_bar_bg")
        timer_bg_card.setFrame(0, bar_full_width, -0.008, 0.008)
        timer_bg_card.setColor(0, 0, 0, 0.5)
        timer_bar_bg = frame.attachNewNode(timer_bg_card.generate())
        timer_bar_bg.setPos(bar_left, 0, -frame_height / 2 + 0.015)
        timer_bar_bg.setTransparency(TransparencyAttrib.MAlpha)

        timer_card = CardMaker("timer_bar")
        timer_card.setFrame(0, 1, -0.008, 0.008)
        timer_card.setColor(1, 1, 1, 0.8)
        timer_bar = frame.attachNewNode(timer_card.generate())
        timer_bar.setPos(bar_left, 0, -frame_height / 2 + 0.015)
        timer_bar.setScale(bar_full_width, 1, 1)
        timer_bar.setTransparency(TransparencyAttrib.MAlpha)

        notif_data = {
            'violation': violation,
            'frame': frame,
            'message': message_text,
            'icon': icon_text,
            'timer_bar': timer_bar,
            'timer_bar_bg': timer_bar_bg,
            'created_time': violation.timestamp,
            'duration': violation.duration
        }

        self.active_notifications.append(notif_data)
        self.notification_history.append(notif_data)

        if len(self.active_notifications) > self.max_notifications:
            oldest = self.active_notifications.pop(0)
            self._destroy_notification(oldest)

    def _update_notifications(self, current_time: float):
        to_remove = []

        for notif in self.active_notifications:
            elapsed = current_time - notif['created_time']
            remaining = max(0, notif['duration'] - elapsed)

            if remaining <= 0:
                to_remove.append(notif)
            else:
                progress = remaining / notif['duration']
                frame_width = 0.8
                full_bar_width = frame_width - 0.04
                notif['timer_bar'].setSx(progress)

                alpha = min(1, remaining / 1.0)
                color = notif['frame'].getColor()
                notif['frame'].setColor(color[0], color[1], color[2], 0.85 * alpha)

        for notif in to_remove:
            self.active_notifications.remove(notif)
            self._destroy_notification(notif)

    def _refresh_notification_positions(self):
        for i, notif in enumerate(reversed(self.active_notifications)):
            y_pos = self.notification_y_start - i * self.notification_y_spacing
            notif['frame'].setZ(y_pos)

    def _destroy_notification(self, notif: dict):
        for key in ['frame', 'message', 'icon', 'timer_bar', 'timer_bar_bg']:
            if key in notif and notif[key]:
                if hasattr(notif[key], 'destroy'):
                    notif[key].destroy()
                else:
                    notif[key].removeNode()

    def _get_severity_color(self, severity: str) -> tuple:
        colors = {
            'warning': (0.9, 0.7, 0, 1),
            'critical': (0.9, 0.3, 0, 1),
            'danger': (0.8, 0, 0, 1)
        }
        return colors.get(severity, (0.5, 0.5, 0.5, 1))

    def _get_severity_icon(self, severity: str) -> str:
        icons = {
            'warning': '⚠',
            'critical': '⚡',
            'danger': '⛔'
        }
        return icons.get(severity, '●')

    def show_custom_message(self, message: str, severity: str = "info", duration: float = 3.0):
        color_map = {
            'info': (0, 0.5, 0.8, 1),
            'success': (0, 0.6, 0.2, 1),
            'warning': (0.9, 0.7, 0, 1),
            'danger': (0.8, 0, 0, 1)
        }
        icon_map = {
            'info': 'ℹ',
            'success': '✓',
            'warning': '⚠',
            'danger': '⛔'
        }

        color = color_map.get(severity, (0.5, 0.5, 0.5, 1))
        icon = icon_map.get(severity, '●')

        violation = Violation("custom", message, time.time(), severity)
        violation.duration = duration

        self._create_notification(violation)

    def get_violation_summary(self) -> dict:
        from collections import Counter
        types = Counter()
        severities = Counter()

        for notif in self.notification_history:
            types[notif['violation'].type] += 1
            severities[notif['violation'].severity] += 1

        return {
            'total': len(self.notification_history),
            'by_type': dict(types),
            'by_severity': dict(severities)
        }

    def cleanup(self):
        for notif in self.active_notifications:
            self._destroy_notification(notif)
        self.active_notifications.clear()
