"""
Configuration settings for the Gold Sentiment Analysis application
"""

import os
from typing import List

class Config:
    """Base configuration class"""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    # Redis settings
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    CACHE_EXPIRATION = int(os.environ.get('CACHE_EXPIRATION', '3600'))  # 1 hour
    
    # Analysis settings
    GOLD_QUERIES: List[str] = [
        "gold market",
        "gold price", 
        "gold news",
        "gold trends",
        "gold forecast",
        "gold investment"
    ]
    
    ARTICLES_PER_QUERY = int(os.environ.get('ARTICLES_PER_QUERY', '5'))
    MAX_WORKERS = int(os.environ.get('MAX_WORKERS', '5'))
    REQUEST_TIMEOUT = int(os.environ.get('REQUEST_TIMEOUT', '10'))
    MIN_CONTENT_LENGTH = int(os.environ.get('MIN_CONTENT_LENGTH', '100'))
    
    # AI Model settings
    FINBERT_MODEL = "yiyanghkust/finbert-tone"
    MAX_TEXT_LENGTH = 512
    
    # Performance settings
    ANALYSIS_TIMEOUT = int(os.environ.get('ANALYSIS_TIMEOUT', '60'))  # 60 seconds
    
class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    
class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    
class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    ARTICLES_PER_QUERY = 2  # Reduced for faster tests
    MAX_WORKERS = 2

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}