import random
from panda3d.core import LVector3
from config.settings import (
    STATUS_WAITING, STATUS_TAXIING, STATUS_TAKEOFF, STATUS_LANDING,
    STATUS_DEPARTED, STATUS_ARRIVED, MIN_SPAWN_INTERVAL, MAX_SPAWN_INTERVAL,
    RUNWAY_LENGTH
)
from aircraft.aircraft import Aircraft
from utils.helpers import random_range


class Dispatcher:
    def __init__(self, render, loader, airport_builder):
        self.render = render
        self.loader = loader
        self.airport = airport_builder
        self.aircrafts = []
        self.runway_busy = False
        self.spawn_timer = 0
        self.next_spawn_interval = random_range(MIN_SPAWN_INTERVAL, MAX_SPAWN_INTERVAL)
        self.selected_aircraft = None
        self.on_aircraft_click = None
        self.on_status_change = None

    def create_initial_aircrafts(self, count=4):
        for i in range(count):
            gate = self.airport.get_available_gate()
            if gate:
                is_departure = random.choice([True, True, False])
                aircraft = Aircraft(is_departure=is_departure)
                start_pos = LVector3(gate['position'].getX(), gate['position'].getY(), 0.5)
                aircraft.create_model(self.render, self.loader, start_pos, (180, 0, 0))
                aircraft.gate_id = gate['id']
                aircraft.set_status(STATUS_WAITING)
                self.airport.occupy_gate(gate['id'], aircraft)
                self.aircrafts.append(aircraft)

    def update(self, dt):
        self.spawn_timer += dt
        if self.spawn_timer >= self.next_spawn_interval:
            self.spawn_timer = 0
            self.next_spawn_interval = random_range(MIN_SPAWN_INTERVAL, MAX_SPAWN_INTERVAL)
            self._try_spawn_aircraft()

        for aircraft in self.aircrafts:
            if aircraft.status == STATUS_DEPARTED:
                continue
            if aircraft.status == STATUS_TAXIING or aircraft.status == STATUS_TAKEOFF or aircraft.status == STATUS_LANDING:
                aircraft.update(dt)

        self._cleanup_departed()

    def _try_spawn_aircraft(self):
        if self.runway_busy:
            return

        active_count = len([a for a in self.aircrafts if a.status != STATUS_DEPARTED])
        if active_count >= 8:
            return

        is_departure = random.choice([True, False])

        if is_departure:
            gate = self.airport.get_available_gate()
            if not gate:
                return
            aircraft = Aircraft(is_departure=True)
            start_pos = LVector3(gate['position'].getX(), gate['position'].getY(), 0.5)
            aircraft.create_model(self.render, self.loader, start_pos, (180, 0, 0))
            aircraft.gate_id = gate['id']
            aircraft.set_status(STATUS_WAITING)
            self.airport.occupy_gate(gate['id'], aircraft)
            self.aircrafts.append(aircraft)

            if self.on_status_change:
                self.on_status_change(aircraft)
        else:
            aircraft = Aircraft(is_departure=False)
            approach_point = self.airport.get_runway_approach_point()
            start_pos = LVector3(approach_point.getX(), approach_point.getY() - 20, approach_point.getZ() + 5)
            aircraft.create_model(self.render, self.loader, start_pos, (0, 0, 0))
            aircraft.set_status(STATUS_WAITING)
            self.aircrafts.append(aircraft)

            if self.on_status_change:
                self.on_status_change(aircraft)

    def _cleanup_departed(self):
        to_remove = []
        for aircraft in self.aircrafts:
            if aircraft.status == STATUS_DEPARTED:
                if aircraft.gate_id is not None:
                    self.airport.release_gate(aircraft.gate_id)
                to_remove.append(aircraft)

        for aircraft in to_remove:
            if aircraft in self.aircrafts:
                self.aircrafts.remove(aircraft)
            aircraft.destroy()

    def request_takeoff(self, aircraft):
        if aircraft.status != STATUS_WAITING or not aircraft.is_departure:
            return False
        if self.runway_busy:
            return False
        if aircraft.gate_id is None:
            return False

        self.runway_busy = True
        gate = self.airport.get_gate_by_id(aircraft.gate_id)
        if not gate:
            self.runway_busy = False
            return False

        runway_start = self.airport.runway_start
        runway_end = self.airport.runway_end
        departure_point = self.airport.get_runway_departure_point()

        taxi_to_runway = LVector3(0, runway_start.getY() + 5, 0.5)
        runway_pos = LVector3(0, runway_start.getY(), 0.5)
        takeoff_end = LVector3(0, runway_end.getY() + 30, 20)

        path = [
            LVector3(gate['position'].getX(), gate['position'].getY() - 8, 0.5),
            LVector3(gate['position'].getX(), -30, 0.5),
            taxi_to_runway,
            runway_pos,
            LVector3(0, runway_end.getY(), 0.5),
            takeoff_end,
            departure_point
        ]

        aircraft.set_path(path)
        aircraft.set_status(STATUS_TAXIING)
        self.airport.release_gate(aircraft.gate_id)
        aircraft.gate_id = None

        self._schedule_takeoff_transition(aircraft, path)

        if self.on_status_change:
            self.on_status_change(aircraft)
        return True

    def _schedule_takeoff_transition(self, aircraft, path):
        runway_idx = 3

        def check_transition():
            if aircraft.status == STATUS_DEPARTED:
                self.runway_busy = False
                return

            if aircraft.current_path_index == runway_idx and aircraft.status == STATUS_TAXIING:
                aircraft.set_status(STATUS_TAKEOFF)
                if self.on_status_change:
                    self.on_status_change(aircraft)
            elif aircraft.current_path_index >= len(path) - 1:
                self.runway_busy = False
                return

            if aircraft.status != STATUS_DEPARTED:
                base = self._get_base()
                if base:
                    base.taskMgr.doMethodLater(0.1, lambda t: check_transition() or t.done, 'check_takeoff')

        base = self._get_base()
        if base:
            base.taskMgr.doMethodLater(0.1, lambda t: check_transition() or t.done, 'check_takeoff')

    def request_landing(self, aircraft):
        if aircraft.status != STATUS_WAITING or aircraft.is_departure:
            return False
        if self.runway_busy:
            return False

        gate = self.airport.get_available_gate()
        if not gate:
            return False

        self.runway_busy = True
        aircraft.gate_id = gate['id']

        approach_point = self.airport.get_runway_approach_point()
        runway_end = self.airport.runway_end
        runway_start = self.airport.runway_start

        path = [
            LVector3(approach_point.getX(), approach_point.getY(), approach_point.getZ()),
            LVector3(0, runway_end.getY(), 12),
            LVector3(0, runway_start.getY() + 10, 3),
            LVector3(0, runway_start.getY() - 5, 0.5),
            LVector3(gate['position'].getX(), -30, 0.5),
            LVector3(gate['position'].getX(), gate['position'].getY() - 5, 0.5),
            LVector3(gate['position'].getX(), gate['position'].getY(), 0.5)
        ]

        aircraft.set_path(path)
        aircraft.set_status(STATUS_LANDING)

        self._schedule_landing_transition(aircraft, path, gate)

        if self.on_status_change:
            self.on_status_change(aircraft)
        return True

    def _schedule_landing_transition(self, aircraft, path, gate):
        taxi_idx = 4

        def check_transition():
            if aircraft.status == STATUS_DEPARTED:
                self.runway_busy = False
                return

            if aircraft.current_path_index >= taxi_idx and aircraft.status == STATUS_LANDING:
                aircraft.set_status(STATUS_TAXIING)
                if self.on_status_change:
                    self.on_status_change(aircraft)
            elif aircraft.current_path_index >= len(path) - 1:
                self.runway_busy = False
                self.airport.occupy_gate(gate['id'], aircraft)
                aircraft.set_status(STATUS_ARRIVED)
                aircraft.set_status(STATUS_WAITING)
                aircraft.is_departure = True
                if self.on_status_change:
                    self.on_status_change(aircraft)
                return

            if aircraft.status != STATUS_DEPARTED:
                base = self._get_base()
                if base:
                    base.taskMgr.doMethodLater(0.1, lambda t: check_transition() or t.done, 'check_landing')

        base = self._get_base()
        if base:
            base.taskMgr.doMethodLater(0.1, lambda t: check_transition() or t.done, 'check_landing')

    def toggle_aircraft_status(self, aircraft):
        if aircraft.status == STATUS_WAITING:
            if aircraft.is_departure:
                success = self.request_takeoff(aircraft)
                return 'takeoff_requested' if success else 'request_failed'
            else:
                success = self.request_landing(aircraft)
                return 'landing_requested' if success else 'request_failed'
        elif aircraft.status == STATUS_TAXIING:
            aircraft.set_status(STATUS_WAITING)
            aircraft.set_path([])
            self.runway_busy = False
            if self.on_status_change:
                self.on_status_change(aircraft)
            return 'paused'
        elif aircraft.status == STATUS_TAKEOFF or aircraft.status == STATUS_LANDING:
            return 'cannot_toggle_in_flight'
        return 'no_action'

    def get_aircraft_at_position(self, mpos):
        closest = None
        closest_dist = 5

        for aircraft in self.aircrafts:
            if aircraft.status == STATUS_DEPARTED:
                continue
            pos = aircraft.get_position()
            if pos:
                dist = ((pos.getX() - mpos.getX()) ** 2 +
                        (pos.getY() - mpos.getY()) ** 2) ** 0.5
                if dist < closest_dist:
                    closest_dist = dist
                    closest = aircraft

        return closest

    def get_all_aircrafts(self):
        return [a for a in self.aircrafts if a.status != STATUS_DEPARTED]

    def _get_base(self):
        try:
            from direct.showbase.ShowBase import ShowBase
            if hasattr(ShowBase, 'base'):
                return ShowBase.base
        except:
            pass
        return None
