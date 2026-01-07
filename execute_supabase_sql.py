#!/usr/bin/env python3
"""
Execute SQL on Supabase using REST API.
Note: This requires the service_role key for security.
We'll try using the Management API or direct database connection.
"""

import os
import requests
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

def execute_sql_via_rest():
    """Try to execute SQL via Supabase REST API."""
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
    
    print("=" * 60)
    print("Executing SQL on Supabase")
    print("=" * 60)
    print()
    
    # Supabase REST API doesn't support raw SQL execution via the anon key
    # We need to use the Management API or psql
    # However, we can try using the Supabase client's RPC or direct connection
    
    # Try using Supabase Python client with raw query
    try:
        from supabase import create_client
        
        client = create_client(supabase_url, supabase_key)
        
        # The Supabase Python client doesn't have a direct SQL execution method
        # We need to use psql or the Management API
        
        print("The Supabase Python client doesn't support raw SQL execution.")
        print("We need to use one of these methods:")
        print()
        print("Method 1: Install psql and use connection string")
        print("  - Get connection string from Supabase Dashboard")
        print("  - Install PostgreSQL client tools")
        print("  - Run: psql 'CONNECTION_STRING' -f supabase_setup.sql")
        print()
        print("Method 2: Use Supabase Dashboard (easiest)")
        print("  - Go to SQL Editor in dashboard")
        print("  - Paste and run the SQL")
        print()
        print("Method 3: Use Supabase CLI")
        print("  - Install: scoop install supabase (or download from GitHub)")
        print("  - Link project: supabase link --project-ref rpygndzdvyqeeygvkheq")
        print("  - Run: supabase db execute --file supabase_setup.sql")
        print()
        
        # Try to check if tables already exist
        try:
            result = client.table("guidelines").select("id").limit(1).execute()
            print("[INFO] Guidelines table already exists!")
            return True
        except Exception as e:
            if "relation" in str(e).lower() or "does not exist" in str(e).lower():
                print("[INFO] Tables don't exist yet. Need to create them.")
            else:
                print(f"[INFO] Could not check table status: {e}")
        
        return False
        
    except Exception as e:
        print(f"Error: {e}")
        return False

def try_with_psql_connection_string():
    """Try to get connection string and use psql."""
    print()
    print("To use psql, you need:")
    print("1. Install PostgreSQL client tools")
    print("2. Get connection string from Supabase Dashboard:")
    print("   - Go to Project Settings > Database")
    print("   - Copy the 'Connection string' (URI format)")
    print("3. Run: psql 'YOUR_CONNECTION_STRING' -f supabase_setup.sql")
    print()
    print("Or use the Supabase Dashboard SQL Editor (recommended):")
    print("1. Go to https://supabase.com/dashboard")
    print(f"2. Select project: rpygndzdvyqeeygvkheq")
    print("3. Go to SQL Editor")
    print("4. Paste the SQL from supabase_setup.sql")
    print("5. Click Run")

if __name__ == "__main__":
    success = execute_sql_via_rest()
    
    if not success:
        try_with_psql_connection_string()
        
        print()
        print("SQL file is ready at: supabase_setup.sql")
        print("You can copy its contents and run in Supabase SQL Editor.")

