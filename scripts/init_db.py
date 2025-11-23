#!/usr/bin/env python3
"""Initialize TimescaleDB schema for Cortex5 AI Hedge Fund."""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data.db_client import TimescaleDBClient, DatabaseError


def main():
    """Initialize the database schema."""
    print("=" * 60)
    print("Cortex5 Database Initialization")
    print("=" * 60)
    
    # Get schema file path
    schema_path = Path(__file__).parent.parent / "src" / "data" / "db_schema.sql"
    
    if not schema_path.exists():
        print(f"✗ Schema file not found: {schema_path}")
        sys.exit(1)
    
    print(f"\n📄 Schema file: {schema_path}")
    
    # Initialize database client
    try:
        print("\n🔌 Connecting to TimescaleDB...")
        db_client = TimescaleDBClient()
        db_client.connect()
        
        print("\n📊 Executing schema creation...")
        db_client.execute_sql_file(str(schema_path))
        
        print("\n✅ Database initialization complete!")
        print("\nCreated tables:")
        print("  • market_data (hypertable)")
        print("  • trade_logs")
        print("  • portfolio_state")
        print("  • cash_balance")
        print("\nCreated views:")
        print("  • market_data_daily (continuous aggregate)")
        print("\nCreated functions:")
        print("  • get_latest_price()")
        print("  • get_portfolio_value()")
        
        # Verify tables exist
        print("\n🔍 Verifying tables...")
        with db_client.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_type = 'BASE TABLE'
                    ORDER BY table_name
                """)
                tables = cursor.fetchall()
                
                if tables:
                    print(f"\n✓ Found {len(tables)} tables:")
                    for table in tables:
                        print(f"  • {table[0]}")
                else:
                    print("\n⚠ No tables found!")
        
        db_client.close()
        
    except DatabaseError as e:
        print(f"\n✗ Database error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("🎉 Ready to ingest market data!")
    print("=" * 60)


if __name__ == "__main__":
    main()
