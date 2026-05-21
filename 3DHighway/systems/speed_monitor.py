from config.settings import SPEED_LIMIT, SPEED_UNIT
from vehicle.car import Car


class SpeedMonitor:
    def __init__(self):
        self.current_speed = 0.0
        self.max_speed_recorded = 0.0
        self.speed_limit = SPEED_LIMIT
        self.speed_history = []
        self.history_max_size = 100

    def update(self, car: Car):
        self.current_speed = car.get_speed_kmh()
        if self.current_speed > self.max_speed_recorded:
            self.max_speed_recorded = self.current_speed

        self.speed_history.append(self.current_speed)
        if len(self.speed_history) > self.history_max_size:
            self.speed_history.pop(0)

    def get_current_speed(self) -> float:
        return self.current_speed

    def get_max_speed_recorded(self) -> float:
        return self.max_speed_recorded

    def get_average_speed(self) -> float:
        if not self.speed_history:
            return 0.0
        return sum(self.speed_history) / len(self.speed_history)

    def is_over_speed_limit(self, margin: float = 0.0) -> bool:
        return self.current_speed > (self.speed_limit + margin)

    def get_over_speed_amount(self, margin: float = 0.0) -> float:
        return max(0, self.current_speed - (self.speed_limit + margin))

    def get_speed_percentage(self) -> float:
        if self.speed_limit == 0:
            return 0.0
        return (self.current_speed / self.speed_limit) * 100

    def reset(self):
        self.current_speed = 0.0
        self.max_speed_recorded = 0.0
        self.speed_history.clear()
