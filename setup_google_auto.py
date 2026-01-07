#!/usr/bin/env python3
"""
Automated Google APIs setup - opens browser and guides through process
"""

import webbrowser
from pathlib import Path

def main():
    print("=" * 60)
    print("Google APIs Setup - Automated Guide")
    print("=" * 60)
    print()
    
    print("Opening Google Cloud Console...")
    webbrowser.open("https://console.cloud.google.com/")
    print()
    
    print("Follow these steps (I'll open the pages for you):")
    print()
    
    # Step 1: Create/Select Project
    print("Step 1: Create or select a project")
    input("Press Enter when ready to continue...")
    webbrowser.open("https://console.cloud.google.com/projectselector2/home/dashboard")
    print()
    
    # Step 2: Enable APIs
    print("Step 2: Enable Gmail API")
    input("Press Enter to open Gmail API page...")
    webbrowser.open("https://console.cloud.google.com/apis/library/gmail.googleapis.com")
    print("  - Click 'Enable'")
    print()
    
    print("Step 3: Enable Google Drive API")
    input("Press Enter to open Drive API page...")
    webbrowser.open("https://console.cloud.google.com/apis/library/drive.googleapis.com")
    print("  - Click 'Enable'")
    print()
    
    # Step 4: Create OAuth Credentials
    print("Step 4: Create OAuth 2.0 credentials")
    input("Press Enter to open Credentials page...")
    webbrowser.open("https://console.cloud.google.com/apis/credentials")
    print("  - Click 'Create Credentials' > 'OAuth client ID'")
    print("  - If prompted, configure OAuth consent screen first")
    print("  - Application type: 'Desktop app'")
    print("  - Name: 'Personal AI Assistant'")
    print("  - Click 'Create'")
    print("  - Download the JSON file")
    print()
    
    # Step 5: Save credentials
    print("Step 5: Save credentials file")
    creds_path = Path("config/google_credentials.json")
    print(f"  - Rename downloaded file to: google_credentials.json")
    print(f"  - Save it to: {creds_path.absolute()}")
    print()
    
    # Check if file exists
    if creds_path.exists():
        print("[OK] Credentials file found!")
        print("Setup complete! The bot will use real Gmail/Drive APIs.")
    else:
        print("[WAITING] Credentials file not found yet.")
        print("After saving the file, run: python setup_google_quick.py")
    
    print()
    print("After setup, start the bot:")
    print("  python main.py run")
    print()
    print("On first run, the bot will:")
    print("  - Open browser for OAuth authentication")
    print("  - Save tokens automatically")
    print("  - Use real Gmail/Drive APIs")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSetup cancelled.")
    except Exception as e:
        print(f"\nError: {e}")

