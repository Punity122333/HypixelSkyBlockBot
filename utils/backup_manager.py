import os
import shutil
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Optional
import zipfile

class BackupManager:
    def __init__(self, db_path: str, backup_dir: str = "backups", interval_hours: int = 6, max_backups: int = 10) -> None:
        self.db_path: str = db_path
        self.backup_dir: str = backup_dir
        self.interval_seconds: int = interval_hours * 3600
        self.max_backups: int = max_backups
        self.backup_task: Optional[asyncio.Task] = None
        Path(self.backup_dir).mkdir(exist_ok=True)
    
    async def create_backup(self) -> str:
        timestamp: str = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename: str = f"skyblock_backup_{timestamp}.db"
        backup_path: str = os.path.join(self.backup_dir, backup_filename)
        await asyncio.to_thread(shutil.copy2, self.db_path, backup_path)
        zip_path: str = backup_path.replace(".db", ".zip")
        await asyncio.to_thread(self._zip_file, backup_path, zip_path)
        await asyncio.to_thread(os.remove, backup_path)
        print(f"💾 Database backup created: {zip_path}")
        await self.cleanup_old_backups()
        return zip_path
    
    def _zip_file(self, src: str, dest: str) -> None:
        with zipfile.ZipFile(dest, 'w', zipfile.ZIP_DEFLATED) as zf:
            zf.write(src, os.path.basename(src))
    
    async def cleanup_old_backups(self) -> None:
        backup_files: list[str] = sorted(
            [f for f in os.listdir(self.backup_dir) if f.startswith("skyblock_backup_") and f.endswith(".zip")],
            reverse=True
        )
        if len(backup_files) > self.max_backups:
            for old_backup in backup_files[self.max_backups:]:
                old_path: str = os.path.join(self.backup_dir, old_backup)
                await asyncio.to_thread(os.remove, old_path)
                print(f"🗑️  Removed old backup: {old_backup}")
    
    async def backup_loop(self) -> None:
        await self.create_backup()
        while True:
            try:
                await asyncio.sleep(self.interval_seconds)
                await self.create_backup()
            except asyncio.CancelledError:
                print("🛑 Backup task cancelled")
                break
            except Exception as e:
                print(f"❌ Backup error: {e}")
                await asyncio.sleep(60)
    
    def start(self, loop: asyncio.AbstractEventLoop) -> None:
        self.backup_task = loop.create_task(self.backup_loop())
        print(f"✅ Backup manager started (interval: {self.interval_seconds // 3600}h, max backups: {self.max_backups})")
    
    def stop(self) -> None:
        if self.backup_task:
            self.backup_task.cancel()
    
    async def restore_from_backup(self, backup_filename: str) -> Optional[bool]:
        """Restore database from a specific backup file"""
        try:
            backup_path = os.path.join(self.backup_dir, backup_filename)
            
            if not os.path.exists(backup_path):
                print(f"❌ Backup file not found: {backup_path}")
                return False
            
            # Backup the current (corrupted) database
            if os.path.exists(self.db_path):
                corrupted_backup = f"{self.db_path}.corrupted.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                await asyncio.to_thread(shutil.copy2, self.db_path, corrupted_backup)
                print(f"💾 Current database backed up to: {corrupted_backup}")
                await asyncio.to_thread(os.remove, self.db_path)
            
            # Extract and restore from zip
            await asyncio.to_thread(self._extract_backup, backup_path, self.db_path)
            print(f"✅ Database restored from: {backup_filename}")
            return True
            
        except Exception as e:
            print(f"❌ Restore failed: {e}")
            return False
    
    def _extract_backup(self, zip_path: str, dest: str) -> None:
        """Extract database from zip backup"""
        with zipfile.ZipFile(zip_path, 'r') as zf:
            with zf.open(zf.namelist()[0]) as source:
                with open(dest, 'wb') as target:
                    shutil.copyfileobj(source, target)
    
    def get_latest_backup(self) -> Optional[str]:
        """Get the filename of the most recent backup"""
        backups = sorted(
            [f for f in os.listdir(self.backup_dir) if f.startswith("skyblock_backup_") and f.endswith(".zip")],
            reverse=True
        )
        return backups[0] if backups else None
