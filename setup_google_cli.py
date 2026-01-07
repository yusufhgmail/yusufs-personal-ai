#!/usr/bin/env python3
"""
Attempt to set up Google APIs via CLI using gcloud
"""

import subprocess
import sys
import json
from pathlib import Path

def check_gcloud():
    """Check if gcloud CLI is installed."""
    try:
        result = subprocess.run(
            ["gcloud", "--version"],
            capture_output=True,
            text=True
        )
        return result.returncode == 0, result.stdout
    except FileNotFoundError:
        return False, None

def install_gcloud_instructions():
    """Provide instructions for installing gcloud."""
    print("=" * 60)
    print("Google Cloud SDK Installation")
    print("=" * 60)
    print()
    print("To install gcloud CLI:")
    print()
    print("Option 1: Using installer (Windows)")
    print("  1. Download from: https://cloud.google.com/sdk/docs/install")
    print("  2. Run the installer")
    print("  3. Restart your terminal")
    print()
    print("Option 2: Using package manager")
    print("  - Chocolatey: choco install gcloudsdk")
    print("  - Scoop: scoop install gcloud")
    print()
    print("After installation, run this script again.")

def enable_apis_via_cli(project_id):
    """Enable Gmail and Drive APIs via gcloud."""
    print("Enabling APIs...")
    
    apis = [
        "gmail.googleapis.com",
        "drive.googleapis.com"
    ]
    
    for api in apis:
        try:
            result = subprocess.run(
                ["gcloud", "services", "enable", api, "--project", project_id],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print(f"  [OK] Enabled {api}")
            else:
                print(f"  [ERROR] Failed to enable {api}: {result.stderr}")
        except Exception as e:
            print(f"  [ERROR] Exception enabling {api}: {e}")

def create_oauth_credentials_via_cli(project_id, output_path):
    """Try to create OAuth credentials via CLI."""
    print("Creating OAuth credentials...")
    print()
    print("Note: gcloud CLI has limited support for OAuth credential creation.")
    print("You may need to use the web console for this step.")
    print()
    
    # Try using gcloud to create credentials
    # Note: This might not work for OAuth2 desktop app credentials
    try:
        # gcloud doesn't have a direct command for OAuth2 desktop app credentials
        # We'll need to guide the user to the web console
        print("OAuth2 credentials must be created via web console:")
        print(f"  https://console.cloud.google.com/apis/credentials?project={project_id}")
        print()
        print("Steps:")
        print("  1. Click 'Create Credentials' > 'OAuth client ID'")
        print("  2. Application type: 'Desktop app'")
        print("  3. Download the JSON file")
        print(f"  4. Save it as: {output_path}")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    print("=" * 60)
    print("Google APIs Setup via CLI")
    print("=" * 60)
    print()
    
    # Check if gcloud is installed
    gcloud_installed, version = check_gcloud()
    
    if not gcloud_installed:
        print("[MISSING] gcloud CLI is not installed")
        print()
        install_gcloud_instructions()
        return
    
    print(f"[OK] gcloud CLI is installed")
    print(f"     {version.split(chr(10))[0] if version else ''}")
    print()
    
    # Check if user is authenticated
    try:
        result = subprocess.run(
            ["gcloud", "auth", "list"],
            capture_output=True,
            text=True
        )
        if "No credentialed accounts" in result.stdout:
            print("[ACTION NEEDED] Not authenticated with gcloud")
            print("  Run: gcloud auth login")
            print()
            return
        else:
            print("[OK] Authenticated with gcloud")
            print()
    except Exception as e:
        print(f"[ERROR] Could not check authentication: {e}")
        return
    
    # Get current project
    try:
        result = subprocess.run(
            ["gcloud", "config", "get-value", "project"],
            capture_output=True,
            text=True
        )
        project_id = result.stdout.strip()
        
        if not project_id:
            print("[ACTION NEEDED] No project selected")
            print("  Run: gcloud config set project YOUR_PROJECT_ID")
            print("  Or create a project: gcloud projects create YOUR_PROJECT_ID")
            print()
            return
        
        print(f"[OK] Current project: {project_id}")
        print()
    except Exception as e:
        print(f"[ERROR] Could not get project: {e}")
        return
    
    # Enable APIs
    print("Step 1: Enabling APIs...")
    enable_apis_via_cli(project_id)
    print()
    
    # Create OAuth credentials
    print("Step 2: Creating OAuth credentials...")
    output_path = Path("config/google_credentials.json")
    success = create_oauth_credentials_via_cli(project_id, output_path)
    
    if not success:
        print()
        print("=" * 60)
        print("Manual Step Required")
        print("=" * 60)
        print()
        print("OAuth2 credentials must be created via web console:")
        print(f"  https://console.cloud.google.com/apis/credentials?project={project_id}")
        print()
        print("After creating and downloading credentials:")
        print(f"  1. Rename to: google_credentials.json")
        print(f"  2. Save to: {output_path.absolute()}")
        print()
        print("Then run: python setup_google_quick.py")
    
    print()
    print("After credentials are in place, the bot will use real Gmail/Drive APIs!")

if __name__ == "__main__":
    main()

