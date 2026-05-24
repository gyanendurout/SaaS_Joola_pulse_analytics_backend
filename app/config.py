from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    supabase_url: str
    supabase_service_role_key: str
    openai_api_key: str
    openai_model_fast: str = "gpt-4o-mini"
    openai_model_smart: str = "gpt-4o"
    port: int = 8001
    app_env: str = "local"
    joola_brand_id: str = "04db8591-37a3-4634-9d11-536975fa6935"
    poll_interval_minutes: int = 15
    enable_scheduler: bool = True


settings = Settings()
