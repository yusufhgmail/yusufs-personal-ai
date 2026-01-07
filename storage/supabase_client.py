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
"""
-- Guidelines table with version history
CREATE TABLE guidelines (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    version INTEGER NOT NULL DEFAULT 1,
    diff_from_previous TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for version lookups
CREATE INDEX idx_guidelines_version ON guidelines(version DESC);

-- Interactions table for conversation history
CREATE TABLE interactions (
    id SERIAL PRIMARY KEY,
    conversation_id TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('user', 'agent')),
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for conversation lookups
CREATE INDEX idx_interactions_conversation ON interactions(conversation_id, created_at);
"""

