from typing import Optional, List, Dict, Any
import aiosqlite
import json


class WorldDB:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn: Optional[aiosqlite.Connection] = None
    
    async def connect(self):
        if not self.conn:
            self.conn = await aiosqlite.connect(self.db_path)
            self.conn.row_factory = aiosqlite.Row

    async def get_slayer_boss(self, boss_type: str):
        if not self.conn:
            return None
        cursor = await self.conn.execute('''
            SELECT * FROM slayer_bosses WHERE boss_id = ?
        ''', (boss_type,))
        row = await cursor.fetchone()
        if row:
            result = dict(row)
            if 'tier_data' in result and result['tier_data']:
                result['tier_data'] = json.loads(result['tier_data'])
            return result
        return None

    async def get_slayer_drops(self, boss_type: str):
        if not self.conn:
            return []
        cursor = await self.conn.execute('''
            SELECT * FROM slayer_drops WHERE boss_id = ?
        ''', (boss_type,))
        return await cursor.fetchall()

    async def add_slayer_boss(self, boss_id: str, name: str, emoji: str, tier_data: Dict):
        if not self.conn:
            return
        await self.conn.execute('''
            INSERT OR REPLACE INTO slayer_bosses (boss_id, name, emoji, tier_data)
            VALUES (?, ?, ?, ?)
        ''', (boss_id, name, emoji, json.dumps(tier_data)))
        await self.conn.commit()

    async def add_slayer_drop(self, boss_id: str, item_id: str, min_amt: int, max_amt: int, drop_chance: float):
        if not self.conn:
            return
        await self.conn.execute('''
            INSERT OR REPLACE INTO slayer_drops (boss_id, item_id, min_amt, max_amt, drop_chance)
            VALUES (?, ?, ?, ?, ?)
        ''', (boss_id, item_id, min_amt, max_amt, drop_chance))
        await self.conn.commit()

    async def get_dungeon_floor(self, floor_id: str):
        if not self.conn:
            return None
        cursor = await self.conn.execute('''
            SELECT * FROM dungeon_floors WHERE floor_id = ?
        ''', (floor_id,))
        return await cursor.fetchone()

    async def add_dungeon_floor(self, floor_id: str, name: str, rewards: int, time: int):
        if not self.conn:
            return
        await self.conn.execute('''
            INSERT OR REPLACE INTO dungeon_floors (floor_id, name, rewards, time)
            VALUES (?, ?, ?, ?)
        ''', (floor_id, name, rewards, time))
        await self.conn.commit()

    async def get_mobs_by_location(self, location_id: str):
        if not self.conn:
            return []
        cursor = await self.conn.execute('''
            SELECT * FROM mob_locations WHERE location_id = ?
        ''', (location_id,))
        return await cursor.fetchall()

    async def get_mob_loot_table(self, mob_name: str):
        if not self.conn:
            return {}
        cursor = await self.conn.execute('''
            SELECT * FROM mob_locations WHERE mob_name = ?
        ''', (mob_name,))
        row = await cursor.fetchone()
        if row:
            row_dict = dict(row)
            return {'coins_min': row_dict.get('coins', 0), 'coins_max': row_dict.get('coins', 0), 'xp': row_dict.get('xp', 0)}
        return {}

    async def get_mob_loot_coins(self, mob_name: str):
        if not self.conn:
            return None
        cursor = await self.conn.execute('''
            SELECT coins, xp FROM mob_locations WHERE mob_name = ?
        ''', (mob_name,))
        row = await cursor.fetchone()
        if row:
            coins = row['coins']
            xp = row['xp']
            return {'min_coins': coins, 'max_coins': coins, 'xp': xp}
        return None

    async def add_mob_location(self, location_id: str, mob_id: str, mob_name: str, health: int, 
                              damage: int, coins: int, xp: int):
        if not self.conn:
            return
        await self.conn.execute('''
            INSERT OR REPLACE INTO mob_locations (location_id, mob_id, mob_name, health, damage, coins, xp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (location_id, mob_id, mob_name, health, damage, coins, xp))
        await self.conn.commit()

    async def get_gathering_drops(self, gathering_type: str, resource_type: str):
        if not self.conn:
            return []
        cursor = await self.conn.execute('''
            SELECT * FROM gathering_drops
            WHERE gathering_type = ? AND resource_type = ?
        ''', (gathering_type, resource_type))
        return await cursor.fetchall()

    async def add_gathering_drop(self, gathering_type: str, resource_type: str, item_id: str, 
                                drop_chance: float, min_amt: int, max_amt: int):
        if not self.conn:
            return
        await self.conn.execute('''
            INSERT OR REPLACE INTO gathering_drops (gathering_type, resource_type, item_id, drop_chance, min_amt, max_amt)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (gathering_type, resource_type, item_id, drop_chance, min_amt, max_amt))
        await self.conn.commit()

    async def get_all_fairy_soul_locations(self):
        if not self.conn:
            return []
        cursor = await self.conn.execute('''
            SELECT location FROM fairy_soul_locations
        ''')
        rows = await cursor.fetchall()
        return [row['location'] for row in rows]

    async def get_collection_categories(self):
        if not self.conn:
            return {}
        cursor = await self.conn.execute('''
            SELECT DISTINCT category FROM collection_items
        ''')
        rows = await cursor.fetchall()
        categories = {}
        for row in rows:
            category = row['category']
            items_cursor = await self.conn.execute('''
                SELECT item_id FROM collection_items WHERE category = ?
            ''', (category,))
            items = await items_cursor.fetchall()
            categories[category] = [item['item_id'] for item in items]
        return categories

    async def get_category_items(self, category: str):
        if not self.conn:
            return []
        cursor = await self.conn.execute('''
            SELECT item_id FROM collection_items WHERE category = ?
        ''', (category,))
        rows = await cursor.fetchall()
        return [row['item_id'] for row in rows]

    async def get_item_category(self, item_id: str):
        if not self.conn:
            return None
        cursor = await self.conn.execute('''
            SELECT category FROM collection_items WHERE item_id = ?
        ''', (item_id,))
        row = await cursor.fetchone()
        if row:
            return row['category']
        return None

    async def add_collection_items(self, category: str, item_id: str, display_name: str, emoji: str):
        if not self.conn:
            return
        await self.conn.execute('''
            INSERT OR REPLACE INTO collection_items (category, item_id, display_name, emoji)
            VALUES (?, ?, ?, ?)
        ''', (category, item_id, display_name, emoji))
        await self.conn.commit()

    async def get_collection_tier_requirements(self, item_id: str):
        if not self.conn:
            return []
        return [100, 250, 500, 1000, 2500, 5000, 10000, 25000, 50000, 100000]

    async def get_all_collection_tier_requirements(self):
        if not self.conn:
            return {}
        return {}

    async def get_collection_tier_reward(self, tier: int):
        if not self.conn:
            return None
        return None

    async def get_all_collection_tier_rewards(self):
        return {
            1: {'coins': 500, 'recipes': []},
            2: {'coins': 1000, 'recipes': []},
            3: {'coins': 2500, 'recipes': []},
            4: {'coins': 5000, 'recipes': []},
            5: {'coins': 10000, 'recipes': []},
            6: {'coins': 25000, 'recipes': []},
            7: {'coins': 50000, 'recipes': []},
            8: {'coins': 100000, 'recipes': []},
            9: {'coins': 250000, 'recipes': []},
            10: {'coins': 500000, 'recipes': []}
        }

    async def get_collection_category_bonuses(self, category: str):
        all_bonuses = await self.get_all_collection_category_bonuses()
        return all_bonuses.get(category, {})

    async def get_all_collection_category_bonuses(self):
        return {
            'farming': {
                10: {'farming_fortune': 5},
                25: {'farming_fortune': 10},
                50: {'farming_fortune': 15},
                100: {'farming_fortune': 25}
            },
            'mining': {
                10: {'mining_fortune': 5},
                25: {'mining_fortune': 10},
                50: {'mining_fortune': 15},
                100: {'mining_fortune': 25}
            },
            'foraging': {
                10: {'foraging_fortune': 5},
                25: {'foraging_fortune': 10},
                50: {'foraging_fortune': 15},
                100: {'foraging_fortune': 25}
            },
            'combat': {
                10: {'strength': 5},
                25: {'strength': 10},
                50: {'strength': 15, 'health': 25},
                100: {'strength': 25, 'health': 50}
            }
        }

    async def get_mob_stats(self, mob_id: str):
        if not self.conn:
            return None
        cursor = await self.conn.execute('''
            SELECT * FROM mob_stats WHERE mob_id = ?
        ''', (mob_id,))
        row = await cursor.fetchone()
        if row:
            return dict(row)
        return None
