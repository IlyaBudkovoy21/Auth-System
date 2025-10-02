from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    sync_database_url: str

    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    celery_broker_url: str
    celery_result_backend: str

    rabbitmq_url: str

    redis_url: str

    smtp_server: str
    smtp_port: int
    smtp_username: str
    smtp_password: str

    debug: bool = False
    allowed_hosts: List[str] = ["localhost", "127.0.0.1"]

    class Config:
        env_file = ".env"


settings = Settings()
