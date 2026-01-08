"""Application settings loaded from environment variables."""

import base64
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
    google_credentials_base64: str = Field(
        default="",
        alias="GOOGLE_CREDENTIALS_BASE64"
    )
    gmail_token_base64: str = Field(
        default="",
        alias="GMAIL_TOKEN_BASE64"
    )
    drive_token_base64: str = Field(
        default="",
        alias="DRIVE_TOKEN_BASE64"
    )
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"
    
    def get_google_credentials_path(self) -> str:
        """
        Get Google credentials path, creating from base64 if needed.
        
        This allows credentials to be provided as a base64-encoded environment
        variable for cloud deployments where file uploads are difficult.
        
        Returns:
            Path to the Google credentials JSON file
        """
        if self.google_credentials_base64:
            # Decode base64 and write to file
            creds_path = Path(self.google_credentials_path)
            creds_path.parent.mkdir(parents=True, exist_ok=True)
            try:
                creds_data = base64.b64decode(self.google_credentials_base64)
                creds_path.write_bytes(creds_data)
                print(f"Successfully decoded and created credentials file at {creds_path}")
                return str(creds_path)
            except Exception as e:
                print(f"Warning: Failed to decode base64 credentials: {e}")
                print("Falling back to file path")
        
        return self.google_credentials_path
    
    def get_token_path(self, token_name: str, base64_env_var: str) -> str:
        """
        Get token file path, creating from base64 if needed.
        
        Args:
            token_name: Name of the token file (e.g., "gmail_token.json")
            base64_env_var: The base64-encoded token content
            
        Returns:
            Path to the token JSON file
        """
        token_path = Path(f"config/{token_name}")
        
        if base64_env_var:
            # Decode base64 and write to file
            token_path.parent.mkdir(parents=True, exist_ok=True)
            try:
                token_data = base64.b64decode(base64_env_var)
                token_path.write_bytes(token_data)
                return str(token_path)
            except Exception as e:
                print(f"Warning: Failed to decode base64 token {token_name}: {e}")
        
        return str(token_path)


def get_settings() -> Settings:
    """Get application settings."""
    return Settings()

