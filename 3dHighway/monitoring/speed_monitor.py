from config.settings import Config


class SpeedMonitor:
    def __init__(self, vehicle_controller):
        self.vehicle_controller = vehicle_controller
        self.current_speed = 0.0
        self.average_speed = 0.0
        self.max_speed = 0.0
        self.speed_history = []
        self.speeding_violations = []
        self.lane_crossing_violations = []
        self.violation_callbacks = []

    def update(self, dt):
        self.current_speed = self.vehicle_controller.get_speed_kmh()
        
        self.speed_history.append(self.current_speed)
        if len(self.speed_history) > 100:
            self.speed_history.pop(0)
        
        self.average_speed = sum(self.speed_history) / len(self.speed_history)
        
        if self.current_speed > self.max_speed:
            self.max_speed = self.current_speed
    
    def get_current_speed(self):
        return self.current_speed
    
    def get_average_speed(self):
        return self.average_speed
    
    def get_max_speed(self):
        return self.max_speed
    
    def reset_max_speed(self):
        self.max_speed = 0.0


class ViolationDetector:
    def __init__(self, vehicle_controller, speed_monitor):
        self.vehicle_controller = vehicle_controller
        self.speed_monitor = speed_monitor
        
        self.is_speeding = False
        self.speeding_violations = []
        self.lane_crossing_violations = []
        self.all_violations = []
        
        self.speeding_start_time = None
        self.lane_crossing_start_time = None
        self.last_lane_crossing = None
        
        self.speed_limit = Config.SPEED_LIMIT_KMH
        self.speeding_threshold = 5.0
    
    def check_speeding(self, current_time):
        speed = self.speed_monitor.get_current_speed()
        
        if speed > self.speed_limit + self.speeding_threshold:
            if not self.is_speeding and self.speeding_start_time is None:
                self.speeding_start_time = self.speeding_start_time or current_time
            self.is_speeding = True
            return True
        else:
            if self.is_speeding:
                duration = current_time - (self.speeding_start_time or current_time)
                if duration > 1.0:
                    violation = {
                        'type': 'speeding',
                        'speed': speed,
                        'start_time': self.speeding_start_time,
                        'end_time': current_time,
                        'duration': duration,
                        'message': f'Speeding Violation: {speed:.1f} km/h, Limit: {self.speed_limit} km/h'
                    }
                    self.speeding_violations.append(violation)
                    self.all_violations.append(violation)
                self.speeding_start_time = None
            self.is_speeding = False
        return False
    
    def check_lane_crossing(self, current_time):
        crossings = self.vehicle_controller.check_lane_crossing()
        
        if crossings:
            line_type = 'dashed'
            if 0 in crossings or Config.LANE_COUNT in crossings:
                line_type = 'solid'
            
            if self.last_lane_crossing != crossings:
                violation = {
                    'type': 'lane_crossing',
                    'line_type': line_type,
                    'lines': crossings,
                    'time': current_time,
                    'message': f'Lane Crossing: {line_type} line'
                }
                self.lane_crossing_violations.append(violation)
                self.all_violations.append(violation)
                self.last_lane_crossing = crossings
                return True
        else:
            self.last_lane_crossing = None
        
        return False
    
    def update(self, current_time, dt):
        speeding = self.check_speeding(current_time)
        lane_crossing = self.check_lane_crossing(current_time)
        
        return {
            'speeding': speeding,
            'lane_crossing': lane_crossing
        }
    
    def get_speeding_violations(self):
        return self.speeding_violations
    
    def get_lane_crossing_violations(self):
        return self.lane_crossing_violations
    
    def get_all_violations(self):
        return self.all_violations
    
    def get_violation_count(self):
        return len(self.all_violations)
    
    def get_speeding_count(self):
        return len(self.speeding_violations)
    
    def get_lane_crossing_count(self):
        return len(self.lane_crossing_violations)
    
    def get_recent_violation(self):
        if self.all_violations:
            return self.all_violations[-1]
        return None
    
    def reset(self):
        self.speeding_violations = []
        self.lane_crossing_violations = []
        self.all_violations = []
        self.is_speeding = False
        self.speeding_start_time = None
        self.lane_crossing_start_time = None
        self.last_lane_crossing = None
