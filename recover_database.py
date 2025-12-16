#!/usr/bin/env python3
"""
Emergency Database Recovery Script
Restores the database from the most recent backup.
"""
import os
import shutil
import zipfile
import sqlite3
from datetime import datetime
from pathlib import Path


def list_backups(backup_dir: str = "backups") -> list:
    """List all available backups sorted by date (newest first)"""
    backup_path = Path(backup_dir)
    if not backup_path.exists():
        print(f"❌ Backup directory '{backup_dir}' not found!")
        return []
    
    backups = sorted(
        [f for f in os.listdir(backup_dir) if f.startswith("skyblock_backup_") and f.endswith(".zip")],
        reverse=True
    )
    return backups


def verify_backup(backup_file: str) -> bool:
    """Verify that a backup file is valid and not corrupted"""
    try:
        with zipfile.ZipFile(backup_file, 'r') as zf:
            # Check if zip is valid
            if zf.testzip() is not None:
                return False
            
            # Extract to temp location and test
            temp_db = "temp_test.db"
            with zf.open(zf.namelist()[0]) as source:
                with open(temp_db, 'wb') as target:
                    shutil.copyfileobj(source, target)
            
            # Try to open and query the database
            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            conn.close()
            
            # Clean up temp file
            os.remove(temp_db)
            
            return len(tables) > 0
    except Exception as e:
        print(f"  ⚠️  Verification failed: {e}")
        return False


def restore_backup(backup_file: str, db_path: str = "skyblock.db") -> bool:
    """Restore database from backup"""
    try:
        # Create backup of corrupted database
        if os.path.exists(db_path):
            corrupted_backup = f"{db_path}.corrupted.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            shutil.copy2(db_path, corrupted_backup)
            print(f"💾 Corrupted database backed up to: {corrupted_backup}")
            os.remove(db_path)
        
        # Extract backup
        with zipfile.ZipFile(backup_file, 'r') as zf:
            with zf.open(zf.namelist()[0]) as source:
                with open(db_path, 'wb') as target:
                    shutil.copyfileobj(source, target)
        
        print(f"✅ Database restored from: {backup_file}")
        return True
    except Exception as e:
        print(f"❌ Restore failed: {e}")
        return False


def main():
    print("=" * 70)
    print("🚨 Emergency Database Recovery")
    print("=" * 70)
    print()
    
    # List available backups
    backups = list_backups()
    
    if not backups:
        print("❌ No backups found!")
        return
    
    print(f"Found {len(backups)} backup(s):\n")
    for i, backup in enumerate(backups[:5], 1):  # Show last 5 backups
        backup_date = backup.replace("skyblock_backup_", "").replace(".zip", "")
        formatted_date = f"{backup_date[:4]}-{backup_date[4:6]}-{backup_date[6:8]} {backup_date[9:11]}:{backup_date[11:13]}:{backup_date[13:15]}"
        print(f"  {i}. {backup} ({formatted_date})")
    
    print()
    print("🔍 Verifying backups...")
    print()
    
    # Find the most recent valid backup
    valid_backup = None
    for backup in backups:
        backup_path = os.path.join("backups", backup)
        print(f"  Checking: {backup}...", end=" ")
        
        if verify_backup(backup_path):
            print("✅ Valid")
            valid_backup = backup_path
            break
        else:
            print("❌ Corrupted or invalid")
    
    print()
    
    if not valid_backup:
        print("❌ No valid backups found!")
        return
    
    print(f"📦 Most recent valid backup: {os.path.basename(valid_backup)}")
    print()
    
    # Confirm restoration
    response = input("Do you want to restore from this backup? (yes/no): ").strip().lower()
    
    if response in ['yes', 'y']:
        print()
        print("🔄 Restoring database...")
        if restore_backup(valid_backup):
            print()
            print("=" * 70)
            print("✅ Database successfully restored!")
            print("=" * 70)
            print()
            print("You can now restart your bot.")
        else:
            print()
            print("=" * 70)
            print("❌ Database restoration failed!")
            print("=" * 70)
    else:
        print("❌ Restoration cancelled.")


if __name__ == "__main__":
    main()
