#!/usr/bin/env python3
"""
Set up the llm_logs table in Supabase.
This script checks if the table exists and creates it if needed.
"""

import os
import subprocess
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# SQL to create only the llm_logs table (assuming other tables exist)
LLM_LOGS_SQL = """
-- LLM logs table for debugging and tracing LLM API calls
CREATE TABLE IF NOT EXISTS llm_logs (
    id SERIAL PRIMARY KEY,
    conversation_id TEXT,
    iteration INTEGER NOT NULL DEFAULT 0,
    provider TEXT NOT NULL CHECK (provider IN ('openai', 'anthropic')),
    model TEXT NOT NULL,
    system_prompt TEXT NOT NULL,
    messages JSONB NOT NULL,
    response TEXT NOT NULL,
    response_metadata JSONB DEFAULT '{}',
    error TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for LLM logs (only if they don't exist)
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_llm_logs_conversation') THEN
        CREATE INDEX idx_llm_logs_conversation ON llm_logs(conversation_id, iteration);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_llm_logs_created') THEN
        CREATE INDEX idx_llm_logs_created ON llm_logs(created_at DESC);
    END IF;
END $$;
"""


def check_table_exists_via_client():
    """Check if llm_logs table exists using Supabase client."""
    try:
        from storage.supabase_client import get_supabase_client
        
        client = get_supabase_client()
        
        # Try to query the table - if it exists, this will work
        try:
            result = client.table("llm_logs").select("id").limit(1).execute()
            print("[✓] llm_logs table already exists!")
            return True
        except Exception as e:
            error_str = str(e).lower()
            if "relation" in error_str or "does not exist" in error_str or "not found" in error_str:
                print("[!] llm_logs table does not exist. Need to create it.")
                return False
            else:
                print(f"[?] Could not determine table status: {e}")
                return None
    except Exception as e:
        print(f"[!] Error checking table: {e}")
        return None


def try_psql_execution():
    """Try to execute SQL using psql if available."""
    supabase_url = os.getenv("SUPABASE_URL", "")
    
    if not supabase_url:
        print("[!] SUPABASE_URL not found in environment")
        return False
    
    # Extract project ref from URL if possible
    # URL format: https://[project-ref].supabase.co
    try:
        project_ref = supabase_url.replace("https://", "").replace(".supabase.co", "").split("/")[0]
        print(f"[i] Detected project: {project_ref}")
    except:
        project_ref = None
    
    # Check if psql is available
    try:
        result = subprocess.run(["psql", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"[✓] Found {version}")
            
            # Try to get connection string from environment or prompt
            db_password = os.getenv("SUPABASE_DB_PASSWORD")
            db_host = os.getenv("SUPABASE_DB_HOST")
            db_user = os.getenv("SUPABASE_DB_USER", "postgres")
            db_name = os.getenv("SUPABASE_DB_NAME", "postgres")
            
            if db_password and db_host:
                # Construct connection string
                conn_string = f"postgresql://{db_user}:{db_password}@{db_host}:5432/{db_name}"
                
                print("[i] Attempting to create llm_logs table via psql...")
                
                # Write SQL to temp file
                temp_sql = Path("temp_llm_logs_setup.sql")
                temp_sql.write_text(LLM_LOGS_SQL)
                
                try:
                    result = subprocess.run(
                        ["psql", conn_string, "-f", str(temp_sql)],
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    
                    if result.returncode == 0:
                        print("[✓] Successfully created llm_logs table!")
                        temp_sql.unlink()  # Clean up
                        return True
                    else:
                        print(f"[!] psql execution failed:")
                        print(result.stderr)
                        temp_sql.unlink()  # Clean up
                        return False
                except subprocess.TimeoutExpired:
                    print("[!] psql execution timed out")
                    temp_sql.unlink()
                    return False
                except Exception as e:
                    print(f"[!] Error running psql: {e}")
                    temp_sql.unlink()
                    return False
            else:
                print("[!] Database connection details not found in environment")
                print("[i] To use psql, set these environment variables:")
                print("   - SUPABASE_DB_PASSWORD")
                print("   - SUPABASE_DB_HOST")
                print("   - SUPABASE_DB_USER (optional, defaults to 'postgres')")
                print("   - SUPABASE_DB_NAME (optional, defaults to 'postgres')")
                print()
                print("[i] You can find these in Supabase Dashboard:")
                print("   Project Settings > Database > Connection string")
                return False
        else:
            return False
    except FileNotFoundError:
        return False


def try_python_execution():
    """Try to execute SQL using Python with psycopg2 if available."""
    try:
        import psycopg2
        from urllib.parse import urlparse
        
        supabase_url = os.getenv("SUPABASE_URL", "")
        db_password = os.getenv("SUPABASE_DB_PASSWORD")
        db_host = os.getenv("SUPABASE_DB_HOST")
        db_user = os.getenv("SUPABASE_DB_USER", "postgres")
        db_name = os.getenv("SUPABASE_DB_NAME", "postgres")
        
        if not (db_password and db_host):
            print("[!] Database connection details not found")
            return False
        
        print("[i] Attempting to create llm_logs table via psycopg2...")
        
        conn = psycopg2.connect(
            host=db_host,
            database=db_name,
            user=db_user,
            password=db_password,
            port=5432,
            connect_timeout=10
        )
        
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Execute the SQL
        cursor.execute(LLM_LOGS_SQL)
        
        cursor.close()
        conn.close()
        
        print("[✓] Successfully created llm_logs table!")
        return True
        
    except ImportError:
        print("[!] psycopg2 not installed. Install with: pip install psycopg2-binary")
        return False
    except Exception as e:
        print(f"[!] Error executing SQL: {e}")
        return False


def main():
    print("=" * 60)
    print("Setting up llm_logs table")
    print("=" * 60)
    print()
    
    # First check if table already exists
    exists = check_table_exists_via_client()
    if exists is True:
        print()
        print("[✓] Setup complete - table already exists!")
        return 0
    
    print()
    print("Attempting to create llm_logs table...")
    print()
    
    # Try psql first
    if try_psql_execution():
        return 0
    
    print()
    print("Trying Python/psycopg2...")
    print()
    
    # Try Python/psycopg2
    if try_python_execution():
        return 0
    
    # If all else fails, provide manual instructions
    print()
    print("=" * 60)
    print("Could not execute SQL automatically")
    print("=" * 60)
    print()
    print("Please run this SQL manually in Supabase SQL Editor:")
    print()
    print("-" * 60)
    print(LLM_LOGS_SQL)
    print("-" * 60)
    print()
    print("Or install psql and set environment variables:")
    print("  - SUPABASE_DB_PASSWORD")
    print("  - SUPABASE_DB_HOST")
    print("  - SUPABASE_DB_USER (optional)")
    print("  - SUPABASE_DB_NAME (optional)")
    print()
    print("Then run: python setup_llm_logs_table.py")
    print()
    
    # Save SQL to file for easy copy-paste
    sql_file = Path("llm_logs_setup.sql")
    sql_file.write_text(LLM_LOGS_SQL)
    print(f"[i] SQL saved to: {sql_file.absolute()}")
    print("    You can copy this file's contents into Supabase SQL Editor")
    
    return 1


if __name__ == "__main__":
    sys.exit(main())

