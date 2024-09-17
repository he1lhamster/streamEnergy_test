import os
from typing import Union, ClassVar
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # DB_HOST: Union[str | int]
    # DB_PORT: int
    # DB_NAME: str
    # DB_USER: str
    # DB_PASS: str
    # JWT_SECRET: str
    # API_TOKEN: str
    #
    # model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
    #     extra="allow",
    #     env_file='.env'
    # )
    #
    # @property
    # def DB_URL(self):
    #     return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    # DB_URL: str = os.getenv('DATABASE_URL', 'postgresql+asyncpg://user:password@localhost:5432/mydatabase')

    DB_NAME: str
    DB_USER: str
    DB_PASS: str
    DB_URL: str
    API_TOKEN: str
    FASTAPI_URL: str
    JWT_SECRET: str

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'


settings = Settings()
