from panda3d.core import Vec3
from config.settings import Config


class VehicleController:
    def __init__(self, vehicle_node, highway):
        self.vehicle_node = vehicle_node
        self.highway = highway
        
        self.position = Vec3(0, 0, 0)
        self.velocity = Vec3(0, 0, 0)
        self.heading = 0.0
        
        self.speed = 0.0
        self.acceleration = 0.0
        self.turn_rate = 0.0
        
        self.is_accelerating = False
        self.is_braking = False
        self.is_turning_left = False
        self.is_turning_right = False
        
        self.road_bounds = highway.get_road_bounds()
        self.lane_lines = highway.get_lane_lines()
    
    def reset(self):
        self.position = Vec3(0, self.highway.get_lane_center(1), 0)
        self.velocity = Vec3(0, 0, 0)
        self.heading = 0.0
        self.speed = 0.0
        self.vehicle_node.setPos(self.position)
        self.vehicle_node.setH(self.heading)
    
    def accelerate(self, active):
        self.is_accelerating = active
    
    def brake(self, active):
        self.is_braking = active
    
    def turn_left(self, active):
        self.is_turning_left = active
    
    def turn_right(self, active):
        self.is_turning_right = active
    
    def update(self, dt):
        if self.is_accelerating:
            self.speed += Config.ACCELERATION * dt
        elif self.is_braking:
            self.speed -= Config.BRAKE_DECELERATION * dt
        else:
            self.speed -= 5.0 * dt
        
        self.speed = max(0.0, min(self.speed, Config.MAX_SPEED))
        
        self.turn_rate = 0.0
        if self.is_turning_left:
            self.turn_rate = Config.TURN_SPEED
        if self.is_turning_right:
            self.turn_rate = -Config.TURN_SPEED
        
        if self.speed > 1.0:
            self.heading += self.turn_rate * dt * (self.speed / 50.0)
        
        heading_rad = self.heading * 3.14159 / 180.0
        self.velocity.setX(self.speed * 1.0)
        self.velocity.setY(self.speed * -heading_rad * 0.5)
        
        self.position += self.velocity * dt
        
        road_left, road_right = self.road_bounds
        half_width = Config.VEHICLE_WIDTH / 2
        
        if self.position.getY() - half_width < road_left:
            self.position.setY(road_left + half_width)
        if self.position.getY() + half_width > road_right:
            self.position.setY(road_right - half_width)
        
        if self.position.getX() > Config.ROAD_LENGTH - 100:
            self.position.setX(self.position.getX() - Config.ROAD_LENGTH / 2)
        
        self.vehicle_node.setPos(self.position)
        self.vehicle_node.setH(self.heading)
    
    def get_speed_kmh(self):
        return self.speed * 3.6
    
    def get_position(self):
        return self.position
    
    def get_heading(self):
        return self.heading
    
    def check_lane_crossing(self):
        vehicle_y = self.position.getY()
        half_width = Config.VEHICLE_WIDTH / 2
        vehicle_left = vehicle_y - half_width
        vehicle_right = vehicle_y + half_width
        
        crossings = []
        for i, line_y in enumerate(self.lane_lines):
            if abs(vehicle_left - line_y) < Config.LINE_CROSSING_THRESHOLD or \
               abs(vehicle_right - line_y) < Config.LINE_CROSSING_THRESHOLD:
                crossings.append(i)
        
        return crossings
    
    def get_current_lane(self):
        vehicle_y = self.position.getY()
        lane_width = Config.LANE_WIDTH
        road_half_width = (Config.LANE_WIDTH * Config.LANE_COUNT) / 2
        
        lane = int((vehicle_y + road_half_width) / lane_width)
        return max(0, min(Config.LANE_COUNT - 1, lane))
