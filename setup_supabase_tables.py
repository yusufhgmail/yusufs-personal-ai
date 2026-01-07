#!/usr/bin/env python3
"""
Script to set up Supabase database tables.
This will create the SQL file and provide instructions.
"""

from pathlib import Path

# SQL from storage/supabase_client.py
SQL = """
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

def main():
    print("=" * 60)
    print("Supabase Database Setup")
    print("=" * 60)
    print()
    
    # Save SQL to file
    sql_file = Path("supabase_setup.sql")
    sql_file.write_text(SQL.strip())
    print(f"[OK] SQL saved to: {sql_file.absolute()}")
    print()
    
    print("Next steps:")
    print("1. Go to https://supabase.com/dashboard")
    print("2. Select your project: 'Yusuf's Personal AI yai26'")
    print("3. Go to SQL Editor (left sidebar)")
    print("4. Click 'New query'")
    print("5. Copy and paste the SQL from supabase_setup.sql")
    print("6. Click 'Run' (or press Ctrl+Enter)")
    print()
    print("Or you can copy this SQL directly:")
    print("-" * 60)
    print(SQL.strip())
    print("-" * 60)
    print()
    print("After running the SQL, the database will be ready!")

if __name__ == "__main__":
    main()

