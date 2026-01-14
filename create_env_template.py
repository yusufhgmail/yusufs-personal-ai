#!/usr/bin/env python3
"""
Create .env template file with OpenAI key pre-filled
"""

import os
from pathlib import Path

# OpenAI key - set via environment variable or user input
OPENAI_KEY = os.getenv("OPENAI_API_KEY", "")

env_content = f"""# LLM Configuration
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o
OPENAI_API_KEY={OPENAI_KEY}

# Supabase Configuration
# Get these from: https://supabase.com/dashboard > Your Project > Settings > API
SUPABASE_URL=
SUPABASE_KEY=

# Discord Configuration
# Get token from: https://discord.com/developers/applications > Your Bot > Token
DISCORD_BOT_TOKEN=
DISCORD_CHANNEL_ID=

# Google API Configuration (Optional - for Gmail/Drive features)
# Download from: https://console.cloud.google.com > APIs & Services > Credentials
GOOGLE_CREDENTIALS_PATH=config/google_credentials.json
"""

def main():
    env_path = Path(".env")
    
    if env_path.exists():
        print(f".env file already exists at {env_path.absolute()}")
        print("Delete it first if you want to recreate it.")
        return
    
    env_path.write_text(env_content)
    print(f"[OK] Created .env template at {env_path.absolute()}")
    print()
    print("Next steps:")
    print("1. Fill in SUPABASE_URL and SUPABASE_KEY")
    print("2. Fill in DISCORD_BOT_TOKEN")
    print("3. (Optional) Set up Google credentials for Gmail/Drive features")

if __name__ == "__main__":
    main()

