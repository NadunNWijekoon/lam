from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton, 
    QComboBox, QCheckBox, QListWidget, QFileDialog
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QPixmap
import os
import subprocess

from config import (
    COLOR_BACKGROUND, COLOR_CARD_BG, COLOR_PRIMARY, COLOR_SECONDARY,
    COLOR_SUCCESS, COLOR_WARNING, COLOR_DANGER, COLOR_BORDER, EXPORTS_DIR, ICONS_DIR
)
from services.report_generator import ReportGenerator

class ReportsTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.report_gen = ReportGenerator()
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
        
        title = QLabel("Simulation Report Export Centre")
        title.setStyleSheet("font-size: 15px; font-weight: bold; color: #FFFFFF;")
        subtitle = QLabel("Generate Compliance Documents")
        subtitle.setStyleSheet("font-size: 12px; color: #00BCD4;")
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(subtitle)
        layout.addWidget(header)
        
        # 2. Main Body (Config on left, Actions on right)
        body_layout = QHBoxLayout()
        body_layout.setSpacing(15)
        
        # LEFT CONFIG CARD
        cfg_panel = QFrame()
        cfg_panel.setObjectName("card")
        cfg_layout = QVBoxLayout(cfg_panel)
        cfg_layout.setContentsMargins(15, 15, 15, 15)
        cfg_layout.setSpacing(12)
        
        lbl_cfg_title = QLabel("Report Parameters")
        lbl_cfg_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #FFFFFF; border-bottom: 1px solid #333333; padding-bottom: 5px;")
        cfg_layout.addWidget(lbl_cfg_title)
        
        # Select Report Type
        cfg_layout.addWidget(QLabel("Select Report Category:"))
        self.combo_type = QComboBox()
        self.combo_type.addItems(["Daily Summary Report", "Traffic Flow Analysis", "Accident & Incident Log", "Full System Telemetry"])
        self.combo_type.setStyleSheet(f"background-color: {COLOR_BACKGROUND}; border: 1px solid {COLOR_BORDER}; padding: 6px; border-radius: 4px; color: white;")
        cfg_layout.addWidget(self.combo_type)
        
        # Select Time range
        cfg_layout.addWidget(QLabel("Simulation Timeline Scope:"))
        self.combo_scope = QComboBox()
        self.combo_scope.addItems(["Current Run Session", "Last 1 Hour Logs", "Last 24 Hours Logs", "All Database Entries"])
        self.combo_scope.setStyleSheet(f"background-color: {COLOR_BACKGROUND}; border: 1px solid {COLOR_BORDER}; padding: 6px; border-radius: 4px; color: white;")
        cfg_layout.addWidget(self.combo_scope)
        
        # Include sections checkboxes
        cfg_layout.addWidget(QLabel("Include Attachments:"))
        self.chk_charts = QCheckBox("Generate Trends Charts Graph Plots")
        self.chk_charts.setChecked(True)
        self.chk_ai = QCheckBox("Include AI Delay Congestion Predictions")
        self.chk_ai.setChecked(True)
        self.chk_recommendations = QCheckBox("Include Optimization Recommendations")
        self.chk_recommendations.setChecked(True)
        
        for chk in [self.chk_charts, self.chk_ai, self.chk_recommendations]:
            chk.setStyleSheet("color: #CCCCCC; font-size: 12px;")
            cfg_layout.addWidget(chk)
            
        cfg_layout.addStretch()
        body_layout.addWidget(cfg_panel, stretch=3)
        
        # RIGHT ACTIONS CARD
        actions_panel = QFrame()
        actions_panel.setObjectName("card")
        actions_layout = QVBoxLayout(actions_panel)
        actions_layout.setContentsMargins(15, 15, 15, 15)
        actions_layout.setSpacing(15)
        
        lbl_act_title = QLabel("Generate Compliance Exports")
        lbl_act_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #FFFFFF; border-bottom: 1px solid #333333; padding-bottom: 5px;")
        actions_layout.addWidget(lbl_act_title)
        
        # PDF BUTTON
        self.btn_pdf = QPushButton("EXPORT PDF COMPLIANCE REPORT")
        self.btn_pdf.setStyleSheet(f"background-color: {COLOR_DANGER}; color: white; padding: 10px; font-weight: bold;")
        self.btn_pdf.clicked.connect(self.export_pdf)
        actions_layout.addWidget(self.btn_pdf)
        
        # EXCEL BUTTON
        self.btn_excel = QPushButton("EXPORT EXCEL WORKSHEET")
        self.btn_excel.setStyleSheet(f"background-color: {COLOR_SUCCESS}; color: white; padding: 10px; font-weight: bold;")
        self.btn_excel.clicked.connect(self.export_excel)
        actions_layout.addWidget(self.btn_excel)
        
        # CSV BUTTON
        self.btn_csv = QPushButton("EXPORT RAW DATA CSV")
        self.btn_csv.setStyleSheet(f"background-color: {COLOR_PRIMARY}; color: white; padding: 10px; font-weight: bold;")
        self.btn_csv.clicked.connect(self.export_csv)
        actions_layout.addWidget(self.btn_csv)
        
        # Logging scroll
        actions_layout.addWidget(QLabel("Output Log Console:"))
        self.log_list = QListWidget()
        self.log_list.setStyleSheet(f"background-color: {COLOR_BACKGROUND}; border: 1px solid {COLOR_BORDER}; font-family: Consolas; font-size: 11px;")
        actions_layout.addWidget(self.log_list)
        
        body_layout.addWidget(actions_panel, stretch=4)
        layout.addLayout(body_layout)

    def log_message(self, message):
        """Append operational steps to log box."""
        self.log_list.addItem(f"[{os.path.basename(message)}]")
        self.log_list.scrollToBottom()

    def export_pdf(self):
        self.log_list.addItem("Starting PDF compilation engine...")
        filename = f"LAM_Report_{self.combo_type.currentText().replace(' ', '_')}_{self.combo_scope.currentText().replace(' ', '_')}.pdf"
        filepath, msg = self.report_gen.generate_pdf(filename)
        
        if filepath:
            self.log_list.addItem(f"SUCCESS: PDF created at: {filepath}")
            self.log_list.addItem("Double-click list item to open file.")
            # Auto-launch file viewer on system
            try:
                os.startfile(filepath)
            except:
                pass
        else:
            self.log_list.addItem(f"ERROR: {msg}")

    def export_excel(self):
        self.log_list.addItem("Generating styled spreadsheet tabs...")
        filename = f"LAM_Report_{self.combo_type.currentText().replace(' ', '_')}_{self.combo_scope.currentText().replace(' ', '_')}.xlsx"
        filepath, msg = self.report_gen.generate_excel(filename)
        
        if filepath:
            self.log_list.addItem(f"SUCCESS: Excel worksheet at: {filepath}")
            try:
                os.startfile(filepath)
            except:
                pass
        else:
            self.log_list.addItem(f"ERROR: {msg}")

    def export_csv(self):
        self.log_list.addItem("Writing raw data vectors to CSV...")
        filename = f"LAM_Report_{self.combo_type.currentText().replace(' ', '_')}_{self.combo_scope.currentText().replace(' ', '_')}.csv"
        filepath, msg = self.report_gen.generate_csv(filename)
        
        if filepath:
            self.log_list.addItem(f"SUCCESS: CSV saved at: {filepath}")
            try:
                os.startfile(filepath)
            except:
                pass
        else:
            self.log_list.addItem(f"ERROR: {msg}")
