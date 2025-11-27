import time
from typing import Dict, List, Optional

from .base import DatabaseBase


class PlayerDatabase(DatabaseBase):
    async def create_player(self, user_id: int, username: str):
        await self.conn.execute(
            'INSERT OR IGNORE INTO players (user_id, username, coins) VALUES (?, ?, ?)',
            (user_id, username, 0)
        )
        
        skills = ['farming', 'mining', 'combat', 'foraging', 'fishing', 'enchanting', 'alchemy', 'taming', 'carpentry', 'runecrafting', 'social']
        for skill in skills:
            await self.conn.execute(
                'INSERT OR IGNORE INTO skills (user_id, skill_name) VALUES (?, ?)',
                (user_id, skill)
            )
        
        await self.conn.execute(
            'INSERT OR IGNORE INTO player_progression (user_id) VALUES (?)',
            (user_id,)
        )
        
        await self.conn.commit()

    async def get_player(self, user_id: int) -> Optional[Dict]:
        async with self.conn.execute(
            'SELECT * FROM players WHERE user_id = ?', (user_id,)
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                columns = [description[0] for description in cursor.description]
                return dict(zip(columns, row))
            return None

    async def update_player(self, user_id: int, **kwargs):
        set_clause = ', '.join([f'{k} = ?' for k in kwargs.keys()])
        values = list(kwargs.values()) + [user_id]
        await self.conn.execute(
            f'UPDATE players SET {set_clause} WHERE user_id = ?',
            values
        )
        await self.conn.commit()

    async def get_player_progression(self, user_id: int) -> Optional[Dict]:
        async with self.conn.execute(
            'SELECT * FROM player_progression WHERE user_id = ?', (user_id,)
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                columns = [description[0] for description in cursor.description]
                return dict(zip(columns, row))
            return None

    async def update_progression(self, user_id: int, **kwargs):
        progression = await self.get_player_progression(user_id)
        
        if not progression:
            await self.conn.execute(
                'INSERT INTO player_progression (user_id) VALUES (?)', (user_id,)
            )
            await self.conn.commit()
        
        set_clause = ', '.join([f'{k} = ?' for k in kwargs.keys()])
        values = list(kwargs.values()) + [user_id]
        await self.conn.execute(
            f'UPDATE player_progression SET {set_clause} WHERE user_id = ?',
            values
        )
        await self.conn.commit()

    async def log_rare_drop(self, user_id: int, item_id: str, rarity: str, source: str):
        await self.conn.execute('''
            INSERT INTO item_rarity_drops (user_id, item_id, rarity, dropped_from, timestamp)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, item_id, rarity, source, int(time.time())))
        await self.conn.commit()

    async def get_leaderboard(self, category: str, limit: int = 100) -> List[Dict]:
        if category == 'coins':
            query = 'SELECT user_id, username, coins FROM players ORDER BY coins DESC LIMIT ?'
        elif category == 'networth':
            query = 'SELECT user_id, username, (coins + bank) as networth FROM players ORDER BY networth DESC LIMIT ?'
        elif category == 'skill_avg':
            query = '''
                SELECT p.user_id, p.username, AVG(s.level) as skill_avg
                FROM players p
                JOIN skills s ON p.user_id = s.user_id
                GROUP BY p.user_id
                ORDER BY skill_avg DESC
                LIMIT ?
            '''
        elif category == 'catacombs':
            query = 'SELECT user_id, username, catacombs_level FROM players ORDER BY catacombs_level DESC LIMIT ?'
        elif category == 'slayer':
            query = '''
                SELECT user_id, username, (revenant_xp + tarantula_xp + sven_xp + voidgloom_xp + inferno_xp) as total_slayer
                FROM players ORDER BY total_slayer DESC LIMIT ?
            '''
        else:
            return []
        
        async with self.conn.execute(query, (limit,)) as cursor:
            rows = await cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
