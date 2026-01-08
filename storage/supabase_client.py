"""Supabase database client."""

from supabase import create_client, Client
from config.settings import get_settings


_client: Client | None = None


def get_supabase_client() -> Client:
    """Get or create Supabase client singleton."""
    global _client
    if _client is None:
        settings = get_settings()
        _client = create_client(settings.supabase_url, settings.supabase_key)
    return _client


# SQL for creating tables (run in Supabase SQL editor):
# See supabase_setup.sql for the complete schema including llm_logs table

