from pydantic import BaseSettings, HttpUrl


class Settings(BaseSettings):
    DB_SERVICE_URL: HttpUrl = "http://localhost:8001"


settings = Settings()
