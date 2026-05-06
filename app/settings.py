from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    hn_base_url: str

    class Config:
        env_file = '.env'

settings = Settings()
