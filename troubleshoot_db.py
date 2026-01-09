#!/usr/bin/env python3
"""
Database troubleshooting script.
Reads database tables, schemas, and data for debugging.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from typing import Optional, Dict, List, Any
import json

load_dotenv()


def get_connection_details() -> Optional[Dict[str, Any]]:
    """Get database connection details from environment."""
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
    
    if not db_password:
        print("[!] Error: SUPABASE_DB_PASSWORD not found in environment")
        return None
    
    if not db_host:
        print("[!] Error: Could not determine database host")
        print(f"[i] SUPABASE_URL: {supabase_url}")
        print("[i] Set SUPABASE_DB_HOST environment variable or ensure SUPABASE_URL is correct")
        return None
    
    return {
        "host": db_host,
        "database": db_name,
        "user": db_user,
        "password": db_password,
        "port": 5432
    }


def get_db_connection(conn_details: Dict[str, Any]):
    """Get database connection using psycopg2."""
    try:
        import psycopg2
        return psycopg2.connect(
            host=conn_details["host"],
            database=conn_details["database"],
            user=conn_details["user"],
            password=conn_details["password"],
            port=conn_details["port"],
            connect_timeout=10
        )
    except ImportError:
        print("[!] Error: psycopg2 not installed")
        print("[i] Install with: pip install psycopg2-binary")
        return None
    except Exception as e:
        print(f"[!] Connection error: {e}")
        return None


def list_tables(conn) -> List[str]:
    """List all tables in the public schema."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        ORDER BY table_name
    """)
    tables = [row[0] for row in cursor.fetchall()]
    cursor.close()
    return tables


def get_table_schema(conn, table_name: str) -> List[Dict[str, Any]]:
    """Get schema information for a table."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            column_name,
            data_type,
            character_maximum_length,
            is_nullable,
            column_default
        FROM information_schema.columns
        WHERE table_schema = 'public' 
        AND table_name = %s
        ORDER BY ordinal_position
    """, (table_name,))
    
    columns = []
    for row in cursor.fetchall():
        columns.append({
            "name": row[0],
            "type": row[1],
            "max_length": row[2],
            "nullable": row[3] == "YES",
            "default": row[4]
        })
    
    cursor.close()
    return columns


def get_table_row_count(conn, table_name: str) -> int:
    """Get row count for a table."""
    cursor = conn.cursor()
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cursor.fetchone()[0]
    cursor.close()
    return count


def get_table_sample(conn, table_name: str, limit: int = 5) -> List[Dict[str, Any]]:
    """Get sample rows from a table."""
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table_name} LIMIT %s", (limit,))
    
    # Get column names
    columns = [desc[0] for desc in cursor.description]
    
    # Fetch rows
    rows = cursor.fetchall()
    
    # Convert to list of dicts
    result = []
    for row in rows:
        row_dict = {}
        for i, col in enumerate(columns):
            value = row[i]
            # Convert non-serializable types to strings
            if value is not None:
                try:
                    json.dumps(value)
                    row_dict[col] = value
                except (TypeError, ValueError):
                    row_dict[col] = str(value)
            else:
                row_dict[col] = None
        result.append(row_dict)
    
    cursor.close()
    return result


def get_table_indexes(conn, table_name: str) -> List[Dict[str, Any]]:
    """Get indexes for a table."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            indexname,
            indexdef
        FROM pg_indexes
        WHERE schemaname = 'public' 
        AND tablename = %s
        ORDER BY indexname
    """, (table_name,))
    
    indexes = []
    for row in cursor.fetchall():
        indexes.append({
            "name": row[0],
            "definition": row[1]
        })
    
    cursor.close()
    return indexes


def print_table_info(conn, table_name: str):
    """Print comprehensive information about a table."""
    print(f"\n{'='*80}")
    print(f"Table: {table_name}")
    print(f"{'='*80}")
    
    # Schema
    schema = get_table_schema(conn, table_name)
    print(f"\nSchema ({len(schema)} columns):")
    print("-" * 80)
    for col in schema:
        type_str = col["type"]
        if col["max_length"]:
            type_str += f"({col['max_length']})"
        nullable = "NULL" if col["nullable"] else "NOT NULL"
        default = f" DEFAULT {col['default']}" if col["default"] else ""
        print(f"  {col['name']:<30} {type_str:<20} {nullable}{default}")
    
    # Indexes
    indexes = get_table_indexes(conn, table_name)
    if indexes:
        print(f"\nIndexes ({len(indexes)}):")
        print("-" * 80)
        for idx in indexes:
            print(f"  {idx['name']}")
            print(f"    {idx['definition']}")
    
    # Row count
    row_count = get_table_row_count(conn, table_name)
    print(f"\nRow count: {row_count}")
    
    # Sample data
    if row_count > 0:
        print(f"\nSample rows (showing up to 5 of {row_count}):")
        print("-" * 80)
        samples = get_table_sample(conn, table_name, limit=5)
        for i, row in enumerate(samples, 1):
            print(f"\n  Row {i}:")
            for key, value in row.items():
                # Truncate long values
                value_str = str(value)
                if len(value_str) > 100:
                    value_str = value_str[:97] + "..."
                print(f"    {key}: {value_str}")
    else:
        print("\n[No rows in table]")


def main():
    """Main troubleshooting function."""
    print("="*80)
    print("Database Troubleshooting Tool")
    print("="*80)
    print()
    
    # Get connection details
    conn_details = get_connection_details()
    if not conn_details:
        print("\n[!] Cannot proceed without connection details")
        return 1
    
    print(f"[i] Connecting to: {conn_details['host']}:{conn_details['port']}/{conn_details['database']}")
    print(f"[i] User: {conn_details['user']}")
    print()
    
    # Connect to database
    conn = get_db_connection(conn_details)
    if not conn:
        return 1
    
    print("[OK] Connected successfully!")
    print()
    
    try:
        # List all tables
        tables = list_tables(conn)
        print(f"Found {len(tables)} table(s): {', '.join(tables) if tables else 'none'}")
        print()
        
        if not tables:
            print("[!] No tables found in the database")
            return 0
        
        # Show info for each table
        for table in tables:
            print_table_info(conn, table)
        
        print()
        print("="*80)
        print("Troubleshooting complete!")
        print("="*80)
        
        return 0
        
    except Exception as e:
        print(f"\n[!] Error during troubleshooting: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        conn.close()
        print("\n[i] Connection closed")


if __name__ == "__main__":
    sys.exit(main())

