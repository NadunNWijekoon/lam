import sqlite3
import os
import threading
from config import DATABASE_PATH

class DBManager:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if not cls._instance:
                cls._instance = super(DBManager, cls).__new__(cls, *args, **kwargs)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self.db_path = DATABASE_PATH
        self.init_db()
        self._initialized = True

    def _get_connection(self):
        """Returns a sqlite3 connection for the current thread."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        """Initializes database tables if they do not exist."""
        # Ensure parent folder exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Vehicles table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vehicles (
                id TEXT PRIMARY KEY,
                type TEXT NOT NULL,
                speed REAL NOT NULL,
                fuel REAL NOT NULL,
                status TEXT NOT NULL,
                position_x REAL NOT NULL,
                position_y REAL NOT NULL,
                destination_x REAL NOT NULL,
                destination_y REAL NOT NULL
            )
        """)
        
        # Events table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                location TEXT NOT NULL,
                time TEXT NOT NULL,
                severity TEXT NOT NULL
            )
        """)
        
        # Statistics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS statistics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vehicles_count INTEGER NOT NULL,
                avg_speed REAL NOT NULL,
                traffic_density REAL NOT NULL,
                timestamp TEXT NOT NULL
            )
        """)
        
        conn.commit()
        conn.close()

    def log_vehicles(self, vehicles_list):
        """Inserts or replaces vehicle telemetry in the database."""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM vehicles")  # Keep only active vehicles current state
            for v in vehicles_list:
                cursor.execute("""
                    INSERT OR REPLACE INTO vehicles (
                        id, type, speed, fuel, status, 
                        position_x, position_y, destination_x, destination_y
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    v["id"], v["type"], v["speed"], v["fuel"], v["status"],
                    v["position_x"], v["position_y"], v["destination_x"], v["destination_y"]
                ))
            conn.commit()
        except sqlite3.Error as e:
            print(f"Database error in log_vehicles: {e}")
        finally:
            conn.close()

    def log_event(self, event_type, location, severity, time_str):
        """Logs a simulation event."""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO events (event_type, location, time, severity)
                VALUES (?, ?, ?, ?)
            """, (event_type, location, time_str, severity))
            conn.commit()
        except sqlite3.Error as e:
            print(f"Database error in log_event: {e}")
        finally:
            conn.close()

    def log_statistics(self, vehicles_count, avg_speed, traffic_density, timestamp):
        """Logs aggregated statistics for trend analysis."""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO statistics (vehicles_count, avg_speed, traffic_density, timestamp)
                VALUES (?, ?, ?, ?)
            """, (vehicles_count, avg_speed, traffic_density, timestamp))
            conn.commit()
        except sqlite3.Error as e:
            print(f"Database error in log_statistics: {e}")
        finally:
            conn.close()

    def get_latest_statistics(self, limit=100):
        """Retrieves history of statistics for graphing."""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT vehicles_count, avg_speed, traffic_density, timestamp 
                FROM statistics 
                ORDER BY id DESC LIMIT ?
            """, (limit,))
            rows = cursor.fetchall()
            return [dict(row) for row in reversed(rows)]
        except sqlite3.Error as e:
            print(f"Database error in get_latest_statistics: {e}")
            return []
        finally:
            conn.close()

    def get_all_events(self, limit=100):
        """Retrieves logged events."""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT event_type, location, time, severity 
                FROM events 
                ORDER BY id DESC LIMIT ?
            """, (limit,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            print(f"Database error in get_all_events: {e}")
            return []
        finally:
            conn.close()

    def clear_all_data(self):
        """Clears the database log tables."""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM vehicles")
            cursor.execute("DELETE FROM events")
            cursor.execute("DELETE FROM statistics")
            conn.commit()
        except sqlite3.Error as e:
            print(f"Database error in clear_all_data: {e}")
        finally:
            conn.close()
