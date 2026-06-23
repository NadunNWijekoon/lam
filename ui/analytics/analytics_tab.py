from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGridLayout
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np

from config import COLOR_BACKGROUND, COLOR_CARD_BG, COLOR_PRIMARY, COLOR_SECONDARY, COLOR_WARNING, COLOR_DANGER, COLOR_TEXT
from database.db_manager import DBManager

class AnalyticsCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi, facecolor=COLOR_CARD_BG)
        self.axes = fig.add_subplot(111, facecolor=COLOR_BACKGROUND)
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

class AnalyticsTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = DBManager()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Header QFrame
        header = QFrame()
        header.setObjectName("card")
        header.setFixedHeight(50)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(15, 0, 15, 0)
        
        title = QLabel("Historical Analytics Command Centre")
        title.setStyleSheet("font-size: 15px; font-weight: bold; color: #FFFFFF;")
        subtitle = QLabel("Aggregate Database Logs Analysis")
        subtitle.setStyleSheet("font-size: 12px; color: #00BCD4;")
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(subtitle)
        layout.addWidget(header)
        
        # Analytics Graphs Grid (2x2)
        grid = QGridLayout()
        grid.setSpacing(10)
        
        self.canvas_trends = AnalyticsCanvas(self)
        self.canvas_distribution = AnalyticsCanvas(self)
        self.canvas_accidents = AnalyticsCanvas(self)
        self.canvas_heatmap = AnalyticsCanvas(self)
        
        grid.addWidget(self.canvas_trends, 0, 0)
        grid.addWidget(self.canvas_distribution, 0, 1)
        grid.addWidget(self.canvas_accidents, 1, 0)
        grid.addWidget(self.canvas_heatmap, 1, 1)
        
        layout.addLayout(grid)

    def showEvent(self, event):
        """Called when this tab becomes visible. Refresh data from DB."""
        super().showEvent(event)
        self.refresh_analytics()

    def refresh_analytics(self):
        """Queries statistics and formats graphs."""
        stats = self.db.get_latest_statistics(limit=300)
        events = self.db.get_all_events(limit=500)
        
        if not stats:
            # Render empty states with labels
            self._draw_empty_state()
            return
            
        times = [row["timestamp"] for row in stats]
        vehicles = [row["vehicles_count"] for row in stats]
        speeds = [row["avg_speed"] for row in stats]
        densities = [row["traffic_density"] for row in stats]
        
        # Truncate labels for cleaner ticks
        x_indices = np.linspace(0, len(times) - 1, min(5, len(times)), dtype=int)
        x_labels = [times[i] for i in x_indices]
        
        # 1. Congestion and Load Trends
        self.canvas_trends.axes.cla()
        self.canvas_trends.axes.grid(True, color='#222222', linestyle='--')
        self.canvas_trends.axes.plot(vehicles, color=COLOR_PRIMARY, label="Active Vehicles", linewidth=2)
        self.canvas_trends.axes.plot(densities, color=COLOR_SECONDARY, label="Density %", linewidth=2, linestyle="--")
        self.canvas_trends.axes.set_title("Load & Congestion Indices Over Time", fontsize=9, pad=4)
        self.canvas_trends.axes.set_xticks(x_indices)
        self.canvas_trends.axes.set_xticklabels(x_labels, rotation=15, fontsize=7)
        self.canvas_trends.axes.legend(facecolor=COLOR_CARD_BG, edgecolor='#444444', labelcolor='white', fontsize=7)
        self.canvas_trends.draw()
        
        # 2. Speed Profile Distribution (Histogram)
        self.canvas_distribution.axes.cla()
        self.canvas_distribution.axes.grid(True, color='#222222', linestyle='--')
        self.canvas_distribution.axes.hist(speeds, bins=10, color=COLOR_PRIMARY, edgecolor=COLOR_BORDER, alpha=0.8)
        self.canvas_distribution.axes.set_title("Average Speed Distribution Profile", fontsize=9, pad=4)
        self.canvas_distribution.axes.set_xlabel("Speed (km/h)", fontsize=7)
        self.canvas_distribution.axes.set_ylabel("Step Count", fontsize=7)
        self.canvas_distribution.draw()
        
        # 3. Incident Severity Bar chart
        # Count event types
        event_counts = {"Accident": 0, "Emergency": 0, "Weather Change": 0, "Clearance": 0}
        for ev in events:
            etype = ev["event_type"]
            if etype in event_counts:
                event_counts[etype] += 1
            else:
                # Merge into standard keys
                if "Accident" in etype:
                    event_counts["Accident"] += 1
                elif "Emergency" in etype:
                    event_counts["Emergency"] += 1
                elif "Clear" in etype:
                    event_counts["Clearance"] += 1
        
        categories = list(event_counts.keys())
        counts = list(event_counts.values())
        
        self.canvas_accidents.axes.cla()
        self.canvas_accidents.axes.grid(True, color='#222222', linestyle='--')
        colors_bar = [COLOR_DANGER, COLOR_WARNING, COLOR_PRIMARY, COLOR_SUCCESS]
        self.canvas_accidents.axes.bar(categories, counts, color=colors_bar, width=0.5)
        self.canvas_accidents.axes.set_title("Smart City Incident Frequencies", fontsize=9, pad=4)
        self.canvas_accidents.axes.tick_params(axis='x', labelsize=8)
        self.canvas_accidents.draw()
        
        # 4. Traffic Flow Density Heatmap (using historical data density profiles)
        self.canvas_heatmap.axes.cla()
        # Generate custom matrix mapping grid densities (synthetic representation based on counts)
        grid_data = np.zeros((4, 5))
        for d in densities[-20:]: # Average last 20 frames
            # Distribute mock values inside cells
            grid_data += np.random.uniform(0.1, 0.9, (4, 5)) * (d / 100.0)
            
        grid_data /= 20.0
        grid_data = np.clip(grid_data * 100, 0, 100)
        
        im = self.canvas_heatmap.axes.imshow(grid_data, cmap="coolwarm", interpolation="nearest", aspect="auto", vmin=0, vmax=100)
        self.canvas_heatmap.axes.set_title("Junction Load Heatmap (Grid Node Load %)", fontsize=9, pad=4)
        self.canvas_heatmap.axes.set_xticks(range(5))
        self.canvas_heatmap.axes.set_yticks(range(4))
        self.canvas_heatmap.draw()

    def _draw_empty_state(self):
        for canvas, name in [
            (self.canvas_trends, "Load Trends"),
            (self.canvas_distribution, "Speed Distribution"),
            (self.canvas_accidents, "Incident Frequencies"),
            (self.canvas_heatmap, "Junction Heatmap")
        ]:
            canvas.axes.cla()
            canvas.axes.text(0.5, 0.5, "No Simulation Logs Found.\nStart simulation to record data.",
                             color='#777777', ha='center', va='center')
            canvas.axes.set_title(name, fontsize=9)
            canvas.draw()
