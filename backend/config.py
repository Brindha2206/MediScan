import os

class Config:
    """Configuration settings for MediScan"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'mediscan-dev-key-2024'
    DEBUG = True
    CORS_ORIGINS = ["http://localhost:8000", "http://127.0.0.1:8000"]