from panda3d.core import (
    GeomVertexData, GeomVertexFormat, GeomVertexWriter,
    Geom, GeomTriangles, GeomNode, NodePath
)
from config.settings import Config


class Highway:
    def __init__(self, render):
        self.render = render
        self.road_segments = []
        self.line_segments = []
        self.grass_segments = []
        
    def create_road_segment(self, segment_start, segment_end):
        vdata = GeomVertexData('road', GeomVertexFormat.getV3c4(), Geom.UHStatic)
        vertex = GeomVertexWriter(vdata, 'vertex')
        color = GeomVertexWriter(vdata, 'color')
        
        road_half_width = (Config.LANE_WIDTH * Config.LANE_COUNT) / 2
        
        vertices = [
            (segment_start, -road_half_width, 0),
            (segment_start, road_half_width, 0),
            (segment_end, road_half_width, 0),
            (segment_end, -road_half_width, 0),
        ]
        
        for x, y, z in vertices:
            vertex.addData3f(x, y, z)
            color.addData4f(*Config.ROAD_COLOR)
        
        prim = GeomTriangles(Geom.UHStatic)
        prim.addVertices(0, 1, 2)
        prim.addVertices(0, 2, 3)
        
        geom = Geom(vdata)
        geom.addPrimitive(prim)
        
        node = GeomNode('road_segment')
        node.addGeom(geom)
        return NodePath(node)
    
    def create_line_segment(self, segment_start, segment_end, y_pos, is_dashed=False):
        vdata = GeomVertexData('line', GeomVertexFormat.getV3c4(), Geom.UHStatic)
        vertex = GeomVertexWriter(vdata, 'vertex')
        color = GeomVertexWriter(vdata, 'color')
        
        line_half_width = Config.LINE_WIDTH / 2
        
        if is_dashed:
            dash_length = 2.0
            gap_length = 2.0
            segments = []
            current_pos = segment_start
            while current_pos < segment_end:
                dash_end = min(current_pos + dash_length, segment_end)
                segments.append((current_pos, dash_end))
                current_pos += dash_length + gap_length
            
            for start, end in segments:
                vertices = [
                    (start, y_pos - line_half_width, 0.01),
                    (start, y_pos + line_half_width, 0.01),
                    (end, y_pos + line_half_width, 0.01),
                    (end, y_pos - line_half_width, 0.01),
                ]
                for x, y, z in vertices:
                    vertex.addData3f(x, y, z)
                    color.addData4f(*Config.LINE_COLOR)
                
                prim = GeomTriangles(Geom.UHStatic)
                base_idx = len(segments) * 4
                prim.addVertices(0, 1, 2)
                prim.addVertices(0, 2, 3)
        else:
            vertices = [
                (segment_start, y_pos - line_half_width, 0.01),
                (segment_start, y_pos + line_half_width, 0.01),
                (segment_end, y_pos + line_half_width, 0.01),
                (segment_end, y_pos - line_half_width, 0.01),
            ]
            
            for x, y, z in vertices:
                vertex.addData3f(x, y, z)
                color.addData4f(*Config.LINE_COLOR)
            
            prim = GeomTriangles(Geom.UHStatic)
            prim.addVertices(0, 1, 2)
            prim.addVertices(0, 2, 3)
        
        geom = Geom(vdata)
        geom.addPrimitive(prim)
        
        node = GeomNode('line_segment')
        node.addGeom(geom)
        return NodePath(node)
    
    def create_grass_segment(self, segment_start, segment_end):
        vdata = GeomVertexData('grass', GeomVertexFormat.getV3c4(), Geom.UHStatic)
        vertex = GeomVertexWriter(vdata, 'vertex')
        color = GeomVertexWriter(vdata, 'color')
        
        road_half_width = (Config.LANE_WIDTH * Config.LANE_COUNT) / 2
        grass_half_width = road_half_width + 20
        
        vertices = [
            (segment_start, -grass_half_width, -0.1),
            (segment_start, -road_half_width, -0.1),
            (segment_end, -road_half_width, -0.1),
            (segment_end, -grass_half_width, -0.1),
            (segment_start, road_half_width, -0.1),
            (segment_start, grass_half_width, -0.1),
            (segment_end, grass_half_width, -0.1),
            (segment_end, road_half_width, -0.1),
        ]
        
        for x, y, z in vertices:
            vertex.addData3f(x, y, z)
            color.addData4f(*Config.GRASS_COLOR)
        
        prim = GeomTriangles(Geom.UHStatic)
        prim.addVertices(0, 1, 2)
        prim.addVertices(0, 2, 3)
        prim.addVertices(4, 5, 6)
        prim.addVertices(4, 6, 7)
        
        geom = Geom(vdata)
        geom.addPrimitive(prim)
        
        node = GeomNode('grass_segment')
        node.addGeom(geom)
        return NodePath(node)
    
    def build(self):
        segment_length = 200
        num_segments = int(Config.ROAD_LENGTH // segment_length) + 1
        
        road_half_width = (Config.LANE_WIDTH * Config.LANE_COUNT) / 2
        
        for i in range(num_segments):
            start = i * segment_length
            end = (i + 1) * segment_length
            
            road_segment = self.create_road_segment(start, end)
            road_segment.reparentTo(self.render)
            self.road_segments.append(road_segment)
            
            grass_segment = self.create_grass_segment(start, end)
            grass_segment.reparentTo(self.render)
            self.grass_segments.append(grass_segment)
            
            for lane in range(Config.LANE_COUNT + 1):
                y_pos = -road_half_width + lane * Config.LANE_WIDTH
                is_dashed = 0 < lane < Config.LANE_COUNT
                line_segment = self.create_line_segment(start, end, y_pos, is_dashed)
                line_segment.reparentTo(self.render)
                self.line_segments.append(line_segment)
    
    def get_lane_center(self, lane_index):
        road_half_width = (Config.LANE_WIDTH * Config.LANE_COUNT) / 2
        return -road_half_width + (lane_index + 0.5) * Config.LANE_WIDTH
    
    def get_road_bounds(self):
        road_half_width = (Config.LANE_WIDTH * Config.LANE_COUNT) / 2
        return (-road_half_width, road_half_width)
    
    def get_lane_lines(self):
        road_half_width = (Config.LANE_WIDTH * Config.LANE_COUNT) / 2
        lines = []
        for lane in range(Config.LANE_COUNT + 1):
            lines.append(-road_half_width + lane * Config.LANE_WIDTH)
        return lines
