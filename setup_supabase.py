#!/usr/bin/env python3
"""
Script to help set up Supabase database tables
Uses Supabase CLI if available, or provides SQL to run manually
"""

import subprocess
import sys
from pathlib import Path

def check_supabase_cli():
    """Check if Supabase CLI is installed."""
    try:
        result = subprocess.run(
            ["supabase", "--version"],
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False

def get_sql():
    """Get the SQL for creating tables."""
    sql_path = Path("storage/supabase_client.py")
    if sql_path.exists():
        content = sql_path.read_text()
        # Extract SQL from the docstring
        start = content.find('"""')
        end = content.find('"""', start + 3)
        if start != -1 and end != -1:
            sql = content[start + 3:end].strip()
            # Remove the comment line
            sql = sql.replace('# SQL for creating tables (run in Supabase SQL editor):\n', '')
            return sql
    return None

def setup_via_cli():
    """Try to set up via Supabase CLI."""
    print("Attempting to use Supabase CLI...")
    
    # Check if we're in a Supabase project
    if not Path("supabase").exists():
        print("Initializing Supabase project...")
        subprocess.run(["supabase", "init"], check=False)
    
    # Link to remote project
    print("\nTo link to your Supabase project:")
    print("1. Get your project reference ID from Supabase dashboard")
    print("2. Run: supabase link --project-ref YOUR_PROJECT_REF")
    print("3. Then run this script again")
    
    return False

def main():
    """Main setup function."""
    print("=" * 60)
    print("Supabase Database Setup")
    print("=" * 60)
    print()
    
    sql = get_sql()
    if not sql:
        print("❌ Could not find SQL in storage/supabase_client.py")
        return
    
    if check_supabase_cli():
        print("✅ Supabase CLI is installed")
        print()
        choice = input("Use CLI to set up? (y/n): ").strip().lower()
        if choice == 'y':
            if setup_via_cli():
                print("✅ Setup complete via CLI")
                return
    
    print("\n" + "=" * 60)
    print("Manual Setup Instructions")
    print("=" * 60)
    print()
    print("1. Go to https://supabase.com/dashboard")
    print("2. Select your project")
    print("3. Go to SQL Editor")
    print("4. Click 'New query'")
    print("5. Copy and paste the SQL below:")
    print()
    print("-" * 60)
    print(sql)
    print("-" * 60)
    print()
    print("6. Click 'Run' to execute the SQL")
    print()
    
    # Save SQL to file for easy copying
    sql_file = Path("supabase_setup.sql")
    sql_file.write_text(sql)
    print(f"✅ SQL saved to {sql_file.absolute()}")
    print("   You can copy it from there if needed")

if __name__ == "__main__":
    main()

