from pydantic_settings import BaseSettings
from functools import lru_cache
from pathlib import Path


class Settings(BaseSettings):
    # Database
    MYSQL_HOST: str
    MYSQL_PORT: int
    MYSQL_USER: str
    MYSQL_PASSWORD: str
    MYSQL_DATABASE: str

    # JWT Secret
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    # Model Settings
    MODEL_PATH: str = "../artifacts/skill_proficiency_model.pt"
    FEATURES_PATH: str = "../artifacts/student_skill_features.csv"
    ACTIVITIES_PATH: str = "../artifacts/activities.json"
    RETRAIN_INTERVAL_HOURS: int = 24  # Retrain every 24 hours

    # App Settings
    APP_NAME: str = "Skill Gap Prediction API"
    APP_VERSION: str = "1.0.0"

    @property
    def DATABASE_URL(self) -> str:
        return f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"

    @property
    def ARTIFACTS_DIR_ABSOLUTE(self) -> Path:
        """Get absolute path to artifacts directory."""
        backend_dir = Path(__file__).parent.parent
        project_root = backend_dir.parent
        return project_root / "artifacts"

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings():
    return Settings()
