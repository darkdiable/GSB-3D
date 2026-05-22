import random
import math
from panda3d.core import LVector3
from config.settings import AIRLINE_PREFIXES


def generate_flight_number():
    prefix = random.choice(AIRLINE_PREFIXES)
    number = random.randint(100, 9999)
    return f"{prefix}{number}"


def lerp(a, b, t):
    return a + (b - a) * t


def lerp_vector(v1, v2, t):
    return LVector3(
        lerp(v1.getX(), v2.getX(), t),
        lerp(v1.getY(), v2.getY(), t),
        lerp(v1.getZ(), v2.getZ(), t)
    )


def distance(p1, p2):
    return math.sqrt(
        (p1.getX() - p2.getX()) ** 2 +
        (p1.getY() - p2.getY()) ** 2 +
        (p1.getZ() - p2.getZ()) ** 2
    )


def get_angle_to_point(from_pos, to_pos):
    dx = to_pos.getX() - from_pos.getX()
    dy = to_pos.getY() - from_pos.getY()
    angle = math.degrees(math.atan2(dy, dx))
    return -angle + 90


def random_range(min_val, max_val):
    return min_val + random.random() * (max_val - min_val)


def clamp(value, min_val, max_val):
    return max(min_val, min(max_val, value))
