from typing import Dict, List, Optional, Any
from .core import DatabaseCore


class TalismansDB(DatabaseCore):
    """Database operations for talisman pouch system"""
    
    async def get_talisman_count(self, user_id: int) -> int:
        """Get the count of talismans in a player's pouch"""
        row = await self.fetchone(
            'SELECT COUNT(*) as count FROM player_talisman_pouch WHERE user_id = ?',
            (user_id,)
        )
        return row['count'] if row else 0
    
    async def get_talisman_by_id(self, user_id: int, talisman_id: str) -> Optional[Dict[str, Any]]:
        """Check if a player has a specific talisman in their pouch"""
        row = await self.fetchone(
            'SELECT * FROM player_talisman_pouch WHERE user_id = ? AND talisman_id = ?',
            (user_id, talisman_id)
        )
        return dict(row) if row else None
    
    async def get_talisman_by_slot(self, user_id: int, slot: int) -> Optional[Dict[str, Any]]:
        """Get talisman at a specific slot"""
        row = await self.fetchone(
            'SELECT * FROM player_talisman_pouch WHERE user_id = ? AND slot = ?',
            (user_id, slot)
        )
        return dict(row) if row else None
    
    async def add_talisman(self, user_id: int, talisman_id: str, slot: int) -> None:
        """Add a talisman to player's pouch"""
        await self.execute(
            '''INSERT INTO player_talisman_pouch (user_id, talisman_id, slot, equipped)
               VALUES (?, ?, ?, 1)''',
            (user_id, talisman_id, slot)
        )
        await self.commit()
    
    async def remove_talisman(self, user_id: int, slot: int) -> None:
        """Remove a talisman from player's pouch by slot"""
        await self.execute(
            'DELETE FROM player_talisman_pouch WHERE user_id = ? AND slot = ?',
            (user_id, slot)
        )
        await self.commit()
    
    async def shift_talismans_down(self, user_id: int, from_slot: int) -> None:
        """Shift all talismans down after a slot to fill gaps"""
        await self.execute(
            '''UPDATE player_talisman_pouch 
               SET slot = slot - 1 
               WHERE user_id = ? AND slot > ?''',
            (user_id, from_slot)
        )
        await self.commit()
    
    async def get_all_talismans(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all equipped talismans for a player, ordered by slot"""
        rows = await self.fetchall(
            'SELECT * FROM player_talisman_pouch WHERE user_id = ? AND equipped = 1 ORDER BY slot',
            (user_id,)
        )
        return [dict(row) for row in rows]
    
    async def toggle_talisman_equipped(self, user_id: int, slot: int, equipped: bool) -> None:
        """Toggle whether a talisman is equipped or not"""
        await self.execute(
            'UPDATE player_talisman_pouch SET equipped = ? WHERE user_id = ? AND slot = ?',
            (1 if equipped else 0, user_id, slot)
        )
        await self.commit()
