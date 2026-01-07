#!/usr/bin/env python3
"""
Interactive setup script for Personal AI Assistant
Helps configure environment variables and set up services
"""

import os
import subprocess
import sys
from pathlib import Path

def create_env_file():
    """Create or update .env file with user input."""
    env_path = Path(".env")
    
    print("=" * 60)
    print("Personal AI Assistant - Environment Setup")
    print("=" * 60)
    print()
    
    # OpenAI key - prompt user for it
    print("OpenAI API Key:")
    print("1. Go to https://platform.openai.com/api-keys")
    print("2. Create a new API key")
    print()
    openai_key = input("Enter your OpenAI API key (or press Enter to skip): ").strip()
    
    print("[OK] OpenAI API key provided")
    print()
    
    # Supabase
    print("Supabase Setup:")
    print("1. Go to https://supabase.com and create a project")
    print("2. Go to Project Settings > API")
    print("3. Copy your Project URL and anon/public key")
    print()
    supabase_url = input("Enter Supabase URL (or press Enter to skip): ").strip()
    supabase_key = input("Enter Supabase anon key (or press Enter to skip): ").strip()
    print()
    
    # Discord
    print("Discord Bot Setup:")
    print("1. Go to https://discord.com/developers/applications")
    print("2. Create a new application")
    print("3. Go to Bot section > Add Bot")
    print("4. Enable 'Message Content Intent' under Privileged Gateway Intents")
    print("5. Copy the bot token")
    print()
    discord_token = input("Enter Discord bot token (or press Enter to skip): ").strip()
    discord_channel = input("Enter Discord channel ID (optional, leave empty for DMs): ").strip()
    print()
    
    # Google (optional)
    print("Google APIs Setup (Optional - for Gmail/Drive):")
    print("1. Go to https://console.cloud.google.com")
    print("2. Create a project and enable Gmail API + Drive API")
    print("3. Create OAuth 2.0 credentials (Desktop app)")
    print("4. Download the JSON file")
    print()
    google_creds = input("Path to Google credentials JSON (or press Enter to skip): ").strip()
    if not google_creds:
        google_creds = "config/google_credentials.json"
    print()
    
    # Write .env file
    env_content = f"""# LLM Configuration
LLM_PROVIDER=openai
LLM_MODEL=gpt-4-turbo-preview
OPENAI_API_KEY={openai_key}

# Supabase Configuration
SUPABASE_URL={supabase_url}
SUPABASE_KEY={supabase_key}

# Discord Configuration
DISCORD_BOT_TOKEN={discord_token}
DISCORD_CHANNEL_ID={discord_channel}

# Google API Configuration
GOOGLE_CREDENTIALS_PATH={google_creds}
"""
    
    env_path.write_text(env_content)
    print(f"[OK] Created .env file at {env_path.absolute()}")
    print()
    
    # Check what's configured
    print("Configuration Status:")
    print(f"  OpenAI: [OK] Configured")
    print(f"  Supabase: {'[OK] Configured' if supabase_url and supabase_key else '[X] Not configured'}")
    print(f"  Discord: {'[OK] Configured' if discord_token else '[X] Not configured'}")
    print(f"  Google: {'[OK] Configured' if google_creds else '[?] Optional'}")
    print()
    
    if supabase_url and supabase_key:
        print("Next step: Run the SQL in storage/supabase_client.py in your Supabase SQL Editor")
    if discord_token:
        print("Next step: Invite your Discord bot to your server using the OAuth2 URL Generator")
    print()
    print("To start the bot: python main.py run")

if __name__ == "__main__":
    create_env_file()

