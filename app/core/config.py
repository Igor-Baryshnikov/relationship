import jwt
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: str
    DB_USER: str
    DB_PASS: str
    DB_NAME: str
    SECRET_KEY: str
    ALGORITHM: str

    @property
    def ASYNC_DATABASE_URL(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    def create_jwt_token(self, data: dict) -> str:
        return jwt.encode(data, self.SECRET_KEY, algorithm=self.ALGORITHM)

    class Config:
        env_file = ".env"


settings = Settings()
