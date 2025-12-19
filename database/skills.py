from typing import Dict, List, Optional
from .core import DatabaseCore

class SkillsDB(DatabaseCore):
    async def get_skills(self, user_id: int) -> List[Dict]:
        rows = await self.fetchall(
            'SELECT * FROM skills WHERE user_id = ? ORDER BY skill_name',
            (user_id,)
        )
        return [dict(row) for row in rows]

    async def update_skill(self, user_id: int, skill_name: str, **kwargs):
        await self.execute(
            'INSERT OR IGNORE INTO skills (user_id, skill_name, level, xp) VALUES (?, ?, 0, 0)',
            (user_id, skill_name)
        )
        set_clause = ', '.join([f'{k} = ?' for k in kwargs.keys()])
        values = list(kwargs.values()) + [user_id, skill_name]
        await self.execute(
            f'UPDATE skills SET {set_clause} WHERE user_id = ? AND skill_name = ?',
            tuple(values)
        )
        await self.commit()

    async def get_collection(self, user_id: int, collection_name: str) -> int:

        normalized_name = collection_name.lower().replace(' ', '_')
        row = await self.fetchone(
            'SELECT amount FROM collections WHERE user_id = ? AND collection_name = ?',
            (user_id, normalized_name)
        )
        return row['amount'] if row else 0

    async def add_collection(self, user_id: int, collection_name: str, amount: int):

        normalized_name = collection_name.lower().replace(' ', '_')
        await self.execute(
            '''INSERT INTO collections (user_id, collection_name, amount)
               VALUES (?, ?, ?)
               ON CONFLICT(user_id, collection_name) 
               DO UPDATE SET amount = amount + ?''',
            (user_id, normalized_name, amount, amount)
        )
        await self.commit()

    async def get_top_collections(self, collection_name: str, limit: int = 10) -> List[Dict]:
        rows = await self.fetchall(
            '''SELECT user_id, amount FROM collections 
               WHERE collection_name = ? 
               ORDER BY amount DESC LIMIT ?''',
            (collection_name, limit)
        )
        return [dict(row) for row in rows]

    async def get_fairy_souls(self, user_id: int) -> int:
        await self.execute(
            'INSERT OR IGNORE INTO fairy_souls (user_id, souls_collected) VALUES (?, 0)',
            (user_id,)
        )
        await self.commit()
        
        row = await self.fetchone(
            'SELECT souls_collected FROM fairy_souls WHERE user_id = ?',
            (user_id,)
        )
        return row['souls_collected'] if row else 0

    async def collect_fairy_soul(self, user_id: int, location: str) -> bool:
        row = await self.fetchone(
            'SELECT collected FROM player_fairy_souls WHERE user_id = ? AND location = ?',
            (user_id, location)
        )

        if row and row['collected']:
            return False

        await self.execute(
            'UPDATE player_fairy_souls SET collected = 1 WHERE user_id = ? AND location = ?',
            (user_id, location)
        )

        await self.execute(
            'INSERT OR IGNORE INTO fairy_souls (user_id, souls_collected) VALUES (?, 0)',
            (user_id,)
        )
        await self.execute(
            'UPDATE fairy_souls SET souls_collected = souls_collected + 1 WHERE user_id = ?',
            (user_id,)
        )

        await self.commit()
        return True

    async def get_slayer_stats(self, user_id: int, slayer_type: str) -> Optional[Dict]:
        row = await self.fetchone(
            'SELECT * FROM player_slayer_progress WHERE user_id = ? AND slayer_type = ?',
            (user_id, slayer_type)
        )
        return dict(row) if row else None

    async def update_slayer_xp(self, user_id: int, slayer_type: str, xp_gain: int):
        await self.execute(
            '''INSERT INTO player_slayer_progress (user_id, slayer_type, xp, total_kills)
               VALUES (?, ?, ?, 0)
               ON CONFLICT(user_id, slayer_type)
               DO UPDATE SET xp = xp + ?, total_kills = total_kills + 1''',
            (user_id, slayer_type, xp_gain, xp_gain)
        )
        await self.commit()
