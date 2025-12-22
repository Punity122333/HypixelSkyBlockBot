from typing import Dict, List, Optional
from .core import DatabaseCore
import time


class PlayersDB(DatabaseCore):
    async def create_player(self, user_id: int, username: str):
        await self.execute(
            'INSERT OR IGNORE INTO players (user_id, username, created_at) VALUES (?, ?, ?)',
            (user_id, username, int(time.time()))
        )
        
        await self.execute(
            'INSERT OR IGNORE INTO player_stats (user_id) VALUES (?)',
            (user_id,)
        )
        
        await self.execute(
            'INSERT OR IGNORE INTO player_economy (user_id) VALUES (?)',
            (user_id,)
        )
        
        await self.execute(
            'INSERT OR IGNORE INTO player_dungeon_stats (user_id) VALUES (?)',
            (user_id,)
        )
        
        await self.execute(
            'INSERT OR IGNORE INTO player_progression (user_id) VALUES (?)',
            (user_id,)
        )
        
        skills = ['farming', 'mining', 'combat', 'foraging', 'fishing', 'enchanting', 'alchemy', 'taming', 'carpentry', 'runecrafting', 'social']
        for skill in skills:
            await self.execute(
                'INSERT OR IGNORE INTO skills (user_id, skill_name) VALUES (?, ?)',
                (user_id, skill)
            )
        
        await self.commit()

    async def get_player(self, user_id: int) -> Optional[Dict]:
        row = await self.fetchone(
            '''SELECT 
               p.user_id, p.username, p.created_at,
               s.*,
               e.coins, e.bank, e.bank_capacity, e.total_earned, e.total_spent, 
               e.trading_reputation, e.merchant_level,
               d.catacombs_level, d.catacombs_xp
               FROM players p
               LEFT JOIN player_stats s ON p.user_id = s.user_id
               LEFT JOIN player_economy e ON p.user_id = e.user_id
               LEFT JOIN player_dungeon_stats d ON p.user_id = d.user_id
               WHERE p.user_id = ?''',
            (user_id,)
        )
        return dict(row) if row else None

    async def update_player(self, user_id: int, **kwargs):
        stat_fields = [
            'health', 'max_health', 'mana', 'max_mana', 'defense', 'strength', 
            'crit_chance', 'crit_damage', 'intelligence', 'speed', 'sea_creature_chance',
            'magic_find', 'pet_luck', 'ferocity', 'ability_damage', 'mining_speed',
            'mining_fortune', 'farming_fortune', 'foraging_fortune', 'fishing_speed',
            'attack_speed', 'true_defense'
        ]

        economy_fields = [
            'coins', 'bank', 'bank_capacity', 'total_earned', 'total_spent',
            'trading_reputation', 'merchant_level'
        ]
        
        dungeon_fields = ['catacombs_level', 'catacombs_xp']
        player_fields = ['username', 'playtime_minutes']

        stat_updates = {k: v for k, v in kwargs.items() if k in stat_fields}
        player_updates = {k: v for k, v in kwargs.items() if k in player_fields}
        economy_updates = {k: v for k, v in kwargs.items() if k in economy_fields}
        dungeon_updates = {k: v for k, v in kwargs.items() if k in dungeon_fields}

        if stat_updates:
            set_clause = ', '.join([f'{k} = ?' for k in stat_updates.keys()])
            values = list(stat_updates.values()) + [user_id]
            await self.execute(
                f'UPDATE player_stats SET {set_clause} WHERE user_id = ?',
                tuple(values)
            )

        if player_updates:
            set_clause = ', '.join([f'{k} = ?' for k in player_updates.keys()])
            values = list(player_updates.values()) + [user_id]
            await self.execute(
                f'UPDATE players SET {set_clause} WHERE user_id = ?',
                tuple(values)
            )

        if economy_updates:
            set_clause = ', '.join([f'{k} = ?' for k in economy_updates.keys()])
            values = list(economy_updates.values()) + [user_id]
            await self.execute(
                f'UPDATE player_economy SET {set_clause} WHERE user_id = ?',
                tuple(values)
            )

        if dungeon_updates:
            set_clause = ', '.join([f'{k} = ?' for k in dungeon_updates.keys()])
            values = list(dungeon_updates.values()) + [user_id]
            await self.execute(
                f'UPDATE player_dungeon_stats SET {set_clause} WHERE user_id = ?',
                tuple(values)
            )

        await self.commit()

    async def get_player_stats(self, user_id: int) -> Optional[Dict]:
        row = await self.fetchone(
            'SELECT * FROM player_stats WHERE user_id = ?',
            (user_id,)
        )
        return dict(row) if row else None

    async def update_player_stats(self, user_id: int, **kwargs):
        await self.execute(
            'INSERT OR IGNORE INTO player_stats (user_id) VALUES (?)',
            (user_id,)
        )
        
        if not kwargs:
            return
        
        set_clause = ', '.join([f'{k} = ?' for k in kwargs.keys()])
        values = list(kwargs.values()) + [user_id]
        await self.execute(
            f'UPDATE player_stats SET {set_clause} WHERE user_id = ?',
            tuple(values)
        )
        await self.commit()

    async def get_leaderboard(self, category: str, limit: int = 100) -> List[Dict]:
        category = category.lower().strip()
        if category == 'coins':
            query = '''SELECT p.user_id, p.username, e.coins 
                      FROM players p 
                      JOIN player_economy e ON p.user_id = e.user_id
                      ORDER BY e.coins DESC LIMIT ?'''
        elif category == 'networth':
            query = '''SELECT p.user_id, p.username, (e.coins + e.bank) as networth 
                      FROM players p
                      JOIN player_economy e ON p.user_id = e.user_id
                      ORDER BY networth DESC LIMIT ?'''
        elif category == 'skill_avg':
            query = '''SELECT p.user_id, p.username, AVG(s.level) as skill_avg
                      FROM players p
                      JOIN skills s ON p.user_id = s.user_id
                      GROUP BY p.user_id
                      ORDER BY skill_avg DESC LIMIT ?'''
        elif category == 'catacombs':
            query = '''SELECT p.user_id, p.username, d.catacombs_level
                      FROM players p
                      JOIN player_dungeon_stats d ON p.user_id = d.user_id
                      ORDER BY d.catacombs_level DESC LIMIT ?'''
        elif category == 'slayer':
            query = '''SELECT p.user_id, p.username, SUM(sp.xp) as total_slayer
                      FROM players p
                      JOIN player_slayer_progress sp ON p.user_id = sp.user_id
                      GROUP BY p.user_id
                      ORDER BY total_slayer DESC LIMIT ?'''
        else:
            return []
        
        rows = await self.fetchall(query, (limit,))
        return [dict(row) for row in rows]

    async def get_player_progression(self, user_id: int) -> Optional[Dict]:
        row = await self.fetchone(
            'SELECT * FROM player_progression WHERE user_id = ?',
            (user_id,)
        )
        return dict(row) if row else None

    async def update_progression(self, user_id: int, **kwargs):
        progression = await self.get_player_progression(user_id)
        
        if not progression:
            await self.execute(
                'INSERT INTO player_progression (user_id) VALUES (?)',
                (user_id,)
            )
            await self.commit()
        
        if not kwargs:
            return
        
        set_clause = ', '.join([f'{k} = ?' for k in kwargs.keys()])
        values = list(kwargs.values()) + [user_id]
        
        try:
            await self.execute(
                f'UPDATE player_progression SET {set_clause} WHERE user_id = ?',
                tuple(values)
            )
            await self.commit()
        except Exception as e:
            print(f"Error updating progression for user {user_id}: {e}")
            print(f"Attempted to update columns: {list(kwargs.keys())}")
            if self.conn:
                cursor = await self.conn.execute("PRAGMA table_info(player_progression)")
                columns = await cursor.fetchall()
                existing_cols = [col['name'] for col in columns]
                print(f"Existing columns in player_progression: {existing_cols}")
            raise

    async def unlock_achievement(self, user_id: int, achievement_id: str):
        await self.execute(
            'INSERT OR IGNORE INTO player_achievements (user_id, achievement_id, unlocked_at) VALUES (?, ?, ?)',
            (user_id, achievement_id, int(time.time()))
        )
        await self.commit()

    async def get_achievements(self, user_id: int) -> List[str]:
        rows = await self.fetchall(
            'SELECT achievement_id FROM player_achievements WHERE user_id = ?',
            (user_id,)
        )
        return [row['achievement_id'] for row in rows]

    async def unlock_location(self, user_id: int, location_id: str):
        await self.execute(
            'INSERT OR IGNORE INTO player_unlocked_locations (user_id, location_id, unlocked_at) VALUES (?, ?, ?)',
            (user_id, location_id, int(time.time()))
        )
        await self.commit()

    async def get_unlocked_locations(self, user_id: int) -> List[str]:
        rows = await self.fetchall(
            'SELECT location_id FROM player_unlocked_locations WHERE user_id = ?',
            (user_id,)
        )
        return [row['location_id'] for row in rows]

    async def log_rare_drop(self, user_id: int, item_id: str, rarity: str, source: str):
        await self.execute(
            '''INSERT INTO item_rarity_drops (user_id, item_id, rarity, dropped_from, timestamp)
               VALUES (?, ?, ?, ?, ?)''',
            (user_id, item_id, rarity, source, int(time.time()))
        )
        await self.commit()

    async def get_talisman_pouch_capacity(self, user_id: int) -> int:
        progression = await self.get_player_progression(user_id)
        if progression and 'talisman_pouch_capacity' in progression:
            return progression['talisman_pouch_capacity']
        return 24

    async def upgrade_talisman_pouch_capacity(self, user_id: int, new_capacity: int) -> bool:
        await self.update_progression(user_id, talisman_pouch_capacity=new_capacity)
        return True
