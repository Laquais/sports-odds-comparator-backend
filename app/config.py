import os
from dotenv import load_dotenv 
from pydantic_settings import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    DB_HOST_BETTING: str = os.getenv("DB_HOST_BETTING")
    DB_USER_BETTING: str = os.getenv("DB_USER_BETTING")
    DB_PASS_BETTING: str = os.getenv("DB_PASS_BETTING")
    DB_NAME_BETTING: str = os.getenv("DB_NAME_BETTING")
    DB_PORT_BETTING: str = os.getenv("DB_PORT_BETTING")

    JWT_SECRET: str = os.getenv("JWT_SECRET", "your-secret-key-change-this-in-production")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

    @property
    def database_url(self) -> str:
        return (f"postgresql+psycopg2://{self.DB_USER_BETTING}:{self.DB_PASS_BETTING}@{self.DB_HOST_BETTING}:"
                f"{self.DB_PORT_BETTING}/{self.DB_NAME_BETTING}")

    class Config:
        env_file = ".env"

settings = Settings()
