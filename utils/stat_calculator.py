from typing import Dict, List, Optional, Any

class StatCalculator:
    
    @staticmethod
    async def calculate_player_stats(db, game_data, user_id: int) -> Dict[str, Any]:
        base_player = await db.get_player(user_id)
        if not base_player:
            return {}
        
        stats = {
            'health': base_player.get('health', 100),
            'max_health': base_player.get('max_health', 100),
            'defense': base_player.get('defense', 0),
            'strength': base_player.get('strength', 0),
            'crit_chance': base_player.get('crit_chance', 30),
            'crit_damage': base_player.get('crit_damage', 50),
            'intelligence': base_player.get('intelligence', 0),
            'speed': base_player.get('speed', 100),
            'mana': base_player.get('mana', 100),
            'max_mana': base_player.get('max_mana', 100),
            'sea_creature_chance': base_player.get('sea_creature_chance', 0),
            'magic_find': base_player.get('magic_find', 0),
            'pet_luck': base_player.get('pet_luck', 0),
            'ferocity': base_player.get('ferocity', 0),
            'ability_damage': base_player.get('ability_damage', 0),
            'mining_speed': base_player.get('mining_speed', 0),
            'mining_fortune': base_player.get('mining_fortune', 0),
            'farming_fortune': base_player.get('farming_fortune', 0),
            'foraging_fortune': base_player.get('foraging_fortune', 0),
            'fishing_speed': base_player.get('fishing_speed', 0),
            'attack_speed': base_player.get('attack_speed', 0),
            'true_defense': base_player.get('true_defense', 0),
        }
        
        inventory = await db.get_inventory(user_id)
        
        for item_data in inventory:
            if item_data.get('equipped', 0) == 1:
                item = await game_data.get_item(item_data['item_id'])
                if item:
                    for stat, value in item.stats.items():
                        if stat in stats:
                            stats[stat] += value
        
        skills = await db.get_skills(user_id)
        for skill in skills:
            skill_name = skill['skill_name']
            level = skill['level']
            
            if skill_name == 'farming':
                stats['health'] += level * 2
                stats['farming_fortune'] += level * 4
            elif skill_name == 'mining':
                stats['defense'] += level * 1
                stats['mining_fortune'] += level * 4
                stats['mining_speed'] += level * 2
            elif skill_name == 'combat':
                stats['crit_chance'] += level * 0.5
                stats['strength'] += level * 4
            elif skill_name == 'foraging':
                stats['strength'] += level * 1
                stats['foraging_fortune'] += level * 4
            elif skill_name == 'fishing':
                stats['health'] += level * 2
                stats['sea_creature_chance'] += level * 0.1
                stats['fishing_speed'] += level * 2
            elif skill_name == 'enchanting':
                stats['intelligence'] += level * 1
                stats['ability_damage'] += level * 0.5
            elif skill_name == 'alchemy':
                stats['intelligence'] += level * 1
            elif skill_name == 'taming':
                stats['pet_luck'] += level * 1
        
        stats['max_health'] = stats['health']
        stats['max_mana'] = 100 + stats['intelligence']
        
        return stats
    
    @staticmethod
    def apply_combat_effects(stats: Dict, item: Optional[Dict], enchants: Optional[List] = None) -> Dict[str, Any]:
        damage = 5 + stats.get('strength', 0)
        crit_chance = stats.get('crit_chance', 30) / 100
        crit_damage = 1 + (stats.get('crit_damage', 50) / 100)
        attack_speed_bonus = stats.get('attack_speed', 0)
        
        if item and item.get('stats', {}).get('damage'):
            damage += item['stats']['damage']
        
        return {
            'base_damage': damage,
            'crit_chance': crit_chance,
            'crit_damage_multiplier': crit_damage,
            'attack_speed': 100 + attack_speed_bonus,
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
        damage_reduction = defense / (defense + 100)
        damage_reduction = min(0.75, damage_reduction)
        true_defense_reduction = true_defense / (true_defense + 100)
        total_reduction = damage_reduction + (true_defense_reduction * (1 - damage_reduction))
        return 1 - total_reduction
    
    @staticmethod
    def calculate_drop_bonus(magic_find: int, pet_luck: int = 0) -> float:
        return 1 + ((magic_find + pet_luck) / 100)

async def get_enchantment(game_data, enchant_name: str) -> Optional[Dict]:
    return await game_data.get_enchantment(enchant_name.lower())

async def get_reforge_stats(game_data, reforge_name: str, item_type: str) -> Dict[str, int]:
    reforge = await game_data.get_reforge(reforge_name.lower())
    if not reforge:
        return {}
    
    if item_type.upper() in reforge.get('applies_to', []):
        return reforge.get('stat_bonuses', {})
    return {}
