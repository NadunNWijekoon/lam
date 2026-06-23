import time
import random
import math
import networkx as nx
from PySide6.QtCore import QThread, Signal
from config import GRID_ROWS, GRID_COLS, GRID_SPACING, WEATHER_IMPACT, MAX_VEHICLES
from models.vehicle import Vehicle
from models.event import Event
from database.db_manager import DBManager
from simulations.weather.weather_manager import WeatherManager

class TrafficEngine(QThread):
    # Signals to communicate with the UI
    tick_signal = Signal(dict)  # Emits current state (vehicles, lights, stats)
    event_signal = Signal(dict) # Emits log events
    
    def __init__(self):
        super().__init__()
        self.running = False
        self.paused = False
        self.db = DBManager()
        self.weather_mgr = WeatherManager()
        
        # Build the Smart City Graph
        self.graph = nx.DiGraph()
        self.nodes = {}
        self.edges = {}
        self.init_city_graph()
        
        # Simulation States
        self.vehicles = {}
        self.next_vehicle_id = 1
        self.active_accidents = {}  # vehicle_id -> (edge, timestamp, duration)
        
        # Traffic Lights state: node_id -> "H_GREEN" (Horizontal Green) or "V_GREEN" (Vertical Green)
        self.traffic_lights = {}
        self.light_timer = 0.0
        self.light_cycle_duration = 5.0  # seconds per green phase
        
        self.init_traffic_lights()
        self.init_vehicles()
        
        # Cumulative stats
        self.total_fuel_consumed = 0.0
        self.total_accidents = 0
        self.simulation_start_time = time.time()
        self.elapsed_simulation_seconds = 0
        
    def init_city_graph(self):
        """Creates the grid city street graph."""
        # Add nodes
        for c in range(GRID_COLS):
            for r in range(GRID_ROWS):
                node_id = (c, r)
                x = (c + 1) * GRID_SPACING + 50
                y = (r + 1) * GRID_SPACING + 50
                self.nodes[node_id] = {"x": x, "y": y}
                self.graph.add_node(node_id, x=x, y=y)
                
        # Add edges (bidirectional streets)
        for c in range(GRID_COLS):
            for r in range(GRID_ROWS):
                node_id = (c, r)
                # Horizontal connection
                if c < GRID_COLS - 1:
                    next_node = (c + 1, r)
                    self.add_street_segment(node_id, next_node)
                # Vertical connection
                if r < GRID_ROWS - 1:
                    next_node = (c, r + 1)
                    self.add_street_segment(node_id, next_node)
                    
    def add_street_segment(self, u, v):
        """Adds two directed edges to the graph to represent a bidirectional road segment."""
        # Calculate length/distance between nodes
        x1, y1 = self.nodes[u]["x"], self.nodes[u]["y"]
        x2, y2 = self.nodes[v]["x"], self.nodes[v]["y"]
        dist = math.hypot(x2 - x1, y2 - y1)
        
        # Add directed edge u -> v
        self.graph.add_edge(u, v, weight=dist, capacity=15.0, vehicles_count=0, closed=False, name=self.get_road_name(u, v))
        self.edges[(u, v)] = {"capacity": 15.0, "vehicles_count": 0, "closed": False, "length": dist, "name": self.get_road_name(u, v)}
        
        # Add directed edge v -> u
        self.graph.add_edge(v, u, weight=dist, capacity=15.0, vehicles_count=0, closed=False, name=self.get_road_name(v, u))
        self.edges[(v, u)] = {"capacity": 15.0, "vehicles_count": 0, "closed": False, "length": dist, "name": self.get_road_name(v, u)}

    def get_road_name(self, u, v):
        """Generate human readable street name from nodes coordinates."""
        c1, r1 = u
        c2, r2 = v
        horizontal_streets = ["Broadway Street", "Main Street", "Grand Avenue", "Wall Street"]
        vertical_avenues = ["1st Avenue", "2nd Avenue", "3rd Avenue", "4th Avenue", "5th Avenue"]
        
        if r1 == r2:
            street_idx = r1 % len(horizontal_streets)
            return horizontal_streets[street_idx]
        else:
            ave_idx = c1 % len(vertical_avenues)
            return vertical_avenues[ave_idx]

    def init_traffic_lights(self):
        """Initialize traffic light phase for each node in the grid."""
        for node_id in self.nodes.keys():
            # Alternate start phases
            self.traffic_lights[node_id] = "H_GREEN" if (node_id[0] + node_id[1]) % 2 == 0 else "V_GREEN"

    def init_vehicles(self):
        """Populate initial batch of vehicles."""
        for _ in range(50):  # Start with 50 active vehicles
            self.spawn_vehicle()

    def spawn_vehicle(self):
        """Spawns a vehicle at a random node and computes its path to another random destination."""
        if len(self.vehicles) >= MAX_VEHICLES:
            return
            
        start_node = random.choice(list(self.nodes.keys()))
        dest_node = random.choice(list(self.nodes.keys()))
        while dest_node == start_node:
            dest_node = random.choice(list(self.nodes.keys()))
            
        v_id = f"V_{self.next_vehicle_id:04d}"
        self.next_vehicle_id += 1
        
        vehicle = Vehicle(v_id)
        vehicle.position = (self.nodes[start_node]["x"], self.nodes[start_node]["y"])
        vehicle.destination = (self.nodes[dest_node]["x"], self.nodes[dest_node]["y"])
        
        # Calculate path
        try:
            path = nx.shortest_path(self.graph, start_node, dest_node, weight='weight')
            if len(path) > 1:
                vehicle.path = path
                vehicle.path_index = 0
                first_edge = (path[0], path[1])
                vehicle.current_edge = first_edge
                vehicle.edge_length = self.edges[first_edge]["length"]
                self.vehicles[v_id] = vehicle
                
                # Increment edge count
                self.edges[first_edge]["vehicles_count"] += 1
                self.graph[first_edge[0]][first_edge[1]]["vehicles_count"] = self.edges[first_edge]["vehicles_count"]
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            pass

    def run(self):
        self.running = True
        self.paused = False
        self.simulation_start_time = time.time() - self.elapsed_simulation_seconds
        
        while self.running:
            if not self.paused:
                t0 = time.time()
                
                self.elapsed_simulation_seconds = int(time.time() - self.simulation_start_time)
                
                self.update_traffic_lights()
                self.update_vehicles()
                self.detect_accidents()
                self.resolve_accidents()
                
                # Periodically spawn new vehicles if under limit to maintain activity
                if len(self.vehicles) < 80 and random.random() < 0.2:
                    self.spawn_vehicle()
                
                # Calculate aggregated stats
                stats = self.calculate_statistics()
                
                # Write to DB every 2 seconds (20 ticks of 100ms)
                if int(t0 * 10) % 20 == 0:
                    self.db.log_vehicles([v.to_dict() for v in self.vehicles.values()])
                    timestamp = time.strftime("%H:%M:%S")
                    self.db.log_statistics(
                        stats["active_vehicles"],
                        stats["avg_speed"],
                        stats["traffic_density"],
                        timestamp
                    )
                
                # Emit tick state
                state = {
                    "vehicles": [v.to_dict() for v in self.vehicles.values()],
                    "lights": self.traffic_lights,
                    "stats": stats,
                    "weather": self.weather_mgr.get_status()
                }
                self.tick_signal.emit(state)
                
                # Sleep to maintain 100ms cycle
                elapsed = time.time() - t0
                sleep_time = max(0.005, 0.1 - elapsed)
                time.sleep(sleep_time)
            else:
                time.sleep(0.2)

    def stop_simulation(self):
        self.running = False
        self.wait()

    def toggle_pause(self):
        self.paused = not self.paused
        if not self.paused:
            # Shift start time to account for pause duration
            self.simulation_start_time = time.time() - self.elapsed_simulation_seconds

    def update_traffic_lights(self):
        """Cycle light states periodically."""
        self.light_timer += 0.1
        if self.light_timer >= self.light_cycle_duration:
            self.light_timer = 0.0
            for node_id in self.traffic_lights.keys():
                # Toggle
                self.traffic_lights[node_id] = "V_GREEN" if self.traffic_lights[node_id] == "H_GREEN" else "H_GREEN"

    def update_vehicles(self):
        """Move and update state of all active vehicles."""
        weather_impact = self.weather_mgr.get_impact_factors()
        w_speed_factor = weather_impact["speed_factor"]
        
        vehicles_to_remove = []
        
        for v_id, v in list(self.vehicles.items()):
            # 1. Skip if vehicle is in an accident
            if v.status == "Accident":
                v.speed = 0.0
                v.tick_fuel(idle=True)
                continue
                
            # 2. Check fuel
            if v.fuel <= 0.0:
                v.status = "Stopped"
                v.speed = 0.0
                # Dispatch alert once
                if random.random() < 0.02:
                    self.trigger_event("Fuel Depleted", f"{v.type} ({v.id}) run out of fuel", "Warning")
                    vehicles_to_remove.append(v_id) # remove fuel-exhausted vehicles
                continue
            
            # 3. Check path index
            if v.path_index >= len(v.path) - 1:
                # Reached final destination, remove and spawn a new one later
                self.edges[v.current_edge]["vehicles_count"] = max(0, self.edges[v.current_edge]["vehicles_count"] - 1)
                self.graph[v.current_edge[0]][v.current_edge[1]]["vehicles_count"] = self.edges[v.current_edge]["vehicles_count"]
                vehicles_to_remove.append(v_id)
                continue
                
            curr_node = v.path[v.path_index]
            next_node = v.path[v.path_index + 1]
            edge = (curr_node, next_node)
            
            # Recalculate if current edge is closed due to an accident
            if self.edges[edge]["closed"]:
                # Re-route
                try:
                    remaining_path = nx.shortest_path(self.graph, curr_node, v.path[-1], weight='weight')
                    if len(remaining_path) > 1:
                        # Release old edge count
                        self.edges[v.current_edge]["vehicles_count"] = max(0, self.edges[v.current_edge]["vehicles_count"] - 1)
                        self.graph[v.current_edge[0]][v.current_edge[1]]["vehicles_count"] = self.edges[v.current_edge]["vehicles_count"]
                        
                        v.path = remaining_path
                        v.path_index = 0
                        next_node = v.path[1]
                        edge = (curr_node, next_node)
                        v.current_edge = edge
                        v.edge_length = self.edges[edge]["length"]
                        v.distance_traveled_on_edge = 0.0
                        
                        self.edges[edge]["vehicles_count"] += 1
                        self.graph[edge[0]][edge[1]]["vehicles_count"] = self.edges[edge]["vehicles_count"]
                except (nx.NetworkXNoPath, nx.NodeNotFound):
                    # No path possible, vehicle stops and waits
                    v.speed = 0.0
                    v.status = "Stopped"
                    v.tick_fuel(idle=True)
                    continue

            # Calculate congestion slowdown factor
            density = self.edges[edge]["vehicles_count"] / self.edges[edge]["capacity"]
            congestion_slowdown = max(0.2, 1.0 - density)
            
            # Speed limits based on vehicle type and weather
            target_speed = v.MAX_SPEEDS[v.type] * w_speed_factor * congestion_slowdown
            
            # 4. Check traffic lights slowdown as approaching the next intersection (node next_node)
            dist_remaining = v.edge_length - v.distance_traveled_on_edge
            is_horizontal_road = (curr_node[1] == next_node[1])
            light_state = self.traffic_lights.get(next_node)
            
            stopped_at_light = False
            if dist_remaining < 30.0: # Close to intersection
                if is_horizontal_road and light_state == "V_GREEN": # Red for horizontal
                    stopped_at_light = True
                elif not is_horizontal_road and light_state == "H_GREEN": # Red for vertical
                    stopped_at_light = True
                    
            if stopped_at_light:
                # Decelerate or stop
                v.speed = max(0.0, v.speed - 15.0)
                v.status = "Stopped"
                v.tick_fuel(idle=True)
            else:
                # Accelerate to target speed
                v.speed = min(target_speed, v.speed + 10.0)
                v.status = "Moving"
                v.tick_fuel(idle=False)
                
            # Accumulate total fuel consumed
            self.total_fuel_consumed += v.FUEL_RATES[v.type] * (0.3 if v.status == "Stopped" else 1.0) * 0.1 # scaled for time
            
            # Update position along edge
            v.distance_traveled_on_edge += (v.speed * 0.1) # speed is pixels per second, tick is 100ms
            
            # Clip distance
            if v.distance_traveled_on_edge >= v.edge_length:
                # Transition to next edge in path
                self.edges[edge]["vehicles_count"] = max(0, self.edges[edge]["vehicles_count"] - 1)
                self.graph[edge[0]][edge[1]]["vehicles_count"] = self.edges[edge]["vehicles_count"]
                
                v.path_index += 1
                v.distance_traveled_on_edge = 0.0
                
                if v.path_index < len(v.path) - 1:
                    new_edge = (v.path[v.path_index], v.path[v.path_index + 1])
                    v.current_edge = new_edge
                    v.edge_length = self.edges[new_edge]["length"]
                    self.edges[new_edge]["vehicles_count"] += 1
                    self.graph[new_edge[0]][new_edge[1]]["vehicles_count"] = self.edges[new_edge]["vehicles_count"]
                    
                    # Update coordinates to start of new edge
                    x1, y1 = self.nodes[new_edge[0]]["x"], self.nodes[new_edge[0]]["y"]
                    v.position = (x1, y1)
            else:
                # Interpolate coordinate
                x1, y1 = self.nodes[curr_node]["x"], self.nodes[curr_node]["y"]
                x2, y2 = self.nodes[next_node]["x"], self.nodes[next_node]["y"]
                ratio = v.distance_traveled_on_edge / v.edge_length
                px = x1 + (x2 - x1) * ratio
                py = y1 + (y2 - y1) * ratio
                v.position = (px, py)
                
        # Remove dead vehicles
        for v_id in vehicles_to_remove:
            if v_id in self.vehicles:
                del self.vehicles[v_id]
                
    def detect_accidents(self):
        """Randomly triggers an accident depending on weather conditions."""
        weather_impact = self.weather_mgr.get_impact_factors()
        base_prob = weather_impact["accident_probability"]
        
        # Scale probability by number of active moving vehicles
        moving_vehicles = [v for v in self.vehicles.values() if v.status == "Moving"]
        
        if not moving_vehicles:
            return
            
        # Overall crash probability per tick
        crash_chance = base_prob * len(moving_vehicles) * 0.02
        
        if random.random() < crash_chance:
            victim = random.choice(moving_vehicles)
            
            # Trigger crash
            victim.status = "Accident"
            victim.speed = 0.0
            edge = victim.current_edge
            
            if edge:
                self.edges[edge]["closed"] = True
                self.graph[edge[0]][edge[1]]["weight"] = 99999.0  # Pathfinding penalty
                
                # Log incident
                road_name = self.edges[edge]["name"]
                event_msg = f"Accident reported at {road_name}"
                self.trigger_event("Accident", event_msg, "Critical")
                
                # Record crash details
                self.active_accidents[victim.id] = {
                    "edge": edge,
                    "time": time.time(),
                    "cleared_step": 0, # 0 = accident, 1 = ambulance dispatched, 2 = cleared
                    "road_name": road_name
                }
                self.total_accidents += 1

    def resolve_accidents(self):
        """Handles emergency dispatch and clearance stages of accidents."""
        now = time.time()
        cleared_accidents = []
        
        for v_id, details in list(self.active_accidents.items()):
            elapsed = now - details["time"]
            edge = details["edge"]
            road_name = details["road_name"]
            
            if details["cleared_step"] == 0 and elapsed > 4.0:
                # Dispatch Ambulance/Police
                details["cleared_step"] = 1
                self.trigger_event("Emergency", f"Emergency services dispatched to {road_name}", "Warning")
                
                # Spawn a police car / ambulance near the accident spot
                self.spawn_emergency_vehicle(edge[0])
                
            elif details["cleared_step"] == 1 and elapsed > 10.0:
                # Clear accident
                details["cleared_step"] = 2
                self.edges[edge]["closed"] = False
                self.graph[edge[0]][edge[1]]["weight"] = self.edges[edge]["length"]  # Restore cost
                
                self.trigger_event("Clearance", f"Accident cleared at {road_name}. Traffic flow restored.", "Info")
                
                # Restore victim status
                if v_id in self.vehicles:
                    self.vehicles[v_id].status = "Moving"
                    # Force recalculate path
                    try:
                        curr_node = self.vehicles[v_id].path[self.vehicles[v_id].path_index]
                        dest_node = self.vehicles[v_id].path[-1]
                        self.vehicles[v_id].path = nx.shortest_path(self.graph, curr_node, dest_node, weight='weight')
                        self.vehicles[v_id].path_index = 0
                    except:
                        pass
                
                cleared_accidents.append(v_id)
                
        for v_id in cleared_accidents:
            del self.active_accidents[v_id]

    def spawn_emergency_vehicle(self, target_node):
        """Spawns an Ambulance or Police car heading to target_node."""
        if len(self.vehicles) >= MAX_VEHICLES:
            return
            
        start_nodes = [n for n in self.nodes.keys() if n != target_node]
        if not start_nodes:
            return
        start_node = random.choice(start_nodes)
        
        v_id = f"EM_{self.next_vehicle_id:04d}"
        self.next_vehicle_id += 1
        
        e_type = random.choice(["Ambulance", "Police"])
        vehicle = Vehicle(v_id, vehicle_type=e_type)
        vehicle.position = (self.nodes[start_node]["x"], self.nodes[start_node]["y"])
        vehicle.destination = (self.nodes[target_node]["x"], self.nodes[target_node]["y"])
        
        try:
            path = nx.shortest_path(self.graph, start_node, target_node, weight='weight')
            if len(path) > 1:
                vehicle.path = path
                vehicle.path_index = 0
                first_edge = (path[0], path[1])
                vehicle.current_edge = first_edge
                vehicle.edge_length = self.edges[first_edge]["length"]
                self.vehicles[v_id] = vehicle
                
                self.edges[first_edge]["vehicles_count"] += 1
                self.graph[first_edge[0]][first_edge[1]]["vehicles_count"] = self.edges[first_edge]["vehicles_count"]
        except:
            pass

    def trigger_event(self, event_type, message, severity):
        """Fires an event, logs it to database, and notifies UI."""
        timestamp = time.strftime("%H:%M:%S")
        self.db.log_event(event_type, message, severity, timestamp)
        
        event_dict = {
            "event_type": event_type,
            "location": message,
            "severity": severity,
            "time": timestamp
        }
        self.event_signal.emit(event_dict)

    def calculate_statistics(self):
        """Aggregate current active telemetry counts."""
        active_count = len(self.vehicles)
        speeds = [v.speed for v in self.vehicles.values() if v.status == "Moving"]
        avg_speed = sum(speeds) / len(speeds) if speeds else 0.0
        
        # Calculate overall density: occupied edges ratio
        active_edges = sum(1 for e in self.edges.values() if e["vehicles_count"] > 0)
        total_edges = len(self.edges)
        traffic_density = (active_edges / total_edges * 100.0) if total_edges else 0.0
        
        emergencies = sum(1 for v in self.vehicles.values() if v.type in ["Ambulance", "Police"])
        
        return {
            "active_vehicles": active_count,
            "avg_speed": round(avg_speed, 1),
            "traffic_density": round(traffic_density, 1),
            "fuel_consumption": round(self.total_fuel_consumed, 1),
            "emergencies": emergencies + len(self.active_accidents),
            "active_accidents": len(self.active_accidents),
            "total_accidents": self.total_accidents,
            "simulation_time": time.strftime("%H:%M:%S", time.gmtime(self.elapsed_simulation_seconds))
        }

    def force_accident(self):
        """UI interaction to trigger a manual accident immediately."""
        moving_vehicles = [v for v in self.vehicles.values() if v.status == "Moving"]
        if moving_vehicles:
            victim = random.choice(moving_vehicles)
            victim.status = "Accident"
            victim.speed = 0.0
            edge = victim.current_edge
            if edge:
                self.edges[edge]["closed"] = True
                self.graph[edge[0]][edge[1]]["weight"] = 99999.0
                road_name = self.edges[edge]["name"]
                self.trigger_event("Manual Accident", f"System override: Accident caused at {road_name}", "Critical")
                self.active_accidents[victim.id] = {
                    "edge": edge,
                    "time": time.time(),
                    "cleared_step": 0,
                    "road_name": road_name
                }
                self.total_accidents += 1
                return True
        return False
