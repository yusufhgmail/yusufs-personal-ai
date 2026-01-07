#!/usr/bin/env python3
"""
Script to help set up Discord bot
Provides step-by-step instructions and can verify bot token
"""

import requests
import sys
from pathlib import Path
from dotenv import load_dotenv
import os

def verify_bot_token(token):
    """Verify a Discord bot token by making an API call."""
    if not token:
        return False, "No token provided"
    
    try:
        headers = {"Authorization": f"Bot {token}"}
        response = requests.get("https://discord.com/api/v10/users/@me", headers=headers)
        
        if response.status_code == 200:
            bot_info = response.json()
            return True, f"✅ Bot verified: {bot_info.get('username', 'Unknown')}#{bot_info.get('discriminator', '0000')}"
        elif response.status_code == 401:
            return False, "❌ Invalid token"
        else:
            return False, f"❌ Error: {response.status_code}"
    except Exception as e:
        return False, f"❌ Error: {str(e)}"

def main():
    """Main setup function."""
    print("=" * 60)
    print("Discord Bot Setup")
    print("=" * 60)
    print()
    
    print("Step-by-step instructions:")
    print()
    print("1. Go to https://discord.com/developers/applications")
    print("2. Click 'New Application'")
    print("3. Name it (e.g., 'Personal AI Assistant') and click 'Create'")
    print("4. Go to 'Bot' section in the left sidebar")
    print("5. Click 'Add Bot' -> 'Yes, do it!'")
    print("6. Under 'Privileged Gateway Intents', enable:")
    print("   ✅ Message Content Intent (REQUIRED)")
    print("7. Click 'Reset Token' → copy the token")
    print("8. Go to 'OAuth2' → 'URL Generator'")
    print("   - Select scope: 'bot'")
    print("   - Select permissions: 'Send Messages', 'Read Message History', 'View Channels'")
    print("   - Copy the generated URL and open it in browser")
    print("   - Select your server and authorize")
    print()
    
    # Check if .env exists and has token
    env_path = Path(".env")
    if env_path.exists():
        load_dotenv()
        token = os.getenv("DISCORD_BOT_TOKEN")
        if token:
            print(f"Found token in .env file")
            print()
            verify, message = verify_bot_token(token)
            print(message)
            if verify:
                print()
                print("✅ Your Discord bot is configured and ready!")
                return
    
    print("Enter your bot token to verify (or press Enter to skip):")
    token = input("Token: ").strip()
    
    if token:
        print()
        verify, message = verify_bot_token(token)
        print(message)
        if verify:
            print()
            print("✅ Token is valid! Add it to your .env file:")
            print(f"   DISCORD_BOT_TOKEN={token}")
    else:
        print()
        print("⚠️  No token entered. Follow the instructions above to create a bot.")
        print("   Then add the token to your .env file.")

if __name__ == "__main__":
    try:
        import requests
    except ImportError:
        print("Installing requests library...")
        subprocess.run([sys.executable, "-m", "pip", "install", "requests"], check=True)
        import requests
    
    main()

