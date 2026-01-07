"""Application settings loaded from environment variables."""

import os
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings."""
    
    # LLM Configuration
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    anthropic_api_key: str = Field(default="", alias="ANTHROPIC_API_KEY")
    llm_provider: str = Field(default="openai", alias="LLM_PROVIDER")
    llm_model: str = Field(default="gpt-4o", alias="LLM_MODEL")
    
    # Supabase Configuration
    supabase_url: str = Field(default="", alias="SUPABASE_URL")
    supabase_key: str = Field(default="", alias="SUPABASE_KEY")
    
    # Discord Configuration
    discord_bot_token: str = Field(default="", alias="DISCORD_BOT_TOKEN")
    discord_channel_id: str = Field(default="", alias="DISCORD_CHANNEL_ID")
    
    # Google API Configuration
    google_credentials_path: str = Field(
        default="config/google_credentials.json", 
        alias="GOOGLE_CREDENTIALS_PATH"
    )
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


def get_settings() -> Settings:
    """Get application settings."""
    return Settings()

