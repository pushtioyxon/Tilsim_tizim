from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    PROJECT_NAME: str = "Tilsim Test API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # SQLite default database path
    DATABASE_URL: str = f"sqlite:///{BASE_DIR / 'tilsim.db'}"
    
    # Security
    SECRET_KEY: str = "tilsim-super-secret-key-change-in-production-12345"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # Media & Uploads
    UPLOAD_DIR: Path = BASE_DIR / "uploads"

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
