#!/usr/bin/env python3
"""
Run Supabase SQL setup via Python client.
Note: Supabase Python client doesn't support raw SQL execution directly.
We'll need to use the REST API or psql.
"""

import os
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

def run_sql_via_rest_api():
    """Try to run SQL via Supabase REST API."""
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        print("Error: SUPABASE_URL and SUPABASE_KEY must be set in .env")
        return False
    
    # Read SQL file
    sql_file = Path("supabase_setup.sql")
    if not sql_file.exists():
        print("Error: supabase_setup.sql not found")
        return False
    
    sql = sql_file.read_text()
    
    # Supabase REST API endpoint for running SQL
    # Note: This requires the service_role key, not the anon key
    # For security, we should use the SQL Editor or psql
    
    print("=" * 60)
    print("Supabase SQL Setup")
    print("=" * 60)
    print()
    print("The Supabase Python client doesn't support raw SQL execution.")
    print("We need to use one of these methods:")
    print()
    print("Option 1: Use Supabase CLI (if installed)")
    print("  supabase db execute --file supabase_setup.sql")
    print()
    print("Option 2: Use psql (PostgreSQL client)")
    print("  psql 'postgresql://postgres:[PASSWORD]@[HOST]:5432/postgres' -f supabase_setup.sql")
    print()
    print("Option 3: Use Supabase Dashboard SQL Editor (easiest)")
    print("  1. Go to https://supabase.com/dashboard")
    print("  2. Select your project")
    print("  3. Go to SQL Editor")
    print("  4. Paste the SQL and run it")
    print()
    print("SQL to run:")
    print("-" * 60)
    print(sql)
    print("-" * 60)
    print()
    
    # Try to get connection string from environment
    # Supabase provides a connection string in project settings
    print("To get your database connection string:")
    print("1. Go to Supabase Dashboard > Project Settings > Database")
    print("2. Find 'Connection string' section")
    print("3. Copy the 'URI' connection string")
    print("4. Use it with psql:")
    print("   psql 'YOUR_CONNECTION_STRING' -f supabase_setup.sql")
    print()
    
    return False

def try_psql():
    """Try to run SQL using psql if available."""
    import subprocess
    
    # Check if psql is available
    try:
        result = subprocess.run(["psql", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print("psql is available!")
            print("To run the SQL, you need:")
            print("1. Get your database connection string from Supabase Dashboard")
            print("2. Run: psql 'YOUR_CONNECTION_STRING' -f supabase_setup.sql")
            return True
    except FileNotFoundError:
        pass
    
    return False

if __name__ == "__main__":
    print("Attempting to run SQL via CLI...")
    print()
    
    if try_psql():
        print()
        print("psql is installed. You can run:")
        print("  psql 'YOUR_CONNECTION_STRING' -f supabase_setup.sql")
    else:
        print("psql not found. Trying alternative methods...")
        print()
        run_sql_via_rest_api()

