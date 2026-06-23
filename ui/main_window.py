from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, 
    QStackedWidget, QLabel, QFrame, QLineEdit, QMenu
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QAction, QPixmap
import os

from config import (
    QSS_THEME, COLOR_PRIMARY, COLOR_SECONDARY, COLOR_BACKGROUND, 
    COLOR_CARD_BG, COLOR_BORDER, ICONS_DIR
)
from ui.dashboard.dashboard_tab import DashboardTab
from ui.simulations_tab import SimulationsTab
from ui.analytics.analytics_tab import AnalyticsTab
from ui.reports.reports_tab import ReportsTab
from ui.settings_tab import SettingsTab

class MainWindow(QMainWindow):
    def __init__(self, simulation_engine):
        super().__init__()
        self.engine = simulation_engine
        self.setWindowTitle("LAM — Real-Time Simulation Platform")
        self.setMinimumSize(1200, 800)
        self.setStyleSheet(QSS_THEME)
        
        self.init_ui()
        
        # Connect engine signals to updating UI tabs
        self.engine.tick_signal.connect(self.handle_simulation_tick)
        self.engine.event_signal.connect(self.tab_simulations.handle_incoming_event)

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 1. LEFT NAVIGATION SIDEBAR
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(240)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 15, 0, 15)
        sidebar_layout.setSpacing(8)
        
        # App Title & Branding
        brand_layout = QHBoxLayout()
        brand_layout.setContentsMargins(15, 0, 15, 10)
        brand_icon = QLabel()
        brand_icon.setFixedSize(30, 30)
        logo_path = os.path.join(ICONS_DIR, "ai_engine.svg")
        if os.path.exists(logo_path):
            brand_icon.setPixmap(QPixmap(logo_path).scaled(30, 30, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            brand_icon.setText("🌀")
            
        brand_text_layout = QVBoxLayout()
        brand_text_layout.setSpacing(0)
        lbl_appname = QLabel("LAM")
        lbl_appname.setStyleSheet("font-size: 20px; font-weight: bold; color: white; letter-spacing: 1px;")
        lbl_tagline = QLabel("SIMULATION ENGINE")
        lbl_tagline.setStyleSheet("font-size: 9px; color: #00BCD4; font-weight: bold;")
        brand_text_layout.addWidget(lbl_appname)
        brand_text_layout.addWidget(lbl_tagline)
        
        brand_layout.addWidget(brand_icon)
        brand_layout.addLayout(brand_text_layout)
        sidebar_layout.addLayout(brand_layout)
        
        sidebar_layout.addWidget(self.create_separator())
        
        # Navigation Buttons
        self.nav_buttons = []
        self.btn_dashboard = self.create_nav_button("Dashboard", "dashboard.svg", 0)
        self.btn_simulations = self.create_nav_button("Simulations", "simulation.svg", 1)
        self.btn_analytics = self.create_nav_button("Analytics", "statistics.svg", 2)
        self.btn_reports = self.create_nav_button("Reports", "export.svg", 3)
        self.btn_ai = self.create_nav_button("AI Prediction", "ai_engine.svg", 0) # Switches to Dashboard, focuses AI
        self.btn_settings = self.create_nav_button("Settings", "settings.svg", 4)
        
        for btn in [self.btn_dashboard, self.btn_simulations, self.btn_analytics, self.btn_reports, self.btn_ai, self.btn_settings]:
            sidebar_layout.addWidget(btn)
            self.nav_buttons.append(btn)
            
        sidebar_layout.addStretch()
        
        # Version and connection status at bottom of sidebar
        lbl_status = QLabel("● SIMULATOR ONLINE")
        lbl_status.setStyleSheet("font-size: 10px; font-weight: bold; color: #4CAF50; padding-left: 20px;")
        sidebar_layout.addWidget(lbl_status)
        
        main_layout.addWidget(sidebar)
        
        # 2. MAIN CENTER CONTENT AREA
        content_container = QWidget()
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # Top Header Bar
        top_bar = QFrame()
        top_bar.setStyleSheet(f"background-color: {COLOR_CARD_BG}; border-bottom: 1px solid {COLOR_BORDER};")
        top_bar.setFixedHeight(55)
        top_bar_layout = QHBoxLayout(top_bar)
        top_bar_layout.setContentsMargins(15, 0, 15, 0)
        
        # Left Breadcrumb path
        self.lbl_path = QLabel("LAM / Dashboard")
        self.lbl_path.setStyleSheet("font-size: 13px; font-weight: bold; color: #CCCCCC;")
        top_bar_layout.addWidget(self.lbl_path)
        
        top_bar_layout.addStretch()
        
        # Center Search
        search_edit = QLineEdit()
        search_edit.setPlaceholderText("Search simulation logs...")
        search_edit.setStyleSheet(f"background-color: {COLOR_BACKGROUND}; border: 1px solid {COLOR_BORDER}; padding: 6px 12px; border-radius: 15px; width: 200px; color: white;")
        top_bar_layout.addWidget(search_edit)
        
        # Right User profile
        profile_btn = QPushButton("Admin Operator")
        profile_btn.setObjectName("secondary_btn")
        profile_btn.setStyleSheet(f"border-radius: 15px; padding: 5px 15px; font-size: 11px; border: 1px solid {COLOR_BORDER};")
        
        menu = QMenu(self)
        menu.setStyleSheet("background-color: #1E1E1E; color: white; border: 1px solid #2D2D2D;")
        act_logout = QAction("Logout Session", self)
        act_logout.triggered.connect(self.close)
        menu.addAction(act_logout)
        profile_btn.setMenu(menu)
        
        top_bar_layout.addWidget(profile_btn)
        
        content_layout.addWidget(top_bar)
        
        # Stacked Tabs
        self.stacked_tabs = QStackedWidget()
        self.tab_dashboard = DashboardTab()
        self.tab_simulations = SimulationsTab(self.engine)
        self.tab_analytics = AnalyticsTab()
        self.tab_reports = ReportsTab()
        self.tab_settings = SettingsTab(self.engine)
        
        self.stacked_tabs.addWidget(self.tab_dashboard)   # Index 0
        self.stacked_tabs.addWidget(self.tab_simulations) # Index 1
        self.stacked_tabs.addWidget(self.tab_analytics)   # Index 2
        self.stacked_tabs.addWidget(self.tab_reports)     # Index 3
        self.stacked_tabs.addWidget(self.tab_settings)    # Index 4
        
        content_layout.addWidget(self.stacked_tabs)
        main_layout.addWidget(content_container)
        
        # Set default active navigation tab visual style
        self.set_active_navigation_visual(0)

    def create_nav_button(self, name, icon_filename, stack_idx):
        btn = QPushButton(f"  {name}")
        btn.setCheckable(True)
        btn.setIconSize(QSize(18, 18))
        btn.setStyleSheet(
            "QPushButton {"
            "  text-align: left;"
            "  background-color: transparent;"
            "  border: none;"
            "  border-left: 3px solid transparent;"
            "  color: #CCCCCC;"
            "  padding: 12px 20px;"
            "  font-weight: 500;"
            "  font-size: 13px;"
            "}"
            "QPushButton:hover {"
            "  background-color: rgba(255, 255, 255, 0.05);"
            "  color: white;"
            "}"
            "QPushButton:checked {"
            f"  background-color: rgba(0, 188, 212, 0.08);"
            f"  border-left: 3px solid {COLOR_SECONDARY};"
            "  color: white;"
            "  font-weight: bold;"
            "}"
        )
        
        icon_path = os.path.join(ICONS_DIR, icon_filename)
        if os.path.exists(icon_path):
            btn.setIcon(QIcon(icon_path))
            
        btn.clicked.connect(lambda: self.switch_tab(stack_idx, name))
        return btn

    def create_separator(self):
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet(f"background-color: {COLOR_BORDER}; max-height: 1px;")
        return line

    def switch_tab(self, idx, name):
        """Changes the stacked widget view index."""
        # Special case: AI Prediction switches to Dashboard tab and highlights the panel
        if name == "AI Prediction":
            self.stacked_tabs.setCurrentIndex(0)
            self.lbl_path.setText("LAM / Dashboard / AI Predictions")
            self.set_active_navigation_visual(0)
            # Find the AI button in nav and check it, uncheck the rest
            self.btn_ai.setChecked(True)
            return
            
        self.stacked_tabs.setCurrentIndex(idx)
        self.lbl_path.setText(f"LAM / {name}")
        self.set_active_navigation_visual(idx)

    def set_active_navigation_visual(self, active_idx):
        # Uncheck all buttons except the selected index
        mapping = {
            0: self.btn_dashboard,
            1: self.btn_simulations,
            2: self.btn_analytics,
            3: self.btn_reports,
            4: self.btn_settings
        }
        
        # Turn off auto-check exclusive to handle manual toggles
        for btn in self.nav_buttons:
            btn.setChecked(False)
            
        active_btn = mapping.get(active_idx)
        if active_btn:
            active_btn.setChecked(True)

    def handle_simulation_tick(self, state_dict):
        """Core signal handler driving the ticks updates across active tabs."""
        # 1. Update active tab to conserve CPU cycles (opt target FPS 60)
        curr_idx = self.stacked_tabs.currentIndex()
        
        if curr_idx == 0: # Dashboard tab active
            self.tab_dashboard.update_dashboard(state_dict)
        elif curr_idx == 1: # Simulation tab active
            self.tab_simulations.update_simulation_ui(state_dict)
            
    def closeEvent(self, event):
        """Shut down thread safely when window closes."""
        self.engine.stop_simulation()
        super().closeEvent(event)
