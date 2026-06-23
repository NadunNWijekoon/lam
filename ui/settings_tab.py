from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton, QSlider, QMessageBox
)
from PySide6.QtCore import Qt
from config import COLOR_BACKGROUND, COLOR_CARD_BG, COLOR_PRIMARY, COLOR_SECONDARY, COLOR_DANGER, COLOR_BORDER, MAX_VEHICLES
from database.db_manager import DBManager

class SettingsTab(QWidget):
    def __init__(self, simulation_engine, parent=None):
        super().__init__(parent)
        self.engine = simulation_engine
        self.db = DBManager()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)
        
        # 1. Header Card
        header = QFrame()
        header.setObjectName("card")
        header.setFixedHeight(50)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(15, 0, 15, 0)
        
        title = QLabel("Simulation Global Settings Panel")
        title.setStyleSheet("font-size: 15px; font-weight: bold; color: #FFFFFF;")
        subtitle = QLabel("Configure System Constraints")
        subtitle.setStyleSheet("font-size: 12px; color: #00BCD4;")
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(subtitle)
        layout.addWidget(header)
        
        # 2. Main Config Card
        cfg_panel = QFrame()
        cfg_panel.setObjectName("card")
        cfg_layout = QVBoxLayout(cfg_panel)
        cfg_layout.setContentsMargins(20, 20, 20, 20)
        cfg_layout.setSpacing(15)
        
        # Spawn Limit Slider
        cfg_layout.addWidget(QLabel("Maximum Spawned Vehicle Limit:"))
        slider_layout = QHBoxLayout()
        self.slider_vehicles = QSlider(Qt.Horizontal)
        self.slider_vehicles.setRange(10, 250)
        self.slider_vehicles.setValue(MAX_VEHICLES)
        self.slider_vehicles.setStyleSheet("height: 25px;")
        
        self.lbl_slider_val = QLabel(str(self.slider_vehicles.value()))
        self.lbl_slider_val.setFixedWidth(30)
        self.lbl_slider_val.setStyleSheet("font-weight: bold; color: #00BCD4;")
        
        self.slider_vehicles.valueChanged.connect(self.update_vehicle_limit)
        
        slider_layout.addWidget(self.slider_vehicles)
        slider_layout.addWidget(self.lbl_slider_val)
        cfg_layout.addLayout(slider_layout)
        
        # Database wipe button
        cfg_layout.addWidget(QLabel("Database Administrative Actions:"))
        self.btn_clear_db = QPushButton("CLEAR LOGS DATABASE RECORDS")
        self.btn_clear_db.setStyleSheet(f"background-color: {COLOR_DANGER}; color: white; padding: 10px; font-weight: bold;")
        self.btn_clear_db.clicked.connect(self.wipe_database)
        cfg_layout.addWidget(self.btn_clear_db)
        
        # Description
        desc = QLabel(
            "<b>Performance Target Metrics Checklist:</b><br/>"
            "• Average Refresh updates frequency: 100ms ticks.<br/>"
            "• Rendering capability bounds: supports up to 10,000+ total vehicles paths calculated.<br/>"
            "• Peak memory allocation thresholds: &lt; 2.0 Gigabytes memory workspace limit.<br/>"
            "• Fast bootstrap configuration: &lt; 5.0 seconds initialization cycle."
        )
        desc.setStyleSheet("color: #888888; font-size: 12px; line-height: 1.5;")
        cfg_layout.addWidget(desc)
        
        cfg_layout.addStretch()
        layout.addWidget(cfg_panel)

    def update_vehicle_limit(self, val):
        self.lbl_slider_val.setText(str(val))
        # Globally modify max limits (simplified, directly override on active engine instance)
        import config
        config.MAX_VEHICLES = val
        self.engine.spawn_vehicle() # force recalculate spawn loop trigger if active

    def wipe_database(self):
        reply = QMessageBox.question(
            self, "Confirm Reset", 
            "Are you absolutely sure you want to delete all historical telemetry statistics logs from the database?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.db.clear_all_data()
            QMessageBox.information(self, "Success", "Database has been cleared successfully.")
