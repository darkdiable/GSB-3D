from direct.gui.OnscreenText import OnscreenText
from direct.gui.OnscreenImage import OnscreenImage
from panda3d.core import TextNode, Vec3, Vec4
from config.settings import Config


class HUD:
    def __init__(self, base):
        self.base = base
        self.elements = {}
        self.violation_display = None
        self.violation_timer = 0.0
        
    def create_speed_display(self):
        speed_label = OnscreenText(
            text='Speed:',
            pos=(-1.3, 0.85),
            scale=0.08,
            fg=(1, 1, 1, 1),
            align=TextNode.ALeft,
            mayChange=False
        )
        self.elements['speed_label'] = speed_label
        
        speed_value = OnscreenText(
            text='0 km/h',
            pos=(-1.0, 0.85),
            scale=0.1,
            fg=(0, 1, 0, 1),
            align=TextNode.ALeft,
            mayChange=True
        )
        self.elements['speed_value'] = speed_value
        
        speed_limit_label = OnscreenText(
            text=f'Limit: {Config.SPEED_LIMIT_KMH} km/h',
            pos=(-1.3, 0.75),
            scale=0.06,
            fg=(1, 1, 0, 1),
            align=TextNode.ALeft,
            mayChange=False
        )
        self.elements['speed_limit'] = speed_limit_label
    
    def create_lane_display(self):
        lane_label = OnscreenText(
            text='Lane:',
            pos=(-1.3, 0.65),
            scale=0.06,
            fg=(1, 1, 1, 1),
            align=TextNode.ALeft,
            mayChange=False
        )
        self.elements['lane_label'] = lane_label
        
        lane_value = OnscreenText(
            text='1',
            pos=(-1.0, 0.65),
            scale=0.07,
            fg=(0.5, 0.8, 1, 1),
            align=TextNode.ALeft,
            mayChange=True
        )
        self.elements['lane_value'] = lane_value
    
    def create_violation_counter(self):
        violation_label = OnscreenText(
            text='Violations:',
            pos=(0.8, 0.85),
            scale=0.06,
            fg=(1, 1, 1, 1),
            align=TextNode.ARight,
            mayChange=False
        )
        self.elements['violation_label'] = violation_label
        
        violation_value = OnscreenText(
            text='0',
            pos=(1.05, 0.85),
            scale=0.07,
            fg=(1, 0.5, 0, 1),
            align=TextNode.ARight,
            mayChange=True
        )
        self.elements['violation_value'] = violation_value
        
        speeding_count = OnscreenText(
            text='Speeding: 0',
            pos=(1.05, 0.78),
            scale=0.05,
            fg=(1, 0.3, 0.3, 1),
            align=TextNode.ARight,
            mayChange=True
        )
        self.elements['speeding_count'] = speeding_count
        
        lane_crossing_count = OnscreenText(
            text='Lane Cross: 0',
            pos=(1.05, 0.72),
            scale=0.05,
            fg=(1, 0.3, 0.3, 1),
            align=TextNode.ARight,
            mayChange=True
        )
        self.elements['lane_crossing_count'] = lane_crossing_count
    
    def create_controls_help(self):
        help_text = [
            "Controls:",
            "W/Up - Accelerate",
            "S/Down - Brake",
            "A/Left - Turn Left",
            "D/Right - Turn Right",
            "R - Reset Vehicle",
            "ESC - Exit"
        ]
        
        y_pos = 0.5
        for i, text in enumerate(help_text):
            help_item = OnscreenText(
                text=text,
                pos=(-1.3, y_pos - i * 0.06),
                scale=0.05,
                fg=(0.8, 0.8, 0.8, 1),
                align=TextNode.ALeft,
                mayChange=False
            )
            self.elements[f'help_{i}'] = help_item
    
    def create_violation_alert(self):
        self.violation_display = OnscreenText(
            text='',
            pos=(0, 0.5),
            scale=0.12,
            fg=(1, 0, 0, 1),
            align=TextNode.ACenter,
            mayChange=True
        )
        self.elements['violation_alert'] = self.violation_display
    
    def build(self):
        self.create_speed_display()
        self.create_lane_display()
        self.create_violation_counter()
        self.create_controls_help()
        self.create_violation_alert()
    
    def update_speed(self, speed_kmh):
        if 'speed_value' in self.elements:
            self.elements['speed_value'].setText(f'{speed_kmh:.1f} km/h')
            if speed_kmh > Config.SPEED_LIMIT_KMH:
                self.elements['speed_value'].setFg((1, 0, 0, 1))
            else:
                self.elements['speed_value'].setFg((0, 1, 0, 1))
    
    def update_lane(self, lane):
        if 'lane_value' in self.elements:
            self.elements['lane_value'].setText(str(lane + 1))
    
    def update_violation_count(self, total, speeding, lane_crossing):
        if 'violation_value' in self.elements:
            self.elements['violation_value'].setText(str(total))
        if 'speeding_count' in self.elements:
            self.elements['speeding_count'].setText(f'Speeding: {speeding}')
        if 'lane_crossing_count' in self.elements:
            self.elements['lane_crossing_count'].setText(f'Lane Cross: {lane_crossing}')
    
    def show_violation(self, message):
        if self.violation_display:
            self.violation_display.setText(message)
            self.violation_timer = Config.VIOLATION_DISPLAY_TIME
    
    def update(self, dt):
        if self.violation_timer > 0:
            self.violation_timer -= dt
            if self.violation_timer <= 0:
                self.violation_display.setText('')
    
    def cleanup(self):
        for element in self.elements.values():
            element.destroy()
        self.elements.clear()
