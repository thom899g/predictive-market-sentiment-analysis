"""
Configuration management for Market Sentiment Analysis System.
Uses Pydantic for validation and environment variable handling.
"""
import os
from typing import Optional, List
from pydantic import BaseSettings, Field, validator
from enum import Enum
import structlog

logger = structlog.get_logger()

class Environment(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"

class Settings(BaseSettings):
    """Application settings with validation"""
    
    # Environment
    env: Environment = Environment.DEVELOPMENT
    debug: bool = Field(False, env="DEBUG")
    
    # Firebase Configuration (CRITICAL: For all database/state needs)
    firebase_credentials_path: str = Field(..., env="FIREBASE_CREDENTIALS_PATH")
    firestore_collection_prefix: str = Field("market_sentiment_", env="FIRESTORE_COLLECTION_PREFIX")
    
    # Data Collection Sources
    newsapi_api_key: Optional[str] = Field(None, env="NEWSAPI_API_KEY")
    twitter_bearer_token: Optional[str] = Field(None, env="TWITTER_BEARER_TOKEN")
    
    # Model Configuration
    model_version: str = Field("v1.0", env="MODEL_VERSION")
    prediction_confidence_threshold: float = Field(0.7, ge=0.0, le=1.0)
    
    # Processing
    batch_size: int = Field(100, gt=0)
    max_text_length: int = Field(5000, gt=0)
    
    # Logging
    log_level: str = Field("INFO", env="LOG_LEVEL")
    log_format: str = Field("json", env="LOG_FORMAT")
    
    @validator('firebase_credentials_path')
    def validate_firebase_creds(cls, v):
        """Ensure Firebase credentials file exists"""
        if not os.path.exists(v):
            logger.error("firebase_credentials_not_found", path=v)
            raise FileNotFoundError(f"Firebase credentials file not found: {v}")
        return v
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

# Singleton instance
_settings_instance = None

def get_settings() -> Settings:
    """Get or create settings singleton with error handling"""
    global _settings_instance
    try:
        if _settings_instance is None:
            _settings_instance = Settings()
            logger.info("settings_initialized", env=_settings_instance.env)
        return _settings_instance
    except Exception as e:
        logger.critical("settings_initialization_failed", error=str(e))
        raise