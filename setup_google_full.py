#!/usr/bin/env python3
"""
Complete Google APIs setup - automates what's possible via CLI
"""

import subprocess
import sys
import json
import webbrowser
from pathlib import Path

def install_gcloud():
    """Try to install gcloud via available package managers."""
    print("Attempting to install gcloud CLI...")
    print()
    
    # Try Chocolatey
    try:
        result = subprocess.run(
            ["choco", "--version"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print("[OK] Chocolatey is available")
            print("Installing gcloud via Chocolatey...")
            subprocess.run(["choco", "install", "gcloudsdk", "-y"], check=False)
            print("Please restart your terminal and run this script again.")
            return True
    except FileNotFoundError:
        pass
    
    # Try Scoop
    try:
        result = subprocess.run(
            ["scoop", "--version"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print("[OK] Scoop is available")
            print("Installing gcloud via Scoop...")
            subprocess.run(["scoop", "bucket", "add", "main"], check=False)
            subprocess.run(["scoop", "install", "gcloud"], check=False)
            print("Please restart your terminal and run this script again.")
            return True
    except FileNotFoundError:
        pass
    
    print("[INFO] No package manager found. Manual installation required.")
    print()
    print("Download and install from:")
    print("  https://cloud.google.com/sdk/docs/install")
    print()
    return False

def check_gcloud():
    """Check if gcloud is installed."""
    try:
        result = subprocess.run(
            ["gcloud", "--version"],
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False

def setup_via_python_api():
    """Alternative: Use Python to help with OAuth setup."""
    print("=" * 60)
    print("Setting up Google APIs via Python")
    print("=" * 60)
    print()
    
    print("This will help you:")
    print("1. Open Google Cloud Console to create project")
    print("2. Guide you through enabling APIs")
    print("3. Help create OAuth credentials")
    print("4. Handle the OAuth flow automatically")
    print()
    
    # Open Google Cloud Console
    print("Opening Google Cloud Console...")
    webbrowser.open("https://console.cloud.google.com/")
    print()
    
    print("Manual steps (can't be fully automated):")
    print("1. Create a project (or select existing)")
    print("2. Enable APIs:")
    print("   - Go to APIs & Services > Library")
    print("   - Search 'Gmail API' > Enable")
    print("   - Search 'Google Drive API' > Enable")
    print("3. Create OAuth credentials:")
    print("   - Go to APIs & Services > Credentials")
    print("   - Create Credentials > OAuth client ID")
    print("   - Application type: Desktop app")
    print("   - Download the JSON file")
    print()
    
    # Check if credentials file exists
    creds_path = Path("config/google_credentials.json")
    if creds_path.exists():
        print("[OK] Credentials file found!")
        print(f"     Location: {creds_path.absolute()}")
        print()
        print("Next: Run the bot and it will handle OAuth authentication:")
        print("  python main.py run")
        return True
    else:
        print("[MISSING] Credentials file not found")
        print(f"         Expected: {creds_path.absolute()}")
        print()
        print("After downloading credentials.json from Google:")
        print(f"  1. Rename to: google_credentials.json")
        print(f"  2. Save to: {creds_path.absolute()}")
        print()
        print("Then run the bot - it will handle OAuth automatically!")
        return False

def main():
    print("=" * 60)
    print("Google APIs Setup (Gmail & Drive)")
    print("=" * 60)
    print()
    
    # Check if gcloud is installed
    if not check_gcloud():
        print("[MISSING] gcloud CLI not found")
        print()
        
        choice = input("Install gcloud CLI? (y/n): ").strip().lower()
        if choice == 'y':
            if install_gcloud():
                return
        else:
            print()
            print("Using Python-based setup instead...")
            print()
    
    # Try Python-based setup
    setup_via_python_api()
    
    print()
    print("=" * 60)
    print("Note on OAuth Credentials")
    print("=" * 60)
    print()
    print("OAuth2 credentials for desktop apps cannot be fully automated")
    print("because they require:")
    print("  1. Creating credentials in Google Cloud Console (web interface)")
    print("  2. Downloading the JSON file")
    print()
    print("However, once you have the credentials file, the bot will:")
    print("  - Automatically handle OAuth authentication")
    print("  - Open browser for you to sign in")
    print("  - Save tokens automatically")
    print("  - Use real Gmail/Drive APIs")
    print()

if __name__ == "__main__":
    main()

