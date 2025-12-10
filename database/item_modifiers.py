from typing import Dict, Optional, List, Any
import time
import json
import random
from .core import DatabaseCore

class ItemModifierDB(DatabaseCore):
    
    LORE_PREFIXES = {
        'arcane': {'name': '⚡ Arcane', 'color': 'blue', 'stats': {'intelligence': 5, 'ability_damage': 3}},
        'blazing': {'name': '🔥 Blazing', 'color': 'red', 'stats': {'strength': 3, 'crit_damage': 5}},
        'bloodbound': {'name': '🩸 Bloodbound', 'color': 'dark_red', 'stats': {'health': 20, 'ferocity': 2}},
        'frozen': {'name': '❄️ Frozen', 'color': 'cyan', 'stats': {'intelligence': 3, 'defense': 5}},
        'gilded': {'name': '✨ Gilded', 'color': 'gold', 'stats': {'magic_find': 2, 'pet_luck': 1}},
        'hallowed': {'name': '✝️ Hallowed', 'color': 'white', 'stats': {'defense': 5, 'health': 15}},
        'titanic': {'name': '⚔️ Titanic', 'color': 'purple', 'stats': {'strength': 5, 'health': 10}},
        'swift': {'name': '💨 Swift', 'color': 'green', 'stats': {'speed': 10, 'attack_speed': 5}},
        'vampiric': {'name': '🧛 Vampiric', 'color': 'dark_red', 'stats': {'health': 25, 'strength': 2}},
        'wise': {'name': '🧙 Wise', 'color': 'purple', 'stats': {'intelligence': 10, 'mana': 50}},
        'lucky': {'name': '🍀 Lucky', 'color': 'green', 'stats': {'magic_find': 5, 'pet_luck': 3}},
        'powerful': {'name': '💪 Powerful', 'color': 'red', 'stats': {'strength': 7, 'crit_damage': 10}},
        'fortified': {'name': '🛡️ Fortified', 'color': 'gray', 'stats': {'defense': 10, 'true_defense': 3}},
        'prosperous': {'name': '💰 Prosperous', 'color': 'gold', 'stats': {'mining_fortune': 10, 'farming_fortune': 10}},
    }
    
    LORE_SUFFIXES = {
        'the_end': {'name': 'of the End', 'stats': {'health': 10, 'defense': 5}},
        'the_nether': {'name': 'of the Nether', 'stats': {'strength': 5, 'ferocity': 2}},
        'dragons': {'name': 'of Dragons', 'stats': {'health': 20, 'strength': 10}},
        'the_depths': {'name': 'of the Depths', 'stats': {'fishing_speed': 10, 'sea_creature_chance': 5}},
        'mining': {'name': 'of Mining', 'stats': {'mining_speed': 10, 'mining_fortune': 15}},
        'farming': {'name': 'of Farming', 'stats': {'farming_fortune': 15, 'speed': 5}},
        'combat': {'name': 'of Combat', 'stats': {'crit_chance': 5, 'crit_damage': 15}},
        'wealth': {'name': 'of Wealth', 'stats': {'magic_find': 3}},
    }
    
    STAT_MUTATIONS = [
        {'stat': 'strength', 'min': 1, 'max': 10, 'weight': 10},
        {'stat': 'crit_damage', 'min': 2, 'max': 20, 'weight': 8},
        {'stat': 'health', 'min': 5, 'max': 50, 'weight': 10},
        {'stat': 'defense', 'min': 2, 'max': 15, 'weight': 9},
        {'stat': 'intelligence', 'min': 2, 'max': 25, 'weight': 7},
        {'stat': 'mining_fortune', 'min': 3, 'max': 20, 'weight': 6},
        {'stat': 'farming_fortune', 'min': 3, 'max': 20, 'weight': 6},
        {'stat': 'foraging_fortune', 'min': 3, 'max': 20, 'weight': 6},
        {'stat': 'magic_find', 'min': 1, 'max': 5, 'weight': 3},
        {'stat': 'pet_luck', 'min': 1, 'max': 3, 'weight': 2},
        {'stat': 'speed', 'min': 5, 'max': 15, 'weight': 5},
        {'stat': 'attack_speed', 'min': 2, 'max': 10, 'weight': 4},
        {'stat': 'ferocity', 'min': 1, 'max': 5, 'weight': 4},
        {'stat': 'true_defense', 'min': 1, 'max': 5, 'weight': 2},
    ]
    
    async def apply_random_modifier(self, user_id: int, inventory_item_id: int, item_id: str) -> Optional[Dict[str, Any]]:
        modifier_chance = random.random()
        
        if modifier_chance < 0.3:
            return None
        
        modifier_type = random.choice(['prefix', 'suffix', 'stat_mutation', 'double'])
        
        modifiers = []
        total_stats: Dict[str, int] = {}
        
        if modifier_type == 'prefix' or modifier_type == 'double':
            prefix_id = random.choice(list(self.LORE_PREFIXES.keys()))
            prefix_data = self.LORE_PREFIXES[prefix_id]
            modifiers.append({'type': 'prefix', 'id': prefix_id, 'name': prefix_data['name']})
            
            for stat, value in prefix_data['stats'].items():
                total_stats[stat] = total_stats.get(stat, 0) + value
        
        if modifier_type == 'suffix' or modifier_type == 'double':
            suffix_id = random.choice(list(self.LORE_SUFFIXES.keys()))
            suffix_data = self.LORE_SUFFIXES[suffix_id]
            modifiers.append({'type': 'suffix', 'id': suffix_id, 'name': suffix_data['name']})
            
            for stat, value in suffix_data['stats'].items():
                total_stats[stat] = total_stats.get(stat, 0) + value
        
        if modifier_type == 'stat_mutation':
            num_mutations = random.randint(1, 3)
            selected_mutations = random.sample(self.STAT_MUTATIONS, min(num_mutations, len(self.STAT_MUTATIONS)))
            
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
