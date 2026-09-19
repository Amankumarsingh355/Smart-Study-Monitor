import os
from pydantic import BaseModel


class BackendConfig(BaseModel):
    app_name: str = "Smart Study Monitor API"
    version: str = "1.0.0"
    api_v1_prefix: str = "/api/v1"
    db_path: str = os.getenv("SSM_DB_PATH", "data/study_monitor.db")
    cors_origins: list[str] = ["*"]
    host: str = "127.0.0.1"
    port: int = 8000


backend_config = BackendConfig()
