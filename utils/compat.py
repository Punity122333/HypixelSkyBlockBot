import random
from typing import Dict, List, Optional, Tuple

async def get_item(game_data_manager, item_id: str):
    return await game_data_manager.get_item(item_id)

async def get_items_by_type(game_data_manager, item_type: str):
    return await game_data_manager.get_items_by_type(item_type)

async def get_enchantment(game_data_manager, enchant_name: str) -> Optional[Dict]:
    return await game_data_manager.get_enchantment(enchant_name.lower())

async def get_reforge_stats(game_data_manager, reforge_name: str, item_type: str) -> Dict[str, int]:
    reforge = await game_data_manager.get_reforge(reforge_name.lower())
    if not reforge:
        return {}
    
    if item_type.upper() in reforge.get('applies_to', []):
        return reforge.get('stat_bonuses', {})
    return {}

async def roll_loot(game_data_manager, loot_table: Dict, magic_find: float = 0, fortune: int = 0) -> List[Tuple[str, int]]:
    return await game_data_manager.roll_loot(loot_table, magic_find, fortune)

def get_coins_reward(loot_table: Dict) -> int:
    if 'coins' in loot_table:
        min_coins, max_coins = loot_table['coins']
        return random.randint(min_coins, max_coins)
    return 0

def get_xp_reward(loot_table: Dict) -> int:
    return loot_table.get('xp', 0)

def check_sea_creature_spawn(sea_creature_chance: float) -> bool:
    base_chance = 0.02
    total_chance = base_chance + (sea_creature_chance / 100)
    return random.random() < total_chance

async def get_xp_for_level(game_data_manager, skill: str, level: int) -> int:
    return await game_data_manager.get_xp_for_level(skill, level)

async def calculate_level_from_xp(game_data_manager, skill: str, xp: int) -> int:
    return await game_data_manager.calculate_level_from_xp(skill, xp)

async def get_skill_stat_bonuses(game_data_manager, skill_name: str, level: int) -> Dict[str, float]:
    return await game_data_manager.get_skill_stat_bonuses(skill_name, level)
