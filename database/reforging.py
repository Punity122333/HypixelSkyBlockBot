from typing import Dict, Optional, List, Any
from .core import DatabaseCore
import random
import json


class ReforgingDB(DatabaseCore):
    
    async def get_rarity_stat_ranges(self, rarity: str) -> Optional[Dict[str, tuple]]:
        row = await self.fetchone(
            '''SELECT strength_min, strength_max, crit_damage_min, crit_damage_max,
                      defense_min, defense_max, health_min, health_max
               FROM reforge_rarity_stat_ranges WHERE rarity = ?''',
            (rarity,)
        )
        if not row:
            return None
        return {
            'strength': (row['strength_min'], row['strength_max']),
            'crit_damage': (row['crit_damage_min'], row['crit_damage_max']),
            'defense': (row['defense_min'], row['defense_max']),
            'health': (row['health_min'], row['health_max'])
        }
    
    async def reroll_item_stats(self, user_id: int, inventory_item_id: int, rarity: str) -> Dict[str, Any]:
        stat_ranges = await self.get_rarity_stat_ranges(rarity)
        if not stat_ranges:
            return {'success': False, 'error': 'Invalid rarity'}
        
        num_stats = random.randint(1, min(3, len(stat_ranges)))
        selected_stats = random.sample(list(stat_ranges.keys()), num_stats)
        
        new_stats = {}
        for stat in selected_stats:
            min_val, max_val = stat_ranges[stat]
            new_stats[stat] = random.randint(min_val, max_val)
        
        await self.execute(
            '''INSERT OR REPLACE INTO inventory_item_reforged_stats 
               (inventory_item_id, reforged_stats, reforged_at)
               VALUES (?, ?, ?)''',
            (inventory_item_id, json.dumps(new_stats), self._get_timestamp())
        )
        await self.commit()
        
        return {'success': True, 'stats': new_stats}
    
    async def get_reforged_stats(self, inventory_item_id: int) -> Optional[Dict[str, int]]:
        row = await self.fetchone(
            'SELECT reforged_stats FROM inventory_item_reforged_stats WHERE inventory_item_id = ?',
            (inventory_item_id,)
        )
        
        if row and row['reforged_stats']:
            return json.loads(row['reforged_stats'])
        
        return None
    
    def _get_timestamp(self) -> int:
        import time
        return int(time.time())
