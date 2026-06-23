from PySide6.QtWidgets import (
    QWidget, QGridLayout, QHBoxLayout, QVBoxLayout, QLabel, QFrame, QProgressBar
)
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtCore import Qt, QSize
import os
import matplotlib
matplotlib.use("QtAgg")
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from config import (
    COLOR_BACKGROUND, COLOR_CARD_BG, COLOR_PRIMARY, COLOR_SECONDARY,
    COLOR_SUCCESS, COLOR_WARNING, COLOR_DANGER, COLOR_TEXT, ICONS_DIR
)
from simulations.ai.predictor import AIPredictor

class MplCanvas(FigureCanvas):
    """A clean dark-themed canvas for rendering embedded Matplotlib graphs."""
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        # Create figure with dark gray facecolor matching card backgrounds
        fig = Figure(figsize=(width, height), dpi=dpi, facecolor=COLOR_CARD_BG)
        self.axes = fig.add_subplot(111, facecolor=COLOR_BACKGROUND)
        
        # Configure borders and tick colors
        self.axes.spines['bottom'].set_color('#444444')
        self.axes.spines['top'].set_color('#444444')
        self.axes.spines['left'].set_color('#444444')
        self.axes.spines['right'].set_color('#444444')
        self.axes.tick_params(colors=COLOR_TEXT, labelsize=8)
        self.axes.yaxis.label.set_color(COLOR_TEXT)
        self.axes.xaxis.label.set_color(COLOR_TEXT)
        self.axes.title.set_color(COLOR_SECONDARY)
        self.axes.grid(True, color='#222222', linestyle='--')
        
        super().__init__(fig)
        self.setParent(parent)

class DashboardTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ai_predictor = AIPredictor()
        
        # Historical buffer for live charts
        self.history_limit = 30
        self.h_vehicle_count = []
        self.h_avg_speed = []
        self.h_congestion = []
        self.h_accidents = []
        
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(15)
        
        # 1. LIVE STATS CARDS LAYOUT
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(10)
        
        self.card_vehicles = self.create_stat_card("Active Vehicles", "0", "dashboard.svg", COLOR_PRIMARY)
        self.card_density = self.create_stat_card("Traffic Density", "0.0%", "traffic.svg", COLOR_SECONDARY)
        self.card_fuel = self.create_stat_card("Fuel Consumed", "0.0 L", "roads.svg", COLOR_SUCCESS)
        self.card_emergencies = self.create_stat_card("Emergencies", "0", "emergency.svg", COLOR_DANGER)
        self.card_weather = self.create_stat_card("Weather Status", "22°C, Rain", "weather.svg", COLOR_WARNING)
        
        cards_layout.addWidget(self.card_vehicles)
        cards_layout.addWidget(self.card_density)
        cards_layout.addWidget(self.card_fuel)
        cards_layout.addWidget(self.card_emergencies)
        cards_layout.addWidget(self.card_weather)
        
        main_layout.addLayout(cards_layout)

        # 2. LIVE GRAPHS LAYOUT (2x2 GRID)
        graphs_layout = QGridLayout()
        graphs_layout.setSpacing(10)
        
        self.canvas_vehicles = MplCanvas(self, width=3, height=2.2)
        self.canvas_speed = MplCanvas(self, width=3, height=2.2)
        self.canvas_congestion = MplCanvas(self, width=3, height=2.2)
        self.canvas_accidents = MplCanvas(self, width=3, height=2.2)
        
        graphs_layout.addWidget(self.canvas_vehicles, 0, 0)
        graphs_layout.addWidget(self.canvas_speed, 0, 1)
        graphs_layout.addWidget(self.canvas_congestion, 1, 0)
        graphs_layout.addWidget(self.canvas_accidents, 1, 1)
        
        main_layout.addLayout(graphs_layout)
        
        # 3. AI PREDICTIONS SCREEN PANEL
        ai_panel = QFrame()
        ai_panel.setObjectName("card")
        ai_panel.setFixedHeight(95)
        ai_layout = QHBoxLayout(ai_panel)
        ai_layout.setContentsMargins(15, 10, 15, 10)
        
        # Left Brain Icon
        self.ai_icon = QLabel()
        brain_path = os.path.join(ICONS_DIR, "ai_engine.svg")
        if os.path.exists(brain_path):
            pixmap = QPixmap(brain_path).scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.ai_icon.setPixmap(pixmap)
        else:
            self.ai_icon.setText("🧠")
            self.ai_icon.setStyleSheet("font-size: 32px;")
        ai_layout.addWidget(self.ai_icon)
        
        # Center Info
        info_layout = QVBoxLayout()
        info_layout.setAlignment(Qt.AlignCenter)
        self.lbl_prediction_title = QLabel("AI TRAFFIC PREDICTOR ENGINE")
        self.lbl_prediction_title.setStyleSheet("font-weight: bold; font-size: 14px; color: #00BCD4;")
        self.lbl_prediction_desc = QLabel("Loading smart city traffic flow telemetry predictions...")
        self.lbl_prediction_desc.setStyleSheet("font-size: 12px; color: #CCCCCC;")
        info_layout.addWidget(self.lbl_prediction_title)
        info_layout.addWidget(self.lbl_prediction_desc)
        ai_layout.addLayout(info_layout, stretch=2)
        
        # Right progress bar (Confidence)
        confidence_layout = QVBoxLayout()
        confidence_layout.setAlignment(Qt.AlignCenter)
        self.lbl_confidence = QLabel("Confidence: --%")
        self.lbl_confidence.setStyleSheet("font-size: 11px; color: #888888; text-align: right;")
        self.prog_confidence = QProgressBar()
        self.prog_confidence.setRange(0, 100)
        self.prog_confidence.setValue(0)
        self.prog_confidence.setFixedHeight(12)
        self.prog_confidence.setFixedWidth(200)
        confidence_layout.addWidget(self.lbl_confidence, alignment=Qt.AlignRight)
        confidence_layout.addWidget(self.prog_confidence)
        ai_layout.addLayout(confidence_layout)
        
        main_layout.addWidget(ai_panel)

    def create_stat_card(self, title, val, icon_name, highlight_color):
        """Creates a modern styled card representing a KPI value."""
        card = QFrame()
        card.setObjectName("card")
        card.setMinimumWidth(160)
        card.setFixedHeight(85)
        
        layout = QHBoxLayout(card)
        layout.setContentsMargins(12, 10, 12, 10)
        
        # Left Text Layout
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        
        lbl_title = QLabel(title)
        lbl_title.setStyleSheet("font-size: 11px; color: #888888; font-weight: bold; text-transform: uppercase;")
        
        lbl_value = QLabel(val)
        lbl_value.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {COLOR_TEXT};")
        
        text_layout.addWidget(lbl_title)
        text_layout.addWidget(lbl_value)
        layout.addLayout(text_layout, stretch=2)
        
        # Right Icon
        lbl_icon = QLabel()
        icon_path = os.path.join(ICONS_DIR, icon_name)
        if os.path.exists(icon_path):
            pixmap = QPixmap(icon_path).scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            # Tint icon using stylesheet colors if needed (simplified, SVGs render nicely directly)
            lbl_icon.setPixmap(pixmap)
        else:
            lbl_icon.setText("📁")
        
        lbl_icon.setFixedWidth(32)
        lbl_icon.setAlignment(Qt.AlignCenter)
        lbl_icon.setStyleSheet(f"border-left: 2px solid {highlight_color}; padding-left: 8px;")
        layout.addWidget(lbl_icon)
        
        # Save pointers to update content later
        card.lbl_value = lbl_value
        return card

    def update_dashboard(self, state_dict):
        """Updates UI components with latest simulation metrics."""
        stats = state_dict["stats"]
        weather = state_dict["weather"]
        
        # 1. Update Stats Cards values
        self.card_vehicles.lbl_value.setText(f"{stats['active_vehicles']:,}")
        self.card_density.lbl_value.setText(f"{stats['traffic_density']}%")
        self.card_fuel.lbl_value.setText(f"{stats['fuel_consumption']} L")
        self.card_emergencies.lbl_value.setText(str(stats['emergencies']))
        self.card_weather.lbl_value.setText(f"{weather['temperature']}°C, {weather['weather']}")
        
        # 2. Update buffers for charts
        self.h_vehicle_count.append(stats["active_vehicles"])
        self.h_avg_speed.append(stats["avg_speed"])
        self.h_congestion.append(stats["traffic_density"])
        self.h_accidents.append(stats["active_accidents"])
        
        # Truncate to limit size
        if len(self.h_vehicle_count) > self.history_limit:
            self.h_vehicle_count.pop(0)
            self.h_avg_speed.pop(0)
            self.h_congestion.pop(0)
            self.h_accidents.pop(0)
            
        # Draw Graphs (Only trigger plot redraws occasionally or if window is active for responsiveness)
        self.redraw_plots()
        
        # 3. Trigger AI Prediction
        pred = self.ai_predictor.predict(
            stats["active_vehicles"], 
            weather["weather"], 
            stats["active_accidents"]
        )
        
        # Format AI text message
        congestion_color = COLOR_SUCCESS
        if pred["congestion_level"] == "High":
            congestion_color = COLOR_DANGER
        elif pred["congestion_level"] == "Moderate":
            congestion_color = COLOR_WARNING
            
        self.lbl_prediction_title.setText(
            f"AI TRAFFIC ENGINE: <font color='{congestion_color}'>{pred['congestion_level']} Congestion</font> predicted in Smart City"
        )
        self.lbl_prediction_desc.setText(
            f"Est. Travel Delays: <b>{pred['delay_min']} Minutes</b> | Accident Collision Index Risk: <b>{pred['risk_pct']}%</b>"
        )
        
        self.lbl_confidence.setText(f"Confidence: {pred['confidence']}%")
        self.prog_confidence.setValue(int(pred["confidence"]))

    def redraw_plots(self):
        """Redraw lines on matplotlib canvases."""
        # 1. Vehicle Count Plot
        self.canvas_vehicles.axes.cla()
        self.canvas_vehicles.axes.grid(True, color='#222222', linestyle='--')
        self.canvas_vehicles.axes.plot(self.h_vehicle_count, color=COLOR_PRIMARY, linewidth=2)
        self.canvas_vehicles.axes.set_title("Vehicle Load Count", fontsize=9, pad=4)
        self.canvas_vehicles.axes.set_ylim(0, max(200, max(self.h_vehicle_count + [10]) * 1.2))
        self.canvas_vehicles.draw()
        
        # 2. Avg Speed Plot
        self.canvas_speed.axes.cla()
        self.canvas_speed.axes.grid(True, color='#222222', linestyle='--')
        self.canvas_speed.axes.plot(self.h_avg_speed, color=COLOR_SECONDARY, linewidth=2)
        self.canvas_speed.axes.set_title("Average Velocity (km/h)", fontsize=9, pad=4)
        self.canvas_speed.axes.set_ylim(0, 80)
        self.canvas_speed.draw()
        
        # 3. Congestion Level Plot
        self.canvas_congestion.axes.cla()
        self.canvas_congestion.axes.grid(True, color='#222222', linestyle='--')
        self.canvas_congestion.axes.plot(self.h_congestion, color=COLOR_WARNING, linewidth=2)
        self.canvas_congestion.axes.set_title("Congestion Index (%)", fontsize=9, pad=4)
        self.canvas_congestion.axes.set_ylim(0, 100)
        self.canvas_congestion.draw()
        
        # 4. Accident Frequency
        self.canvas_accidents.axes.cla()
        self.canvas_accidents.axes.grid(True, color='#222222', linestyle='--')
        self.canvas_accidents.axes.plot(self.h_accidents, color=COLOR_DANGER, linewidth=2)
        self.canvas_accidents.axes.set_title("Active Incidents / Blocks", fontsize=9, pad=4)
        self.canvas_accidents.axes.set_ylim(0, max(5, max(self.h_accidents + [1]) * 1.5))
        self.canvas_accidents.draw()
