from config.settings import (
    ROAD_WIDTH, LANE_COUNT, LANE_WIDTH, LINE_WIDTH,
    VIOLATION_LANE_DEPARTURE_MARGIN
)
from vehicle.car import Car
from road.road_builder import RoadBuilder


class LaneDetection:
    def __init__(self, road_builder: RoadBuilder):
        self.road_builder = road_builder
        self.current_lane = 1
        self.is_lane_departure = False
        self.departure_side = None
        self.departure_amount = 0.0
        self.lane_line_crossed = None
        self.lane_bounds = road_builder.get_all_lane_bounds()
        self.half_road = ROAD_WIDTH / 2

    def update(self, car: Car):
        car_left = car.get_left_bound()
        car_right = car.get_right_bound()
        car_x = car.get_position()[0]

        self.current_lane = self._determine_lane(car_x)

        self._check_lane_departure(car_left, car_right)
        self._check_line_crossing(car_left, car_right)

    def _determine_lane(self, car_x: float) -> int:
        for i, (left, right) in enumerate(self.lane_bounds):
            if left <= car_x < right:
                return i

        if car_x < self.lane_bounds[0][0]:
            return 0
        else:
            return LANE_COUNT - 1

    def _check_lane_departure(self, car_left: float, car_right: float):
        road_left = -self.half_road
        road_right = self.half_road

        left_departure = road_left - car_left
        right_departure = car_right - road_right

        if left_departure > VIOLATION_LANE_DEPARTURE_MARGIN:
            self.is_lane_departure = True
            self.departure_side = "left"
            self.departure_amount = left_departure
        elif right_departure > VIOLATION_LANE_DEPARTURE_MARGIN:
            self.is_lane_departure = True
            self.departure_side = "right"
            self.departure_amount = right_departure
        else:
            self.is_lane_departure = False
            self.departure_side = None
            self.departure_amount = 0.0

    def _check_line_crossing(self, car_left: float, car_right: float):
        self.lane_line_crossed = None

        for lane_idx in range(1, LANE_COUNT):
            line_x = -self.half_road + lane_idx * LANE_WIDTH
            line_left = line_x - LINE_WIDTH / 2
            line_right = line_x + LINE_WIDTH / 2

            if car_left < line_right and car_right > line_left:
                if self.current_lane < lane_idx:
                    self.lane_line_crossed = "right"
                else:
                    self.lane_line_crossed = "left"
                break

    def get_current_lane(self) -> int:
        return self.current_lane

    def is_departing_lane(self) -> bool:
        return self.is_lane_departure

    def get_departure_side(self) -> str:
        return self.departure_side

    def get_departure_amount(self) -> float:
        return self.departure_amount

    def is_crossing_lane_line(self) -> bool:
        return self.lane_line_crossed is not None

    def get_crossing_side(self) -> str:
        return self.lane_line_crossed

    def get_distance_to_lane_edges(self, car_x: float) -> tuple:
        if 0 <= self.current_lane < LANE_COUNT:
            lane_left, lane_right = self.lane_bounds[self.current_lane]
            dist_left = car_x - lane_left
            dist_right = lane_right - car_x
            return (dist_left, dist_right)
        return (0.0, 0.0)

    def get_lane_center_offset(self, car_x: float) -> float:
        if 0 <= self.current_lane < LANE_COUNT:
            lane_left, lane_right = self.lane_bounds[self.current_lane]
            lane_center = (lane_left + lane_right) / 2
            return car_x - lane_center
        return 0.0
