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
    
class CacheSettings(BaseSettings):
    HOST: str 
    PORT: int 
    DB: int

    model_config = SettingsConfigDict(
        env_file=".env", env_ignore_empty=True, extra="ignore", env_prefix="REDIS_"
    )

    def get_url(self) -> str:
        return f"redis://{self.HOST}:{self.PORT}/{self.DB}"
    

class SecuritySettings(BaseSettings):
    SECRET: str 
    ALGO: str
    TOKEN_EXPIRES_MINUTES: int

    model_config = SettingsConfigDict(
        env_file=".env", env_ignore_empty=True, extra="ignore", env_prefix="JWT_"
    )


class NotificationSettings(BaseSettings):
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_PORT: int
    MAIL_SERVER: str
    MAIL_FROM_NAME: str
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False
    VALIDATE_CERTS: bool = True
    
    model_config = SettingsConfigDict(
        env_file=".env", env_ignore_empty=True, extra="ignore"
    )

class TwilioSettings(BaseSettings):
    TWILIO_SID: str 
    TWILIO_AUTH_TOKEN: str
    TWILIO_NUMBER: str
    
    model_config = SettingsConfigDict(
        env_file=".env", env_ignore_empty=True, extra="ignore"
    )

class DeploymentSettings(BaseSettings):
    HOST: str 
    PORT: int 

    model_config = SettingsConfigDict(
        env_file=".env", env_ignore_empty=True, extra="ignore", env_prefix="DEPLOYMENT_"
    )

class UserVerificationSettings(BaseSettings):
    USER_VERIFY_TOKEN_SECRET: str
    EMAIL_TOKEN_SALT: str
    EMAIL_TOKEN_DURATION_MINUTES: int
    PASSWORD_TOKEN_SALT: str
    PASSWORD_TOKEN_DURATION_MINUTES: int

    model_config = SettingsConfigDict(
        env_file=".env", env_ignore_empty=True, extra="ignore"
    )

db_settings = DatabaseSettings()
cache_settings = CacheSettings()
security_settings = SecuritySettings()
notification_settings = NotificationSettings()
twilio_settings = TwilioSettings()
deployment_settings = DeploymentSettings()
user_verification_settings = UserVerificationSettings()

if __name__ == "__main__":
    print(db_settings.model_dump())
    print(db_settings.get_url())
