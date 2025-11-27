from typing import Dict, List, Optional

from .base import DatabaseBase


class SkillsDatabase(DatabaseBase):
    async def get_skills(self, user_id: int) -> List[Dict]:
        async with self.conn.execute(
            'SELECT * FROM skills WHERE user_id = ?', (user_id,)
        ) as cursor:
            rows = await cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in rows]

    async def update_skill(self, user_id: int, skill_name: str, xp: Optional[int] = None, level: Optional[int] = None):
        if xp is not None:
            await self.conn.execute(
                'UPDATE skills SET xp = ? WHERE user_id = ? AND skill_name = ?',
                (xp, user_id, skill_name)
            )
        if level is not None:
            await self.conn.execute(
                'UPDATE skills SET level = ? WHERE user_id = ? AND skill_name = ?',
                (level, user_id, skill_name)
            )
        await self.conn.commit()

    async def get_collection(self, user_id: int, collection_name: str) -> int:
        async with self.conn.execute('''
            SELECT amount FROM collections WHERE user_id = ? AND collection_name = ?
        ''', (user_id, collection_name)) as cursor:
            result = await cursor.fetchone()
            return result[0] if result else 0

    async def add_collection(self, user_id: int, collection_name: str, amount: int):
        async with self.conn.execute('''
            SELECT amount FROM collections WHERE user_id = ? AND collection_name = ?
        ''', (user_id, collection_name)) as cursor:
            result = await cursor.fetchone()
        
        if result:
            new_amount = result[0] + amount
            await self.conn.execute('''
                UPDATE collections SET amount = ? WHERE user_id = ? AND collection_name = ?
            ''', (new_amount, user_id, collection_name))
        else:
            await self.conn.execute('''
                INSERT INTO collections (user_id, collection_name, amount, tier)
                VALUES (?, ?, ?, 0)
            ''', (user_id, collection_name, amount))
        await self.conn.commit()

    async def update_collection(self, user_id: int, collection_name: str, amount: int):
        await self.add_collection(user_id, collection_name, amount)

    async def get_all_collections(self, user_id: int) -> List[Dict]:
        async with self.conn.execute('''
            SELECT * FROM collections WHERE user_id = ? ORDER BY collection_name
        ''', (user_id,)) as cursor:
            rows = await cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
