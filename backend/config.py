import os
from datetime import datetime

class Config:
    """Base configuration."""
    DEBUG = False
    TESTING = False
    JSON_SORT_KEYS = False
    
    # File upload settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
    
    # SLA context (Tanzanian)
    CURRENCY = "TZS"
    SCHOOLS = ["Boma", "Kijenge", "Usa River", "Ilboru", "Sakina"]
    
    # Anomaly detection thresholds
    ANOMALY_THRESHOLD_STD = 2.5  # Flag fees > 2.5 std deviations from mean
    MIN_OUTSTANDING_DAYS = 30    # Flag outstanding payments > 30 days
    COLLECTION_RATE_ALERT = 0.80  # Flag if collection rate < 80%

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
