import secrets
from typing import List, Union, Optional

from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    PROJECT_NAME: str = "Full Stack FastAPI DocumentDB"
    VERSION: str = "1.0.0"
    
    # CORS settings
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # DocumentDB settings
    DOCUMENTDB_CONNECTION_STRING: Optional[str] = None
    DOCUMENTDB_DATABASE_NAME: str = "fastapi_db"
    
    # Development settings
    DEBUG: bool = False

    model_config = {
        "case_sensitive": True,
        "env_file": ".env",
    }


settings = Settings()