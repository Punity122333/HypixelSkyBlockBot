from typing import Dict, Any, List, Optional
from .core import DatabaseCore

class HotmDB(DatabaseCore):
    """Database operations for Heart of the Mountain (HotM) system"""
    
    async def get_hotm_data(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get player's HotM data"""
        row = await self.fetchone('SELECT * FROM player_hotm WHERE user_id = ?', (user_id,))
        return dict(row) if row else None
    
    async def initialize_hotm(self, user_id: int):
        """Initialize HotM data for a player"""
        await self.execute('''
            INSERT OR IGNORE INTO player_hotm (user_id, hotm_level, hotm_xp, hotm_tier, token_of_the_mountain)
            VALUES (?, 1, 0, 1, 2)
        ''', (user_id,))
        await self.commit()
    
    async def update_hotm_xp(self, user_id: int, new_xp: int, new_tier: int, tokens_gained: int):
        """Update player's HotM XP, tier, and tokens"""
        await self.execute('''
            UPDATE player_hotm 
            SET hotm_xp = ?, hotm_tier = ?, token_of_the_mountain = token_of_the_mountain + ?
            WHERE user_id = ?
        ''', (new_xp, new_tier, tokens_gained, user_id))
        await self.commit()
    
    async def get_perk_data(self, perk_id: str) -> Optional[Dict[str, Any]]:
        """Get data for a specific HotM perk"""
        row = await self.fetchone('SELECT * FROM hotm_perks WHERE perk_id = ?', (perk_id,))
        return dict(row) if row else None
    
    async def get_player_perk(self, user_id: int, perk_id: str) -> Optional[Dict[str, Any]]:
        """Get player's specific perk level"""
        row = await self.fetchone(
            'SELECT * FROM player_hotm_perks WHERE user_id = ? AND perk_id = ?',
            (user_id, perk_id)
        )
        return dict(row) if row else None
    
    async def unlock_or_upgrade_perk(self, user_id: int, perk_id: str, new_level: int):
        """Unlock or upgrade a perk for a player"""
        await self.execute('''
            INSERT INTO player_hotm_perks (user_id, perk_id, perk_level)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id, perk_id) DO UPDATE SET perk_level = ?
        ''', (user_id, perk_id, new_level, new_level))
        await self.commit()
    
    async def deduct_tokens(self, user_id: int, cost: int):
        """Deduct tokens from player's HotM"""
        await self.execute('''
            UPDATE player_hotm SET token_of_the_mountain = token_of_the_mountain - ?
            WHERE user_id = ?
        ''', (cost, user_id))
        await self.commit()
    
    async def get_player_perks(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all perks unlocked by a player with details"""
        rows = await self.fetchall('''
            SELECT pp.*, hp.perk_name, hp.max_level, hp.tier, hp.description, hp.stat_bonuses
            FROM player_hotm_perks pp
            JOIN hotm_perks hp ON pp.perk_id = hp.perk_id
            WHERE pp.user_id = ?
        ''', (user_id,))
        return [dict(row) for row in rows]
    
    async def get_all_perks(self) -> List[Dict[str, Any]]:
        """Get all available HotM perks"""
        rows = await self.fetchall('SELECT * FROM hotm_perks')
        return [dict(row) for row in rows]
    
    async def add_powder(self, user_id: int, powder_type: str, amount: int):
        """Add powder to player's HotM"""
        column_map = {
            'mithril': 'powder_mithril',
            'gemstone': 'powder_gemstone',
            'glacite': 'powder_glacite'
        }
        
        column = column_map.get(powder_type, 'powder_mithril')
        
        await self.execute(f'''
            UPDATE player_hotm SET {column} = {column} + ?
            WHERE user_id = ?
        ''', (amount, user_id))
        await self.commit()
