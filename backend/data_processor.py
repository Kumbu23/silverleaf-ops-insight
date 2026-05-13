import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

class DataProcessor:
    """Process fee records and calculate key metrics."""
    
    def __init__(self, anomaly_threshold_std=2.5, min_outstanding_days=30):
        self.anomaly_threshold_std = anomaly_threshold_std
        self.min_outstanding_days = min_outstanding_days
    
    def load_csv(self, filepath: str) -> pd.DataFrame:
        """Load and validate CSV file."""
        try:
            df = pd.read_csv(filepath, encoding='utf-8-sig')
            # Standardize column names
            df.columns = [col.strip().lower().replace(' ', '_') for col in df.columns]
            return df
        except Exception as e:
            raise ValueError(f"Failed to load CSV: {str(e)}")
    
    def calculate_collection_metrics(self, df: pd.DataFrame) -> Dict:
        """Calculate collection rates and outstanding balances by campus."""
        if 'campus' not in df.columns or 'amount_due' not in df.columns:
            raise ValueError("CSV must contain 'campus' and 'amount_due' columns")
        
        metrics = {}
        
        # Ensure amount columns are numeric
        if 'amount_paid' in df.columns:
            df['amount_paid'] = pd.to_numeric(df['amount_paid'], errors='coerce').fillna(0)
        
        df['amount_due'] = pd.to_numeric(df['amount_due'], errors='coerce').fillna(0)
        
        for campus in df['campus'].unique():
            if pd.isna(campus):
                continue
            
            campus_data = df[df['campus'] == campus]
            total_due = campus_data['amount_due'].sum()
            
            if 'amount_paid' in df.columns:
                total_paid = campus_data['amount_paid'].sum()
                collection_rate = (total_paid / total_due * 100) if total_due > 0 else 0
                outstanding = total_due - total_paid
            else:
                total_paid = 0
                collection_rate = 0
                outstanding = total_due
            
            metrics[str(campus)] = {
                'total_due': float(total_due),
                'total_paid': float(total_paid),
                'outstanding': float(outstanding),
                'collection_rate': float(collection_rate),
                'student_count': int(len(campus_data)),
            }
        
        return metrics
    
    def detect_anomalies(self, df: pd.DataFrame) -> List[Dict]:
        """Detect anomalous fee patterns."""
        anomalies = []
        
        if 'amount_due' not in df.columns:
            return anomalies
        
        df['amount_due'] = pd.to_numeric(df['amount_due'], errors='coerce')
        df_clean = df.dropna(subset=['amount_due'])
        
        if len(df_clean) == 0:
            return anomalies
        
        mean_fee = df_clean['amount_due'].mean()
        std_fee = df_clean['amount_due'].std()
        
        # Flag fees as anomalous if they deviate significantly
        for idx, row in df.iterrows():
            if pd.isna(row['amount_due']):
                continue
            
            z_score = abs((row['amount_due'] - mean_fee) / std_fee) if std_fee > 0 else 0
            
            if z_score > self.anomaly_threshold_std:
                anomalies.append({
                    'student_id': str(row.get('student_id', 'N/A')),
                    'campus': str(row.get('campus', 'N/A')),
                    'amount_due': float(row['amount_due']),
                    'flag_reason': f"Unusual fee amount (${row['amount_due']:.0f} vs mean ${mean_fee:.0f})",
                    'severity': 'high' if z_score > self.anomaly_threshold_std * 1.5 else 'medium'
                })
        
        # Flag old outstanding payments
        if 'last_payment_date' in df.columns:
            try:
                df['last_payment_date'] = pd.to_datetime(df['last_payment_date'], errors='coerce')
                today = pd.Timestamp(datetime.now())
                
                for idx, row in df.iterrows():
                    if pd.notna(row.get('last_payment_date')) and row.get('outstanding', 0) > 0:
                        days_outstanding = (today - row['last_payment_date']).days
                        if days_outstanding > self.min_outstanding_days:
                            anomalies.append({
                                'student_id': str(row.get('student_id', 'N/A')),
                                'campus': str(row.get('campus', 'N/A')),
                                'amount_due': float(row.get('outstanding', 0)),
                                'flag_reason': f"Outstanding for {days_outstanding} days",
                                'severity': 'high' if days_outstanding > 90 else 'medium'
                            })
            except:
                pass
        
        return anomalies
    
    def generate_report(self, df: pd.DataFrame) -> Dict:
        """Generate comprehensive report."""
        metrics = self.calculate_collection_metrics(df)
        anomalies = self.detect_anomalies(df)
        
        # Calculate overall stats
        total_due = sum(m['total_due'] for m in metrics.values())
        total_paid = sum(m['total_paid'] for m in metrics.values())
        overall_collection_rate = (total_paid / total_due * 100) if total_due > 0 else 0
        
        return {
            'timestamp': datetime.now().isoformat(),
            'overall_stats': {
                'total_due': float(total_due),
                'total_paid': float(total_paid),
                'overall_outstanding': float(total_due - total_paid),
                'overall_collection_rate': float(overall_collection_rate),
                'total_students': int(len(df)),
                'campuses': len(metrics)
            },
            'by_campus': metrics,
            'anomalies': anomalies,
            'anomaly_count': len(anomalies),
            'high_severity_count': len([a for a in anomalies if a['severity'] == 'high']),
        }
