from pydantic_settings import BaseSettings, SettingsConfigDict

class DatabaseSettings(BaseSettings):
    HOST: str
    PORT: int
    USER: str
    PASSWORD: str
    DB: str

    model_config = SettingsConfigDict(
        env_file=".env", env_ignore_empty=True, extra="ignore", env_prefix="POSTGRES_"
    )

    def get_url(self) -> str:
        return f"postgresql+asyncpg://{self.USER}:{self.PASSWORD}@{self.HOST}:{self.PORT}/{self.DB}"


db_settings = DatabaseSettings()

if __name__ == "__main__":
    print(db_settings.model_dump())
    print(db_settings.get_url())
