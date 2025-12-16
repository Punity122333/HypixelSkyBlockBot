from typing import Dict, Any, List, Optional
from .core import DatabaseCore
import time

class DwarvenMinesDB(DatabaseCore):
    """Database operations for Dwarven Mines system"""
    
    async def get_dwarven_progress(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get player's Dwarven Mines progress"""
        row = await self.fetchone('SELECT * FROM dwarven_mines_progress WHERE user_id = ?', (user_id,))
        return dict(row) if row else None
    
    async def initialize_dwarven_progress(self, user_id: int):
        """Initialize Dwarven Mines progress for a player"""
        await self.execute('''
            INSERT OR IGNORE INTO dwarven_mines_progress 
            (user_id, commissions_completed, reputation, king_yolkar_unlocked, mithril_unlocked, titanium_unlocked)
            VALUES (?, 0, 0, 0, 1, 0)
        ''', (user_id,))
        await self.commit()
    
    async def clear_incomplete_commissions(self, user_id: int):
        """Delete all incomplete commissions for a player"""
        await self.execute('''
            DELETE FROM player_commissions 
            WHERE user_id = ? AND completed = 0
        ''', (user_id,))
        await self.commit()
    
    async def create_commission(self, user_id: int, commission_type: str, requirement: int, 
                               reward_mithril: int, reward_coins: int, expires_at: int):
        """Create a new commission for a player"""
        await self.execute('''
            INSERT INTO player_commissions 
            (user_id, commission_type, requirement, progress, reward_mithril, reward_coins, expires_at)
            VALUES (?, ?, ?, 0, ?, ?, ?)
        ''', (user_id, commission_type, requirement, reward_mithril, reward_coins, expires_at))
        await self.commit()
    
    async def get_active_commissions(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all active (incomplete, not expired) commissions for a player"""
        current_time = int(time.time())
        rows = await self.fetchall('''
            SELECT * FROM player_commissions 
            WHERE user_id = ? AND completed = 0 AND expires_at > ?
        ''', (user_id, current_time))
        return [dict(row) for row in rows]
    
    async def get_commission_by_type(self, user_id: int, commission_type: str) -> Optional[Dict[str, Any]]:
        """Get an active commission of a specific type for a player"""
        current_time = int(time.time())
        row = await self.fetchone('''
            SELECT * FROM player_commissions 
            WHERE user_id = ? AND commission_type = ? AND completed = 0 AND expires_at > ?
        ''', (user_id, commission_type, current_time))
        return dict(row) if row else None
    
    async def update_commission_progress(self, commission_id: int, new_progress: int, completed: bool):
        """Update the progress and completion status of a commission"""
        await self.execute('''
            UPDATE player_commissions 
            SET progress = ?, completed = ?
            WHERE commission_id = ?
        ''', (new_progress, 1 if completed else 0, commission_id))
        await self.commit()
    
    async def increment_commissions_and_reputation(self, user_id: int, reputation_gain: int):
        """Increment completed commissions count and reputation"""
        await self.execute('''
            UPDATE dwarven_mines_progress 
            SET commissions_completed = commissions_completed + 1,
                reputation = reputation + ?
            WHERE user_id = ?
        ''', (reputation_gain, user_id))
        await self.commit()
