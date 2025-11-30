import asyncio
import aiosqlite
import time


async def create_database(db_path: str = 'skyblock.db'):
    print(f"Creating database: {db_path}")
    
    conn = await aiosqlite.connect(db_path)
    conn.row_factory = aiosqlite.Row
    
    print("Creating core player tables...")
    
    await conn.execute('''
    CREATE TABLE IF NOT EXISTS players (
        user_id INTEGER PRIMARY KEY,
        username TEXT NOT NULL,
        coins INTEGER DEFAULT 0,
        bank INTEGER DEFAULT 0,
        bank_capacity INTEGER DEFAULT 10000,
        health INTEGER DEFAULT 100,
        max_health INTEGER DEFAULT 100,
        mana INTEGER DEFAULT 100,
        max_mana INTEGER DEFAULT 100,
        defense INTEGER DEFAULT 0,
        strength INTEGER DEFAULT 0,
        mining_fortune INTEGER DEFAULT 0,
        farming_fortune INTEGER DEFAULT 0,
        foraging_fortune INTEGER DEFAULT 0,
        fishing_speed INTEGER DEFAULT 0,
        total_earned INTEGER DEFAULT 0,
        total_spent INTEGER DEFAULT 0,
        trading_reputation INTEGER DEFAULT 0,
        merchant_level INTEGER DEFAULT 1,
        catacombs_level INTEGER DEFAULT 0,
        catacombs_xp INTEGER DEFAULT 0,
        created_at INTEGER NOT NULL
    )
    ''')
    
    await conn.execute('''
    CREATE TABLE IF NOT EXISTS skills (
        user_id INTEGER NOT NULL,
        skill_name TEXT NOT NULL,
        level INTEGER DEFAULT 0,
        xp INTEGER DEFAULT 0,
        PRIMARY KEY (user_id, skill_name),
        FOREIGN KEY (user_id) REFERENCES players(user_id) ON DELETE CASCADE
    )
    ''')
    
    await conn.execute('''
    CREATE TABLE IF NOT EXISTS collections (
        user_id INTEGER NOT NULL,
        collection_name TEXT NOT NULL,
        amount INTEGER DEFAULT 0,
        PRIMARY KEY (user_id, collection_name),
        FOREIGN KEY (user_id) REFERENCES players(user_id) ON DELETE CASCADE
    )
    ''')
    await conn.execute('''
                       DROP TABLE IF EXISTS fairy_souls''')
    await conn.execute('''
    
    CREATE TABLE IF NOT EXISTS fairy_souls (
        user_id INTEGER NOT NULL,
        location TEXT NOT NULL,
        collected_at INTEGER NOT NULL,
        souls_collected INTEGER DEFAULT 0,
        PRIMARY KEY (user_id, location),
        FOREIGN KEY (user_id) REFERENCES players(user_id) ON DELETE CASCADE
    )
    ''')
    
    print("Creating inventory tables...")
    
    await conn.execute('''
    CREATE TABLE IF NOT EXISTS inventory_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        item_id TEXT NOT NULL,
        amount INTEGER DEFAULT 1,
        slot INTEGER NOT NULL,
        equipped BOOLEAN DEFAULT 0,
        FOREIGN KEY (user_id) REFERENCES players(user_id) ON DELETE CASCADE,
        UNIQUE(user_id, slot)
    )
    ''')
    
    await conn.execute('''
    CREATE TABLE IF NOT EXISTS enderchest (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        item_id TEXT NOT NULL,
        amount INTEGER DEFAULT 1,
        slot INTEGER NOT NULL,
        item_data TEXT,
        FOREIGN KEY (user_id) REFERENCES players(user_id) ON DELETE CASCADE
    )
    ''')
    
    await conn.execute('''
    CREATE TABLE IF NOT EXISTS wardrobe (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        item_id TEXT NOT NULL,
        slot INTEGER NOT NULL,
        item_data TEXT,
        FOREIGN KEY (user_id) REFERENCES players(user_id) ON DELETE CASCADE
    )
    ''')
    
    await conn.execute('''
    CREATE TABLE IF NOT EXISTS armor (
        user_id INTEGER NOT NULL,
        slot TEXT NOT NULL,
        item_id TEXT NOT NULL,
        item_data TEXT,
        PRIMARY KEY (user_id, slot),
        FOREIGN KEY (user_id) REFERENCES players(user_id) ON DELETE CASCADE
    )
    ''')
    
    await conn.execute('''
    CREATE TABLE IF NOT EXISTS accessory_bag (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        item_id TEXT NOT NULL,
        slot INTEGER NOT NULL,
        FOREIGN KEY (user_id) REFERENCES players(user_id) ON DELETE CASCADE
    )
    ''')
    
    print("Creating pet and minion tables...")
    
    await conn.execute('''
    CREATE TABLE IF NOT EXISTS player_pets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        pet_type TEXT NOT NULL,
        rarity TEXT NOT NULL,
        level INTEGER DEFAULT 1,
        xp INTEGER DEFAULT 0,
        active BOOLEAN DEFAULT 0,
        FOREIGN KEY (user_id) REFERENCES players(user_id) ON DELETE CASCADE
    )
    ''')
    
    await conn.execute('''
    CREATE TABLE IF NOT EXISTS player_minions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        minion_type TEXT NOT NULL,
        tier INTEGER DEFAULT 1,
        storage INTEGER DEFAULT 0,
        last_collected INTEGER NOT NULL,
        FOREIGN KEY (user_id) REFERENCES players(user_id) ON DELETE CASCADE
    )
    ''')
    
    print("Creating progression tables...")
    
    await conn.execute('''
    CREATE TABLE IF NOT EXISTS player_progression (
        user_id INTEGER PRIMARY KEY,
        tutorial_completed BOOLEAN DEFAULT 0,
        first_mine_date INTEGER,
        first_farm_date INTEGER,
        first_auction_date INTEGER,
        first_trade_date INTEGER,
        FOREIGN KEY (user_id) REFERENCES players(user_id) ON DELETE CASCADE
    )
    ''')
    
    await conn.execute('''
    CREATE TABLE IF NOT EXISTS player_achievements (
        user_id INTEGER NOT NULL,
        achievement_id TEXT NOT NULL,
        unlocked_at INTEGER NOT NULL,
        PRIMARY KEY (user_id, achievement_id),
        FOREIGN KEY (user_id) REFERENCES players(user_id) ON DELETE CASCADE
    )
    ''')
    
    await conn.execute('''
    CREATE TABLE IF NOT EXISTS rare_drops (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        item_id TEXT NOT NULL,
        rarity TEXT NOT NULL,
        source TEXT NOT NULL,
        timestamp INTEGER NOT NULL,
        FOREIGN KEY (user_id) REFERENCES players(user_id) ON DELETE CASCADE
    )
    ''')
    
    print("Creating market tables...")
    
    await conn.execute('''
    CREATE TABLE IF NOT EXISTS bazaar_products (
        product_id TEXT PRIMARY KEY,
        buy_price REAL NOT NULL,
        sell_price REAL NOT NULL,
        buy_volume INTEGER DEFAULT 0,
        sell_volume INTEGER DEFAULT 0,
        last_update INTEGER NOT NULL
    )
    ''')
    
    await conn.execute('''
    CREATE TABLE IF NOT EXISTS bazaar_orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        product_id TEXT NOT NULL,
        order_type TEXT NOT NULL,
        price REAL NOT NULL,
        amount INTEGER NOT NULL,
        filled INTEGER DEFAULT 0,
        active BOOLEAN DEFAULT 1,
        created_at INTEGER NOT NULL,
        FOREIGN KEY (user_id) REFERENCES players(user_id) ON DELETE CASCADE
    )
    ''')
    
    await conn.execute('''
    CREATE TABLE IF NOT EXISTS auction_house (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        seller_id INTEGER NOT NULL,
        item_id TEXT NOT NULL,
        starting_bid INTEGER NOT NULL,
        current_bid INTEGER DEFAULT 0,
        highest_bidder_id INTEGER,
        buy_now_price INTEGER,
        end_time INTEGER NOT NULL,
        bin BOOLEAN DEFAULT 0,
        ended BOOLEAN DEFAULT 0,
        claimed BOOLEAN DEFAULT 0,
        created_at INTEGER NOT NULL,
        item_data TEXT,
        FOREIGN KEY (seller_id) REFERENCES players(user_id) ON DELETE CASCADE,
        FOREIGN KEY (highest_bidder_id) REFERENCES players(user_id) ON DELETE SET NULL
    )
    ''')
    
    await conn.execute('''
    CREATE TABLE IF NOT EXISTS bazaar_transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        seller_id INTEGER NOT NULL,
        buyer_id INTEGER NOT NULL,
        product_id TEXT NOT NULL,
        amount INTEGER NOT NULL,
        price REAL NOT NULL,
        timestamp INTEGER NOT NULL
    )
    ''')
    
    await conn.execute('''
    CREATE TABLE IF NOT EXISTS bazaar_flips (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        product_id TEXT NOT NULL,
        buy_price REAL NOT NULL,
        sell_price REAL NOT NULL,
        amount INTEGER NOT NULL,
        profit REAL NOT NULL,
        timestamp INTEGER NOT NULL,
        FOREIGN KEY (user_id) REFERENCES players(user_id) ON DELETE CASCADE
    )
    ''')
    
    await conn.execute('''
    CREATE TABLE IF NOT EXISTS market_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id TEXT NOT NULL,
        price REAL NOT NULL,
        volume INTEGER NOT NULL,
        timestamp INTEGER NOT NULL
    )
    ''')
    
    await conn.execute('''
    CREATE TABLE IF NOT EXISTS auction_bots (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        bot_name TEXT NOT NULL,
        coins INTEGER DEFAULT 100000,
        trading_strategy TEXT NOT NULL,
        risk_tolerance REAL DEFAULT 0.5,
        trades_completed INTEGER DEFAULT 0
    )
    ''')
    
    await conn.execute('''
    CREATE TABLE IF NOT EXISTS merchant_deals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        npc_name TEXT NOT NULL,
        item_id TEXT NOT NULL,
        buy_price INTEGER,
        sell_price INTEGER,
        stock INTEGER DEFAULT -1,
        expires_at INTEGER,
        active BOOLEAN DEFAULT 1
    )
    ''')
    
    print("Creating stocks and trading tables...")
    
    await conn.execute('''
    CREATE TABLE IF NOT EXISTS stocks (
        symbol TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        current_price REAL NOT NULL,
        open_price REAL NOT NULL,
        high_price REAL NOT NULL,
        low_price REAL NOT NULL,
        volume INTEGER DEFAULT 0,
        last_update INTEGER NOT NULL
    )
    ''')
    
    await conn.execute('''
    CREATE TABLE IF NOT EXISTS player_stocks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        symbol TEXT NOT NULL,
        shares INTEGER NOT NULL,
        avg_buy_price REAL NOT NULL,
        FOREIGN KEY (user_id) REFERENCES players(user_id) ON DELETE CASCADE,
        UNIQUE(user_id, symbol)
    )
    ''')
    
    print("Creating quest tables...")
    
    await conn.execute('''
    CREATE TABLE IF NOT EXISTS player_quests (
        user_id INTEGER NOT NULL,
        quest_id TEXT NOT NULL,
        progress INTEGER DEFAULT 0,
        completed BOOLEAN DEFAULT 0,
        claimed BOOLEAN DEFAULT 0,
        started_at INTEGER NOT NULL,
        completed_at INTEGER,
        PRIMARY KEY (user_id, quest_id),
        FOREIGN KEY (user_id) REFERENCES players(user_id) ON DELETE CASCADE
    )
    ''')
    
    await conn.execute('''
    CREATE TABLE IF NOT EXISTS daily_rewards (
        user_id INTEGER PRIMARY KEY,
        last_claim INTEGER NOT NULL,
        streak INTEGER DEFAULT 0,
        FOREIGN KEY (user_id) REFERENCES players(user_id) ON DELETE CASCADE
    )
    ''')
    
    print("Creating game data tables...")
    
    await conn.execute('''
    CREATE TABLE IF NOT EXISTS game_items (
        item_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        rarity TEXT NOT NULL,
        item_type TEXT NOT NULL,
        stats TEXT,
        lore TEXT,
        special_ability TEXT,
        craft_recipe TEXT,
        npc_sell_price INTEGER DEFAULT 0,
        collection_req TEXT,
        default_bazaar_price REAL DEFAULT 100
    )
    ''')
    
    await conn.execute('''
    CREATE TABLE IF NOT EXISTS enchantments (
        enchant_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        max_level INTEGER NOT NULL,
        applies_to TEXT NOT NULL,
        description TEXT,
        stat_bonuses TEXT
    )
    ''')
    
    await conn.execute('''
    CREATE TABLE IF NOT EXISTS reforges (
        reforge_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        applies_to TEXT NOT NULL,
        stat_bonuses TEXT NOT NULL,
        cost_formula TEXT
    )
    ''')
    
    await conn.execute('''
    CREATE TABLE IF NOT EXISTS loot_tables (
        table_id TEXT PRIMARY KEY,
        category TEXT NOT NULL,
        loot_data TEXT NOT NULL
    )
    ''')
    
    await conn.execute('''
    CREATE TABLE IF NOT EXISTS skill_configs (
        skill_name TEXT PRIMARY KEY,
        display_name TEXT NOT NULL,
        max_level INTEGER NOT NULL,
        xp_requirements TEXT NOT NULL,
        level_rewards TEXT,
        stat_bonuses TEXT
    )
    ''')
    
    await conn.execute('''
    CREATE TABLE IF NOT EXISTS game_pets (
        pet_id INTEGER PRIMARY KEY AUTOINCREMENT,
        pet_type TEXT NOT NULL,
        rarity TEXT NOT NULL,
        stats TEXT NOT NULL,
        max_level INTEGER DEFAULT 100,
        description TEXT,
        UNIQUE(pet_type, rarity)
    )
    ''')
    
    await conn.execute('''
    CREATE TABLE IF NOT EXISTS minion_data (
        minion_type TEXT PRIMARY KEY,
        base_speed INTEGER NOT NULL,
        max_tier INTEGER DEFAULT 11,
        drops TEXT NOT NULL
    )
    ''')
    
    await conn.execute('''
    CREATE TABLE IF NOT EXISTS collection_items (
        collection_id TEXT PRIMARY KEY,
        display_name TEXT NOT NULL,
        emoji TEXT,
        category TEXT NOT NULL
    )
    ''')
    
    await conn.execute('''
    CREATE TABLE IF NOT EXISTS mob_locations (
        mob_id TEXT NOT NULL,
        location_name TEXT NOT NULL,
        required_level INTEGER DEFAULT 0,
        PRIMARY KEY (mob_id, location_name)
    )
    ''')
    
    await conn.execute('''
    CREATE TABLE IF NOT EXISTS dungeon_floors (
        floor_id TEXT PRIMARY KEY,
        floor_number INTEGER NOT NULL,
        required_level INTEGER DEFAULT 0,
        boss_name TEXT,
        loot_table TEXT
    )
    ''')
    
    await conn.execute('''
    CREATE TABLE IF NOT EXISTS slayer_bosses (
        slayer_type TEXT NOT NULL,
        tier INTEGER NOT NULL,
        health INTEGER NOT NULL,
        damage INTEGER NOT NULL,
        cost INTEGER NOT NULL,
        xp_reward INTEGER NOT NULL,
        PRIMARY KEY (slayer_type, tier)
    )
    ''')
    
    await conn.execute('''
    CREATE TABLE IF NOT EXISTS crafting_recipes (
        recipe_id INTEGER PRIMARY KEY AUTOINCREMENT,
        output_item TEXT NOT NULL,
        ingredients TEXT NOT NULL,
        crafting_station TEXT
    )
    ''')
    
    print("Creating indexes...")
    
    await conn.execute('CREATE INDEX IF NOT EXISTS idx_inventory_user ON inventory_items(user_id)')
    await conn.execute('CREATE INDEX IF NOT EXISTS idx_inventory_item ON inventory_items(item_id)')
    await conn.execute('CREATE INDEX IF NOT EXISTS idx_skills_user ON skills(user_id)')
    await conn.execute('CREATE INDEX IF NOT EXISTS idx_collections_user ON collections(user_id)')
    await conn.execute('CREATE INDEX IF NOT EXISTS idx_bazaar_orders_user ON bazaar_orders(user_id)')
    await conn.execute('CREATE INDEX IF NOT EXISTS idx_bazaar_orders_product ON bazaar_orders(product_id)')
    await conn.execute('CREATE INDEX IF NOT EXISTS idx_auction_house_seller ON auction_house(seller_id)')
    await conn.execute('CREATE INDEX IF NOT EXISTS idx_auction_house_status ON auction_house(ended, claimed)')
    await conn.execute('CREATE INDEX IF NOT EXISTS idx_pets_user ON pets(user_id)')
    await conn.execute('CREATE INDEX IF NOT EXISTS idx_pets_active ON pets(user_id, active)')
    await conn.execute('CREATE INDEX IF NOT EXISTS idx_minions_user ON minions(user_id)')
    
    await conn.commit()
    await conn.close()
    
    print("✅ All database tables created successfully!")


if __name__ == "__main__":
    asyncio.run(create_database())
