from panda3d.core import *
from config.settings import (
    AIRPORT_SIZE, RUNWAY_LENGTH, RUNWAY_WIDTH,
    NUM_GATES, GATE_SIZE, GATE_COLORS
)
from utils.model_builder import create_box


class AirportBuilder:
    def __init__(self, render, loader):
        self.render = render
        self.loader = loader
        self.airport_node = None
        self.runway_node = None
        self.gates = []
        self.runway_start = None
        self.runway_end = None

    def build(self):
        self._create_ground()
        self._create_runway()
        self._create_gates()
        self._create_taxiway_lines()
        return self

    def _create_ground(self):
        self.airport_node = self.render.attachNewNode('airport')

        ground = create_box(AIRPORT_SIZE, AIRPORT_SIZE, 1)
        ground.reparentTo(self.airport_node)
        ground.setPos(0, 0, -0.5)

        ground_material = Material()
        ground_material.setDiffuse((0.3, 0.35, 0.3, 1))
        ground_material.setSpecular((0.1, 0.1, 0.1, 1))
        ground.setMaterial(ground_material)

        grass_node = self.render.attachNewNode('grass')
        grass = create_box(AIRPORT_SIZE * 2, AIRPORT_SIZE * 2, 1)
        grass.reparentTo(grass_node)
        grass.setPos(0, 0, -1)

        grass_material = Material()
        grass_material.setDiffuse((0.2, 0.5, 0.2, 1))
        grass.setMaterial(grass_material)

    def _create_runway(self):
        self.runway_node = self.airport_node.attachNewNode('runway')

        runway = create_box(RUNWAY_WIDTH, RUNWAY_LENGTH, 0.2)
        runway.reparentTo(self.runway_node)
        runway.setPos(0, 0, 0.1)

        runway_material = Material()
        runway_material.setDiffuse((0.2, 0.2, 0.2, 1))
        runway.setMaterial(runway_material)

        self.runway_start = LVector3(0, -RUNWAY_LENGTH / 2, 0.2)
        self.runway_end = LVector3(0, RUNWAY_LENGTH / 2, 0.2)

        line_segments = LineSegs()
        line_segments.setColor(1, 1, 1, 1)
        line_segments.setThickness(2)

        dashes = 20
        dash_length = RUNWAY_LENGTH / (dashes * 2)
        for i in range(dashes):
            y_start = -RUNWAY_LENGTH / 2 + i * dash_length * 2 + dash_length * 0.5
            y_end = y_start + dash_length
            line_segments.moveTo(-1, y_start, 0.21)
            line_segments.drawTo(-1, y_end, 0.21)
            line_segments.moveTo(1, y_start, 0.21)
            line_segments.drawTo(1, y_end, 0.21)

        line_segments.moveTo(-RUNWAY_WIDTH / 2 + 1, -RUNWAY_LENGTH / 2 + 2, 0.21)
        line_segments.drawTo(-RUNWAY_WIDTH / 2 + 1, RUNWAY_LENGTH / 2 - 2, 0.21)
        line_segments.moveTo(RUNWAY_WIDTH / 2 - 1, -RUNWAY_LENGTH / 2 + 2, 0.21)
        line_segments.drawTo(RUNWAY_WIDTH / 2 - 1, RUNWAY_LENGTH / 2 - 2, 0.21)

        threshold = create_box(RUNWAY_WIDTH - 2, 3, 0.22)
        threshold.reparentTo(self.runway_node)
        threshold.setPos(0, -RUNWAY_LENGTH / 2 + 1.5, 0.11)
        threshold.setColor(1, 1, 1, 1)

        threshold2 = create_box(RUNWAY_WIDTH - 2, 3, 0.22)
        threshold2.reparentTo(self.runway_node)
        threshold2.setPos(0, RUNWAY_LENGTH / 2 - 1.5, 0.11)
        threshold2.setColor(1, 1, 1, 1)

        line_node = line_segments.create()
        self.runway_node.attachNewNode(line_node)

    def _create_gates(self):
        gate_positions = []
        spacing = 12
        start_x = -(NUM_GATES - 1) * spacing / 2

        for i in range(NUM_GATES):
            x = start_x + i * spacing
            gate_positions.append((x, -25, 0.2))

        for i, pos in enumerate(gate_positions):
            gate_node = self.airport_node.attachNewNode(f'gate_{i}')
            gate_node.setPos(*pos)

            gate = create_box(GATE_SIZE, GATE_SIZE, 0.3)
            gate.reparentTo(gate_node)
            gate.setPos(0, 0, 0.15)

            gate_material = Material()
            color = GATE_COLORS[i % len(GATE_COLORS)]
            gate_material.setDiffuse(color)
            gate_material.setEmission((color[0] * 0.3, color[1] * 0.3, color[2] * 0.3, 1))
            gate.setMaterial(gate_material)

            label = TextNode(f'gate_label_{i}')
            label.setText(f'{i + 1}')
            label.setAlign(TextNode.ACenter)
            label.setTextColor(1, 1, 1, 1)
            label_np = gate_node.attachNewNode(label)
            label_np.setPos(0, 0, 1)
            label_np.setScale(1.5)
            label_np.setBillboardPointEye()

            border = create_box(GATE_SIZE + 0.5, GATE_SIZE + 0.5, 0.1)
            border.reparentTo(gate_node)
            border.setPos(0, 0, 0.05)
            border.setColor(0.1, 0.1, 0.1, 1)

            self.gates.append({
                'id': i,
                'node': gate_node,
                'position': LVector3(*pos),
                'color': color,
                'occupied': False,
                'aircraft': None
            })

    def _create_taxiway_lines(self):
        line_segments = LineSegs()
        line_segments.setColor(1, 0.8, 0.2, 1)
        line_segments.setThickness(1.5)

        start_x = -(NUM_GATES - 1) * 6 - GATE_SIZE / 2
        end_x = (NUM_GATES - 1) * 6 + GATE_SIZE / 2

        line_segments.moveTo(start_x, -25, 0.22)
        line_segments.drawTo(end_x, -25, 0.22)

        line_segments.moveTo(end_x, -25, 0.22)
        line_segments.drawTo(end_x, -RUNWAY_LENGTH / 2 + 5, 0.22)

        line_segments.moveTo(-end_x, -25, 0.22)
        line_segments.drawTo(-end_x, -RUNWAY_LENGTH / 2 + 5, 0.22)

        line_segments.moveTo(-end_x, -RUNWAY_LENGTH / 2 + 5, 0.22)
        line_segments.drawTo(end_x, -RUNWAY_LENGTH / 2 + 5, 0.22)

        line_node = line_segments.create()
        self.airport_node.attachNewNode(line_node)

    def get_available_gate(self):
        for gate in self.gates:
            if not gate['occupied']:
                return gate
        return None

    def get_gate_by_id(self, gate_id):
        for gate in self.gates:
            if gate['id'] == gate_id:
                return gate
        return None

    def occupy_gate(self, gate_id, aircraft):
        gate = self.get_gate_by_id(gate_id)
        if gate:
            gate['occupied'] = True
            gate['aircraft'] = aircraft
            return True
        return False

    def release_gate(self, gate_id):
        gate = self.get_gate_by_id(gate_id)
        if gate:
            gate['occupied'] = False
            gate['aircraft'] = None
            return True
        return False

    def get_runway_approach_point(self):
        return LVector3(0, -RUNWAY_LENGTH / 2 - 15, 15)

    def get_runway_departure_point(self):
        return LVector3(0, RUNWAY_LENGTH / 2 + 20, 20)

    def get_taxiway_point(self):
        return LVector3(0, -RUNWAY_LENGTH / 2 + 10, 0.5)
