#!/usr/bin/env python3
"""
Script to run database migrations for the SkyBlock bot.
This will normalize the database schema.
"""
import asyncio
import sys
from migrations.migration_runner import MigrationRunner


async def main():
    print("=" * 60)
    print("SkyBlock Bot - Database Migration Runner")
    print("=" * 60)
    print()
    
    runner = MigrationRunner(db_path="skyblock.db", migrations_dir="migrations")
    
    print("⚠️  WARNING: This will modify your database structure!")
    print("A backup will be created automatically before migration.")
    print()
    
    # Run migrations
    try:
        await runner.run_migrations()
        print()
        print("=" * 60)
        print("✅ Migration completed successfully!")
        print("=" * 60)
    except Exception as e:
        print()
        print("=" * 60)
        print(f"❌ Migration failed: {e}")
        print("=" * 60)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
