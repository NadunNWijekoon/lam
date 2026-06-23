from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton, QListWidget, QSlider, QComboBox
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QPixmap
import os

from config import (
    COLOR_BACKGROUND, COLOR_CARD_BG, COLOR_PRIMARY, COLOR_SECONDARY,
    COLOR_SUCCESS, COLOR_WARNING, COLOR_DANGER, COLOR_BORDER, ICONS_DIR
)
from ui.simulation_view import SimulationView

class SimulationsTab(QWidget):
    def __init__(self, simulation_engine, parent=None):
        super().__init__(parent)
        self.engine = simulation_engine
        self.init_ui()
        
        # Give simulation view initial map data
        self.sim_view.set_simulation_data(self.engine.nodes, self.engine.edges)

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # 1. TOP BODY AREA (Map on left, quick metrics panel on right)
        top_layout = QHBoxLayout()
        top_layout.setSpacing(10)
        
        # Left Map View
        self.sim_view = SimulationView()
        self.sim_view.setMinimumHeight(400)
        top_layout.addWidget(self.sim_view, stretch=5)
        
        # Right Side Control & Quick Panel
        right_panel = QFrame()
        right_panel.setObjectName("card")
        right_panel.setFixedWidth(220)
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(12, 12, 12, 12)
        right_layout.setSpacing(12)
        
        # A. Quick simulation controls
        lbl_ctrl_title = QLabel("SIMULATION CONTROL")
        lbl_ctrl_title.setStyleSheet("font-size: 11px; font-weight: bold; color: #888888;")
        right_layout.addWidget(lbl_ctrl_title)
        
        btn_layout = QHBoxLayout()
        self.btn_play = QPushButton()
        self.btn_pause = QPushButton()
        self.btn_stop = QPushButton()
        
        # Set icon pixmaps
        for btn, name, tooltip in [
            (self.btn_play, "play.svg", "Start/Resume Simulation"),
            (self.btn_pause, "pause.svg", "Pause Simulation"),
            (self.btn_stop, "stop.svg", "Restart/Clear Simulation")
        ]:
            icon_path = os.path.join(ICONS_DIR, name)
            if os.path.exists(icon_path):
                btn.setIcon(QIcon(icon_path))
                btn.setIconSize(QSize(16, 16))
            btn.setFixedSize(QSize(36, 36))
            btn.setToolTip(tooltip)
            btn_layout.addWidget(btn)
            
        self.btn_play.clicked.connect(self.play_simulation)
        self.btn_pause.clicked.connect(self.pause_simulation)
        self.btn_stop.clicked.connect(self.stop_simulation)
        
        right_layout.addLayout(btn_layout)
        
        # B. Traffic status indicators
        right_layout.addWidget(QLabel("TRAFFIC STATUS:"))
        self.lbl_traffic_status = QLabel("● Smooth Flow")
        self.lbl_traffic_status.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {COLOR_SUCCESS};")
        right_layout.addWidget(self.lbl_traffic_status)
        
        # C. Weather controller
        right_layout.addWidget(QLabel("WEATHER SYSTEM CONTROLS:"))
        self.combo_weather = QComboBox_Weather(self)
        right_layout.addWidget(self.combo_weather)
        
        self.lbl_temp = QLabel("Temp: 25.0 °C")
        self.lbl_temp.setStyleSheet("font-size: 12px; color: #CCCCCC;")
        right_layout.addWidget(self.lbl_temp)
        
        # D. Time indicator
        right_layout.addWidget(QLabel("SIMULATION CLOCK:"))
        self.lbl_time = QLabel("00:00:00")
        self.lbl_time.setStyleSheet(f"font-size: 24px; font-weight: bold; font-family: monospace; color: {COLOR_SECONDARY};")
        right_layout.addWidget(self.lbl_time)
        
        # E. Manual Event overrides
        right_layout.addStretch()
        self.btn_accident_override = QPushButton("TRIGGER ACCIDENT")
        self.btn_accident_override.setStyleSheet(f"background-color: {COLOR_DANGER}; color: white; font-weight: bold; font-size: 11px;")
        self.btn_accident_override.clicked.connect(self.trigger_manual_accident)
        right_layout.addWidget(self.btn_accident_override)
        
        top_layout.addWidget(right_panel, stretch=1)
        main_layout.addLayout(top_layout, stretch=4)
        
        # 2. BOTTOM DETAILS AREA (Event logs, notifications, statistics)
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(10)
        bottom_layout.setFixedHeight(180)
        
        # A. Scrollable event logs
        frame_logs = QFrame()
        frame_logs.setObjectName("card")
        logs_layout = QVBoxLayout(frame_logs)
        logs_layout.setContentsMargins(10, 8, 10, 8)
        
        lbl_logs_title = QLabel("EVENT LOG REGISTRY")
        lbl_logs_title.setStyleSheet("font-size: 11px; font-weight: bold; color: #888888;")
        logs_layout.addWidget(lbl_logs_title)
        
        self.list_logs = QListWidget()
        self.list_logs.setStyleSheet(f"background-color: {COLOR_BACKGROUND}; border: none; font-size: 12px; font-family: Consolas;")
        logs_layout.addWidget(self.list_logs)
        
        bottom_layout.addWidget(frame_logs, stretch=3)
        
        # B. Key metrics stats summaries
        frame_stats = QFrame()
        frame_stats.setObjectName("card")
        stats_layout = QVBoxLayout(frame_stats)
        stats_layout.setContentsMargins(10, 8, 10, 8)
        
        lbl_stats_title = QLabel("SYSTEM METRIC LOGS")
        lbl_stats_title.setStyleSheet("font-size: 11px; font-weight: bold; color: #888888;")
        stats_layout.addWidget(lbl_stats_title)
        
        self.lbl_stat_vehicles = QLabel("Active Vehicles: 0")
        self.lbl_stat_density = QLabel("Traffic Density: 0.0%")
        self.lbl_stat_speed = QLabel("Avg Velocity: 0.0 km/h")
        self.lbl_stat_fuel = QLabel("Fuel Consumed: 0.0 L")
        
        for lbl in [self.lbl_stat_vehicles, self.lbl_stat_density, self.lbl_stat_speed, self.lbl_stat_fuel]:
            lbl.setStyleSheet("font-size: 13px; color: #FFFFFF;")
            stats_layout.addWidget(lbl)
            
        stats_layout.addStretch()
        bottom_layout.addWidget(frame_stats, stretch=2)
        
        # C. Notifications board
        frame_notifications = QFrame()
        frame_notifications.setObjectName("card")
        notif_layout = QVBoxLayout(frame_notifications)
        notif_layout.setContentsMargins(10, 8, 10, 8)
        
        lbl_notif_title = QLabel("ALERTS & CRITICAL NOTIFICATIONS")
        lbl_notif_title.setStyleSheet("font-size: 11px; font-weight: bold; color: #888888;")
        notif_layout.addWidget(lbl_notif_title)
        
        self.list_notifications = QListWidget()
        self.list_notifications.setStyleSheet(f"background-color: {COLOR_BACKGROUND}; border: none; font-size: 12px; font-family: Consolas; color: {COLOR_WARNING};")
        notif_layout.addWidget(self.list_notifications)
        
        bottom_layout.addWidget(frame_notifications, stretch=3)
        
        main_layout.addLayout(bottom_layout, stretch=1)

    def play_simulation(self):
        if not self.engine.isRunning():
            self.engine.start()
            self.log_event_ui("Simulation launched successfully.", "Info")
        elif self.engine.paused:
            self.engine.toggle_pause()
            self.log_event_ui("Simulation resumed.", "Info")

    def pause_simulation(self):
        if self.engine.isRunning() and not self.engine.paused:
            self.engine.toggle_pause()
            self.log_event_ui("Simulation paused.", "Warning")

    def stop_simulation(self):
        if self.engine.isRunning():
            self.engine.stop_simulation()
            
        # Reset counters and UI
        self.engine.vehicles.clear()
        self.engine.active_accidents.clear()
        self.engine.total_fuel_consumed = 0.0
        self.engine.total_accidents = 0
        self.engine.elapsed_simulation_seconds = 0
        self.engine.init_vehicles()
        self.engine.db.clear_all_data()
        
        # Clear UI list widgets
        self.list_logs.clear()
        self.list_notifications.clear()
        self.sim_view.update()
        
        self.lbl_time.setText("00:00:00")
        self.log_event_ui("Simulation reset. Database records cleared.", "Info")

    def update_simulation_ui(self, state_dict):
        """Update simulation screen panels with ticks."""
        stats = state_dict["stats"]
        weather = state_dict["weather"]
        
        # Update map widget frame
        self.sim_view.update_frame(state_dict)
        
        # Update clock
        self.lbl_time.setText(stats["simulation_time"])
        
        # Update side stats labels
        self.lbl_stat_vehicles.setText(f"Active Vehicles: {stats['active_vehicles']}")
        self.lbl_stat_density.setText(f"Traffic Density: {stats['traffic_density']}%")
        self.lbl_stat_speed.setText(f"Avg Velocity: {stats['avg_speed']} km/h")
        self.lbl_stat_fuel.setText(f"Fuel Consumed: {stats['fuel_consumption']} L")
        self.lbl_temp.setText(f"Temp: {weather['temperature']} °C")
        
        # Update traffic density color dot indicator
        density = stats["traffic_density"]
        if density > 65.0:
            self.lbl_traffic_status.setText("● Congested Flow")
            self.lbl_traffic_status.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {COLOR_DANGER};")
        elif density > 35.0:
            self.lbl_traffic_status.setText("● Moderate Flow")
            self.lbl_traffic_status.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {COLOR_WARNING};")
        else:
            self.lbl_traffic_status.setText("● Smooth Flow")
            self.lbl_traffic_status.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {COLOR_SUCCESS};")

    def log_event_ui(self, message, severity):
        """Helper to append a log line on UI lists."""
        timestamp = time.strftime("%H:%M:%S")
        self.list_logs.addItem(f"[{timestamp}] {message}")
        self.list_logs.scrollToBottom()
        
        if severity in ["Warning", "Critical"]:
            self.list_notifications.addItem(f"[{timestamp}] ALERT: {message}")
            self.list_notifications.scrollToBottom()

    def change_weather(self, weather_str):
        self.engine.weather_mgr.set_weather(weather_str)
        self.log_event_ui(f"Weather changed to {weather_str}.", "Info")

    def trigger_manual_accident(self):
        success = self.engine.force_accident()
        if not success:
            self.log_event_ui("Override failed: No active moving vehicles to crash.", "Warning")

    def handle_incoming_event(self, event_dict):
        """Slot connected to engine's custom event dispatcher."""
        self.list_logs.addItem(f"[{event_dict['time']}] {event_dict['location']}")
        self.list_logs.scrollToBottom()
        
        if event_dict["severity"] in ["Warning", "Critical"]:
            self.list_notifications.addItem(f"[{event_dict['time']}] ALERT: {event_dict['location']}")
            self.list_notifications.scrollToBottom()


class QComboBox_Weather(QFrame):
    """Custom compact selector widget for simulation weather changes."""
    def __init__(self, parent_tab):
        super().__init__()
        self.tab = parent_tab
        self.setStyleSheet(f"background-color: {COLOR_BACKGROUND}; border: 1px solid {COLOR_BORDER}; border-radius: 4px;")
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(2)
        
        self.combo = QComboBox()
        self.combo.addItems(["Sunny", "Rain", "Storm", "Fog", "Snow"])
        self.combo.setStyleSheet("border: none; padding: 4px; color: white;")
        self.combo.currentTextChanged.connect(self.tab.change_weather)
        
        layout.addWidget(self.combo)
import time
