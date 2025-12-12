from typing import Dict, Optional, List, Any
from .core import DatabaseCore
import time
import json


class BossRotationDB(DatabaseCore):
    
    ROTATION_CYCLE_HOURS = 6
    
    async def get_boss_rotation_data(self) -> List[Dict[str, Any]]:
        rows = await self.fetchall(
            'SELECT boss_id, name, emoji, health, damage, defense, rewards_coins, rewards_xp, rotation_order FROM boss_rotation_data ORDER BY rotation_order ASC'
        )
        return [dict(row) for row in rows]
    
    async def get_boss_by_id(self, boss_id: str) -> Optional[Dict[str, Any]]:
        row = await self.fetchone(
            'SELECT boss_id, name, emoji, health, damage, defense, rewards_coins, rewards_xp FROM boss_rotation_data WHERE boss_id = ?',
            (boss_id,)
        )
        return dict(row) if row else None
    
    async def get_current_boss(self) -> Dict[str, Any]:
        boss_rotation = await self.get_boss_rotation_data()
        if not boss_rotation:
            return {}
        
        current_time = int(time.time())
        rotation_seconds = self.ROTATION_CYCLE_HOURS * 3600
        index = (current_time // rotation_seconds) % len(boss_rotation)
        return boss_rotation[index]
    
    def get_time_until_next_boss(self) -> int:
        current_time = int(time.time())
        rotation_seconds = self.ROTATION_CYCLE_HOURS * 3600
        time_in_cycle = current_time % rotation_seconds
        return rotation_seconds - time_in_cycle
    
    async def get_next_boss(self) -> Dict[str, Any]:
        boss_rotation = await self.get_boss_rotation_data()
        if not boss_rotation:
            return {}
        
        current_time = int(time.time())
        rotation_seconds = self.ROTATION_CYCLE_HOURS * 3600
        next_index = ((current_time // rotation_seconds) + 1) % len(boss_rotation)
        return boss_rotation[next_index]
    
    async def record_boss_kill(self, user_id: int, boss_id: str, damage_dealt: int, time_taken: int):
        await self.execute(
            '''INSERT INTO boss_rotation_kills 
               (user_id, boss_id, damage_dealt, time_taken, killed_at)
               VALUES (?, ?, ?, ?, ?)''',
            (user_id, boss_id, damage_dealt, time_taken, int(time.time()))
        )
        await self.commit()
    
    async def get_boss_leaderboard(self, boss_id: str, limit: int = 10) -> List[Dict]:
        rows = await self.fetchall(
            '''SELECT user_id, MIN(time_taken) as best_time, MAX(damage_dealt) as max_damage, COUNT(*) as kills
               FROM boss_rotation_kills 
               WHERE boss_id = ?
               GROUP BY user_id
               ORDER BY best_time ASC LIMIT ?''',
            (boss_id, limit)
        )
        return [dict(row) for row in rows]
    
    async def get_player_boss_stats(self, user_id: int, boss_id: str) -> Optional[Dict]:
        row = await self.fetchone(
            '''SELECT COUNT(*) as total_kills, MIN(time_taken) as best_time, MAX(damage_dealt) as max_damage
               FROM boss_rotation_kills 
               WHERE user_id = ? AND boss_id = ?''',
            (user_id, boss_id)
        )
        
        if row:
            return dict(row)
        return None
