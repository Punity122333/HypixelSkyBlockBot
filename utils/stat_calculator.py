from typing import Dict, List, Optional, Any
from .comprehensive_stat_calculator import ComprehensiveStatCalculator


class StatCalculator:
    
    @staticmethod
    async def calculate_player_stats(db, game_data, user_id: int) -> Dict[str, Any]:
        return await ComprehensiveStatCalculator.calculate_full_stats(db, user_id)
    
    @staticmethod
    def apply_combat_effects(stats: Dict, item: Optional[Dict], enchants: Optional[List] = None) -> Dict[str, Any]:
        weapon_damage = 0
        if item and item.get('stats', {}).get('damage'):
            weapon_damage = item['stats']['damage']
        
        damage = ComprehensiveStatCalculator.calculate_damage(stats, weapon_damage, False)
        crit_damage = ComprehensiveStatCalculator.calculate_damage(stats, weapon_damage, True)
        
        return {
            'base_damage': damage,
            'crit_chance': ComprehensiveStatCalculator.get_crit_chance(stats),
            'crit_damage_multiplier': crit_damage / damage if damage > 0 else 1.0,
            'attack_speed': ComprehensiveStatCalculator.calculate_attack_speed(stats),
            'ability_damage': stats.get('ability_damage', 0)
        }
    
    @staticmethod
    def apply_gathering_effects(stats: Dict, tool_type: str) -> Dict[str, Any]:
        effects = {
            'speed_bonus': 0,
            'fortune_bonus': 0,
            'efficiency': 1.0
        }
        
        if tool_type == 'pickaxe':
            effects['speed_bonus'] = stats.get('mining_speed', 0)
            effects['fortune_bonus'] = stats.get('mining_fortune', 0)
        elif tool_type == 'axe':
            effects['fortune_bonus'] = stats.get('foraging_fortune', 0)
        elif tool_type == 'hoe':
            effects['fortune_bonus'] = stats.get('farming_fortune', 0)
        elif tool_type == 'fishing_rod':
            effects['speed_bonus'] = stats.get('fishing_speed', 0)
            effects['sea_creature_chance'] = stats.get('sea_creature_chance', 0)
        
        return effects
    
    @staticmethod
    def calculate_damage_reduction(defense: int, true_defense: int = 0) -> float:
        base_reduction = defense / (defense + 100)
        base_reduction = min(0.75, base_reduction)
        
        true_def_reduction = true_defense / (true_defense + 100)
        total_reduction = base_reduction + (true_def_reduction * (1 - base_reduction))
        
        total_reduction = min(0.99, total_reduction)
        
        return total_reduction
    
    @staticmethod
    def calculate_drop_bonus(magic_find: int, pet_luck: int = 0) -> float:
        stats = {'magic_find': magic_find, 'pet_luck': pet_luck}
        return ComprehensiveStatCalculator.calculate_drop_multiplier(stats)

    @staticmethod
    def calculate_pet_stats(pet: Dict) -> Dict[str, int]:
        pet_stats = {}
        
        pet_type = pet.get('pet_type', '')
        rarity = pet.get('rarity', 'COMMON')
        level = pet.get('level', 1)
        
        base_stats_map = {
            'COMMON': {'health': 5, 'strength': 2},
            'UNCOMMON': {'health': 10, 'strength': 5},
            'RARE': {'health': 20, 'strength': 10},
            'EPIC': {'health': 40, 'strength': 20},
            'LEGENDARY': {'health': 100, 'strength': 50},
            'MYTHIC': {'health': 200, 'strength': 100}
        }
        
        base_stats = base_stats_map.get(rarity, {'health': 5, 'strength': 2})
        
        for stat, value in base_stats.items():
            scaled_value = int(value * (level / 100))
            pet_stats[stat] = scaled_value
        
        return pet_stats


async def get_enchantment(game_data, enchant_name: str) -> Optional[Dict]:
    return await game_data.get_enchantment(enchant_name.lower())


async def get_reforge_stats(game_data, reforge_name: str, item_type: str) -> Dict[str, int]:
    reforge = await game_data.get_reforge(reforge_name.lower())
    if not reforge:
        return {}
    
    if item_type.upper() in reforge.get('applies_to', []):
        return reforge.get('stat_bonuses', {})
    return {}

