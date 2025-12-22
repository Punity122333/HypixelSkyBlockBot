from typing import Dict, List
import time
from .core import DatabaseCore

class BadgeDB(DatabaseCore):
    
    async def get_badges_dict(self) -> Dict:
        rows = await self.fetchall('SELECT * FROM game_badges')
        return {row['badge_id']: {'name': row['name'], 'description': row['description'], 'category': row['category']} for row in rows}
    
    async def get_all_badges(self) -> List[Dict]:
        rows = await self.fetchall('SELECT * FROM game_badges ORDER BY category, badge_id')
        return [dict(row) for row in rows]
    
    async def unlock_badge(self, user_id: int, badge_id: str) -> bool:
        if not user_id or not badge_id:
            return False
            
        badges = await self.get_badges_dict()
        if badge_id not in badges:
            return False
        
        existing = await self.fetchone(
            'SELECT id FROM player_badges WHERE user_id = ? AND badge_id = ?',
            (user_id, badge_id)
        )
        
        if existing:
            return False
        
        await self.execute(
            'INSERT INTO player_badges (user_id, badge_id, unlocked_at) VALUES (?, ?, ?)',
            (user_id, badge_id, int(time.time()))
        )
        await self.commit()
        
        return True
    
    async def get_player_badges(self, user_id: int) -> List[Dict]:
        rows = await self.fetchall(
            '''SELECT pb.*, gb.name, gb.description, gb.category 
               FROM player_badges pb
               JOIN game_badges gb ON pb.badge_id = gb.badge_id
               WHERE pb.user_id = ? 
               ORDER BY pb.unlocked_at DESC''',
            (user_id,)
        )
        
        return [dict(row) for row in rows]
    
    async def check_and_unlock_badges(self, user_id: int, context: str, **kwargs):
        player = await self.fetchone('SELECT * FROM players WHERE user_id = ?', (user_id,))
        if not player:
            return
        
        stats = await self.fetchone('SELECT * FROM player_stats WHERE user_id = ?', (user_id,))
        
        if context == 'death':
            death_count = kwargs.get('death_count', 0)
            if death_count == 1:
                await self.unlock_badge(user_id, 'first_death')
            elif death_count == 100:
                await self.unlock_badge(user_id, 'death_100')
            elif death_count == 1000:
                await self.unlock_badge(user_id, 'death_1000')
        
        elif context == 'networth':
            networth = kwargs.get('networth', 0)
            if networth >= 1000:
                await self.unlock_badge(user_id, 'networth_1k')
            if networth >= 10000:
                await self.unlock_badge(user_id, 'networth_10k')
            if networth >= 100000:
                await self.unlock_badge(user_id, 'networth_100k')
            if networth >= 1000000:
                await self.unlock_badge(user_id, 'networth_1m')
            if networth >= 10000000:
                await self.unlock_badge(user_id, 'networth_10m')
        
        elif context == 'minion':
            minion_count = kwargs.get('minion_count', 0)
            if minion_count == 1:
                await self.unlock_badge(user_id, 'first_minion')
            elif minion_count >= 10:
                await self.unlock_badge(user_id, 'minion_10')
        
        elif context == 'coins':
            player_economy = await self.fetchone('SELECT coins FROM player_economy WHERE user_id = ?', (user_id,))
            if player_economy and player_economy['coins'] == 0:
                await self.unlock_badge(user_id, 'broke')
        
        elif context == 'stats' and stats:
            speed = stats['speed'] if 'speed' in stats.keys() else 0
            defense = stats['defense'] if 'defense' in stats.keys() else 0
            strength = stats['strength'] if 'strength' in stats.keys() else 0
            intelligence = stats['intelligence'] if 'intelligence' in stats.keys() else 0
            crit_chance = stats['crit_chance'] if 'crit_chance' in stats.keys() else 0
            
            if speed >= 500:
                await self.unlock_badge(user_id, 'speed_demon')
            if defense >= 1000:
                await self.unlock_badge(user_id, 'tank')
            if strength >= 500 and defense < 100:
                await self.unlock_badge(user_id, 'glass_cannon')
            if intelligence >= 1000:
                await self.unlock_badge(user_id, 'wizard')
            if crit_chance >= 100:
                await self.unlock_badge(user_id, 'crit_master')
