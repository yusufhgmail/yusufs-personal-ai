#!/usr/bin/env python3
"""
Quick setup helper for Google APIs
Checks if credentials exist and provides instructions
"""

from pathlib import Path
import os

def main():
    print("=" * 60)
    print("Google APIs Setup (Gmail & Drive)")
    print("=" * 60)
    print()
    
    creds_path = Path("config/google_credentials.json")
    
    if creds_path.exists():
        print("[OK] Google credentials file found!")
        print(f"     Location: {creds_path.absolute()}")
        print()
        print("Next steps:")
        print("1. Start the bot: python main.py run")
        print("2. On first run, a browser will open for OAuth authentication")
        print("3. Sign in with your Google account and grant permissions")
        print("4. The bot will save tokens automatically")
        print()
        print("The bot is ready to use Gmail and Drive features!")
    else:
        print("[MISSING] Google credentials file not found")
        print()
        print("To set up:")
        print("1. Go to https://console.cloud.google.com")
        print("2. Create a new project (or select existing)")
        print("3. Enable APIs:")
        print("   - Gmail API")
        print("   - Google Drive API")
        print("4. Create OAuth 2.0 credentials:")
        print("   - Go to APIs & Services > Credentials")
        print("   - Create Credentials > OAuth client ID")
        print("   - Application type: Desktop app")
        print("   - Download the JSON file")
        print("5. Save it as: config/google_credentials.json")
        print()
        print("See SETUP_GOOGLE_APIS.md for detailed instructions")
        print()
        
        # Check if config directory exists
        config_dir = Path("config")
        if not config_dir.exists():
            print("Creating config directory...")
            config_dir.mkdir()
            print("[OK] Created config directory")
        else:
            print("[OK] Config directory exists")
        
        print()
        print("After downloading credentials.json from Google:")
        print("  - Rename it to: google_credentials.json")
        print("  - Move it to: config/google_credentials.json")

if __name__ == "__main__":
    main()

