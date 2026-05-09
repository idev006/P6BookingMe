from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

# Base Path Management (Strictly Portable)
# backend/ folder path
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Centralized Directory Definitions
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
UPLOADS_DIR = BASE_DIR / "uploads"

# Ensure essential directories exist
for directory in [DATA_DIR, LOGS_DIR, UPLOADS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    PROJECT_NAME: str = "P6BookingMe"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"

    # Database
    DATABASE_URL: str = f"sqlite+aiosqlite:///{DATA_DIR.as_posix()}/bookingme.db"
    
    # Paths (Exported for other modules to use)
    BASE_DIR: Path = BASE_DIR
    DATA_DIR: Path = DATA_DIR
    LOGS_DIR: Path = LOGS_DIR
    UPLOADS_DIR: Path = UPLOADS_DIR

    # CORS — frontend dev server
    ALLOWED_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:5174", "http://localhost:3000"]

    # JWT
    SECRET_KEY: str = "change-this-secret-key-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 8  # 8 hours
    
    # Uploads
    MAX_UPLOAD_SIZE: int = 5 * 1024 * 1024  # 5MB
    ALLOWED_IMAGE_TYPES: list[str] = ["image/jpeg", "image/png", "image/webp"]


settings = Settings()
