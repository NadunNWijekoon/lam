import sys
import os
from PySide6.QtWidgets import QApplication
from database.db_manager import DBManager
from simulations.traffic.traffic_engine import TrafficEngine
from ui.main_window import MainWindow

def main():
    # Adjust directory context so imports and local files bind correctly
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Initialize SQLite tables
    db = DBManager()
    
    # Initialize PySide6 GUI QApplication
    app = QApplication(sys.argv)
    app.setStyle('Fusion') # Clean consistent visual rendering across Win/Mac/Linux
    
    # Initialize core background simulation engine thread
    engine = TrafficEngine()
    
    # Build and launch Main UI window
    window = MainWindow(engine)
    window.show()
    
    # Execute application main event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
