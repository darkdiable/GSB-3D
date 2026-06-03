from panda3d.core import (
    GeomVertexData, GeomVertexFormat, GeomVertexWriter,
    Geom, GeomTriangles, GeomNode, NodePath, Vec3
)
from config.settings import Config


class VehicleModel:
    def __init__(self, render):
        self.render = render
        self.vehicle_node = None
        self.body_color = (0.8, 0.2, 0.2, 1)
        self.window_color = (0.3, 0.5, 0.7, 1)
        self.wheel_color = (0.1, 0.1, 0.1, 1)
        
    def create_box(self, center, size, color):
        vdata = GeomVertexData('box', GeomVertexFormat.getV3c4(), Geom.UHStatic)
        vertex = GeomVertexWriter(vdata, 'vertex')
        color_writer = GeomVertexWriter(vdata, 'color')
        
        cx, cy, cz = center
        sx, sy, sz = size
        
        vertices = [
            (cx - sx/2, cy - sy/2, cz - sz/2),
            (cx + sx/2, cy - sy/2, cz - sz/2),
            (cx + sx/2, cy + sy/2, cz - sz/2),
            (cx - sx/2, cy + sy/2, cz - sz/2),
            (cx - sx/2, cy - sy/2, cz + sz/2),
            (cx + sx/2, cy - sy/2, cz + sz/2),
            (cx + sx/2, cy + sy/2, cz + sz/2),
            (cx - sx/2, cy + sy/2, cz + sz/2),
        ]
        
        for x, y, z in vertices:
            vertex.addData3f(x, y, z)
            color_writer.addData4f(*color)
        
        prim = GeomTriangles(Geom.UHStatic)
        
        faces = [
            (0, 1, 2), (0, 2, 3),
            (4, 6, 5), (4, 7, 6),
            (0, 4, 5), (0, 5, 1),
            (2, 6, 7), (2, 7, 3),
            (0, 3, 7), (0, 7, 4),
            (1, 5, 6), (1, 6, 2),
        ]
        
        for v1, v2, v3 in faces:
            prim.addVertices(v1, v2, v3)
        
        geom = Geom(vdata)
        geom.addPrimitive(prim)
        
        node = GeomNode('box')
        node.addGeom(geom)
        return NodePath(node)
    
    def create_wheel(self, center, radius, width, color):
        vdata = GeomVertexData('wheel', GeomVertexFormat.getV3c4(), Geom.UHStatic)
        vertex = GeomVertexWriter(vdata, 'vertex')
        color_writer = GeomVertexWriter(vdata, 'color')
        
        cx, cy, cz = center
        segments = 12
        
        for i in range(segments):
            angle1 = (i / segments) * 3.14159 * 2
            angle2 = ((i + 1) / segments) * 3.14159 * 2
            
            x1 = cx + radius * 1
            y1 = cy + radius * 0
            z1 = cz + radius * 0
            
            vertices = []
            
            x1 = cx
            y1 = cy - width/2
            z1 = cz + radius
            
            x2 = cx
            y2 = cy + width/2
            z2 = cz + radius
            
            x3 = cx
            y3 = cy + width/2
            z3 = cz - radius
            
            x4 = cx
            y4 = cy - width/2
            z4 = cz - radius
            
            for x, y, z in [(x1, y1, z1), (x2, y2, z2), (x3, y3, z3), (x4, y4, z4)]:
                vertex.addData3f(x, y, z)
                color_writer.addData4f(*color)
        
        prim = GeomTriangles(Geom.UHStatic)
        for i in range(0, 4 * segments, 4):
            prim.addVertices(i, i + 1, i + 2)
            prim.addVertices(i, i + 2, i + 3)
        
        geom = Geom(vdata)
        geom.addPrimitive(prim)
        
        node = GeomNode('wheel')
        node.addGeom(geom)
        wheel_np = NodePath(node)
        
        vdata2 = GeomVertexData('wheel_side', GeomVertexFormat.getV3c4(), Geom.UHStatic)
        vertex2 = GeomVertexWriter(vdata2, 'vertex')
        color2 = GeomVertexWriter(vdata2, 'color')
        
        for side_y in [cy - width/2, cy + width/2]:
            for i in range(segments):
                angle1 = (i / segments) * 3.14159 * 2
                angle2 = ((i + 1) / segments) * 3.14159 * 2
                
                z1 = cz + radius * 0
                x1 = cx + radius * 1
                
                vertex2.addData3f(cx, side_y, cz)
                color2.addData4f(*color)
                
                vertex2.addData3f(cx + radius, side_y, cz)
                color2.addData4f(*color)
                
                vertex2.addData3f(cx + radius * 0.866, side_y, cz + radius * 0.5)
                color2.addData4f(*color)
        
        geom2 = Geom(vdata2)
        prim2 = GeomTriangles(Geom.UHStatic)
        for i in range(0, 3 * segments * 2, 3):
            prim2.addVertices(i, i + 1, i + 2)
        geom2.addPrimitive(prim2)
        
        node2 = GeomNode('wheel_side')
        node2.addGeom(geom2)
        wheel_side_np = NodePath(node2)
        wheel_side_np.reparentTo(wheel_np)
        
        return wheel_np
    
    def create_simple_car(self):
        car_root = NodePath('car')
        
        body = self.create_box(
            (0, 0, Config.VEHICLE_HEIGHT / 2),
            (Config.VEHICLE_LENGTH, Config.VEHICLE_WIDTH, Config.VEHICLE_HEIGHT),
            self.body_color
        )
        body.reparentTo(car_root)
        
        cabin = self.create_box(
            (Config.VEHICLE_LENGTH * 0.1, 0, Config.VEHICLE_HEIGHT * 1.3),
            (Config.VEHICLE_LENGTH * 0.5, Config.VEHICLE_WIDTH * 0.85, Config.VEHICLE_HEIGHT * 0.6),
            self.window_color
        )
        cabin.reparentTo(car_root)
        
        wheel_radius = 0.35
        wheel_width = 0.2
        
        wheel_positions = [
            (Config.VEHICLE_LENGTH * 0.35, -Config.VEHICLE_WIDTH * 0.55, wheel_radius),
            (Config.VEHICLE_LENGTH * 0.35, Config.VEHICLE_WIDTH * 0.55, wheel_radius),
            (-Config.VEHICLE_LENGTH * 0.35, -Config.VEHICLE_WIDTH * 0.55, wheel_radius),
            (-Config.VEHICLE_LENGTH * 0.35, Config.VEHICLE_WIDTH * 0.55, wheel_radius),
        ]
        
        for pos in wheel_positions:
            wheel = self.create_wheel(pos, wheel_radius, wheel_width, self.wheel_color)
            wheel.reparentTo(car_root)
        
        return car_root
    
    def build(self):
        self.vehicle_node = self.create_simple_car()
        self.vehicle_node.reparentTo(self.render)
        return self.vehicle_node
