#!/usr/bin/env python3
import asyncio
import sys
from migrations.migration_runner import MigrationRunner


async def main():
    print("=" * 60)
    print("Running Migration 068: Add Drop XP Tables")
    print("=" * 60)
    print()
    
    runner = MigrationRunner(db_path="skyblock.db", migrations_dir="migrations")
    
    try:
        await runner.run_migrations()
        print()
        print("=" * 60)
        print("Migration completed successfully!")
        print("=" * 60)
    except Exception as e:
        print(f"Migration failed: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
