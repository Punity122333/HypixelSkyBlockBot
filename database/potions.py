from typing import Dict, List, Optional, Any
from .core import DatabaseCore
import time


class PotionsDB(DatabaseCore):
    """Database operations for potion system"""
    
    async def add_active_potion(self, user_id: int, potion_id: str, level: int, duration: int) -> None:
        """Add an active potion effect for a player"""
        current_time = int(time.time())
        expires_at = current_time + duration
        
        await self.execute(
            '''INSERT INTO active_potions (user_id, potion_id, level, duration, applied_at, expires_at)
               VALUES (?, ?, ?, ?, ?, ?)''',
            (user_id, potion_id, level, duration, current_time, expires_at)
        )
        await self.commit()
    
    async def remove_expired_potions(self, user_id: int) -> None:
        """Remove all expired potions for a player"""
        current_time = int(time.time())
        
        await self.execute(
            'DELETE FROM active_potions WHERE user_id = ? AND expires_at <= ?',
            (user_id, current_time)
        )
        await self.commit()
    
    async def get_active_potions(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all active (non-expired) potions for a player"""
        current_time = int(time.time())
        
        rows = await self.fetchall(
            '''SELECT * FROM active_potions 
               WHERE user_id = ? AND expires_at > ?
               ORDER BY expires_at DESC''',
            (user_id, current_time)
        )
        
        return [dict(row) for row in rows]
    
    async def clear_all_potions(self, user_id: int) -> None:
        """Clear all active potions for a player"""
        await self.execute(
            'DELETE FROM active_potions WHERE user_id = ?',
            (user_id,)
        )
        await self.commit()
