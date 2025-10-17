from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
import os
from dotenv import load_dotenv

load_dotenv()
class Config(BaseSettings):
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    DATABASE_SESSION_URL: str = os.getenv("DATABASE_SESSION_URL")

    # Twilio/Similar Service (Assuming Account_SID/AUTH_TOKEN)
    Account_SID: str = os.getenv("Account_SID")
    AUTH_TOKEN: str = os.getenv("AUTH_TOKEN")
    
    # OAuth/External Service Credentials
    CLIENT_ID: str = os.getenv("CLIENT_ID")
    CLIENT_SECRET: str = os.getenv("CLIENT_SECRET")
    ACCESS_TOKEN: str = os.getenv("ACCESS_TOKEN") # Generic access token

    # AI/ML Keys
    AI_KEY: str = os.getenv("AI_KEY")
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY")
    GOOGLE_GENAI_USE_VERTEXAI: str = os.getenv("GOOGLE_GENAI_USE_VERTEXAI") # Could be 'true' or 'false'
    MODEL_NAME: str = os.getenv("MODEL_NAME")

    # Payment/Fintech Keys (e.g., Mono)
    MONO_TEST_PUBLIC_KEY: str = os.getenv("MONO_PUBLIC_KEY")
    MONO_TEST_SECRET_KEY: str = os.getenv("MONO_SECRET_KEY")
    
    #LIVE_KEYS
    MONO_LIVE_PUBLIC_KEY: str = os.getenv("MONO_PUBLIC_KEY")
    MONO_LIVE_SECRET_KEY: str = os.getenv("MONO_SECRET_KEY")
    BASE_URL: str = os.getenv("BASE_URL")

    # Messaging/Platform (e.g., WhatsApp/Meta)
    PHONE_NUMBER_ID: str = os.getenv("PHONE_NUMBER_ID")
    BUSINESS_ACCOUNT_ID: str = os.getenv("BUSINESS_ACCOUNT_ID")
    VERIFY_TOKEN: str = os.getenv("VERIFY_TOKEN")
    APP_ID: str = os.getenv("APP_ID")
    APP_SECRET: str = os.getenv("APP_SECRET")

    # Cryptography/Keys
    RSA: str = os.getenv("RSA") # Could be the path to a key or the key itself
    PRIVATE_KEY_PASSWORD: str = os.getenv("PRIVATE_KEY_PASSWORD")
    PUBLIC_KEY: str = os.getenv("PUBLIC_KEY")
    
    REDIRECT_URL: str = os.getenv("REDIRECT_URL")

    # Caching/Redis
    REDIS_HOST: str = os.getenv("REDIS_HOST")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", 6379)) # Cast to int, provide default if not set
    
    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_file=Path(__file__).resolve().parent.parent.parent / ".env",  # Adjusted to point to the root directory
        env_file_encoding="utf-8",
    )
config = Config()

class Settings:
    PROJECT_NAME: str = "Ègòsmart"
    PROJECT_VERSION: str = "0.0.1"
    PROJECT_DESCRIPTION: str = "A whatsapp based financial system"
    
setting=Settings()