import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from dotenv import load_dotenv
import boto3
from botocore.exceptions import ClientError

load_dotenv()

def get_ssm_parameter(name: str, region_name: str = "us-east-1") -> Optional[str]:
    try:
        ssm = boto3.client("ssm", region_name=region_name)
        response = ssm.get_parameter(Name=name, WithDecryption=True)
        return response["Parameter"]["Value"]
    except ClientError:
        return None

class Settings(BaseSettings):
    DATABASE_URL: Optional[str] = None
    TEST_DATABASE_URL: Optional[str] = None
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    AWS_REGION: Optional[str] = None
    AWS_SSM_DB_SECRET_NAME: Optional[str] = None

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def load_db_from_ssm(cls, v, info):
        env = os.getenv("ENVIRONMENT", "development")  # fallback for validator context
        if env in ("production", "staging") and not v:
            ssm_name = os.getenv("AWS_SSM_DB_SECRET_NAME")
            aws_region = os.getenv("AWS_REGION", "us-east-1")
            if ssm_name:
                val = get_ssm_parameter(ssm_name, aws_region)
                if val:
                    return val
        return v or "sqlite:///./test.db"

settings = Settings()
