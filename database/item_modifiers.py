from typing import Dict, Optional, List, Any
import time
import json
import random
from .core import DatabaseCore

class ItemModifierDB(DatabaseCore):
    
    async def get_lore_prefix(self, prefix_id: str) -> Optional[Dict]:
        row = await self.fetchone(
            'SELECT prefix_id, display_name, color, stats FROM item_lore_prefixes WHERE prefix_id = ?',
            (prefix_id,)
        )
        if not row:
            return None
        return {
            'name': row['display_name'],
            'color': row['color'],
            'stats': json.loads(row['stats'])
        }
    
    async def get_all_lore_prefixes(self) -> Dict[str, Dict]:
        rows = await self.fetchall('SELECT prefix_id, display_name, color, stats FROM item_lore_prefixes')
        return {
            row['prefix_id']: {
                'name': row['display_name'],
                'color': row['color'],
                'stats': json.loads(row['stats'])
            }
            for row in rows
        }
    
    async def get_lore_suffix(self, suffix_id: str) -> Optional[Dict]:
        row = await self.fetchone(
            'SELECT suffix_id, display_name, stats FROM item_lore_suffixes WHERE suffix_id = ?',
            (suffix_id,)
        )
        if not row:
            return None
        return {
            'name': row['display_name'],
            'stats': json.loads(row['stats'])
        }
    
    async def get_all_lore_suffixes(self) -> Dict[str, Dict]:
        rows = await self.fetchall('SELECT suffix_id, display_name, stats FROM item_lore_suffixes')
        return {
            row['suffix_id']: {
                'name': row['display_name'],
                'stats': json.loads(row['stats'])
            }
            for row in rows
        }
    
    async def get_stat_mutations(self) -> List[Dict]:
        rows = await self.fetchall('SELECT stat, min_value, max_value, weight FROM item_stat_mutations')
        return [{'stat': row['stat'], 'min': row['min_value'], 'max': row['max_value'], 'weight': row['weight']} for row in rows]
    
    async def apply_random_modifier(self, user_id: int, inventory_item_id: int, item_id: str) -> Optional[Dict[str, Any]]:
        modifier_chance = random.random()
        
        if modifier_chance < 0.3:
            return None
        
        modifier_type = random.choice(['prefix', 'suffix', 'stat_mutation', 'double'])
        
        modifiers = []
        total_stats: Dict[str, int] = {}
        
        if modifier_type == 'prefix' or modifier_type == 'double':
            all_prefixes = await self.get_all_lore_prefixes()
            prefix_id = random.choice(list(all_prefixes.keys()))
            prefix_data = all_prefixes[prefix_id]
            modifiers.append({'type': 'prefix', 'id': prefix_id, 'name': prefix_data['name']})
            
            for stat, value in prefix_data['stats'].items():
                total_stats[stat] = total_stats.get(stat, 0) + value
        
        if modifier_type == 'suffix' or modifier_type == 'double':
            all_suffixes = await self.get_all_lore_suffixes()
            suffix_id = random.choice(list(all_suffixes.keys()))
            suffix_data = all_suffixes[suffix_id]
            modifiers.append({'type': 'suffix', 'id': suffix_id, 'name': suffix_data['name']})
            
            for stat, value in suffix_data['stats'].items():
                total_stats[stat] = total_stats.get(stat, 0) + value
        
        if modifier_type == 'stat_mutation':
            stat_mutations = await self.get_stat_mutations()
            num_mutations = random.randint(1, 3)
            selected_mutations = random.sample(stat_mutations, min(num_mutations, len(stat_mutations)))
            
            for mutation in selected_mutations:
                stat_value = random.randint(mutation['min'], mutation['max'])
                total_stats[mutation['stat']] = total_stats.get(mutation['stat'], 0) + stat_value
                modifiers.append({'type': 'mutation', 'stat': mutation['stat'], 'value': stat_value})
        
        modifier_data = {
            'modifiers': modifiers,
            'stats': total_stats
        }
        
        await self.execute(
            '''INSERT OR REPLACE INTO inventory_item_modifiers (inventory_item_id, modifier_data, applied_at)
               VALUES (?, ?, ?)''',
            (inventory_item_id, json.dumps(modifier_data), int(time.time()))
        )
        await self.commit()
        
        return modifier_data
    
    async def get_item_modifiers(self, inventory_item_id: int) -> Optional[Dict[str, Any]]:
        row = await self.fetchone(
            'SELECT modifier_data FROM inventory_item_modifiers WHERE inventory_item_id = ?',
            (inventory_item_id,)
        )
        
        if row and row['modifier_data']:
            return json.loads(row['modifier_data'])
        
        return None
    
    async def calculate_modifier_stats(self, modifiers: Optional[Dict[str, Any]]) -> Dict[str, int]:
        if not modifiers or 'stats' not in modifiers:
            return {}
        
        return modifiers['stats']
    
    def format_modifier_display(self, modifiers: Optional[Dict[str, Any]]) -> str:
        if not modifiers or 'modifiers' not in modifiers:
            return ''
        
        parts = []
        
        for modifier in modifiers['modifiers']:
            if modifier['type'] == 'prefix':
                parts.append(modifier['name'])
            elif modifier['type'] == 'suffix':
                parts.append(modifier['name'])
            elif modifier['type'] == 'mutation':
                parts.append(f"+{modifier['value']} {modifier['stat'].replace('_', ' ').title()}")
        
        return ' | '.join(parts)
