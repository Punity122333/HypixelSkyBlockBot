from typing import Optional, Dict, List, Any
import aiosqlite
import json


class EventsDB:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn: Optional[aiosqlite.Connection] = None
    
    async def connect(self):
        if not self.conn:
            self.conn = await aiosqlite.connect(self.db_path)
            self.conn.row_factory = aiosqlite.Row

    async def get_all_game_events(self):
        if not self.conn:
            return []
        cursor = await self.conn.execute('''
            SELECT * FROM game_events
        ''')
        rows = await cursor.fetchall()
        events = []
        for row in rows:
            event = dict(row)
            if 'bonuses' in event and event['bonuses']:
                try:
                    event['bonuses'] = json.loads(event['bonuses'])
                except:
                    event['bonuses'] = {}
            events.append(event)
        return events

    async def get_game_event(self, event_id: str):
        if not self.conn:
            return None
        cursor = await self.conn.execute('''
            SELECT * FROM game_events WHERE event_id = ?
        ''', (event_id,))
        row = await cursor.fetchone()
        if row:
            event = dict(row)
            if 'bonuses' in event and event['bonuses']:
                event['bonuses'] = json.loads(event['bonuses'])
            return event
        return None

    async def add_game_event(self, event_id: str, name: str, description: str, duration: int, 
                            occurs_every: int, bonuses: Dict):
        if not self.conn:
            return
        await self.conn.execute('''
            INSERT OR REPLACE INTO game_events (event_id, name, description, duration, occurs_every, bonuses)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (event_id, name, description, duration, occurs_every, json.dumps(bonuses)))
        await self.conn.commit()

    async def get_all_seasons(self):
        if not self.conn:
            return []
        cursor = await self.conn.execute('''
            SELECT season_name FROM seasons ORDER BY season_id
        ''')
        rows = await cursor.fetchall()
        return [row['season_name'] for row in rows]

    async def add_season(self, season_id: int, season_name: str):
        if not self.conn:
            return
        await self.conn.execute('''
            INSERT OR REPLACE INTO seasons (season_id, season_name)
            VALUES (?, ?)
        ''', (season_id, season_name))
        await self.conn.commit()

    async def get_all_mayors(self):
        if not self.conn:
            return []
        cursor = await self.conn.execute('''
            SELECT * FROM mayors
        ''')
        rows = await cursor.fetchall()
        mayors = []
        for row in rows:
            mayor = dict(row)
            if 'bonuses' in mayor and mayor['bonuses']:
                try:
                    mayor['bonuses'] = json.loads(mayor['bonuses'])
                except:
                    mayor['bonuses'] = {}
            else:
                mayor['bonuses'] = {}
            mayors.append({
                'mayor_id': mayor.get('mayor_id'),
                'mayor_name': mayor.get('name'),
                'perks': mayor.get('perks'),
                'bonuses': mayor['bonuses']
            })
        return mayors

    async def add_mayor(self, mayor_id: str, name: str, perks: str):
        if not self.conn:
            return
        await self.conn.execute('''
            INSERT OR REPLACE INTO mayors (mayor_id, name, perks)
            VALUES (?, ?, ?)
        ''', (mayor_id, name, perks))
        await self.conn.commit()

    async def get_all_game_quests(self):
        if not self.conn:
            return []
        cursor = await self.conn.execute('''
            SELECT * FROM game_quests
        ''')
        rows = await cursor.fetchall()
        result = []
        for row in rows:
            quest = dict(row)
            if 'reward_items' in quest and quest['reward_items']:
                quest['reward_items'] = json.loads(quest['reward_items'])
            result.append(quest)
        return result

    async def get_game_quest(self, quest_id: str):
        if not self.conn:
            return None
        cursor = await self.conn.execute('''
            SELECT * FROM game_quests WHERE quest_id = ?
        ''', (quest_id,))
        row = await cursor.fetchone()
        if row:
            quest = dict(row)
            if 'reward_items' in quest and quest['reward_items']:
                quest['reward_items'] = json.loads(quest['reward_items'])
            return quest
        return None

    async def add_game_quest(self, quest_id: str, name: str, description: str, requirement_type: str,
                            requirement_item: Optional[str] = None, requirement_amount: int = 0, 
                            reward_coins: int = 0, reward_items: Optional[List] = None):
        if not self.conn:
            return
        await self.conn.execute('''
            INSERT OR REPLACE INTO game_quests (quest_id, name, description, requirement_type, 
                                               requirement_item, requirement_amount, reward_coins, reward_items)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (quest_id, name, description, requirement_type, requirement_item, requirement_amount, 
              reward_coins, json.dumps(reward_items or [])))
        await self.conn.commit()

    async def get_game_pet(self, pet_id: str):
        if not self.conn:
            return None
        cursor = await self.conn.execute('''
            SELECT * FROM game_pets WHERE pet_id = ?
        ''', (pet_id,))
        row = await cursor.fetchone()
        if row:
            pet = dict(row)
            if 'stats' in pet and pet['stats']:
                pet['stats'] = json.loads(pet['stats'])
            return pet
        return None

    async def add_game_pet(self, pet_id: str, pet_type: str, rarity: str, stats: Dict, max_level: int, description: str):
        if not self.conn:
            return
        await self.conn.execute('''
            INSERT OR REPLACE INTO game_pets (pet_id, pet_type, rarity, stats, max_level, description)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (pet_id, pet_type, rarity, json.dumps(stats), max_level, description))
        await self.conn.commit()

    async def get_minion_data(self, minion_type: str):
        if not self.conn:
            return None
        cursor = await self.conn.execute('''
            SELECT * FROM game_minions WHERE minion_type = ?
        ''', (minion_type,))
        return await cursor.fetchone()

    async def add_game_minion(self, minion_type: str, produces: str, base_speed: int, max_tier: int, 
                             category: str, description: str):
        if not self.conn:
            return
        await self.conn.execute('''
            INSERT OR REPLACE INTO game_minions (minion_type, produces, base_speed, max_tier, category, description)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (minion_type, produces, base_speed, max_tier, category, description))
        await self.conn.commit()
