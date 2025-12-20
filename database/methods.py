from typing import Optional, Any
import json
import time


class GameDatabaseMethods:
    conn: Optional[Any] = None
    db_path: str = ""
    players: Any = None
    skills: Any = None
    inventory: Any = None
    market: Any = None
    game_data: Any = None
    world: Any = None
    events: Any = None
    minion_upgrades: Any = None
    bestiary: Any = None
    museum: Any = None
    achievements: Any = None

    async def init_bot_traders(self):
        if not self.conn:
            return
        await self.conn.execute('''
            CREATE TABLE IF NOT EXISTS bazaar_bots (
                bot_id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id TEXT NOT NULL,
                min_buy_price REAL,
                max_sell_price REAL,
                stock INTEGER DEFAULT 0,
                created_at INTEGER DEFAULT 0
            )
        ''')
        await self.conn.commit()

    async def init_auction_bots(self):
        if not self.conn:
            return
        await self.conn.execute('''
            CREATE TABLE IF NOT EXISTS auction_bots (
                bot_id INTEGER PRIMARY KEY AUTOINCREMENT,
                bot_name TEXT NOT NULL,
                min_bid INTEGER,
                max_bid INTEGER,
                target_categories TEXT,
                active INTEGER DEFAULT 1
            )
        ''')
        await self.conn.commit()

    async def init_stock_market(self):
        if not self.conn:
            return
        await self.conn.execute('''
            CREATE TABLE IF NOT EXISTS stock_market (
                symbol TEXT PRIMARY KEY,
                stock_symbol TEXT,
                company_name TEXT,
                current_price REAL,
                opening_price REAL,
                daily_high REAL,
                daily_low REAL,
                change_percent REAL,
                volume INTEGER,
                market_cap INTEGER,
                volatility REAL,
                last_update INTEGER
            )
        ''')
        await self.conn.commit()
        
        stocks = await self.conn.execute('SELECT COUNT(*) as count FROM stock_market')
        row = await stocks.fetchone()
        if row and row['count'] == 0:
            stock_data = [
                ('ENCH', 'ENCH', 'Enchanted Corp', 100.0, 100.0, 0.15),
                ('MINE', 'MINE', 'Mining Industries', 50.0, 50.0, 0.20),
                ('FARM', 'FARM', 'Farming Co', 75.0, 75.0, 0.12),
                ('COMB', 'COMB', 'Combat Systems', 150.0, 150.0, 0.25),
                ('FISH', 'FISH', 'Fishing Enterprises', 60.0, 60.0, 0.18),
            ]
            for symbol, stock_symbol, company_name, price, opening_price, volatility in stock_data:
                await self.conn.execute('''
                    INSERT INTO stock_market (symbol, stock_symbol, company_name, current_price, opening_price, 
                                            daily_high, daily_low, change_percent, volume, market_cap, volatility, last_update)
                    VALUES (?, ?, ?, ?, ?, ?, ?, 0.0, 0, ?, ?, ?)
                ''', (symbol, stock_symbol, company_name, price, opening_price, price, price, int(price * 1000000), volatility, int(time.time())))
            await self.conn.commit()

    async def get_active_merchant_deals(self):
        if not self.conn:
            return []
        
        current_time = int(time.time())
        
        await self.conn.execute('''
            UPDATE merchant_deals 
            SET active = 0 
            WHERE active = 1 AND (created_at + duration) < ?
        ''', (current_time,))
        await self.conn.commit()
        
        cursor = await self.conn.execute('''
            SELECT * FROM merchant_deals 
            WHERE active = 1 
            AND stock > 0 
            AND (created_at + duration) > ?
            ORDER BY created_at DESC
        ''', (current_time,))
        return await cursor.fetchall()

    async def create_merchant_deal(self, item_id: str, price: int, stock: int, duration: int, npc_name: str = 'Merchant', deal_type: str = 'sell'):
        if not self.conn:
            return
        await self.conn.execute('''
            INSERT INTO merchant_deals (item_id, price, stock, duration, created_at, active, npc_name, deal_type)
            VALUES (?, ?, ?, ?, ?, 1, ?, ?)
        ''', (item_id, price, stock, duration, int(time.time()), npc_name, deal_type))
        await self.conn.commit()

    async def get_active_bot_traders(self):
        if not self.conn:
            return []
        cursor = await self.conn.execute('''
            SELECT * FROM bazaar_bots WHERE stock > 0
        ''')
        return await cursor.fetchall()

    async def get_auction_bots(self):
        if not self.conn:
            return []
        cursor = await self.conn.execute('''
            SELECT * FROM auction_bots WHERE active = 1
        ''')
        return await cursor.fetchall()

    async def end_expired_auctions(self):
        if not self.conn:
            return
        current_time = int(time.time())
        await self.conn.execute('''
            UPDATE auction_house SET ended = 1 WHERE end_time <= ? AND ended = 0
        ''', (current_time,))
        await self.conn.commit()

    async def log_bazaar_flip(self, user_id: int, product_id: str, buy_price: float, sell_price: float, profit: float):
        if not self.conn:
            return
        await self.conn.execute('''
            INSERT INTO bazaar_flips (user_id, product_id, buy_price, sell_price, profit, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, product_id, buy_price, sell_price, profit, int(time.time())))
        await self.conn.commit()

    async def create_bazaar_order(self, user_id: int, product_id: str, order_type: str, amount: float, price: float):
        if not self.conn:
            return
        if order_type.lower() == 'buy':
            await self.conn.execute('''
                INSERT INTO bazaar_buy_orders (user_id, product_id, price, amount, created_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, product_id, price, amount, int(time.time())))
        elif order_type.lower() == 'sell':
            await self.conn.execute('''
                INSERT INTO bazaar_sell_orders (user_id, product_id, price, amount, created_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, product_id, price, amount, int(time.time())))
        await self.conn.commit()

    async def buy_bin(self, user_id: int, auction_id: int, price: int):
        if not self.conn:
            return False
        player = await self.get_player(user_id)
        if not player or player['coins'] < price:
            return False
        
        cursor = await self.conn.execute('''
            SELECT ah.*, ai.item_id, ai.amount
            FROM auction_house ah
            JOIN auction_items ai ON ah.id = ai.auction_id
            WHERE ah.id = ? AND ah.bin = 1 AND ah.ended = 0
        ''', (auction_id,))
        auction = await cursor.fetchone()
        
        if not auction:
            return False
        
        await self.update_player(user_id, coins=player['coins'] - price)
        await self.add_item_to_inventory(user_id, auction['item_id'], auction['amount'])
        
        await self.conn.execute('''
            UPDATE auction_house SET ended = 1, highest_bidder_id = ? WHERE id = ?
        ''', (user_id, auction_id))
        await self.conn.commit()
        return True

    async def update_auction_bot(self, bot_id: int, **kwargs):
        if not self.conn:
            return
        fields = ', '.join([f"{k} = ?" for k in kwargs.keys()])
        values = list(kwargs.values()) + [bot_id]
        await self.conn.execute(f'''
            UPDATE auction_bots SET {fields} WHERE bot_id = ?
        ''', values)
        await self.conn.commit()

    async def get_top_flippers(self, limit: int = 10):
        if not self.conn:
            return []
        cursor = await self.conn.execute('''
            SELECT user_id, SUM(profit) as total_profit
            FROM bazaar_flips
            GROUP BY user_id
            ORDER BY total_profit DESC
            LIMIT ?
        ''', (limit,))
        return await cursor.fetchall()

    async def get_top_category_collectors(self, category: str, limit: int = 1):
        if not self.conn:
            return []
        cursor = await self.conn.execute('''
            SELECT user_id, amount
            FROM collections
            WHERE collection_name = ?
            ORDER BY amount DESC
            LIMIT ?
        ''', (category, limit))
        return await cursor.fetchall()

    async def get_quest(self, user_id: int, quest_id: str):
        if not self.conn:
            return None
        cursor = await self.conn.execute('''
            SELECT * FROM player_quests WHERE user_id = ? AND quest_id = ?
        ''', (user_id, quest_id))
        return await cursor.fetchone()

    async def create_quest(self, user_id: int, quest_id: str, progress: int = 0):
        if not self.conn:
            return
        await self.conn.execute('''
            INSERT INTO player_quests (user_id, quest_id, progress, completed, started_at)
            VALUES (?, ?, ?, 0, ?)
        ''', (user_id, quest_id, progress, int(time.time())))
        await self.conn.commit()

    async def get_user_quests(self, user_id: int):
        if not self.conn:
            return []
        cursor = await self.conn.execute('''
            SELECT * FROM player_quests WHERE user_id = ?
        ''', (user_id,))
        return await cursor.fetchall()

    async def complete_quest(self, user_id: int, quest_id: str):
        if not self.conn:
            return
        await self.conn.execute('''
            UPDATE player_quests SET completed = 1, completed_at = ? WHERE user_id = ? AND quest_id = ?
        ''', (int(time.time()), user_id, quest_id))
        await self.conn.commit()

    async def get_active_pet(self, user_id: int):
        if not self.conn:
            return None
        cursor = await self.conn.execute('''
            SELECT * FROM player_pets WHERE user_id = ? AND active = 1
        ''', (user_id,))
        return await cursor.fetchone()

    async def update_stock_price(self, symbol: str, price: float, change_percent: float, volume: int):
        if not self.conn:
            return
        existing = await self.conn.execute('SELECT * FROM stock_market WHERE symbol = ?', (symbol,))
        row = await existing.fetchone()
        if row:
            daily_high = max(row['daily_high'], price)
            daily_low = min(row['daily_low'], price)
            await self.conn.execute('''
                UPDATE stock_market 
                SET current_price = ?, change_percent = ?, volume = ?, daily_high = ?, daily_low = ?, last_update = ?
                WHERE symbol = ?
            ''', (price, change_percent, volume, daily_high, daily_low, int(time.time()), symbol))
        else:
            await self.conn.execute('''
                INSERT INTO stock_market (symbol, stock_symbol, company_name, current_price, opening_price, 
                                        daily_high, daily_low, change_percent, volume, market_cap, volatility, last_update)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0, 0.15, ?)
            ''', (symbol, symbol, symbol, price, price, price, price, change_percent, volume, int(time.time())))
        await self.conn.commit()

    async def add_minion(self, user_id: int, minion_type: str, tier: int = 1, island_slot: int = 1):
        if not self.conn:
            return
        await self.conn.execute('''
            INSERT INTO player_minions (user_id, minion_type, tier, island_slot, storage, last_collected)
            VALUES (?, ?, ?, ?, '[]', ?)
        ''', (user_id, minion_type, tier, island_slot, int(time.time())))
        await self.conn.commit()
        
        from utils.systems.badge_system import BadgeSystem
        minions = await self.get_user_minions(user_id)
        minion_count = len(list(minions)) if minions else 0
        await BadgeSystem.check_and_unlock_badges(self, user_id, 'minion', minion_count=minion_count)

    async def cancel_bazaar_order(self, order_id: int, order_type: Optional[str] = None):
        if not self.conn:
            return
        if order_type and order_type.lower() == 'buy':
            await self.conn.execute('''
                DELETE FROM bazaar_buy_orders WHERE id = ?
            ''', (order_id,))
        elif order_type and order_type.lower() == 'sell':
            await self.conn.execute('''
                DELETE FROM bazaar_sell_orders WHERE id = ?
            ''', (order_id,))
        else:
            await self.conn.execute('''
                DELETE FROM bazaar_buy_orders WHERE id = ?
            ''', (order_id,))
            await self.conn.execute('''
                DELETE FROM bazaar_sell_orders WHERE id = ?
            ''', (order_id,))
        await self.conn.commit()

    async def claim_daily_reward(self, user_id: int):
        if not self.conn:
            return (0, 0)
        current_time = int(time.time())
        
        cursor = await self.conn.execute('''
            SELECT last_claim, streak FROM daily_rewards WHERE user_id = ?
        ''', (user_id,))
        result = await cursor.fetchone()
        
        if result:
            last_claim = result['last_claim']
            streak = result['streak']
            
            if (current_time - last_claim) < 86400:
                return (0, streak)
            
            if (current_time - last_claim) < 172800:
                streak += 1
            else:
                streak = 1
        else:
            streak = 1
        
        coins = 5000 + (streak * 100)
        
        await self.conn.execute('''
            INSERT OR REPLACE INTO daily_rewards (user_id, last_claim, streak)
            VALUES (?, ?, ?)
        ''', (user_id, current_time, streak))
        await self.conn.commit()
        
        player = await self.get_player(user_id)
        if player:
            await self.update_player(user_id, coins=player['coins'] + coins)
        
        return (coins, streak)

    async def claim_merchant_deal(self, user_id: int, deal_id: int):
        if not self.conn:
            return False
        cursor = await self.conn.execute('''
            SELECT * FROM merchant_deals WHERE id = ? AND active = 1
        ''', (deal_id,))
        deal = await cursor.fetchone()
        
        if not deal:
            return False
        
        bestiary_discount = await self.bestiary.calculate_bestiary_merchant_discount(user_id)
        final_price = int(deal['price'] * bestiary_discount)
        
        player = await self.get_player(user_id)
        if player and player['coins'] >= final_price:
            await self.update_player(user_id, coins=player['coins'] - final_price)
            await self.add_item_to_inventory(user_id, deal['item_id'], 1)
            
            await self.conn.execute('''
                UPDATE merchant_deals SET stock = stock - 1 WHERE id = ?
            ''', (deal_id,))
            await self.conn.commit()
            return True
        return False

    async def claim_quest_reward(self, user_id: int, quest_id: str):
        if not self.conn:
            return
        await self.conn.execute('''
            UPDATE player_quests SET claimed = 1, completed_at = ? WHERE user_id = ? AND quest_id = ?
        ''', (int(time.time()), user_id, quest_id))
        await self.conn.commit()

    async def delete_minion(self, minion_id: int, user_id: int):
        if not self.conn:
            return
        await self.conn.execute('''
            DELETE FROM player_minions WHERE id = ? AND user_id = ?
        ''', (minion_id, user_id))
        await self.conn.commit()

    async def equip_pet(self, user_id: int, pet_id: int):
        if not self.conn:
            return
        await self.conn.execute('''
            UPDATE player_pets SET active = 0 WHERE user_id = ?
        ''', (user_id,))
        await self.conn.execute('''
            UPDATE player_pets SET active = 1 WHERE id = ?
        ''', (pet_id,))
        await self.conn.commit()
        
    async def unequip_pet(self, user_id: int):
        if not self.conn:
            return
        await self.conn.execute('''
            UPDATE player_pets SET active = 0 WHERE user_id = ?
        ''', (user_id,))
        await self.conn.commit()

    async def get_all_bazaar_products(self):
        if not self.conn:
            return []
        cursor = await self.conn.execute('''
            SELECT * FROM bazaar_products
        ''')
        return await cursor.fetchall()

    async def get_fairy_soul_locations(self, user_id: int):
        if not self.conn:
            return []

        cursor = await self.conn.execute('''
            SELECT location 
            FROM player_fairy_souls 
            WHERE user_id = ? AND collected = 1
        ''', (user_id,))
        rows = await cursor.fetchall()
        return [row['location'] for row in rows]

    async def get_minion(self, minion_id: int):
        if not self.conn:
            return None
        cursor = await self.conn.execute('''
            SELECT * FROM player_minions WHERE id = ?
        ''', (minion_id,))
        return await cursor.fetchone()

    async def get_user_auctions(self, user_id: int):
        if not self.conn:
            return []
        cursor = await self.conn.execute('''
            SELECT ah.*, ai.item_id, ai.amount, ai.metadata
            FROM auction_house ah
            JOIN auction_items ai ON ah.id = ai.auction_id
            WHERE ah.seller_id = ? AND ah.ended = 0
        ''', (user_id,))
        return await cursor.fetchall()

    async def get_user_bazaar_orders(self, user_id: int):
        if not self.conn:
            return []
        buy_orders = await self.conn.execute('''
            SELECT *, 'buy' as order_type FROM bazaar_buy_orders WHERE user_id = ? AND active = 1
        ''', (user_id,))
        sell_orders = await self.conn.execute('''
            SELECT *, 'sell' as order_type FROM bazaar_sell_orders WHERE user_id = ? AND active = 1
        ''', (user_id,))
        return await buy_orders.fetchall() + await sell_orders.fetchall()

    async def get_user_minions(self, user_id: int):
        if not self.conn:
            return []
        cursor = await self.conn.execute('''
            SELECT * FROM player_minions WHERE user_id = ?
        ''', (user_id,))
        return await cursor.fetchall()

    async def get_user_pets(self, user_id: int):
        if not self.conn:
            return []
        cursor = await self.conn.execute('''
            SELECT * FROM player_pets WHERE user_id = ?
        ''', (user_id,))
        return await cursor.fetchall()

    async def update_collection(self, user_id: int, collection_name: str, amount: int):
        if not self.conn:
            return
        normalized_name = collection_name.lower().replace(' ', '_')
        await self.conn.execute('''
            INSERT INTO collections (user_id, collection_name, amount)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id, collection_name) DO UPDATE SET amount = amount + ?
        ''', (user_id, normalized_name, amount, amount))
        await self.conn.commit()

    async def update_minion_storage(self, minion_id: int, storage: int):
        if not self.conn:
            return
        await self.conn.execute('''
            UPDATE player_minions SET storage = ? WHERE id = ?
        ''', (storage, minion_id))
        await self.conn.commit()

    async def upgrade_minion(self, minion_id: int):
        if not self.conn:
            return
        await self.conn.execute('''
            UPDATE player_minions SET tier = tier + 1 WHERE id = ?
        ''', (minion_id,))
        await self.conn.commit()
        
    async def collect_minion(self, minion_id: int):
        if not self.conn:
            return []
        
        cursor = await self.conn.execute('''
            SELECT user_id, minion_type, tier, storage, last_collected FROM player_minions WHERE id = ?
        ''', (minion_id,))
        minion = await cursor.fetchone()
        
        if not minion:
            return []
        
        user_id = minion['user_id']
        minion_type = minion['minion_type']
        tier = minion['tier']
        storage = minion['storage'] if minion['storage'] else '[]'
        last_collected = minion['last_collected']
        
        import json
        stored_items = json.loads(storage) if isinstance(storage, str) else []
        
        current_time = int(time.time())
        time_passed = current_time - last_collected
        
        base_speed = 60
        items_per_action = 1
        speed_seconds = base_speed / tier
        
        upgrades = await self.minion_upgrades.get_minion_upgrades(minion_id)
        if 'fuel' in upgrades and upgrades['fuel'].get('expires_at', 0) > current_time:
            speed_boost = upgrades['fuel'].get('speed_boost', 1.0)
            speed_seconds = speed_seconds * speed_boost
        
        actions_performed = int(time_passed / speed_seconds)
        items_generated = actions_performed * items_per_action
        
        total_items = len(stored_items) + items_generated
        max_storage = 64
        
        if total_items > max_storage:
            total_items = max_storage
        
        collected_items = []
        if total_items > 0:
            item_id = f"{minion_type}"
            collected_items.append({
                'item_id': item_id,
                'amount': total_items
            })
            
            await self.add_item_to_inventory(user_id, item_id, total_items)
        
        await self.conn.execute('''
            UPDATE player_minions SET storage = '[]', last_collected = ? WHERE id = ?
        ''', (current_time, minion_id))
        await self.conn.commit()
        
        return collected_items
        
    async def get_xp_table(self):
        if not self.conn:
            return {}
        cursor = await self.conn.execute(''' SELECT * FROM gathering_xp''')
        return await cursor.fetchall()

    async def get_player(self, user_id: int):
        return await self.players.get_player(user_id)

    async def update_player(self, user_id: int, **kwargs):
        return await self.players.update_player(user_id, **kwargs)

    async def add_item_to_inventory(self, user_id: int, item_id: str, amount: int = 1):
        return await self.inventory.add_item(user_id, item_id, amount)

    async def get_hotm_data(self, user_id: int):
        if not self.conn:
            return None
        cursor = await self.conn.execute('SELECT * FROM player_hotm WHERE user_id = ?', (user_id,))
        row = await cursor.fetchone()
        return dict(row) if row else None
    
    async def get_dwarven_progress(self, user_id: int):
        if not self.conn:
            return None
        cursor = await self.conn.execute('SELECT * FROM dwarven_mines_progress WHERE user_id = ?', (user_id,))
        row = await cursor.fetchone()
        return dict(row) if row else None
    
    async def get_crystal_hollows_progress(self, user_id: int):
        if not self.conn:
            return None
        cursor = await self.conn.execute('SELECT * FROM crystal_hollows_progress WHERE user_id = ?', (user_id,))
        row = await cursor.fetchone()
        return dict(row) if row else None

    async def get_pet_stats_by_type_rarity(self, pet_type: str, rarity: str):
        if not self.conn:
            return None
        pet_id = f"{pet_type}_{rarity}"
        cursor = await self.conn.execute('SELECT stats FROM game_pets WHERE pet_id = ?', (pet_id,))
        row = await cursor.fetchone()
        if row and row['stats']:
            return json.loads(row['stats'])
        return None
    
    async def get_all_pet_stats_dict(self):
        if not self.conn:
            return {}
        cursor = await self.conn.execute('SELECT pet_type, rarity, stats FROM game_pets')
        rows = await cursor.fetchall()
        pet_stats_dict = {}
        for row in rows:
            pet_type = row['pet_type']
            rarity = row['rarity']
            stats = json.loads(row['stats']) if row['stats'] else {}
            if pet_type not in pet_stats_dict:
                pet_stats_dict[pet_type] = {}
            pet_stats_dict[pet_type][rarity] = stats
        return pet_stats_dict
    
    async def get_weapon_ability(self, item_id: str):
        if not self.conn:
            return None
        cursor = await self.conn.execute('SELECT * FROM weapon_abilities WHERE item_id = ?', (item_id,))
        row = await cursor.fetchone()
        return dict(row) if row else None
    
    async def get_all_weapon_abilities(self):
        if not self.conn:
            return []
        cursor = await self.conn.execute('SELECT * FROM weapon_abilities')
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]
    
    async def add_weapon_ability(self, item_id: str, ability_data: dict):
        if not self.conn:
            return
        fields = ['item_id'] + list(ability_data.keys())
        values = [item_id] + list(ability_data.values())
        placeholders = ', '.join(['?' for _ in values])
        field_names = ', '.join(fields)
        await self.conn.execute(
            f'INSERT OR REPLACE INTO weapon_abilities ({field_names}) VALUES ({placeholders})',
            tuple(values)
        )
        await self.conn.commit()
    
    async def update_weapon_ability(self, item_id: str, **kwargs):
        if not self.conn or not kwargs:
            return
        set_clause = ', '.join([f'{key} = ?' for key in kwargs.keys()])
        values = list(kwargs.values()) + [item_id]
        await self.conn.execute(
            f'UPDATE weapon_abilities SET {set_clause} WHERE item_id = ?',
            tuple(values)
        )
        await self.conn.commit()


