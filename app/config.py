from pydantic_settings import BaseSettings


class Settings(BaseSettings):
	DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@db:5432/wallet_db"

	model_config = {
		"extra": "allow",
		"env_file": ".env"
	}
	POSTGRES_USER: str = "postgres"
	POSTGRES_PASSWORD: str = "postgres"
	POSTGRES_DB: str = "wallet_db"

	
settings = Settings()		