import aiosqlite


class DatabaseBase:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn: aiosqlite.Connection

    async def initialize(self):
        self.conn = await aiosqlite.connect(self.db_path)
        await self._create_tables()

    async def _create_tables(self):
        await self.conn.execute('''
            CREATE TABLE IF NOT EXISTS players (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                coins INTEGER DEFAULT 100,
                bank INTEGER DEFAULT 0,
                bank_capacity INTEGER DEFAULT 5000,
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
                trading_reputation INTEGER DEFAULT 0,
                merchant_level INTEGER DEFAULT 0,
                playtime_minutes INTEGER DEFAULT 0,
                total_earned INTEGER DEFAULT 0,
                total_spent INTEGER DEFAULT 0,
                catacombs_level INTEGER DEFAULT 0,
                catacombs_xp INTEGER DEFAULT 0,
                revenant_xp INTEGER DEFAULT 0,
                tarantula_xp INTEGER DEFAULT 0,
                sven_xp INTEGER DEFAULT 0,
                voidgloom_xp INTEGER DEFAULT 0,
                inferno_xp INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        await self.conn.execute('''
            CREATE TABLE IF NOT EXISTS skills (
                user_id INTEGER,
                skill_name TEXT,
                xp INTEGER DEFAULT 0,
                level INTEGER DEFAULT 0,
                PRIMARY KEY (user_id, skill_name),
                FOREIGN KEY (user_id) REFERENCES players(user_id)
            )
        ''')
        
        await self.conn.execute('''
            CREATE TABLE IF NOT EXISTS collections (
                user_id INTEGER,
                collection_name TEXT,
                amount INTEGER DEFAULT 0,
                tier INTEGER DEFAULT 0,
                PRIMARY KEY (user_id, collection_name),
                FOREIGN KEY (user_id) REFERENCES players(user_id)
            )
        ''')
        
        # Inventory tables
        await self.conn.execute('''
            CREATE TABLE IF NOT EXISTS inventories (
                user_id INTEGER,
                slot INTEGER,
                item_id TEXT,
                item_data TEXT,
                PRIMARY KEY (user_id, slot),
                FOREIGN KEY (user_id) REFERENCES players(user_id)
            )
        ''')
        
        await self.conn.execute('''
            CREATE TABLE IF NOT EXISTS enderchest (
                user_id INTEGER,
                slot INTEGER,
                item_id TEXT,
                item_data TEXT,
                PRIMARY KEY (user_id, slot),
                FOREIGN KEY (user_id) REFERENCES players(user_id)
            )
        ''')
        
        await self.conn.execute('''
            CREATE TABLE IF NOT EXISTS armor (
                user_id INTEGER,
                slot TEXT,
                item_id TEXT,
                item_data TEXT,
                PRIMARY KEY (user_id, slot),
                FOREIGN KEY (user_id) REFERENCES players(user_id)
            )
        ''')
        
        await self.conn.execute('''
            CREATE TABLE IF NOT EXISTS wardrobe (
                user_id INTEGER,
                slot INTEGER,
                item_id TEXT,
                item_data TEXT,
                PRIMARY KEY (user_id, slot),
                FOREIGN KEY (user_id) REFERENCES players(user_id)
            )
        ''')
        
        await self.conn.execute('''
            CREATE TABLE IF NOT EXISTS accessory_bag (
                user_id INTEGER,
                slot INTEGER,
                item_id TEXT,
                item_data TEXT,
                PRIMARY KEY (user_id, slot),
                FOREIGN KEY (user_id) REFERENCES players(user_id)
            )
        ''')
        
        # Market tables
        await self.conn.execute('''
            CREATE TABLE IF NOT EXISTS auction_house (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                seller_id INTEGER,
                item_id TEXT,
                item_data TEXT,
                starting_bid INTEGER,
                current_bid INTEGER,
                highest_bidder_id INTEGER,
                buy_now_price INTEGER,
                end_time INTEGER,
                bin BOOLEAN DEFAULT 0,
                ended BOOLEAN DEFAULT 0,
                claimed BOOLEAN DEFAULT 0,
                created_at INTEGER,
                FOREIGN KEY (seller_id) REFERENCES players(user_id)
            )
        ''')
        
        await self.conn.execute('''
            CREATE TABLE IF NOT EXISTS auction_bids (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                auction_id INTEGER,
                bidder_id INTEGER,
                bid_amount INTEGER,
                timestamp INTEGER,
                FOREIGN KEY (auction_id) REFERENCES auction_house(id),
                FOREIGN KEY (bidder_id) REFERENCES players(user_id)
            )
        ''')
        
        await self.conn.execute('''
            CREATE TABLE IF NOT EXISTS bazaar_products (
                product_id TEXT PRIMARY KEY,
                buy_price REAL DEFAULT 0,
                sell_price REAL DEFAULT 0,
                buy_volume INTEGER DEFAULT 0,
                sell_volume INTEGER DEFAULT 0,
                last_update INTEGER
            )
        ''')
        
        await self.conn.execute('''
            CREATE TABLE IF NOT EXISTS bazaar_orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                product_id TEXT,
                order_type TEXT,
                price REAL,
                amount INTEGER,
                filled INTEGER DEFAULT 0,
                active BOOLEAN DEFAULT 1,
                created_at INTEGER,
                FOREIGN KEY (user_id) REFERENCES players(user_id),
                FOREIGN KEY (product_id) REFERENCES bazaar_products(product_id)
            )
        ''')
        
        await self.conn.execute('''
            CREATE TABLE IF NOT EXISTS bazaar_transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                buyer_id INTEGER,
                seller_id INTEGER,
                product_id TEXT,
                amount INTEGER,
                price REAL,
                timestamp INTEGER,
                FOREIGN KEY (buyer_id) REFERENCES players(user_id),
                FOREIGN KEY (seller_id) REFERENCES players(user_id),
                FOREIGN KEY (product_id) REFERENCES bazaar_products(product_id)
            )
        ''')
        
        await self.conn.execute('''
            CREATE TABLE IF NOT EXISTS market_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id TEXT,
                price REAL,
                volume INTEGER,
                timestamp INTEGER,
                transaction_type TEXT
            )
        ''')
        
        await self.conn.execute('''
            CREATE TABLE IF NOT EXISTS price_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_id TEXT,
                price REAL,
                volume INTEGER,
                timestamp INTEGER,
                price_type TEXT,
                source TEXT
            )
        ''')
        
        # Trading tables
        await self.conn.execute('''
            CREATE TABLE IF NOT EXISTS bot_traders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bot_name TEXT,
                coins INTEGER DEFAULT 100000,
                trading_behavior TEXT,
                active BOOLEAN DEFAULT 1
            )
        ''')
        
        await self.conn.execute('''
            CREATE TABLE IF NOT EXISTS auction_bot_traders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bot_name TEXT UNIQUE,
                coins INTEGER DEFAULT 500000,
                items_owned TEXT DEFAULT '{}',
                trading_strategy TEXT,
                risk_tolerance REAL DEFAULT 0.5,
                active BOOLEAN DEFAULT 1,
                total_profit INTEGER DEFAULT 0,
                trades_completed INTEGER DEFAULT 0,
                success_rate REAL DEFAULT 0.5
            )
        ''')
        
        await self.conn.execute('''
            CREATE TABLE IF NOT EXISTS stock_market (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                stock_symbol TEXT UNIQUE,
                company_name TEXT,
                current_price REAL,
                opening_price REAL,
                daily_high REAL,
                daily_low REAL,
                volume INTEGER DEFAULT 0,
                market_cap INTEGER,
                volatility REAL DEFAULT 0.1,
                last_update INTEGER
            )
        ''')
        
        await self.conn.execute('''
            CREATE TABLE IF NOT EXISTS player_stocks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                stock_symbol TEXT,
                shares INTEGER DEFAULT 0,
                avg_buy_price REAL,
                FOREIGN KEY (user_id) REFERENCES players(user_id),
                FOREIGN KEY (stock_symbol) REFERENCES stock_market(stock_symbol),
                UNIQUE(user_id, stock_symbol)
            )
        ''')
        
        await self.conn.execute('''
            CREATE TABLE IF NOT EXISTS stock_orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                stock_symbol TEXT,
                order_type TEXT,
                shares INTEGER,
                price_limit REAL,
                filled_shares INTEGER DEFAULT 0,
                status TEXT DEFAULT 'pending',
                created_at INTEGER,
                FOREIGN KEY (user_id) REFERENCES players(user_id)
            )
        ''')
        
        await self.conn.execute('''
            CREATE TABLE IF NOT EXISTS merchant_deals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                npc_name TEXT,
                item_id TEXT,
                quantity INTEGER,
                price INTEGER,
                deal_type TEXT,
                expires_at INTEGER,
                available BOOLEAN DEFAULT 1
            )
        ''')
        
        # Pet and minion tables
        await self.conn.execute('''
            CREATE TABLE IF NOT EXISTS pets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                pet_type TEXT,
                rarity TEXT,
                level INTEGER DEFAULT 1,
                xp INTEGER DEFAULT 0,
                held_item TEXT,
                active BOOLEAN DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES players(user_id)
            )
        ''')
        
        await self.conn.execute('''
            CREATE TABLE IF NOT EXISTS minions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                minion_type TEXT,
                tier INTEGER,
                island_slot INTEGER,
                fuel INTEGER DEFAULT 0,
                storage TEXT,
                FOREIGN KEY (user_id) REFERENCES players(user_id)
            )
        ''')
        
        # Quest and progression tables
        await self.conn.execute('''
            CREATE TABLE IF NOT EXISTS player_quests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                quest_id TEXT,
                progress INTEGER DEFAULT 0,
                completed BOOLEAN DEFAULT 0,
                claimed BOOLEAN DEFAULT 0,
                started_at INTEGER,
                FOREIGN KEY (user_id) REFERENCES players(user_id)
            )
        ''')
        
        await self.conn.execute('''
            CREATE TABLE IF NOT EXISTS daily_rewards (
                user_id INTEGER PRIMARY KEY,
                last_claim INTEGER,
                streak INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES players(user_id)
            )
        ''')
        
        await self.conn.execute('''
            CREATE TABLE IF NOT EXISTS player_progression (
                user_id INTEGER PRIMARY KEY,
                tutorial_completed BOOLEAN DEFAULT 0,
                first_mine_date INTEGER,
                first_farm_date INTEGER,
                first_auction_date INTEGER,
                first_trade_date INTEGER,
                unlocked_locations TEXT DEFAULT '["hub"]',
                achievements TEXT DEFAULT '[]',
                FOREIGN KEY (user_id) REFERENCES players(user_id)
            )
        ''')
        
        # Tracking tables
        await self.conn.execute('''
            CREATE TABLE IF NOT EXISTS dungeon_stats (
                user_id INTEGER,
                floor TEXT,
                completions INTEGER DEFAULT 0,
                fastest_time INTEGER,
                best_score INTEGER DEFAULT 0,
                PRIMARY KEY (user_id, floor),
                FOREIGN KEY (user_id) REFERENCES players(user_id)
            )
        ''')
        
        await self.conn.execute('''
            CREATE TABLE IF NOT EXISTS slayer_stats (
                user_id INTEGER,
                slayer_type TEXT,
                xp INTEGER DEFAULT 0,
                level INTEGER DEFAULT 0,
                kills INTEGER DEFAULT 0,
                PRIMARY KEY (user_id, slayer_type),
                FOREIGN KEY (user_id) REFERENCES players(user_id)
            )
        ''')
        
        await self.conn.execute('''
            CREATE TABLE IF NOT EXISTS fairy_souls (
                user_id INTEGER,
                location TEXT,
                collected BOOLEAN DEFAULT 0,
                PRIMARY KEY (user_id, location),
                FOREIGN KEY (user_id) REFERENCES players(user_id)
            )
        ''')
        
        await self.conn.execute('''
            CREATE TABLE IF NOT EXISTS item_rarity_drops (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                item_id TEXT,
                rarity TEXT,
                dropped_from TEXT,
                timestamp INTEGER,
                FOREIGN KEY (user_id) REFERENCES players(user_id)
            )
        ''')
        
        await self.conn.execute('''
            CREATE TABLE IF NOT EXISTS auction_snipes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                auction_id INTEGER,
                item_id TEXT,
                purchase_price INTEGER,
                estimated_value INTEGER,
                profit_potential INTEGER,
                timestamp INTEGER,
                FOREIGN KEY (user_id) REFERENCES players(user_id)
            )
        ''')
        
        await self.conn.execute('''
            CREATE TABLE IF NOT EXISTS bazaar_flips (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                item_id TEXT,
                buy_price REAL,
                sell_price REAL,
                quantity INTEGER,
                profit INTEGER,
                timestamp INTEGER,
                FOREIGN KEY (user_id) REFERENCES players(user_id)
            )
        ''')
        
        # Game data tables
        await self.conn.execute('''
            CREATE TABLE IF NOT EXISTS game_items (
                item_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                rarity TEXT NOT NULL,
                type TEXT NOT NULL,
                stats TEXT,
                lore TEXT,
                special_ability TEXT,
                craft_recipe TEXT,
                npc_sell_price INTEGER DEFAULT 0,
                collection_req TEXT,
                default_bazaar_price REAL DEFAULT 100
            )
        ''')
        
        await self.conn.execute('''
            CREATE TABLE IF NOT EXISTS game_enchantments (
                enchant_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                max_level INTEGER NOT NULL,
                applies_to TEXT,
                description TEXT,
                stat_bonuses TEXT
            )
        ''')
        
        await self.conn.execute('''
            CREATE TABLE IF NOT EXISTS game_loot_tables (
                table_id TEXT PRIMARY KEY,
                category TEXT NOT NULL,
                rarity TEXT NOT NULL,
                loot_data TEXT NOT NULL,
                coins_min INTEGER DEFAULT 0,
                coins_max INTEGER DEFAULT 0,
                xp_reward INTEGER DEFAULT 0
            )
        ''')
        
        await self.conn.execute('''
            CREATE TABLE IF NOT EXISTS game_skills (
                skill_name TEXT PRIMARY KEY,
                display_name TEXT NOT NULL,
                max_level INTEGER DEFAULT 50,
                xp_requirements TEXT,
                level_rewards TEXT,
                stat_bonuses TEXT
            )
        ''')
        
        await self.conn.execute('''
            CREATE TABLE IF NOT EXISTS game_reforges (
                reforge_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                applies_to TEXT,
                stat_bonuses TEXT,
                cost_formula TEXT
            )
        ''')
        
        await self.conn.execute('''
            CREATE TABLE IF NOT EXISTS game_pets (
                pet_id TEXT PRIMARY KEY,
                pet_type TEXT NOT NULL,
                rarity TEXT NOT NULL,
                stats TEXT,
                max_level INTEGER DEFAULT 100,
                description TEXT
            )
        ''')
        
        await self.conn.execute('''
            CREATE TABLE IF NOT EXISTS game_minions (
                minion_type TEXT PRIMARY KEY,
                produces TEXT NOT NULL,
                base_speed INTEGER NOT NULL,
                max_tier INTEGER DEFAULT 11,
                category TEXT NOT NULL,
                description TEXT
            )
        ''')
        
        await self.conn.execute('''
            CREATE TABLE IF NOT EXISTS game_events (
                event_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                duration INTEGER NOT NULL,
                occurs_every INTEGER NOT NULL,
                bonuses TEXT
            )
        ''')
        
        await self.conn.execute('''
            CREATE TABLE IF NOT EXISTS game_quests (
                quest_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                requirement_type TEXT NOT NULL,
                requirement_item TEXT,
                requirement_amount INTEGER,
                reward_coins INTEGER DEFAULT 0,
                reward_items TEXT
            )
        ''')
        
        await self.conn.execute('''
            CREATE TABLE IF NOT EXISTS game_crafting_recipes (
                recipe_id TEXT PRIMARY KEY,
                result_item TEXT NOT NULL,
                ingredients TEXT NOT NULL,
                category TEXT,
                requires_table TEXT
            )
        ''')
        
        await self.conn.execute('''
            CREATE TABLE IF NOT EXISTS game_collection_categories (
                category_name TEXT PRIMARY KEY,
                display_name TEXT NOT NULL,
                items TEXT NOT NULL
            )
        ''')
        
        await self.conn.execute('''
            CREATE TABLE IF NOT EXISTS game_mobs (
                mob_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                health INTEGER NOT NULL,
                damage INTEGER NOT NULL,
                location TEXT,
                coins_reward INTEGER DEFAULT 0,
                xp_reward INTEGER DEFAULT 0
            )
        ''')
        
        await self.conn.execute('''
            CREATE TABLE IF NOT EXISTS game_dungeon_floors (
                floor_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                tier INTEGER NOT NULL,
                required_catacombs INTEGER DEFAULT 0,
                mob_health_multiplier REAL DEFAULT 1.0,
                reward_multiplier REAL DEFAULT 1.0
            )
        ''')
        
        await self.conn.execute('''
            CREATE TABLE IF NOT EXISTS game_calendar (
                data_type TEXT PRIMARY KEY,
                data_content TEXT NOT NULL
            )
        ''')
        
        await self.conn.execute('''
            CREATE TABLE IF NOT EXISTS game_tool_tiers (
                tool_type TEXT NOT NULL,
                tier INTEGER NOT NULL,
                item_id TEXT NOT NULL,
                name TEXT NOT NULL,
                stats TEXT,
                recipe TEXT,
                PRIMARY KEY (tool_type, tier)
            )
        ''')
        
        await self.conn.execute('''
            CREATE TABLE IF NOT EXISTS game_slayer_bosses (
                boss_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                emoji TEXT,
                tier_data TEXT NOT NULL
            )
        ''')
        
        await self.conn.execute('''
            CREATE TABLE IF NOT EXISTS game_constants (
                constant_key TEXT PRIMARY KEY,
                constant_value TEXT NOT NULL,
                description TEXT
            )
        ''')
        
        await self.conn.execute('''
            CREATE TABLE IF NOT EXISTS npc_shops (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                npc_name TEXT,
                item_id TEXT,
                price INTEGER,
                stock INTEGER DEFAULT -1,
                restock_time INTEGER,
                available BOOLEAN DEFAULT 1
            )
        ''')
        
        await self.conn.execute('''
            CREATE TABLE IF NOT EXISTS game_collection_items (
                category TEXT NOT NULL,
                item_id TEXT NOT NULL,
                display_name TEXT NOT NULL,
                emoji TEXT,
                PRIMARY KEY (category, item_id)
            )
        ''')
        
        await self.conn.execute('''
            CREATE TABLE IF NOT EXISTS game_mob_locations (
                location_id TEXT NOT NULL,
                mob_id TEXT NOT NULL,
                mob_name TEXT NOT NULL,
                health INTEGER NOT NULL,
                damage INTEGER NOT NULL,
                coins_reward INTEGER DEFAULT 0,
                xp_reward INTEGER DEFAULT 0,
                PRIMARY KEY (location_id, mob_id)
            )
        ''')
        
        await self.conn.execute('''
            CREATE TABLE IF NOT EXISTS game_seasons (
                season_id INTEGER PRIMARY KEY,
                season_name TEXT NOT NULL
            )
        ''')
        
        await self.conn.execute('''
            CREATE TABLE IF NOT EXISTS game_mayors (
                mayor_id TEXT PRIMARY KEY,
                mayor_name TEXT NOT NULL,
                perks TEXT NOT NULL
            )
        ''')
        
        await self.conn.execute('''
            CREATE TABLE IF NOT EXISTS game_gathering_drops (
                drop_id INTEGER PRIMARY KEY AUTOINCREMENT,
                gathering_type TEXT NOT NULL,
                resource_type TEXT NOT NULL,
                item_id TEXT NOT NULL,
                drop_chance REAL DEFAULT 1.0,
                min_amount INTEGER DEFAULT 1,
                max_amount INTEGER DEFAULT 1
            )
        ''')
        
        await self.conn.execute('''
            CREATE TABLE IF NOT EXISTS game_rarity_colors (
                rarity TEXT PRIMARY KEY,
                color_hex TEXT NOT NULL
            )
        ''')
        
        await self.conn.execute('''
            CREATE TABLE IF NOT EXISTS game_slayer_drops (
                boss_id TEXT NOT NULL,
                item_id TEXT NOT NULL,
                min_amount INTEGER DEFAULT 0,
                max_amount INTEGER DEFAULT 0,
                drop_chance REAL DEFAULT 1.0,
                PRIMARY KEY (boss_id, item_id)
            )
        ''')
        
        await self.conn.commit()

    async def close(self):
        if self.conn:
            await self.conn.close()
