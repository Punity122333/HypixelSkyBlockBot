import aiosqlite
import asyncio

async def migrate_fairy_souls():
    async with aiosqlite.connect('skyblock.db') as conn:
        print("🔍 Checking fairy_souls table structure...")
        
        # Check current structure of fairy_souls table
        cursor = await conn.execute("PRAGMA table_info(fairy_souls)")
        columns = await cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        # If fairy_souls has wrong structure (has 'location' column), fix it
        if 'location' in column_names and 'souls_collected' not in column_names:
            print("⚠️  Detected incorrect fairy_souls table structure. Fixing...")
            
            # Drop the incorrectly structured table
            await conn.execute('DROP TABLE fairy_souls')
            
            # Create it with correct structure
            await conn.execute('''
                CREATE TABLE fairy_souls (
                    user_id INTEGER PRIMARY KEY,
                    souls_collected INTEGER DEFAULT 0,
                    FOREIGN KEY (user_id) REFERENCES players(user_id)
                )
            ''')
            await conn.commit()
            print("✅ Fixed fairy_souls table structure!")
        elif 'souls_collected' not in column_names:
            # Table doesn't exist or is empty, create it
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS fairy_souls (
                    user_id INTEGER PRIMARY KEY,
                    souls_collected INTEGER DEFAULT 0,
                    FOREIGN KEY (user_id) REFERENCES players(user_id)
                )
            ''')
            await conn.commit()
            print("✅ Created fairy_souls table!")
        else:
            print("✅ fairy_souls table structure is correct!")
        
        # Add fairy_souls_collected column to players if it doesn't exist
        cursor = await conn.execute("PRAGMA table_info(players)")
        columns = await cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        if 'fairy_souls_collected' not in column_names:
            print("Adding fairy_souls_collected column to players table...")
            await conn.execute('ALTER TABLE players ADD COLUMN fairy_souls_collected INTEGER DEFAULT 0')
            await conn.commit()
            print("✅ Column added successfully!")
        else:
            print("✅ fairy_souls_collected column already exists!")
        
        # Get all players
        cursor = await conn.execute("SELECT user_id FROM players")
        players = await cursor.fetchall()
        player_count = len(list(players))
        
        # Re-fetch for iteration
        cursor = await conn.execute("SELECT user_id FROM players")
        players = await cursor.fetchall()
        
        print(f"\n📊 Processing {player_count} players...")
        
        for (user_id,) in players:
            # Count fairy souls from fairy_soul_locations
            cursor = await conn.execute(
                'SELECT COUNT(*) FROM fairy_soul_locations WHERE user_id = ? AND collected = 1', 
                (user_id,)
            )
            result = await cursor.fetchone()
            souls = result[0] if result else 0
            
            # Update fairy_souls table
            await conn.execute(
                'INSERT OR REPLACE INTO fairy_souls (user_id, souls_collected) VALUES (?, ?)',
                (user_id, souls)
            )
            
            # Update players table
            await conn.execute(
                'UPDATE players SET fairy_souls_collected = ? WHERE user_id = ?',
                (souls, user_id)
            )
        
        await conn.commit()
        print(f"✅ Migrated data for {player_count} players!")
        
        print("\n💚 Updating player health and mana based on fairy souls...")
        cursor = await conn.execute("SELECT user_id, fairy_souls_collected FROM players")
        players = await cursor.fetchall()
        
        updated = 0
        for user_id, souls in players:
            if souls > 0:  # Only update if they have souls
                health_bonus = souls * 3
                mana_bonus = souls * 2
                
                await conn.execute(
                    '''UPDATE players 
                       SET max_health = max_health + ?, 
                           max_mana = max_mana + ? 
                       WHERE user_id = ?''',
                    (health_bonus, mana_bonus, user_id)
                )
                updated += 1
        
        await conn.commit()
        print(f"✅ Updated health/mana for {updated} players with fairy souls!")

if __name__ == '__main__':
    print("🔧 Starting fairy souls migration...")
    asyncio.run(migrate_fairy_souls())
    print("\n✨ Migration complete!")
