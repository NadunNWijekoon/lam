import numpy as np
from sklearn.ensemble import RandomForestRegressor
import time

class AIPredictor:
    def __init__(self):
        self.rf_congestion = RandomForestRegressor(n_estimators=10, random_state=42)
        self.rf_risk = RandomForestRegressor(n_estimators=10, random_state=42)
        self.rf_delay = RandomForestRegressor(n_estimators=10, random_state=42)
        
        self.weather_mapping = {
            "Sunny": 1.0,
            "Rain": 2.0,
            "Storm": 3.0,
            "Fog": 4.0,
            "Snow": 5.0
        }
        
        self.is_trained = False
        self.train_on_synthetic_data()

    def train_on_synthetic_data(self):
        """Generates mock training data and fits the Random Forest Regressors."""
        np.random.seed(42)
        samples = 300
        
        # Features: [active_vehicles, weather_index, active_accidents]
        X = []
        y_congestion = []
        y_risk = []
        y_delay = []
        
        for _ in range(samples):
            vehicles = np.random.randint(10, 200)
            weather_idx = np.random.randint(1, 6) # 1 to 5
            accidents = np.random.randint(0, 5)
            
            # Formulate targets
            # Congestion index (0 - 100%)
            cong = (vehicles * 0.3) + (weather_idx * 6.0) + (accidents * 12.0) + np.random.normal(0, 3.0)
            cong = max(5.0, min(98.0, cong))
            
            # Accident risk (0 - 100%)
            risk = (vehicles * 0.15) + (weather_idx * 11.0) + (accidents * 8.0) + np.random.normal(0, 4.0)
            risk = max(2.0, min(99.0, risk))
            
            # Delay in minutes (0 - 45 mins)
            delay = (cong * 0.25) + (accidents * 4.0) + np.random.normal(0, 1.0)
            delay = max(0.0, min(60.0, delay))
            
            X.append([vehicles, weather_idx, accidents])
            y_congestion.append(cong)
            y_risk.append(risk)
            y_delay.append(delay)
            
        X = np.array(X)
        self.rf_congestion.fit(X, y_congestion)
        self.rf_risk.fit(X, y_risk)
        self.rf_delay.fit(X, y_delay)
        
        self.is_trained = True

    def predict(self, active_vehicles, weather_str, active_accidents):
        """Runs the RF models to estimate metrics."""
        if not self.is_trained:
            return {"congestion_level": "Smooth", "delay_min": 0, "confidence": 90, "risk_pct": 5}
            
        weather_idx = self.weather_mapping.get(weather_str, 1.0)
        input_data = np.array([[active_vehicles, weather_idx, active_accidents]])
        
        pred_congestion = self.rf_congestion.predict(input_data)[0]
        pred_risk = self.rf_risk.predict(input_data)[0]
        pred_delay = self.rf_delay.predict(input_data)[0]
        
        # Categorize Congestion
        if pred_congestion > 70.0:
            cong_level = "High"
        elif pred_congestion > 40.0:
            cong_level = "Moderate"
        else:
            cong_level = "Smooth"
            
        # Confidence calculation (dynamic formula representing model confidence based on bounds)
        confidence = 95.0 - (active_accidents * 2.5) - (weather_idx * 1.5)
        confidence = max(60.0, min(98.0, confidence + np.random.uniform(-1, 1)))
        
        return {
            "congestion_level": cong_level,
            "congestion_pct": round(pred_congestion, 1),
            "delay_min": int(round(pred_delay)),
            "confidence": round(confidence, 1),
            "risk_pct": round(pred_risk, 1)
        }
