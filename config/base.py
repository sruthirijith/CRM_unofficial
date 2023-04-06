from pydantic import BaseSettings


class Settings(BaseSettings):
    DB_URL: str
    HOST: str
    PORT: int
    JWT_SECRET_KEY: str
    JWT_REFRESH_SECRET_KEY: str
    JWT_TOKEN_EXPIRY_DAYS : int
    ALGORITHM: str
    BASE_API_URL: str
    REFERRAL_CODE_HASH_SALT : str
    SENDGRID_API_KEY: str
    SENDGRID_EMAIL: str
    MSG_91_BASE_URL: str
    MSG_91_OTP_ENDPOINT: str
    MSG_91_RETRY_OTP_ENDPOINT: str
    MSG_91_VERIFY_OTP_ENDPOINT: str
    MSG_91_AUTH_KEY: str
    MSG_91_SENDER: str
    HASH_POLICY: str
    # PASSWORD_SALT: str
    # MONGO_CONN_STR: str
    # MONGO_DB_NAME: str

    API_KEY : str
    PROJECT_HOME: str
    TWILIO_ACCOUNT_SID: str
    TWILIO_AUTH_TOKEN: str
    TWILIO_SERVICE_ID: str
    
    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()
