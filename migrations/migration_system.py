import aiosqlite
import os
import shutil
import hashlib
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple
import traceback


class MigrationSystem:
    def __init__(self, db_path: str, migrations_dir: str = "migrations/scripts"):
        self.db_path = db_path
        self.migrations_dir = Path(migrations_dir)
        self.backup_dir = Path("migrations/backups")
        self.migrations_dir.mkdir(parents=True, exist_ok=True)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
    def _calculate_checksum(self, filepath: str) -> str:
        with open(filepath, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()
    
    async def _create_schema_versions_table(self, conn: aiosqlite.Connection):
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS schema_versions (
                version INTEGER PRIMARY KEY,
                migration_name TEXT NOT NULL,
                applied_at INTEGER NOT NULL,
                checksum TEXT,
                success BOOLEAN DEFAULT 1
            )
        ''')
        await conn.commit()
    
    async def _get_current_version(self, conn: aiosqlite.Connection) -> int:
        async with conn.execute('SELECT MAX(version) FROM schema_versions WHERE success = 1') as cursor:
            result = await cursor.fetchone()
            return result[0] if result and result[0] is not None else 0
    
    def _backup_database(self) -> Optional[str]:
        if not os.path.exists(self.db_path):
            return None
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / f"skyblock_backup_{timestamp}.db"
        
        shutil.copy2(self.db_path, backup_path)
        print(f"✅ Database backed up to: {backup_path}")
        return str(backup_path)
    
    async def _verify_backup(self, backup_path: Optional[str]) -> bool:
        if not backup_path or not os.path.exists(backup_path):
            return False
        
        try:
            async with aiosqlite.connect(backup_path) as conn:
                async with conn.execute("SELECT name FROM sqlite_master WHERE type='table'") as cursor:
                    tables = await cursor.fetchall()
                    return len(list(tables)) > 0
        except Exception:
            return False
    
    async def _restore_from_backup(self, backup_path: str):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        shutil.copy2(backup_path, self.db_path)
        print(f"✅ Database restored from backup: {backup_path}")
    
    def _get_migration_files(self) -> List[Tuple[int, str, str]]:
        migrations = []
        for file in sorted(self.migrations_dir.glob("*.sql")):
            try:
                version = int(file.stem.split('_')[0])
                name = '_'.join(file.stem.split('_')[1:])
                migrations.append((version, name, str(file)))
            except (ValueError, IndexError):
                continue
        return migrations
    
    async def _apply_migration(self, conn: aiosqlite.Connection, version: int, filepath: str) -> bool:
        try:
            with open(filepath, 'r') as f:
                sql = f.read()
            
            await conn.executescript(sql)
            
            checksum = self._calculate_checksum(filepath)
            await conn.execute('''
                INSERT INTO schema_versions (version, migration_name, applied_at, checksum, success)
                VALUES (?, ?, ?, ?, 1)
            ''', (version, os.path.basename(filepath), int(datetime.now().timestamp()), checksum))
            await conn.commit()
            
            return True
        except Exception as e:
            print(f"❌ Error applying migration: {e}")
            traceback.print_exc()
            await conn.execute('''
                INSERT INTO schema_versions (version, migration_name, applied_at, success)
                VALUES (?, ?, ?, 0)
            ''', (version, os.path.basename(filepath), int(datetime.now().timestamp())))
            await conn.commit()
            return False
    
    async def _verify_schema_integrity(self, conn: aiosqlite.Connection) -> bool:
        try:
            async with conn.execute("PRAGMA integrity_check") as cursor:
                result = await cursor.fetchone()
                return result is not None and result[0] == 'ok'
        except Exception:
            return False
    
    async def run_migrations(self, target_version: Optional[int] = None):
        backup_path = self._backup_database()
        
        if backup_path:
            backup_valid = await self._verify_backup(backup_path)
            if not backup_valid:
                raise RuntimeError(f"Backup verification failed: {backup_path}")
        
        try:
            async with aiosqlite.connect(self.db_path) as conn:
                await self._create_schema_versions_table(conn)
                current_version = await self._get_current_version(conn)
                
                print(f"📊 Current schema version: {current_version}")
                
                migration_files = self._get_migration_files()
                
                if not migration_files:
                    print("ℹ️  No migration files found.")
                    return
                
                applied_count = 0
                for version, name, filepath in migration_files:
                    if version <= current_version:
                        continue
                    
                    if target_version and version > target_version:
                        break
                    
                    print(f"🔄 Applying migration {version}: {name}...")
                    
                    success = await self._apply_migration(conn, version, filepath)
                    
                    if not success:
                        raise RuntimeError(f"Migration {version} failed. Rolling back...")
                    
                    integrity_ok = await self._verify_schema_integrity(conn)
                    if not integrity_ok:
                        raise RuntimeError(f"Schema integrity check failed after migration {version}")
                    
                    print(f"✅ Migration {version} applied successfully")
                    applied_count += 1
                
                if applied_count > 0:
                    print(f"\n✨ {applied_count} migration(s) completed successfully")
                else:
                    print("✅ Database is up to date")
        
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            traceback.print_exc()
            
            if backup_path:
                print(f"🔄 Restoring from backup: {backup_path}")
                await self._restore_from_backup(backup_path)
            
            raise
    
    async def rollback_to_version(self, target_version: int):
        print(f"🔄 Rolling back to version {target_version}...")
        
        async with aiosqlite.connect(self.db_path) as conn:
            await self._create_schema_versions_table(conn)
            current_version = await self._get_current_version(conn)
            
            if target_version >= current_version:
                print("❌ Target version is not before current version")
                return
            
            await conn.execute(
                'DELETE FROM schema_versions WHERE version > ?',
                (target_version,)
            )
            await conn.commit()
            
            print(f"✅ Rolled back to version {target_version}")
            print("⚠️  Note: You must restore from a backup to revert schema changes")


async def main():
    import sys
    
    db_path = "skyblock.db"
    migration_system = MigrationSystem(db_path)
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "migrate":
            target = int(sys.argv[2]) if len(sys.argv) > 2 else None
            await migration_system.run_migrations(target)
        elif command == "rollback":
            if len(sys.argv) < 3:
                print("Usage: python migration_system.py rollback <version>")
                return
            target = int(sys.argv[2])
            await migration_system.rollback_to_version(target)
        else:
            print("Unknown command. Use 'migrate' or 'rollback'")
    else:
        await migration_system.run_migrations()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
