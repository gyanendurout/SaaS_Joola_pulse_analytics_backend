import os

from pydantic_settings import BaseSettings, SettingsConfigDict

# Vercel sets VERCEL=1. Serverless instances are frozen between requests, so the
# in-process APScheduler cannot run there — Vercel Cron calls /api/cron/pipeline.
ON_VERCEL = bool(os.environ.get("VERCEL"))


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
    enable_scheduler: bool = not ON_VERCEL
    # Comma-separated allowed origins for direct browser calls.
    cors_origins: str = "http://localhost:3000,http://localhost:3001"
    # Vercel sends `Authorization: Bearer <CRON_SECRET>` on cron invocations.
    cron_secret: str = ""

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()
