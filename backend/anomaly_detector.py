import numpy as np
import pandas as pd
from typing import List, Dict
from sklearn.ensemble import IsolationForest
from datetime import datetime

class AnomalyDetector:
    """
    Advanced anomaly detection for fee patterns.
    Uses Isolation Forest + statistical methods for robust flagging.
    """
    
    def __init__(self, contamination=0.1):
        self.contamination = contamination  # Expected % of anomalies
        self.iso_forest = None
    
    def fit_and_detect(self, df: pd.DataFrame, features=['amount_due', 'days_outstanding']) -> List[int]:
        """
        Train Isolation Forest on fee data and return anomaly indices.
        """
        # Prepare feature matrix
        X = pd.DataFrame()
        
        if 'amount_due' in df.columns:
            X['amount_due'] = pd.to_numeric(df['amount_due'], errors='coerce').fillna(df['amount_due'].median())
        
        # Calculate days outstanding if payment date exists
        if 'last_payment_date' in df.columns:
            try:
                last_payment = pd.to_datetime(df['last_payment_date'], errors='coerce')
                today = pd.Timestamp(datetime.now())
                X['days_outstanding'] = (today - last_payment).dt.days.fillna(0)
            except:
                X['days_outstanding'] = 0
        
        if len(X) == 0 or X.empty:
            return []
        
        # Fit Isolation Forest
        self.iso_forest = IsolationForest(contamination=self.contamination, random_state=42)
        predictions = self.iso_forest.fit_predict(X)
        
        # Return indices where -1 (anomaly)
        return np.where(predictions == -1)[0].tolist()
    
    def get_anomaly_scores(self, df: pd.DataFrame) -> np.ndarray:
        """Get anomaly scores (higher = more anomalous)."""
        if self.iso_forest is None:
            return np.array([])
        
        X = pd.DataFrame()
        if 'amount_due' in df.columns:
            X['amount_due'] = pd.to_numeric(df['amount_due'], errors='coerce').fillna(df['amount_due'].median())
        
        if 'last_payment_date' in df.columns:
            try:
                last_payment = pd.to_datetime(df['last_payment_date'], errors='coerce')
                today = pd.Timestamp(datetime.now())
                X['days_outstanding'] = (today - last_payment).dt.days.fillna(0)
            except:
                X['days_outstanding'] = 0
        
        if X.empty:
            return np.array([])
        
        return -self.iso_forest.score_samples(X)  # Negate so higher is more anomalous
