import asyncio
import aiosqlite
from pathlib import Path


async def create_tables(db_path: str):
    conn = await aiosqlite.connect(db_path)
    
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS game_items (
            item_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            rarity TEXT,
            item_type TEXT,
            stats TEXT,
            lore TEXT,
            special_ability TEXT,
            craft_recipe TEXT,
            npc_sell_price INTEGER DEFAULT 0,
            collection_req TEXT,
            default_bazaar_price REAL DEFAULT 0
        )
    ''')
    
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS enchantments (
            enchant_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            max_level INTEGER,
            applies_to TEXT,
            description TEXT,
            stat_bonuses TEXT
        )
    ''')
    
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS reforges (
            reforge_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            applies_to TEXT,
            stat_bonuses TEXT,
            cost_formula TEXT
        )
    ''')
    
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS loot_tables (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            table_id TEXT NOT NULL,
            category TEXT,
            loot_data TEXT,
            coins_min INTEGER DEFAULT 0,
            coins_max INTEGER DEFAULT 0,
            xp_reward INTEGER DEFAULT 0
        )
    ''')
    
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS skill_configs (
            skill_name TEXT PRIMARY KEY,
            display_name TEXT,
            max_level INTEGER,
            xp_requirements TEXT,
            level_rewards TEXT,
            stat_bonuses TEXT
        )
    ''')
    
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS game_pets (
            pet_id TEXT PRIMARY KEY,
            pet_type TEXT NOT NULL,
            rarity TEXT NOT NULL,
            stats TEXT,
            max_level INTEGER,
            description TEXT
        )
    ''')
    
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS game_minions (
            minion_type TEXT PRIMARY KEY,
            produces TEXT,
            base_speed INTEGER,
            max_tier INTEGER,
            category TEXT,
            description TEXT
        )
    ''')
    
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS game_events (
            event_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            duration INTEGER,
            occurs_every INTEGER,
            bonuses TEXT
        )
    ''')
    
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS game_quests (
            quest_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            requirement_type TEXT,
            requirement_item TEXT,
            requirement_amount INTEGER,
            reward_coins INTEGER,
            reward_items TEXT
        )
    ''')
    
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS collection_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT,
            item_id TEXT,
            display_name TEXT,
            emoji TEXT
        )
    ''')
    
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS mob_locations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            location_id TEXT,
            mob_id TEXT,
            mob_name TEXT,
            health INTEGER,
            damage INTEGER,
            coins INTEGER,
            xp INTEGER
        )
    ''')
    
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS dungeon_floors (
            floor_id TEXT PRIMARY KEY,
            name TEXT,
            rewards INTEGER,
            time INTEGER
        )
    ''')
    
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS slayer_bosses (
            boss_id TEXT PRIMARY KEY,
            name TEXT,
            emoji TEXT,
            tier_data TEXT
        )
    ''')
    
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS slayer_drops (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            boss_id TEXT,
            item_id TEXT,
            min_amt INTEGER,
            max_amt INTEGER,
            drop_chance REAL
        )
    ''')
    
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS seasons (
            season_id INTEGER PRIMARY KEY,
            season_name TEXT
        )
    ''')
    
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS mayors (
            mayor_id TEXT PRIMARY KEY,
            name TEXT,
            perks TEXT
        )
    ''')
    
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS gathering_drops (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            gathering_type TEXT,
            resource_type TEXT,
            item_id TEXT,
            drop_chance REAL,
            min_amt INTEGER,
            max_amt INTEGER
        )
    ''')
    
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS rarity_colors (
            rarity TEXT PRIMARY KEY,
            color_hex TEXT
        )
    ''')
    
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS tool_tiers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tool_type TEXT,
            tier INTEGER,
            item_id TEXT,
            name TEXT,
            stats TEXT,
            recipe TEXT
        )
    ''')
    
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS crafting_recipes (
            recipe_id TEXT PRIMARY KEY,
            output_item TEXT,
            ingredients TEXT
        )
    ''')
    
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS bazaar_products (
            product_id TEXT PRIMARY KEY,
            buy_price REAL,
            sell_price REAL,
            buy_volume INTEGER DEFAULT 0,
            sell_volume INTEGER DEFAULT 0,
            last_update INTEGER DEFAULT 0
        )
    ''')
    
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS bazaar_bots (
            bot_id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id TEXT NOT NULL,
            min_buy_price REAL,
            max_sell_price REAL,
            stock INTEGER DEFAULT 0,
            created_at INTEGER DEFAULT 0
        )
    ''')
    
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS auction_bots (
            bot_id INTEGER PRIMARY KEY AUTOINCREMENT,
            bot_name TEXT NOT NULL,
            min_bid INTEGER,
            max_bid INTEGER,
            target_categories TEXT,
            active INTEGER DEFAULT 1
        )
    ''')
    
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS stock_market (
            symbol TEXT PRIMARY KEY,
            current_price REAL,
            change_percent REAL,
            volume INTEGER,
            last_update INTEGER
        )
    ''')
    
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS merchant_deals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id TEXT,
            price INTEGER,
            stock INTEGER,
            duration INTEGER,
            created_at INTEGER,
            active INTEGER DEFAULT 1
        )
    ''')
    
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS bazaar_flips (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            product_id TEXT,
            buy_price REAL,
            sell_price REAL,
            profit REAL,
            timestamp INTEGER
        )
    ''')
    
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS bazaar_orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            product_id TEXT,
            order_type TEXT,
            amount INTEGER,
            price REAL,
            created_at INTEGER
        )
    ''')
    
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS auctions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            seller_id INTEGER,
            item_id TEXT,
            amount INTEGER,
            starting_bid INTEGER,
            current_bid INTEGER,
            bin_price INTEGER,
            end_time INTEGER,
            bin INTEGER DEFAULT 0,
            ended INTEGER DEFAULT 0,
            winner_id INTEGER
        )
    ''')
    
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS fairy_soul_locations (
            location TEXT PRIMARY KEY
        )
    ''')
    
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS collected_fairy_souls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            location TEXT,
            collected_at INTEGER
        )
    ''')
    
    await conn.commit()
    await conn.close()
    
    print("✅ All game tables created successfully!")


async def main():
    db_path = 'skyblock.db'
    print(f"Creating tables in {db_path}...")
    await create_tables(db_path)


if __name__ == "__main__":
    asyncio.run(main())
