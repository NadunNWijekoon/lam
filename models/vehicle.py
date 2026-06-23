import random

class Vehicle:
    VEHICLE_TYPES = ["Car", "Bus", "Ambulance", "Police", "Truck", "Motorcycle"]
    
    # Fuel consumption rate per tick (arbitrary)
    FUEL_RATES = {
        "Car": 0.05,
        "Bus": 0.12,
        "Ambulance": 0.08,
        "Police": 0.07,
        "Truck": 0.15,
        "Motorcycle": 0.03
    }
    
    # Maximum speeds (base)
    MAX_SPEEDS = {
        "Car": 50.0,
        "Bus": 35.0,
        "Ambulance": 70.0,
        "Police": 65.0,
        "Truck": 30.0,
        "Motorcycle": 55.0
    }

    def __init__(self, vehicle_id, vehicle_type=None):
        self.id = vehicle_id
        self.type = vehicle_type if vehicle_type in self.VEHICLE_TYPES else random.choice(self.VEHICLE_TYPES)
        self.speed = 0.0
        self.fuel = 100.0  # Percentage fuel level
        self.position = (0.0, 0.0)  # Current (x, y)
        self.destination = (0.0, 0.0)  # Destination (x, y)
        self.status = "Moving"  # "Moving", "Stopped", "Accident", "Parked"
        
        # Pathfinding tracking
        self.current_edge = None  # (u, v) node tuple
        self.path = []  # List of nodes to travel
        self.path_index = 0
        self.distance_traveled_on_edge = 0.0
        self.edge_length = 1.0

    def tick_fuel(self, idle=False):
        """Consume fuel based on vehicle type and idle state."""
        rate = self.FUEL_RATES[self.type]
        if idle:
            rate *= 0.3  # Idle consumption is lower
        self.fuel = max(0.0, self.fuel - rate)

    def to_dict(self):
        """Serialize vehicle data for database and UI updates."""
        return {
            "id": self.id,
            "type": self.type,
            "speed": round(self.speed, 2),
            "fuel": round(self.fuel, 2),
            "position_x": self.position[0],
            "position_y": self.position[1],
            "destination_x": self.destination[0],
            "destination_y": self.destination[1],
            "status": self.status
        }
