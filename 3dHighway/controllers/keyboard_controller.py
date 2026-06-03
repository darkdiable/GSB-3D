from panda3d.core import KeyboardButton


class KeyboardController:
    def __init__(self, base, vehicle_controller, app):
        self.base = base
        self.vehicle_controller = vehicle_controller
        self.app = app
        
        self.accept_input()
    
    def accept_input(self):
        self.base.accept('w', self.vehicle_controller.accelerate, [True])
        self.base.accept('w-up', self.vehicle_controller.accelerate, [False])
        self.base.accept('arrow_up', self.vehicle_controller.accelerate, [True])
        self.base.accept('arrow_up-up', self.vehicle_controller.accelerate, [False])
        
        self.base.accept('s', self.vehicle_controller.brake, [True])
        self.base.accept('s-up', self.vehicle_controller.brake, [False])
        self.base.accept('arrow_down', self.vehicle_controller.brake, [True])
        self.base.accept('arrow_down-up', self.vehicle_controller.brake, [False])
        
        self.base.accept('a', self.vehicle_controller.turn_left, [True])
        self.base.accept('a-up', self.vehicle_controller.turn_left, [False])
        self.base.accept('arrow_left', self.vehicle_controller.turn_left, [True])
        self.base.accept('arrow_left-up', self.vehicle_controller.turn_left, [False])
        
        self.base.accept('d', self.vehicle_controller.turn_right, [True])
        self.base.accept('d-up', self.vehicle_controller.turn_right, [False])
        self.base.accept('arrow_right', self.vehicle_controller.turn_right, [True])
        self.base.accept('arrow_right-up', self.vehicle_controller.turn_right, [False])
        
        self.base.accept('r', self.app.reset)
        
        self.base.accept('escape', self.app.exit)
    
    def update(self, dt):
        pass
    
    def cleanup(self):
        self.base.ignore('w')
        self.base.ignore('w-up')
        self.base.ignore('arrow_up')
        self.base.ignore('arrow_up-up')
        self.base.ignore('s')
        self.base.ignore('s-up')
        self.base.ignore('arrow_down')
        self.base.ignore('arrow_down-up')
        self.base.ignore('a')
        self.base.ignore('a-up')
        self.base.ignore('arrow_left')
        self.base.ignore('arrow_left-up')
        self.base.ignore('d')
        self.base.ignore('d-up')
        self.base.ignore('arrow_right')
        self.base.ignore('arrow_right-up')
        self.base.ignore('r')
        self.base.ignore('escape')
