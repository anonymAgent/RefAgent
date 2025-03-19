from pydantic import BaseSettings

class Settings(BaseSettings):
    API_KEY: str
    GITHUB_API_KEY: str
    MODEL_NAME: str


    class Config:
        env_file = ".env"

# Usage
settings = Settings()
print(settings.DATABASE_URL)
print(settings.API_KEY)
