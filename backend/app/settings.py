from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    storage: str = "/data"
    cors_origins: List[str] = ["http://localhost", "http://127.0.0.1", "http://localhost:5173"]
    rife_repo: str = "/opt/rife"

settings = Settings()