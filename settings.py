from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    API_KEY: str
    GITHUB_API_KEY: str
    MODEL_NAME: str


    class Config:
        env_file = ".env"
