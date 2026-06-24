import math
from PySide6.QtCore import Qt, QPointF, QTimer
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QFont, QPolygonF
from config import (
    COLOR_BACKGROUND, COLOR_BORDER, COLOR_PRIMARY, COLOR_SECONDARY,
    COLOR_SUCCESS, COLOR_WARNING, COLOR_DANGER, COLOR_TEXT
)

class SimulationView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setMouseTracking(True)
        
        # Panning & Zooming State
        self.zoom_factor = 1.0
        self.pan_x = 0.0
        self.pan_y = 0.0
        self.last_mouse_pos = None
        self.drag_mode = False
        
        # Data passed from engine ticks
        self.vehicles = []
        self.lights = {}
        self.nodes = {}
        self.edges = {}
        self.weather = {"weather": "Sunny", "temperature": 22.0}
        
        # Grid lines cache
        self.grid_size = 50
        
        # Animation timer for accidents and lights flashing
        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self.update)
        self.anim_timer.start(500) # update graphics animation frame
        self.flash_state = True

    def set_simulation_data(self, nodes, edges):
        self.nodes = nodes
        self.edges = edges
        self.update()

    def update_frame(self, state_dict):
        """Called every 100ms when simulation tick completes."""
        self.vehicles = state_dict["vehicles"]
        self.lights = state_dict["lights"]
        self.weather = state_dict["weather"]
        
        # Update edges congestion state
        # In a real app we'd query the engine, but we'll approximate based on vehicles list counts
        # Clear edge counts first
        for key in self.edges.keys():
            self.edges[key]["vehicles_count"] = 0
            
        for v in self.vehicles:
            # Reconstruct edge key from path if vehicle is moving
            # Wait, vehicle dict has x, y and destination.
            # To simplify, we track vehicle density dynamically or just let traffic engine feed it
            pass
            
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_mode = True
            self.last_mouse_pos = event.position()
            self.setCursor(Qt.ClosedHandCursor)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_mode = False
            self.setCursor(Qt.ArrowCursor)

    def mouseMoveEvent(self, event):
        if self.drag_mode and self.last_mouse_pos is not None:
            delta = event.position() - self.last_mouse_pos
            self.pan_x += delta.x()
            self.pan_y += delta.y()
            self.last_mouse_pos = event.position()
            self.update()

    def wheelEvent(self, event):
        # Zoom around mouse cursor
        zoom_anchor = event.position()
        zoom_step = 1.1 if event.angleDelta().y() > 0 else 0.9
        
        # Limit zoom
        new_zoom = self.zoom_factor * zoom_step
        if 0.3 <= new_zoom <= 4.0:
            # Adjust pan to keep anchor in place
            anchor_world_x = (zoom_anchor.x() - self.pan_x) / self.zoom_factor
            anchor_world_y = (zoom_anchor.y() - self.pan_y) / self.zoom_factor
            
            self.zoom_factor = new_zoom
            self.pan_x = zoom_anchor.x() - anchor_world_x * self.zoom_factor
            self.pan_y = zoom_anchor.y() - anchor_world_y * self.zoom_factor
            self.update()

    def keyPressEvent(self, event):
        # Reset view on Space bar
        if event.key() == Qt.Key_Space:
            self.zoom_factor = 1.0
            self.pan_x = 0.0
            self.pan_y = 0.0
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 1. Background Fill
        painter.fillRect(self.rect(), QColor(COLOR_BACKGROUND))
        
        # 2. Draw Blueprint Gridlines
        self.draw_blueprint_grid(painter)
        
        # Apply Zoom & Pan Transform
        painter.save()
        painter.translate(self.pan_x, self.pan_y)
        painter.scale(self.zoom_factor, self.zoom_factor)
        
        # 3. Draw Roads (Edges)
        self.draw_roads(painter)
        
        # 4. Draw Intersections (Nodes) & Traffic Signals
        self.draw_intersections(painter)
        
        # 5. Draw Vehicles
        self.draw_vehicles(painter)
        
        painter.restore()
        
        # Toggle flash state for blinkers
        self.flash_state = not self.flash_state

    def draw_blueprint_grid(self, painter):
        """Draw grid lines that scale/pan nicely."""
        grid_color = QColor(COLOR_BORDER)
        grid_color.setAlpha(40)
        pen = QPen(grid_color, 1)
        painter.setPen(pen)
        
        # Draw horizontal lines
        height = self.height()
        width = self.width()
        
        # Compute start coordinates based on pan offset
        offset_x = int(self.pan_x) % int(self.grid_size * self.zoom_factor)
        offset_y = int(self.pan_y) % int(self.grid_size * self.zoom_factor)
        
        scaled_grid = self.grid_size * self.zoom_factor
        
        for x in range(0, int(width + scaled_grid), int(scaled_grid)):
            painter.drawLine(x - scaled_grid + offset_x, 0, x - scaled_grid + offset_x, height)
            
        for y in range(0, int(height + scaled_grid), int(scaled_grid)):
            painter.drawLine(0, y - scaled_grid + offset_y, width, y - scaled_grid + offset_y)

    def draw_roads(self, painter):
        """Draw street segments, color-coded by congestion density."""
        for edge_key, info in self.edges.items():
            u, v = edge_key
            if u not in self.nodes or v not in self.nodes:
                continue
                
            x1, y1 = self.nodes[u]["x"], self.nodes[u]["y"]
            x2, y2 = self.nodes[v]["x"], self.nodes[v]["y"]
            
            # Check closed
            is_closed = info.get("closed", False)
            v_count = info.get("vehicles_count", 0)
            capacity = info.get("capacity", 15.0)
            density = v_count / capacity
            
            # Determine Color
            if is_closed:
                road_color = QColor(COLOR_DANGER)  # Closed roads highlight
                pen_style = Qt.DashLine
            else:
                pen_style = Qt.SolidLine
                if density > 0.8:
                    road_color = QColor(COLOR_DANGER)      # Red heavy traffic
                elif density > 0.4:
                    road_color = QColor(COLOR_WARNING)     # Orange moderate traffic
                else:
                    # Fade between background gray and secondary cyan based on active vehicles
                    if v_count > 0:
                        road_color = QColor(COLOR_PRIMARY)
                    else:
                        road_color = QColor("#222233")
            
            # Draw primary wide path
            road_width = 16
            pen = QPen(road_color, road_width, pen_style, Qt.RoundCap, Qt.RoundJoin)
            painter.setPen(pen)
            painter.drawLine(x1, y1, x2, y2)
            
            # Draw a middle line dashed lane marker
            dash_color = QColor(COLOR_TEXT)
            dash_color.setAlpha(120)
            painter.setPen(QPen(dash_color, 1.5, Qt.DashLine, Qt.FlatCap))
            painter.drawLine(x1, y1, x2, y2)

    def draw_intersections(self, painter):
        """Draw round intersections and flashing traffic light points."""
        font = QFont("Segoe UI", 7, QFont.Bold)
        painter.setFont(font)
        
        for node_id, pos in self.nodes.items():
            x, y = pos["x"], pos["y"]
            
            # Junction ring
            painter.setPen(QPen(QColor(COLOR_BORDER), 2))
            painter.setBrush(QBrush(QColor(COLOR_CARD_BG)))
            painter.drawEllipse(QPointF(x, y), 12, 12)
            
            # Draw traffic light dots on the node paths
            # If H_GREEN: Horizontal lanes get Green, Vertical lanes get Red
            phase = self.lights.get(node_id, "H_GREEN")
            h_color = QColor(COLOR_SUCCESS) if phase == "H_GREEN" else QColor(COLOR_DANGER)
            v_color = QColor(COLOR_DANGER) if phase == "H_GREEN" else QColor(COLOR_SUCCESS)
            
            # Horizontal indicators (draw left and right of node center)
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(h_color))
            painter.drawEllipse(QPointF(x - 14, y), 3, 3)
            painter.drawEllipse(QPointF(x + 14, y), 3, 3)
            
            # Vertical indicators (draw top and bottom of node center)
            painter.setBrush(QBrush(v_color))
            painter.drawEllipse(QPointF(x, y - 14), 3, 3)
            painter.drawEllipse(QPointF(x, y + 14), 3, 3)
            
            # Label nodes in faint text
            painter.setPen(QColor("#777777"))
            label = f"N{node_id[0]},{node_id[1]}"
            painter.drawText(int(x - 12), int(y - 18), label)

    def draw_vehicles(self, painter):
        """Draw all simulated vehicles with orientation vectors."""
        for v in self.vehicles:
            vx, vy = v["position_x"], v["position_y"]
            status = v["status"]
            v_type = v["type"]
            
            # Determine color based on vehicle class
            if v_type == "Ambulance":
                v_color = QColor(COLOR_DANGER)  # Emergency red
            elif v_type == "Police":
                v_color = QColor("#007BFF")     # Police light blue
            elif v_type == "Bus":
                v_color = QColor(COLOR_SECONDARY) # Cyan bus
            elif v_type == "Truck":
                v_color = QColor(COLOR_WARNING)   # Orange truck
            elif v_type == "Motorcycle":
                v_color = QColor(COLOR_SUCCESS)   # Green bike
            else:
                v_color = QColor(COLOR_TEXT)      # White standard car
                
            # Setup painter for rotation orientation
            painter.save()
            painter.translate(vx, vy)
            
            # Interpolate direction heading from next destination
            dx = v["destination_x"] - vx
            dy = v["destination_y"] - vy
            angle_rad = math.atan2(dy, dx)
            angle_deg = math.degrees(angle_rad)
            painter.rotate(angle_deg)
            
            # Render Vehicle Body
            painter.setPen(QPen(QColor(COLOR_BORDER), 1))
            painter.setBrush(QBrush(v_color))
            
            # Size vehicle based on type
            v_w, v_h = 8, 5
            if v_type in ["Bus", "Truck"]:
                v_w, v_h = 13, 7
            elif v_type == "Motorcycle":
                v_w, v_h = 6, 3
                
            painter.drawRoundedRect(-v_w/2, -v_h/2, v_w, v_h, 1.5, 1.5)
            
            # Draw emergency sirens if Ambulance or Police
            if v_type in ["Ambulance", "Police"]:
                siren_color = QColor("#FF0000") if self.flash_state else QColor("#0000FF")
                painter.setBrush(QBrush(siren_color))
                painter.setPen(Qt.NoPen)
                painter.drawEllipse(QPointF(0, 0), 2.5, 2.5)
                
            painter.restore()
            
            # Render Accident Alert Icon (Warning triangle above vehicles in collision)
            if status == "Accident":
                self.draw_accident_sign(painter, vx, vy)

    def draw_accident_sign(self, painter, x, y):
        """Draws flashing red/yellow accident triangle above a vehicle."""
        if not self.flash_state:
            # Flash blink rate
            return
            
        painter.save()
        painter.translate(x, y - 18)
        
        # Draw triangle
        triangle = QPolygonF([
            QPointF(0, -8),
            QPointF(-8, 6),
            QPointF(8, 6)
        ])
        
        painter.setPen(QPen(QColor(COLOR_DANGER), 1.5))
        painter.setBrush(QBrush(QColor(COLOR_WARNING)))
        painter.drawPolygon(triangle)
        
        # Exclamation dot inside
        painter.setPen(QPen(QColor(COLOR_DANGER), 1.5))
        painter.drawLine(0, -3, 0, 1)
        painter.drawPoint(0, 4)
        
        painter.restore()
