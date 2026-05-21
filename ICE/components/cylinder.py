from vpython import cylinder, box, vector, color, label, compound

from ICE.utils.constants import (
    CYLINDER_RADIUS,
    CYLINDER_HEIGHT,
    CYLINDER_WALL_THICKNESS,
    CYLINDER_HEAD_HEIGHT,
    CYLINDER_SPACING,
    NUM_CYLINDERS,
    ENGINE_BLOCK_HEIGHT,
    ENGINE_BLOCK_WIDTH,
    ENGINE_BLOCK_LENGTH,
    CRANK_THROW,
)
from ICE.utils.materials import ENGINE_METAL, ALUMINUM, CAST_IRON


class EngineBlock:
    def __init__(self, base_pos):
        self.base_pos = base_pos
        self.block = None
        self.cylinders = []
        self.cylinder_head = None
        self.labels = []
        self._create_block()
        self._create_cylinders()
        self._create_cylinder_head()
        self._add_labels()

    def _create_block(self):
        block_length = ENGINE_BLOCK_LENGTH
        block_width = ENGINE_BLOCK_WIDTH
        block_height = ENGINE_BLOCK_HEIGHT - CYLINDER_HEAD_HEIGHT
        bottom_y = self.base_pos.y - CRANK_THROW - 2.0

        self.block = box(
            pos=vector(
                self.base_pos.x,
                bottom_y + block_height / 2,
                self.base_pos.z
            ),
            length=block_length,
            width=block_width,
            height=block_height,
            color=CAST_IRON,
            opacity=0.9
        )

        oil_pan = box(
            pos=vector(
                self.base_pos.x,
                bottom_y - 0.5,
                self.base_pos.z
            ),
            length=block_length - 1,
            width=block_width - 0.5,
            height=1.0,
            color=ENGINE_METAL
        )

    def _create_cylinders(self):
        start_x = self.base_pos.x - (NUM_CYLINDERS - 1) * CYLINDER_SPACING / 2
        bottom_y = self.base_pos.y - CRANK_THROW

        for i in range(NUM_CYLINDERS):
            x_pos = start_x + i * CYLINDER_SPACING
            center_y = bottom_y + CYLINDER_HEIGHT / 2

            outer_cyl = cylinder(
                pos=vector(x_pos, bottom_y, self.base_pos.z),
                axis=vector(0, CYLINDER_HEIGHT, 0),
                radius=CYLINDER_RADIUS + CYLINDER_WALL_THICKNESS,
                color=ALUMINUM,
                opacity=0.85
            )

            inner_cyl = cylinder(
                pos=vector(x_pos, bottom_y, self.base_pos.z),
                axis=vector(0, CYLINDER_HEIGHT, 0),
                radius=CYLINDER_RADIUS,
                color=CAST_IRON,
                opacity=0.3
            )

            self.cylinders.append({
                "index": i,
                "x_pos": x_pos,
                "bottom_y": bottom_y,
                "outer": outer_cyl,
                "inner": inner_cyl
            })

    def _create_cylinder_head(self):
        block_length = ENGINE_BLOCK_LENGTH
        block_width = ENGINE_BLOCK_WIDTH
        head_y = self.base_pos.y - CRANK_THROW + CYLINDER_HEIGHT

        self.cylinder_head = box(
            pos=vector(
                self.base_pos.x,
                head_y + CYLINDER_HEAD_HEIGHT / 2,
                self.base_pos.z
            ),
            length=block_length,
            width=block_width,
            height=CYLINDER_HEAD_HEIGHT,
            color=ALUMINUM,
            opacity=0.9
        )

        valve_cover = box(
            pos=vector(
                self.base_pos.x,
                head_y + CYLINDER_HEAD_HEIGHT + 0.4,
                self.base_pos.z
            ),
            length=block_length - 0.5,
            width=block_width - 0.5,
            height=0.8,
            color=ENGINE_METAL
        )

    def _add_labels(self):
        head_y = self.base_pos.y - CRANK_THROW + CYLINDER_HEIGHT

        lbl_block = label(
            pos=vector(
                self.base_pos.x - ENGINE_BLOCK_LENGTH / 2 - 1,
                self.base_pos.y,
                self.base_pos.z + ENGINE_BLOCK_WIDTH / 2 + 1
            ),
            text="气缸体\n(Cylinder Block)",
            xoffset=-20,
            yoffset=0,
            color=color.white,
            background=CAST_IRON,
            height=12,
            box=True,
            line=True
        )
        self.labels.append(lbl_block)

        lbl_head = label(
            pos=vector(
                self.base_pos.x + ENGINE_BLOCK_LENGTH / 2 + 1,
                head_y + CYLINDER_HEAD_HEIGHT / 2,
                self.base_pos.z + ENGINE_BLOCK_WIDTH / 2 + 1
            ),
            text="气缸盖\n(Cylinder Head)",
            xoffset=20,
            yoffset=0,
            color=color.white,
            background=ALUMINUM,
            height=12,
            box=True,
            line=True
        )
        self.labels.append(lbl_head)

    def get_cylinder_positions(self):
        return [cyl["x_pos"] for cyl in self.cylinders]

    def get_cylinder_bottom_y(self):
        return self.cylinders[0]["bottom_y"] if self.cylinders else 0

    def set_visibility(self, visible=True):
        self.block.visible = visible
        self.cylinder_head.visible = visible
        for cyl in self.cylinders:
            cyl["outer"].visible = visible
            cyl["inner"].visible = visible
        for lbl in self.labels:
            lbl.visible = visible
