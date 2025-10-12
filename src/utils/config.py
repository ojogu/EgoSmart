from logging.config import dictConfig
import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class Config(BaseSettings):
    DATABASE_URL: str 
    Account_SID: str
    AUTH_TOKEN: str
    CLIENT_ID: str
    CLIENT_SECRET:str
    AI_KEY:str
    GEMINI_KEY: str
    GOOGLE_GENAI_USE_VERTEXAI: str
    MONO_PUBLIC_KEY:str
    MONO_SECRET_KEY:str
    ACCESS_TOKEN:str 
    PHONE_NUMBER_ID: str
    BUSINESS_ACCOUNT_ID: str
    VERIFY_TOKEN: str 
    APP_ID: str
    APP_SECRET: str
    RSA:str 
    PRIVATE_KEY_PASSWORD:str
    MODEL_NAME:str
    PUBLIC_KEY:str 
    REDIS_HOST:str
    REDIS_PORT:int 
    
    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_file=Path(__file__).resolve().parent.parent.parent / ".env",  # Adjusted to point to the root directory
        env_file_encoding="utf-8",
    )
config = Config()

class Settings:
    PROJECT_NAME: str = "egosmart"
    PROJECT_VERSION: str = "0.0.1"
    PROJECT_DESCRIPTION: str = "A whatsapp based financial system"
    
class LoggingSettings:
    @staticmethod
    def setup_logging(log_dir: str = "src/logs", default_filename: str = "app.log"):
        os.makedirs(log_dir, exist_ok=True)
        full_log_path = os.path.join(log_dir, default_filename)
        logging_config = {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                },
                "file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "formatter": "default",
                    "filename": full_log_path,
                    "maxBytes": 10485760,  # 10 MB
                    "backupCount": 5,     # Keep 5 backup files
                },
            },
            "root": {
                "level": "INFO",
                "handlers": ["console", "file"],
            },
        }

        dictConfig(logging_config)

logging_settings = LoggingSettings()