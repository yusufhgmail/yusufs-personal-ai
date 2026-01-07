#!/usr/bin/env python3
"""
Check what's ready and what's missing for the Personal AI Assistant
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

def check_file(path, name, required=True):
    """Check if a file exists."""
    exists = Path(path).exists()
    status = "[OK]" if exists else ("[REQUIRED]" if required else "[OPTIONAL]")
    return exists, status

def check_env_var(name, required=True):
    """Check if an environment variable is set."""
    value = os.getenv(name)
    exists = value and value.strip() != ""
    status = "[OK]" if exists else ("[REQUIRED]" if required else "[OPTIONAL]")
    return exists, status

def check_supabase_tables():
    """Check if Supabase tables exist."""
    try:
        from supabase import create_client
        client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
        
        # Check guidelines table
        try:
            client.table("guidelines").select("id").limit(1).execute()
            guidelines_ok = True
        except:
            guidelines_ok = False
        
        # Check interactions table
        try:
            client.table("interactions").select("id").limit(1).execute()
            interactions_ok = True
        except:
            interactions_ok = False
        
        return guidelines_ok and interactions_ok
    except:
        return False

print("=" * 60)
print("Personal AI Assistant - Status Check")
print("=" * 60)
print()

# Required Configuration
print("REQUIRED CONFIGURATION:")
print("-" * 60)

openai_ok, openai_status = check_env_var("OPENAI_API_KEY")
print(f"  OpenAI API Key: {openai_status}")

supabase_url_ok, url_status = check_env_var("SUPABASE_URL")
supabase_key_ok, key_status = check_env_var("SUPABASE_KEY")
print(f"  Supabase URL: {url_status}")
print(f"  Supabase Key: {key_status}")

discord_ok, discord_status = check_env_var("DISCORD_BOT_TOKEN")
print(f"  Discord Bot Token: {discord_status}")

print()

# Database Setup
print("DATABASE SETUP:")
print("-" * 60)
if supabase_url_ok and supabase_key_ok:
    tables_ok = check_supabase_tables()
    if tables_ok:
        print("  Supabase Tables: [OK] (guidelines, interactions)")
    else:
        print("  Supabase Tables: [REQUIRED] (need to create tables)")
        print("    Run SQL from supabase_setup.sql in Supabase SQL Editor")
else:
    print("  Supabase Tables: [SKIP] (Supabase not configured)")

print()

# Optional Configuration
print("OPTIONAL CONFIGURATION (for Gmail/Drive features):")
print("-" * 60)

google_creds_ok, google_status = check_file(
    os.getenv("GOOGLE_CREDENTIALS_PATH", "config/google_credentials.json"),
    "Google Credentials",
    required=False
)
print(f"  Google Credentials: {google_status}")

if not google_creds_ok:
    print("    - Gmail features will be simulated")
    print("    - Drive features will be simulated")
    print("    - To enable: Download OAuth2 credentials from Google Cloud Console")

print()

# Discord Bot Setup
print("DISCORD BOT SETUP:")
print("-" * 60)
if discord_ok:
    print("  Bot Token: [OK]")
    print("  Message Content Intent: [CHECK MANUALLY]")
    print("    - Go to Discord Developer Portal > Bot section")
    print("    - Verify 'Message Content Intent' is enabled")
    print()
    print("  Bot Invitation: [CHECK MANUALLY]")
    print("    - Bot must be invited to your server (if using server channel)")
    print("    - Or use DMs (no invitation needed)")
else:
    print("  Bot Token: [REQUIRED]")

print()

# Overall Status
print("=" * 60)
print("OVERALL STATUS:")
print("=" * 60)

all_required = (
    openai_ok and 
    supabase_url_ok and 
    supabase_key_ok and 
    discord_ok and
    (supabase_url_ok and supabase_key_ok and check_supabase_tables())
)

if all_required:
    print("[READY] All required components are configured!")
    print()
    print("You can start the bot with:")
    print("  python main.py run")
    print()
    print("Note: Gmail/Drive features are optional and will work in")
    print("      simulation mode if Google credentials are not set up.")
else:
    print("[NOT READY] Some required components are missing.")
    print()
    print("Missing items:")
    if not openai_ok:
        print("  - OpenAI API Key")
    if not supabase_url_ok:
        print("  - Supabase URL")
    if not supabase_key_ok:
        print("  - Supabase Key")
    if not discord_ok:
        print("  - Discord Bot Token")
    if supabase_url_ok and supabase_key_ok and not check_supabase_tables():
        print("  - Supabase database tables (run SQL from supabase_setup.sql)")

print()

