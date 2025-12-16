import asyncio
import aiosqlite
from pathlib import Path


async def add_museum_and_boss_tables():
    db_path = Path(__file__).parent.parent.parent / 'skyblock.db'
    conn = await aiosqlite.connect(str(db_path))
    conn.row_factory = aiosqlite.Row
    
    print("Adding museum tables...")
    
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS museum_donations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            item_id TEXT NOT NULL,
            rarity TEXT NOT NULL,
            points INTEGER DEFAULT 1,
            donated_at INTEGER NOT NULL,
            UNIQUE(user_id, item_id)
        )
    ''')
    
    await conn.execute('''
        CREATE INDEX IF NOT EXISTS idx_museum_donations_user_id 
        ON museum_donations(user_id)
    ''')
    
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS museum_milestones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            milestone INTEGER NOT NULL,
            claimed_at INTEGER NOT NULL,
            UNIQUE(user_id, milestone)
        )
    ''')
    
    await conn.execute('''
        CREATE INDEX IF NOT EXISTS idx_museum_milestones_user_id 
        ON museum_milestones(user_id)
    ''')
    
    print("Adding boss rotation tables...")
    
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS boss_rotation_kills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            boss_id TEXT NOT NULL,
            damage_dealt INTEGER DEFAULT 0,
            time_taken INTEGER DEFAULT 0,
            killed_at INTEGER NOT NULL
        )
    ''')
    
    await conn.execute('''
        CREATE INDEX IF NOT EXISTS idx_boss_kills_user_boss 
        ON boss_rotation_kills(user_id, boss_id)
    ''')
    
    await conn.execute('''
        CREATE INDEX IF NOT EXISTS idx_boss_kills_user_id 
        ON boss_rotation_kills(user_id)
    ''')
    
    print("Adding reforging tables...")
    
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS inventory_item_reforged_stats (
            inventory_item_id INTEGER PRIMARY KEY,
            reforged_stats TEXT NOT NULL,
            reforged_at INTEGER NOT NULL
        )
    ''')
    
    await conn.execute('''
        CREATE INDEX IF NOT EXISTS idx_reforged_stats_inventory_item 
        ON inventory_item_reforged_stats(inventory_item_id)
    ''')
    
    await conn.commit()
    print("✅ All tables created successfully!")
    
    await conn.close()


if __name__ == '__main__':
    asyncio.run(add_museum_and_boss_tables())
