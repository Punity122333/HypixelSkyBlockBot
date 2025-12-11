from typing import Dict, Any, List, Optional
from .core import DatabaseCore


class CrystalHollowsDB(DatabaseCore):
    """Database operations for Crystal Hollows system"""
    
    async def get_crystal_hollows_progress(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get player's Crystal Hollows progress"""
        row = await self.fetchone('SELECT * FROM crystal_hollows_progress WHERE user_id = ?', (user_id,))
        return dict(row) if row else None
    
    async def initialize_progress(self, user_id: int):
        """Initialize Crystal Hollows progress for a player"""
        await self.execute('''
            INSERT OR IGNORE INTO crystal_hollows_progress 
            (user_id, nucleus_runs, crystals_found, jungle_unlocked, mithril_deposits_unlocked, 
             precursor_unlocked, magma_fields_unlocked, goblin_holdout_unlocked)
            VALUES (?, 0, 0, 0, 0, 0, 1, 0)
        ''', (user_id,))
        await self.commit()
    
    async def unlock_zone(self, user_id: int, zone_column: str):
        """Unlock a specific zone for a player"""
        # zone_column should be one of: jungle_unlocked, mithril_deposits_unlocked, etc.
        await self.execute(f'''
            UPDATE crystal_hollows_progress SET {zone_column} = 1
            WHERE user_id = ?
        ''', (user_id,))
        await self.commit()
    
    async def increment_crystals_found(self, user_id: int):
        """Increment the number of crystals found by a player"""
        await self.execute('''
            UPDATE crystal_hollows_progress 
            SET crystals_found = crystals_found + 1
            WHERE user_id = ?
        ''', (user_id,))
        await self.commit()
    
    async def add_crystal_to_inventory(self, user_id: int, crystal_type: str):
        """Add a crystal to player's inventory"""
        await self.execute('''
            INSERT INTO inventory (user_id, item_id, amount, item_type)
            VALUES (?, ?, 1, 'MATERIAL')
            ON CONFLICT(user_id, item_id) DO UPDATE SET amount = amount + 1
        ''', (user_id, crystal_type))
        await self.commit()
    
    async def increment_nucleus_runs(self, user_id: int):
        """Increment the number of nucleus runs completed by a player"""
        await self.execute('''
            UPDATE crystal_hollows_progress 
            SET nucleus_runs = nucleus_runs + 1
            WHERE user_id = ?
        ''', (user_id,))
        await self.commit()
