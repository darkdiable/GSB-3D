import time
from config.settings import (
    VIOLATION_OVERSPEED_MARGIN, VIOLATION_LANE_DEPARTURE_MARGIN,
    NOTIFICATION_DURATION, SPEED_LIMIT
)
from systems.speed_monitor import SpeedMonitor
from systems.lane_detection import LaneDetection


class Violation:
    def __init__(self, violation_type: str, message: str, timestamp: float, severity: str = "warning"):
        self.type = violation_type
        self.message = message
        self.timestamp = timestamp
        self.severity = severity
        self.duration = NOTIFICATION_DURATION

    def is_active(self, current_time: float) -> bool:
        return (current_time - self.timestamp) < self.duration

    def get_remaining_time(self, current_time: float) -> float:
        return max(0, self.duration - (current_time - self.timestamp))


class ViolationDetector:
    def __init__(self, speed_monitor: SpeedMonitor, lane_detection: LaneDetection):
        self.speed_monitor = speed_monitor
        self.lane_detection = lane_detection

        self.active_violations = []
        self.violation_history = []

        self._overspeed_state = False
        self._lane_departure_state = False
        self._line_crossing_state = False

        self._last_overspeed_time = 0
        self._last_lane_departure_time = 0
        self._last_line_crossing_time = 0

        self._min_violation_interval = 2.0

    def update(self, current_time: float = None):
        if current_time is None:
            current_time = time.time()

        self._check_overspeed(current_time)
        self._check_lane_departure(current_time)
        self._check_lane_line_crossing(current_time)

        self.active_violations = [v for v in self.active_violations if v.is_active(current_time)]

    def _check_overspeed(self, current_time: float):
        is_overspeed = self.speed_monitor.is_over_speed_limit(VIOLATION_OVERSPEED_MARGIN)

        if is_overspeed and not self._overspeed_state:
            if current_time - self._last_overspeed_time > self._min_violation_interval:
                over_amount = self.speed_monitor.get_over_speed_amount(VIOLATION_OVERSPEED_MARGIN)
                current_speed = self.speed_monitor.get_current_speed()

                severity = "warning"
                if over_amount > 30:
                    severity = "danger"
                elif over_amount > 10:
                    severity = "critical"

                message = f"超速违章！当前车速: {current_speed:.1f} km/h，限速: {SPEED_LIMIT} km/h，超速: {over_amount:.1f} km/h"
                violation = Violation("overspeed", message, current_time, severity)
                self._add_violation(violation)
                self._last_overspeed_time = current_time

        self._overspeed_state = is_overspeed

    def _check_lane_departure(self, current_time: float):
        is_departing = self.lane_detection.is_departing_lane()

        if is_departing and not self._lane_departure_state:
            if current_time - self._last_lane_departure_time > self._min_violation_interval:
                side = self.lane_detection.get_departure_side()
                amount = self.lane_detection.get_departure_amount()

                side_text = "左侧" if side == "left" else "右侧"
                message = f"车道偏离警告！车辆已偏离{side_text}路面 {amount:.2f} 米"
                violation = Violation("lane_departure", message, current_time, "danger")
                self._add_violation(violation)
                self._last_lane_departure_time = current_time

        self._lane_departure_state = is_departing

    def _check_lane_line_crossing(self, current_time: float):
        is_crossing = self.lane_detection.is_crossing_lane_line()

        if is_crossing and not self._line_crossing_state:
            if current_time - self._last_line_crossing_time > self._min_violation_interval:
                side = self.lane_detection.get_crossing_side()
                current_lane = self.lane_detection.get_current_lane()

                side_text = "向左" if side == "left" else "向右"
                message = f"车道压线警告！车辆{side_text}压线，当前车道: {current_lane + 1}"
                violation = Violation("lane_crossing", message, current_time, "warning")
                self._add_violation(violation)
                self._last_line_crossing_time = current_time

        self._line_crossing_state = is_crossing

    def _add_violation(self, violation: Violation):
        self.active_violations.append(violation)
        self.violation_history.append(violation)

        if len(self.violation_history) > 100:
            self.violation_history.pop(0)

    def get_active_violations(self) -> list:
        return self.active_violations

    def get_violation_history(self) -> list:
        return self.violation_history

    def get_violation_count(self, violation_type: str = None) -> int:
        if violation_type:
            return len([v for v in self.violation_history if v.type == violation_type])
        return len(self.violation_history)

    def has_active_violations(self) -> bool:
        return len(self.active_violations) > 0

    def get_most_severe_violation(self) -> Violation:
        if not self.active_violations:
            return None

        severity_order = {"danger": 3, "critical": 2, "warning": 1}
        return max(self.active_violations, key=lambda v: severity_order.get(v.severity, 0))
