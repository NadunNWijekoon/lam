import unittest
import os
import shutil
import sys

# Ensure parent directory is in python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_manager import DBManager
from simulations.traffic.traffic_engine import TrafficEngine
from simulations.ai.predictor import AIPredictor
from services.report_generator import ReportGenerator
import config

class TestSimulationPlatform(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Override database path for testing to avoid overwriting production DB
        config.DATABASE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_simulation.db")
        cls.db = DBManager()

    @classmethod
    def tearDownClass(cls):
        # Remove test database
        if os.path.exists(config.DATABASE_PATH):
            os.remove(config.DATABASE_PATH)
        # Clear test folder
        test_dir = os.path.dirname(config.DATABASE_PATH)
        
    def test_database_initialization(self):
        """Verify database tables are created correctly."""
        self.db.init_db()
        conn = self.db._get_connection()
        cursor = conn.cursor()
        
        # Query tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        self.assertIn("vehicles", tables)
        self.assertIn("events", tables)
        self.assertIn("statistics", tables)
        conn.close()

    def test_graph_pathfinding(self):
        """Verify NetworkX grid routing works between start and destination nodes."""
        engine = TrafficEngine()
        start = (0, 0)
        end = (4, 3)
        
        import networkx as nx
        path = nx.shortest_path(engine.graph, start, end, weight='weight')
        self.assertTrue(len(path) > 1)
        self.assertEqual(path[0], start)
        self.assertEqual(path[-1], end)

    def test_ai_predictor(self):
        """Verify AIPredictor returns correct regression keys."""
        predictor = AIPredictor()
        res = predictor.predict(100, "Rain", 2)
        
        self.assertIn("congestion_level", res)
        self.assertIn("congestion_pct", res)
        self.assertIn("delay_min", res)
        self.assertIn("confidence", res)
        self.assertIn("risk_pct", res)
        
        # Test values are bounded
        self.assertTrue(0 <= res["congestion_pct"] <= 100)
        self.assertTrue(0 <= res["risk_pct"] <= 100)
        self.assertTrue(50 <= res["confidence"] <= 100)

    def test_report_generation(self):
        """Verify exports generate CSV, Excel and PDF file outputs."""
        # Insert mock stats log to trigger report compiles
        self.db.log_statistics(50, 42.5, 30.0, "12:00:00")
        self.db.log_event("Accident", "Broadway segment blocked", "Critical", "12:01:00")
        
        gen = ReportGenerator()
        
        # Test CSV
        csv_path, csv_msg = gen.generate_csv("test_report.csv")
        self.assertIsNotNone(csv_path)
        self.assertTrue(os.path.exists(csv_path))
        os.remove(csv_path)
        
        # Test Excel
        xlsx_path, xlsx_msg = gen.generate_excel("test_report.xlsx")
        self.assertIsNotNone(xlsx_path)
        self.assertTrue(os.path.exists(xlsx_path))
        os.remove(xlsx_path)
        
        # Test PDF
        pdf_path, pdf_msg = gen.generate_pdf("test_report.pdf")
        self.assertIsNotNone(pdf_path)
        self.assertTrue(os.path.exists(pdf_path))
        os.remove(pdf_path)

if __name__ == "__main__":
    unittest.main()
