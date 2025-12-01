#!/usr/bin/env python3
"""
Quick fix script to add missing normalized player tables to the database.
This creates the player_stats, player_economy, and player_dungeon_stats tables
that are expected by the codebase.
"""
import asyncio
import aiosqlite


async def add_missing_tables():
    print("=" * 60)
    print("Adding missing normalized player tables...")
    print("=" * 60)
    
    conn = await aiosqlite.connect("skyblock.db")
    
    try:
        # Create player_stats table
        print("Creating player_stats table...")
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS player_stats (
                user_id INTEGER PRIMARY KEY,
                health INTEGER DEFAULT 100,
                max_health INTEGER DEFAULT 100,
                mana INTEGER DEFAULT 20,
                max_mana INTEGER DEFAULT 20,
                defense INTEGER DEFAULT 0,
                strength INTEGER DEFAULT 5,
                crit_chance INTEGER DEFAULT 5,
                crit_damage INTEGER DEFAULT 50,
                intelligence INTEGER DEFAULT 0,
                speed INTEGER DEFAULT 100,
                sea_creature_chance INTEGER DEFAULT 5,
                magic_find INTEGER DEFAULT 0,
                pet_luck INTEGER DEFAULT 0,
                ferocity INTEGER DEFAULT 0,
                ability_damage INTEGER DEFAULT 0,
                mining_speed INTEGER DEFAULT 0,
                mining_fortune INTEGER DEFAULT 0,
                farming_fortune INTEGER DEFAULT 0,
                foraging_fortune INTEGER DEFAULT 0,
                fishing_speed INTEGER DEFAULT 0,
                attack_speed INTEGER DEFAULT 0,
                true_defense INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES players(user_id) ON DELETE CASCADE
            )
        ''')
        
        # Migrate existing player stats
        print("Migrating existing player data to player_stats...")
        await conn.execute('''
            INSERT OR IGNORE INTO player_stats (
                user_id, health, max_health, mana, max_mana, defense, strength,
                mining_fortune, farming_fortune, foraging_fortune, fishing_speed
            )
            SELECT 
                user_id, 
                COALESCE(health, 100), 
                COALESCE(max_health, 100), 
                COALESCE(mana, 20), 
                COALESCE(max_mana, 20), 
                COALESCE(defense, 0), 
                COALESCE(strength, 5),
                COALESCE(mining_fortune, 0), 
                COALESCE(farming_fortune, 0), 
                COALESCE(foraging_fortune, 0), 
                COALESCE(fishing_speed, 0)
            FROM players
        ''')
        
        # Create player_economy table
        print("Creating player_economy table...")
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS player_economy (
                user_id INTEGER PRIMARY KEY,
                coins INTEGER DEFAULT 100,
                bank INTEGER DEFAULT 0,
                bank_capacity INTEGER DEFAULT 5000,
                total_earned INTEGER DEFAULT 0,
                total_spent INTEGER DEFAULT 0,
                trading_reputation INTEGER DEFAULT 0,
                merchant_level INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES players(user_id) ON DELETE CASCADE
            )
        ''')
        
        # Migrate existing economy data
        print("Migrating existing economy data...")
        await conn.execute('''
            INSERT OR IGNORE INTO player_economy (
                user_id, coins, bank, bank_capacity, total_earned, 
                total_spent, trading_reputation, merchant_level
            )
            SELECT 
                user_id, 
                COALESCE(coins, 0), 
                COALESCE(bank, 0), 
                COALESCE(bank_capacity, 5000),
                COALESCE(total_earned, 0), 
                COALESCE(total_spent, 0), 
                COALESCE(trading_reputation, 0), 
                COALESCE(merchant_level, 0)
            FROM players
        ''')
        
        # Create player_dungeon_stats table
        print("Creating player_dungeon_stats table...")
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS player_dungeon_stats (
                user_id INTEGER PRIMARY KEY,
                catacombs_level INTEGER DEFAULT 0,
                catacombs_xp INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES players(user_id) ON DELETE CASCADE
            )
        ''')
        
        # Migrate existing dungeon data
        print("Migrating existing dungeon data...")
        await conn.execute('''
            INSERT OR IGNORE INTO player_dungeon_stats (
                user_id, catacombs_level, catacombs_xp
            )
            SELECT 
                user_id, 
                COALESCE(catacombs_level, 0), 
                COALESCE(catacombs_xp, 0)
            FROM players
        ''')
        
        # Create player_slayer_progress table
        print("Creating player_slayer_progress table...")
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS player_slayer_progress (
                user_id INTEGER NOT NULL,
                slayer_type TEXT NOT NULL,
                xp INTEGER DEFAULT 0,
                level INTEGER DEFAULT 0,
                total_kills INTEGER DEFAULT 0,
                PRIMARY KEY (user_id, slayer_type),
                FOREIGN KEY (user_id) REFERENCES players(user_id) ON DELETE CASCADE
            )
        ''')
        
        # Create indexes
        print("Creating indexes...")
        await conn.execute('CREATE INDEX IF NOT EXISTS idx_player_stats_user ON player_stats(user_id)')
        await conn.execute('CREATE INDEX IF NOT EXISTS idx_player_economy_user ON player_economy(user_id)')
        await conn.execute('CREATE INDEX IF NOT EXISTS idx_player_dungeon_stats_user ON player_dungeon_stats(user_id)')
        await conn.execute('CREATE INDEX IF NOT EXISTS idx_player_slayer_progress ON player_slayer_progress(user_id, slayer_type)')
        
        await conn.commit()
        print()
        print("=" * 60)
        print("✅ Successfully added missing tables!")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        await conn.rollback()
        raise
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(add_missing_tables())
