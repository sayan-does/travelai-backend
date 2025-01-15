from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Travel Planner API"
    DEBUG_MODE: bool = False
    API_VERSION: str = "1.0.0"
    MODEL_NAME: str = "Qwen/Qwen2-VL-2B-Instruct"
    HUGGING_FACE_HUB_TOKEN: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'


settings = Settings()
