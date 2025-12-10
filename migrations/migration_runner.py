import aiosqlite
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Optional
import traceback


class MigrationRunner:
    def __init__(self, db_path: str, migrations_dir: str = "migrations"):
        self.db_path = db_path
        self.migrations_dir = Path(migrations_dir)
        self.backup_dir = self.migrations_dir / "backups"
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
    async def create_schema_versions_table(self, conn: aiosqlite.Connection):
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS schema_versions (
                version INTEGER PRIMARY KEY,
                migration_name TEXT NOT NULL,
                applied_at INTEGER NOT NULL,
                checksum TEXT
            )
        ''')
        await conn.commit()
    
    async def get_current_version(self, conn: aiosqlite.Connection) -> int:
        async with conn.execute('SELECT MAX(version) FROM schema_versions') as cursor:
            result = await cursor.fetchone()
            return result[0] if result and result[0] is not None else 0
    
    def backup_database(self) -> Optional[str]:
        if not os.path.exists(self.db_path):
            return None
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / f"skyblock_backup_{timestamp}.db"
        
        shutil.copy2(self.db_path, backup_path)
        return str(backup_path)
    
    async def verify_backup(self, backup_path: Optional[str]) -> bool:
        if not backup_path or not os.path.exists(backup_path):
            return False
        
        try:
            async with aiosqlite.connect(backup_path) as conn:
                async with conn.execute("SELECT name FROM sqlite_master WHERE type='table'") as cursor:
                    tables = await cursor.fetchall()
                    return len(list(tables)) > 0
        except Exception:
            return False
    
    async def restore_from_backup(self, backup_path: str):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        shutil.copy2(backup_path, self.db_path)
    
    def get_migration_files(self) -> List[tuple]:
        migration_files = []
        
        # Check both migrations_dir and migrations_dir/scripts
        search_paths = [self.migrations_dir, self.migrations_dir / "scripts"]
        
        for search_path in search_paths:
            if not search_path.exists():
                continue
                
            for file in sorted(search_path.glob("*.sql")):
                if file.name.startswith("_"):
                    continue
                
                try:
                    version = int(file.stem.split('_')[0])
                    migration_files.append((version, file.name, str(file)))
                except (ValueError, IndexError):
                    continue
        
        return sorted(migration_files, key=lambda x: x[0])
    
    async def apply_migration(self, conn: aiosqlite.Connection, version: int, filepath: str) -> bool:
        try:
            with open(filepath, 'r') as f:
                sql_content = f.read()
            
            statements = [s.strip() for s in sql_content.split(';') if s.strip()]
            
            for statement in statements:
                await conn.execute(statement)
            
            await conn.execute(
                'INSERT INTO schema_versions (version, migration_name, applied_at) VALUES (?, ?, ?)',
                (version, os.path.basename(filepath), int(datetime.now().timestamp()))
            )
            
            await conn.commit()
            return True
        except Exception as e:
            await conn.rollback()
            print(f"Migration {version} failed: {e}")
            traceback.print_exc()
            return False
    
    async def verify_schema_integrity(self, conn: aiosqlite.Connection) -> bool:
        try:
            async with conn.execute("PRAGMA integrity_check") as cursor:
                result = await cursor.fetchone()
                return result is not None and result[0] == 'ok'
        except Exception:
            return False
    
    async def run_migrations(self, target_version: Optional[int] = None):
        backup_path = self.backup_database()
        
        if backup_path:
            backup_valid = await self.verify_backup(backup_path)
            if not backup_valid:
                raise RuntimeError(f"Backup verification failed: {backup_path}")
            print(f"✅ Database backed up to: {backup_path}")
        
        try:
            async with aiosqlite.connect(self.db_path) as conn:
                await self.create_schema_versions_table(conn)
                current_version = await self.get_current_version(conn)
                
                print(f"Current schema version: {current_version}")
                
                migration_files = self.get_migration_files()
                
                if not migration_files:
                    print("No migration files found.")
                    return
                
                for version, name, filepath in migration_files:
                    if version <= current_version:
                        continue
                    
                    if target_version and version > target_version:
                        break
                    
                    print(f"Applying migration {version}: {name}...")
                    
                    success = await self.apply_migration(conn, version, filepath)
                    
                    if not success:
                        raise RuntimeError(f"Migration {version} failed. Rolling back...")
                    
                    integrity_ok = await self.verify_schema_integrity(conn)
                    if not integrity_ok:
                        raise RuntimeError(f"Schema integrity check failed after migration {version}")
                    
                    print(f"✅ Migration {version} applied successfully")
                
                print(f"✅ All migrations completed successfully")
        
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            traceback.print_exc()
            
            if backup_path:
                print(f"Restoring from backup: {backup_path}")
                await self.restore_from_backup(backup_path)
                print("✅ Database restored from backup")
            
            raise
