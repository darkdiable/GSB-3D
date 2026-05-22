import sys
sys.path.insert(0, '.')

print("=== Testing all modules ===")

from utils.model_builder import create_box, create_sphere, create_cylinder
print("1. model_builder: OK")
box = create_box(2, 2, 2)
sphere = create_sphere(1)
cylinder = create_cylinder(0.5, 2)
print("   Geometries created: OK")

from aircraft.aircraft import Aircraft
a = Aircraft(is_departure=True)
print(f"2. aircraft: OK (flight={a.flight_number})")

from airport.airport_builder import AirportBuilder
print("3. airport_builder: OK")

from systems.dispatcher import Dispatcher
print("4. dispatcher: OK")

from ui.dispatch_board import DispatchBoard
print("5. dispatch_board: OK")

from config.settings import AIRPORT_SIZE, NUM_GATES
print(f"6. config: OK (AIRPORT_SIZE={AIRPORT_SIZE}, NUM_GATES={NUM_GATES})")

print("\n=== All tests passed! ===")
