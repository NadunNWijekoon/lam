from datetime import datetime

class Event:
    def __init__(self, event_id, event_type, location, severity="Info", timestamp=None):
        self.id = event_id
        self.event_type = event_type  # e.g., "Accident", "Ambulance Dispatched", "Weather Change", "Road Closed"
        self.location = location      # e.g., "Main St & 3rd Ave"
        self.severity = severity      # "Info", "Warning", "Critical"
        self.timestamp = timestamp if timestamp else datetime.now().strftime("%H:%M:%S")

    def to_dict(self):
        return {
            "id": self.id,
            "event_type": self.event_type,
            "location": self.location,
            "severity": self.severity,
            "time": self.timestamp
        }
