import os

# Application Info
APP_NAME = "LAM"
TAGLINE = "Simulate Reality in Real Time"

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_DIR = os.path.join(BASE_DIR, "database")
DATABASE_PATH = os.path.join(DATABASE_DIR, "simulation.db")
EXPORTS_DIR = os.path.join(BASE_DIR, "exports")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
ICONS_DIR = os.path.join(ASSETS_DIR, "icons")
IMAGES_DIR = os.path.join(ASSETS_DIR, "images")

# Ensure required directories exist
for directory in [DATABASE_DIR, EXPORTS_DIR, ICONS_DIR, IMAGES_DIR]:
    os.makedirs(directory, exist_ok=True)

# Design Language (Theme Colors)
COLOR_PRIMARY = "#1565C0"      # Blue
COLOR_SECONDARY = "#00BCD4"    # Cyan
COLOR_SUCCESS = "#4CAF50"      # Green
COLOR_WARNING = "#FF9800"      # Orange
COLOR_DANGER = "#F44336"       # Red
COLOR_BACKGROUND = "#121212"   # Dark Gray/Black
COLOR_CARD_BG = "#1E1E1E"      # Card Dark Gray
COLOR_TEXT = "#FFFFFF"         # White
COLOR_BORDER = "#2D2D2D"       # Border Gray

# Theme Stylesheets
QSS_THEME = f"""
QMainWindow {{
    background-color: {COLOR_BACKGROUND};
}}

QWidget {{
    color: {COLOR_TEXT};
    font-family: "Segoe UI", "Outfit", "Inter", sans-serif;
    font-size: 13px;
}}

QFrame#card {{
    background-color: {COLOR_CARD_BG};
    border: 1px solid {COLOR_BORDER};
    border-radius: 8px;
}}

QFrame#sidebar {{
    background-color: {COLOR_CARD_BG};
    border-right: 1px solid {COLOR_BORDER};
}}

QLabel#title {{
    font-size: 18px;
    font-weight: bold;
    color: {COLOR_TEXT};
}}

QLabel#subtitle {{
    font-size: 12px;
    color: {COLOR_SECONDARY};
}}

QPushButton {{
    background-color: {COLOR_PRIMARY};
    color: {COLOR_TEXT};
    border: none;
    border-radius: 4px;
    padding: 8px 16px;
    font-weight: bold;
}}

QPushButton:hover {{
    background-color: #1E88E5;
}}

QPushButton:pressed {{
    background-color: #0D47A1;
}}

QPushButton#secondary_btn {{
    background-color: transparent;
    border: 1px solid {COLOR_SECONDARY};
    color: {COLOR_SECONDARY};
}}

QPushButton#secondary_btn:hover {{
    background-color: rgba(0, 188, 212, 0.1);
}}

QProgressBar {{
    border: 1px solid {COLOR_BORDER};
    border-radius: 4px;
    text-align: center;
    background-color: {COLOR_BACKGROUND};
}}

QProgressBar::chunk {{
    background-color: {COLOR_SECONDARY};
    border-radius: 3px;
}}

QListWidget {{
    background-color: {COLOR_BACKGROUND};
    border: 1px solid {COLOR_BORDER};
    border-radius: 4px;
    padding: 4px;
}}

QScrollBar:vertical {{
    border: none;
    background: {COLOR_BACKGROUND};
    width: 8px;
    margin: 0px;
}}

QScrollBar::handle:vertical {{
    background: {COLOR_BORDER};
    min-height: 20px;
    border-radius: 4px;
}}

QScrollBar::handle:vertical:hover {{
    background: {COLOR_SECONDARY};
}}
"""

# Simulation Configuration
SIMULATION_TICK_MS = 100
MAX_VEHICLES = 200

# Weather impacts on simulation
WEATHER_IMPACT = {
    "Sunny": {"speed_factor": 1.0, "accident_probability": 0.001, "congestion_factor": 1.0},
    "Rain": {"speed_factor": 0.8, "accident_probability": 0.005, "congestion_factor": 1.2},
    "Storm": {"speed_factor": 0.6, "accident_probability": 0.015, "congestion_factor": 1.5},
    "Fog": {"speed_factor": 0.5, "accident_probability": 0.020, "congestion_factor": 1.6},
    "Snow": {"speed_factor": 0.4, "accident_probability": 0.030, "congestion_factor": 1.8}
}

# Grid Layout settings (For city map generation)
GRID_COLS = 5
GRID_ROWS = 4
GRID_SPACING = 150  # Pixels between nodes
