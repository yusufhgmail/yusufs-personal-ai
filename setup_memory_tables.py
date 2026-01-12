#!/usr/bin/env python3
"""
Set up memory system tables using direct PostgreSQL connection.
This script reads memory_setup.sql and executes it.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


def load_sql_file():
    """Load SQL from memory_setup.sql file."""
    sql_file = Path("memory_setup.sql")
    if not sql_file.exists():
        print(f"[!] Error: {sql_file} not found")
        return None
    return sql_file.read_text(encoding="utf-8")


def get_connection_details():
    """Get database connection details from environment or prompt."""
    supabase_url = os.getenv("SUPABASE_URL", "")
    
    # Try to extract project ref
    project_ref = None
    if supabase_url:
        try:
            # URL format: https://[project-ref].supabase.co
            project_ref = supabase_url.replace("https://", "").replace("http://", "").split(".")[0]
        except:
            pass
    
    # Get connection details from environment
    db_password = os.getenv("SUPABASE_DB_PASSWORD")
    db_host = os.getenv("SUPABASE_DB_HOST")
    db_user = os.getenv("SUPABASE_DB_USER", "postgres")
    db_name = os.getenv("SUPABASE_DB_NAME", "postgres")
    
    # If we have project_ref but no host, construct it
    if project_ref and not db_host:
        db_host = f"db.{project_ref}.supabase.co"
    
    # If we have project_ref but no password, we need to prompt
    if not db_password:
        print()
        print("=" * 60)
        print("Database Connection Required")
        print("=" * 60)
        print()
        print("To set up the memory tables, we need your database password.")
        print()
        print("You can find it in Supabase Dashboard:")
        print("1. Go to https://supabase.com/dashboard")
        if project_ref:
            print(f"2. Select project: {project_ref}")
        print("3. Go to Project Settings > Database")
        print("4. Find 'Database password' section")
        print("5. Copy the password (or reset it if needed)")
        print()
        print("Then set it as an environment variable:")
        print("  set SUPABASE_DB_PASSWORD=your_password_here")
        print()
        print("Or run this script with the password:")
        print("  set SUPABASE_DB_PASSWORD=your_password && python setup_memory_tables.py")
        print()
        
        # Try to prompt for password
        try:
            password = input("Enter database password (or press Enter to skip): ").strip()
            if password:
                db_password = password
            else:
                return None
        except (KeyboardInterrupt, EOFError):
            print("\nCancelled.")
            return None
    
    if not db_host:
        print("[!] Could not determine database host")
        print("[i] Set SUPABASE_DB_HOST environment variable")
        return None
    
    if not db_password:
        return None
    
    return {
        "host": db_host,
        "database": db_name,
        "user": db_user,
        "password": db_password,
        "port": 5432
    }


def execute_sql_via_psycopg2(conn_details, sql):
    """Execute SQL using psycopg2."""
    try:
        import psycopg2
        
        print()
        print("[i] Connecting to database...")
        conn = psycopg2.connect(
            host=conn_details["host"],
            database=conn_details["database"],
            user=conn_details["user"],
            password=conn_details["password"],
            port=conn_details["port"],
            connect_timeout=10
        )
        
        print("[OK] Connected successfully!")
        print()
        print("[i] Executing SQL setup...")
        
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Execute the SQL
        try:
            cursor.execute(sql)
            print("[OK] SQL executed successfully!")
        except psycopg2.Error as e:
            print(f"[!] SQL execution error: {e}")
            print(f"[i] Error details: {e.pgcode} - {e.pgerror}")
            cursor.close()
            conn.close()
            return False
        
        # Verify tables were created
        print()
        print("[i] Verifying table creation...")
        tables_to_check = ["memory", "current_focus"]
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN %s
        """, (tuple(tables_to_check),))
        
        existing_tables = [row[0] for row in cursor.fetchall()]
        missing_tables = [t for t in tables_to_check if t not in existing_tables]
        
        if missing_tables:
            print(f"[!] Warning: Some tables are missing: {', '.join(missing_tables)}")
        else:
            print("[OK] All tables verified: memory, current_focus")
        
        # Check if pgvector extension is enabled
        cursor.execute("""
            SELECT EXISTS(
                SELECT 1 FROM pg_extension WHERE extname = 'vector'
            )
        """)
        vector_enabled = cursor.fetchone()[0]
        
        if vector_enabled:
            print("[OK] pgvector extension is enabled")
        else:
            print("[!] Warning: pgvector extension may not be enabled")
        
        cursor.close()
        conn.close()
        
        print()
        print("[OK] Memory system setup complete!")
        return True
        
    except ImportError:
        print("[!] psycopg2 not installed. Install with: pip install psycopg2-binary")
        return False
    except psycopg2.OperationalError as e:
        print(f"[!] Connection error: {e}")
        print()
        print("[i] Common issues:")
        print("   - Wrong password")
        print("   - Database host not accessible")
        print("   - Firewall blocking connection")
        print("   - Check that your IP is allowed in Supabase Dashboard > Settings > Database")
        return False
    except Exception as e:
        print(f"[!] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("=" * 60)
    print("Setting up Memory System Tables")
    print("=" * 60)
    print()
    
    # Load SQL file
    sql = load_sql_file()
    if not sql:
        return 1
    
    print("[i] Loaded SQL from memory_setup.sql")
    print(f"[i] SQL contains {len(sql.splitlines())} lines")
    
    # Get connection details
    conn_details = get_connection_details()
    
    if not conn_details:
        print()
        print("=" * 60)
        print("Manual Setup Required")
        print("=" * 60)
        print()
        print("To set up manually:")
        print("1. Go to https://supabase.com/dashboard")
        print("2. Select your project")
        print("3. Go to SQL Editor")
        print("4. Paste the SQL from memory_setup.sql")
        print("5. Click Run")
        print()
        print("SQL file location: memory_setup.sql")
        return 1
    
    # Execute SQL
    success = execute_sql_via_psycopg2(conn_details, sql)
    
    if success:
        print()
        print("=" * 60)
        print("Setup Complete!")
        print("=" * 60)
        print()
        print("The memory system is now ready to use.")
        print("Tables created:")
        print("  - memory (with vector embeddings)")
        print("  - current_focus")
        print()
        return 0
    else:
        print()
        print("=" * 60)
        print("Setup Failed")
        print("=" * 60)
        print()
        print("Please check the error messages above and try again.")
        print("You can also run the SQL manually in Supabase SQL Editor.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
