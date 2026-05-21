from ICE.utils.constants import STROKES, STROKE_DURATION, FIRING_ORDER, NUM_CYLINDERS


class FourStrokeCycle:
    def __init__(self):
        self.strokes = STROKES
        self.stroke_duration = STROKE_DURATION
        self.firing_order = FIRING_ORDER
        self.cylinder_strokes = [0] * NUM_CYLINDERS
        self._initialize_cylinder_phases()

    def _initialize_cylinder_phases(self):
        for i, cyl in enumerate(self.firing_order):
            self.cylinder_strokes[cyl] = (i * self.stroke_duration) % 720

    def get_cylinder_stroke(self, cylinder_index, crank_angle_deg):
        total_angle = (self.cylinder_strokes[cylinder_index] + crank_angle_deg) % 720
        stroke_index = int(total_angle // self.stroke_duration)
        return stroke_index, self.strokes[stroke_index]

    def get_cylinder_stroke_name(self, cylinder_index, crank_angle_deg):
        _, stroke_info = self.get_cylinder_stroke(cylinder_index, crank_angle_deg)
        return stroke_info["name"]

    def get_cylinder_stroke_name_en(self, cylinder_index, crank_angle_deg):
        _, stroke_info = self.get_cylinder_stroke(cylinder_index, crank_angle_deg)
        return stroke_info["name_en"]

    def get_cylinder_stroke_color(self, cylinder_index, crank_angle_deg):
        _, stroke_info = self.get_cylinder_stroke(cylinder_index, crank_angle_deg)
        return stroke_info["color"]

    def is_intake_stroke(self, cylinder_index, crank_angle_deg):
        stroke_idx, _ = self.get_cylinder_stroke(cylinder_index, crank_angle_deg)
        return stroke_idx == 0

    def is_compression_stroke(self, cylinder_index, crank_angle_deg):
        stroke_idx, _ = self.get_cylinder_stroke(cylinder_index, crank_angle_deg)
        return stroke_idx == 1

    def is_power_stroke(self, cylinder_index, crank_angle_deg):
        stroke_idx, _ = self.get_cylinder_stroke(cylinder_index, crank_angle_deg)
        return stroke_idx == 2

    def is_exhaust_stroke(self, cylinder_index, crank_angle_deg):
        stroke_idx, _ = self.get_cylinder_stroke(cylinder_index, crank_angle_deg)
        return stroke_idx == 3

    def should_spark(self, cylinder_index, crank_angle_deg):
        total_angle = (self.cylinder_strokes[cylinder_index] + crank_angle_deg) % 720
        stroke_index = int(total_angle // self.stroke_duration)
        stroke_progress = (total_angle % self.stroke_duration) / self.stroke_duration

        if stroke_index == 1 and stroke_progress > 0.95:
            return True
        return False

    def get_stroke_progress(self, cylinder_index, crank_angle_deg):
        total_angle = (self.cylinder_strokes[cylinder_index] + crank_angle_deg) % 720
        stroke_progress = (total_angle % self.stroke_duration) / self.stroke_duration
        return stroke_progress

    def get_valve_timing(self, cylinder_index, crank_angle_deg):
        stroke_idx, _ = self.get_cylinder_stroke(cylinder_index, crank_angle_deg)
        stroke_progress = self.get_stroke_progress(cylinder_index, crank_angle_deg)

        intake_lift = 0
        exhaust_lift = 0

        if stroke_idx == 0:
            if stroke_progress < 0.1:
                intake_lift = stroke_progress / 0.1
            elif stroke_progress > 0.9:
                intake_lift = (1 - stroke_progress) / 0.1
            else:
                intake_lift = 1.0

        elif stroke_idx == 1:
            if stroke_progress < 0.05:
                intake_lift = (0.05 - stroke_progress) / 0.05

        elif stroke_idx == 2:
            if stroke_progress > 0.9:
                exhaust_lift = (stroke_progress - 0.9) / 0.1

        elif stroke_idx == 3:
            if stroke_progress < 0.1:
                exhaust_lift = stroke_progress / 0.1
            elif stroke_progress > 0.9:
                exhaust_lift = (1 - stroke_progress) / 0.1
            else:
                exhaust_lift = 1.0

        return intake_lift, exhaust_lift

    def get_all_cylinder_strokes(self, crank_angle_deg):
        result = []
        for i in range(NUM_CYLINDERS):
            stroke_idx, stroke_info = self.get_cylinder_stroke(i, crank_angle_deg)
            result.append({
                "cylinder": i,
                "stroke_index": stroke_idx,
                "stroke_name": stroke_info["name"],
                "stroke_name_en": stroke_info["name_en"],
                "color": stroke_info["color"]
            })
        return result
