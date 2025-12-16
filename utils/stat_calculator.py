from typing import Dict, List, Optional, Any, Tuple
import json


class StatCalculator:
    
    BASE_STATS = {
        'health': 100.0,
        'defense': 0.0,
        'strength': 0.0,
        'crit_chance': 30.0,
        'crit_damage': 50.0,
        'intelligence': 0.0,
        'speed': 100.0,
        'attack_speed': 0.0,
        'sea_creature_chance': 0.0,
        'magic_find': 0.0,
        'pet_luck': 0.0,
        'ferocity': 0.0,
        'ability_damage': 0.0,
        'true_defense': 0.0,
        'mining_speed': 0.0,
        'mining_fortune': 0.0,
        'farming_fortune': 0.0,
        'foraging_fortune': 0.0,
        'fishing_speed': 0.0,
        'health_regen': 0.0,
    }
    
    SKILL_STAT_BONUSES = {
        'farming': {'health': 4, 'farming_fortune': 4},
        'mining': {'defense': 1, 'mining_fortune': 4, 'mining_speed': 2},
        'combat': {'crit_chance': 0.5, 'strength': 4},
        'foraging': {'strength': 1, 'foraging_fortune': 4},
        'fishing': {'health': 2, 'sea_creature_chance': 0.1, 'fishing_speed': 2},
        'enchanting': {'intelligence': 1, 'ability_damage': 0.5},
        'alchemy': {'intelligence': 1},
        'taming': {'pet_luck': 1}
    }
    
    FAIRY_SOUL_BONUSES = {'health': 3, 'intelligence': 2}
    
    @classmethod
    async def calculate_player_stats(cls, db, game_data, user_id: int) -> Dict[str, Any]:
        return await cls.calculate_full_stats(db, user_id)
    
    @classmethod
    async def calculate_full_stats(cls, db, user_id: int, context: str = 'general') -> Dict[str, float]:
        stats = cls.BASE_STATS.copy()
        
        await cls._apply_fairy_souls(db, user_id, stats)
        await cls._apply_skill_bonuses(db, user_id, stats)
        await cls._apply_mayor_perks(db, stats)
        await cls._apply_armor_stats(db, user_id, stats)
        await cls._apply_weapon_stats(db, user_id, stats)
        await cls._apply_tool_stats(db, user_id, stats, context)
        await cls._apply_accessory_stats(db, user_id, stats)
        await cls._apply_pet_stats(db, user_id, stats)
        await cls._apply_reforge_stats(db, user_id, stats)
        await cls._apply_enchantment_stats(db, user_id, stats)
        await cls._apply_potion_bonuses(db, user_id, stats)
        await cls._apply_talisman_bonuses(db, user_id, stats)
        await cls._apply_bestiary_bonuses(db, user_id, stats)
        
        achievement_crit_bonus = await db.achievements.calculate_achievement_crit_bonus(user_id)
        stats['crit_chance'] += achievement_crit_bonus * 100
        
        if context == 'dungeon':
            await cls._apply_dungeon_scaling(db, user_id, stats)
        
        stats['max_health'] = stats['health']
        stats['max_mana'] = 100 + stats['intelligence']
        
        return stats
    
    @classmethod
    async def _apply_fairy_souls(cls, db, user_id: int, stats: Dict):
        fairy_souls = await db.get_fairy_souls(user_id)
        for stat, bonus in cls.FAIRY_SOUL_BONUSES.items():
            if stat in stats:
                stats[stat] += fairy_souls * bonus
    
    @classmethod
    async def _apply_skill_bonuses(cls, db, user_id: int, stats: Dict):
        skills = await db.get_skills(user_id)
        for skill_row in skills:
            skill_name = skill_row['skill_name']
            level = skill_row['level']
            
            if skill_name in cls.SKILL_STAT_BONUSES:
                for stat, bonus_per_level in cls.SKILL_STAT_BONUSES[skill_name].items():
                    if stat in stats:
                        stats[stat] += level * bonus_per_level
    
    @classmethod
    async def _apply_mayor_perks(cls, db, stats: Dict):
        import time
        current_time = int(time.time())
        day_of_year = (current_time // 86400) % 365
        year = (current_time // 86400) // 365
        
        mayors = await db.get_all_mayors()
        if not mayors:
            return
        
        current_mayor_data = mayors[year % len(mayors)]
        bonuses = current_mayor_data.get('bonuses', {})
        
        stat_mapping = {
            'pet_luck': 'pet_luck',
            'magic_find': 'magic_find',
            'health': 'health',
            'defense': 'defense',
            'strength': 'strength',
            'intelligence': 'intelligence',
            'crit_chance': 'crit_chance',
            'crit_damage': 'crit_damage',
            'sea_creature_chance': 'sea_creature_chance',
            'fishing_speed': 'fishing_speed',
            'mining_fortune': 'mining_fortune',
            'farming_fortune': 'farming_fortune',
            'foraging_fortune': 'foraging_fortune'
        }
        
        for bonus_key, stat_key in stat_mapping.items():
            if bonus_key in bonuses and stat_key in stats:
                stats[stat_key] += bonuses[bonus_key]
    
    @classmethod
    async def _apply_armor_stats(cls, db, user_id: int, stats: Dict):
        equipped_items = await db.get_equipped_items(user_id)
        equipped_armor = {}
        
        for slot in ['helmet', 'chestplate', 'leggings', 'boots']:
            if equipped_items.get(slot):
                item_data = equipped_items[slot]
                item_id = item_data.get('item_id')
                item_type = item_data.get('item_type')
                
                if item_type in ['HELMET', 'CHESTPLATE', 'LEGGINGS', 'BOOTS']:
                    equipped_armor[item_type] = item_data
                    
                    armor_stats = await db.get_armor_stats(item_id)
                    if armor_stats:
                        for stat_key in ['defense', 'health', 'strength', 'crit_chance', 'crit_damage', 
                                        'intelligence', 'speed', 'magic_find', 'pet_luck', 'true_defense', 'health_regen']:
                            if stat_key in stats and armor_stats.get(stat_key):
                                stats[stat_key] += armor_stats[stat_key]
                    else:
                        item_stats = json.loads(item_data.get('stats', '{}')) if item_data.get('stats') else {}
                        for stat, value in item_stats.items():
                            if stat in stats:
                                stats[stat] += value
        
        if len(equipped_armor) == 4:
            await cls._apply_armor_set_bonus(equipped_armor, stats)
    
    @classmethod
    async def _apply_armor_set_bonus(cls, equipped_armor: Dict, stats: Dict):
        armor_names = [item['name'] for item in equipped_armor.values()]
        
        if all('Superior' in name for name in armor_names):
            stats['health'] += 100
            stats['strength'] += 50
            stats['crit_damage'] += 50
            stats['intelligence'] += 50
            stats['defense'] += 50
            stats['health_regen'] += 10
        elif all('Strong' in name for name in armor_names):
            stats['strength'] += 100
        elif all('Wise' in name for name in armor_names):
            stats['intelligence'] += 200
        elif all('Young' in name for name in armor_names):
            stats['speed'] += 100
            stats['health_regen'] += 5
        elif all('Goldor' in name for name in armor_names):
            stats['defense'] += 100
            stats['health_regen'] += 15
        elif all('Necron' in name for name in armor_names):
            stats['strength'] += 40
            stats['crit_damage'] += 30
            stats['intelligence'] += 20
            stats['health_regen'] += 8
    
    @classmethod
    async def _apply_weapon_stats(cls, db, user_id: int, stats: Dict):
        equipped_items = await db.get_equipped_items(user_id)
        
        sword_item = equipped_items.get('sword')
        if sword_item:
            item_id = sword_item.get('item_id')
            item_type = sword_item.get('item_type')
            
            if item_type == 'SWORD':
                weapon_stats = await db.get_weapon_stats(item_id)
                if weapon_stats:
                    for stat_key in ['damage', 'strength', 'crit_chance', 'crit_damage', 
                                    'attack_speed', 'ability_damage', 'ferocity', 'bonus_attack_speed']:
                        if stat_key in stats and weapon_stats.get(stat_key):
                            stats[stat_key] += weapon_stats[stat_key]
                else:
                    item_stats = json.loads(sword_item.get('stats', '{}')) if sword_item.get('stats') else {}
                    for stat, value in item_stats.items():
                        if stat in stats:
                            stats[stat] += value
        
        bow_item = equipped_items.get('bow')
        if bow_item:
            item_id = bow_item.get('item_id')
            item_type = bow_item.get('item_type')
            
            if item_type == 'BOW':
                weapon_stats = await db.get_weapon_stats(item_id)
                if weapon_stats:
                    for stat_key in ['damage', 'strength', 'crit_chance', 'crit_damage', 
                                    'attack_speed', 'ability_damage', 'ferocity', 'bonus_attack_speed']:
                        if stat_key in stats and weapon_stats.get(stat_key):
                            stats[stat_key] += weapon_stats[stat_key]
                else:
                    item_stats = json.loads(bow_item.get('stats', '{}')) if bow_item.get('stats') else {}
                    for stat, value in item_stats.items():
                        if stat in stats:
                            stats[stat] += value
    
    @classmethod
    async def _apply_accessory_stats(cls, db, user_id: int, stats: Dict):
        equipped_items = await db.get_equipped_items(user_id)
        inventory = await db.get_inventory(user_id)
        seen_accessories = set()
        
        for item_row in inventory:
            if item_row.get('equipped') == 1:
                item_id = item_row['item_id']
                
                if not db.conn:
                    continue
                    
                cursor = await db.conn.execute('SELECT * FROM game_items WHERE item_id = ?', (item_id,))
                item_data = await cursor.fetchone()
                
                if not item_data:
                    continue
                
                item_type = item_data['item_type']
                if item_type == 'ACCESSORY':
                    base_name = item_data['name'].split()[0]
                    
                    if base_name in seen_accessories:
                        continue
                    
                    seen_accessories.add(base_name)
                    
                    item_stats = json.loads(item_data['stats']) if item_data['stats'] else {}
                    for stat, value in item_stats.items():
                        if stat in stats:
                            stats[stat] += value
    
    @classmethod
    async def _apply_tool_stats(cls, db, user_id: int, stats: Dict, context: str = 'general'):
        equipped_items = await db.get_equipped_items(user_id)
        tool_slots = ['pickaxe', 'axe', 'hoe', 'fishing_rod']
        for slot in tool_slots:
            if equipped_items.get(slot):
                item_data = equipped_items[slot]
                item_id = item_data.get('item_id')
                item_type = item_data.get('item_type')
                
                if item_type in ['PICKAXE', 'AXE', 'HOE', 'SHOVEL', 'FISHING_ROD']:
                    tool_stats = await db.get_tool_stats(item_id)
                    if tool_stats:
                        for stat_key in ['mining_speed', 'mining_fortune', 'farming_fortune', 
                                        'foraging_fortune', 'fishing_speed', 'sea_creature_chance', 'breaking_power', 'damage']:
                            if stat_key in stats and tool_stats.get(stat_key):
                                stats[stat_key] += tool_stats[stat_key]
                    else:
                        item_stats = json.loads(item_data.get('stats', '{}')) if item_data.get('stats') else {}
                        for stat, value in item_stats.items():
                            if stat in stats:
                                stats[stat] += value
    
    @classmethod
    async def _apply_pet_stats(cls, db, user_id: int, stats: Dict):
        active_pet = await db.get_active_pet(user_id)
        if not active_pet:
            return
        
        pet_type = active_pet['pet_type'].lower()
        rarity = active_pet['rarity'].upper()
        level = active_pet.get('level', 1)
        
        pet_rarity_stats = await db.get_pet_stats_by_type_rarity(pet_type, rarity)
        
        if not pet_rarity_stats:
            return
        
        level_multiplier = 1 + (level / 100)
        
        for stat, base_value in pet_rarity_stats.items():
            scaled_value = int(base_value * level_multiplier)
            if stat in stats:
                stats[stat] += scaled_value
    
    @classmethod
    async def _apply_reforge_stats(cls, db, user_id: int, stats: Dict):
        inventory = await db.get_inventory(user_id)
        
        for item_row in inventory:
            if item_row.get('equipped') == 1:
                inventory_item_id = item_row.get('id')
                
                if inventory_item_id:
                    reforged_stats = await db.reforging.get_reforged_stats(inventory_item_id)
                    if reforged_stats:
                        for stat, value in reforged_stats.items():
                            if stat in stats:
                                stats[stat] += value
                
                if item_row.get('reforge'):
                    reforge_id = item_row['reforge']
                    item_id = item_row['item_id']
                    
                    if not db.conn:
                        continue
                    
                    cursor = await db.conn.execute('SELECT * FROM game_items WHERE item_id = ?', (item_id,))
                    item_data = await cursor.fetchone()
                    
                    if not item_data:
                        continue
                    
                    item_type = item_data['item_type']
                    
                    cursor = await db.conn.execute('SELECT * FROM reforges WHERE reforge_id = ?', (reforge_id,))
                    reforge_data = await cursor.fetchone()
                    
                    if not reforge_data:
                        continue
                    
                    applies_to = json.loads(reforge_data['applies_to'])
                    if item_type in applies_to:
                        reforge_stats = json.loads(reforge_data['stat_bonuses'])
                        for stat, value in reforge_stats.items():
                            if stat in stats:
                                stats[stat] += value
    
    @classmethod
    async def _apply_enchantment_stats(cls, db, user_id: int, stats: Dict):
        inventory = await db.get_inventory(user_id)
        
        for item_row in inventory:
            if item_row.get('equipped') == 1 and item_row.get('enchantments'):
                enchants_json = item_row.get('enchantments', '{}')
                enchants = json.loads(enchants_json) if enchants_json else {}
                
                for enchant_id, level in enchants.items():
                    if not db.conn:
                        continue
                    
                    cursor = await db.conn.execute('SELECT * FROM enchantments WHERE enchant_id = ?', (enchant_id,))
                    enchant_data = await cursor.fetchone()
                    
                    if not enchant_data:
                        continue
                    
                    stat_bonuses = json.loads(enchant_data.get('stat_bonuses', '{}'))
                    for stat, base_value in stat_bonuses.items():
                        if stat in stats:
                            stats[stat] += base_value * level
    
    @classmethod
    async def _apply_dungeon_scaling(cls, db, user_id: int, stats: Dict):
        player = await db.get_player(user_id)
        if not player:
            return
        
        dungeon_class = player.get('dungeon_class', 'none')
        class_level = player.get(f'{dungeon_class}_level', 0)
        
        class_multipliers = {
            'healer': {'health': 1.3, 'intelligence': 1.2},
            'mage': {'intelligence': 1.5, 'ability_damage': 1.3},
            'berserk': {'strength': 1.5, 'crit_damage': 1.2},
            'archer': {'crit_chance': 1.3, 'crit_damage': 1.2},
            'tank': {'defense': 1.5, 'health': 1.4}
        }
        
        if dungeon_class in class_multipliers:
            for stat, multiplier in class_multipliers[dungeon_class].items():
                if stat in stats:
                    base_bonus = (multiplier - 1.0) * (class_level / 50)
                    stats[stat] *= (1 + base_bonus)
    
    @classmethod
    async def _apply_potion_bonuses(cls, db, user_id: int, stats: Dict):
        from utils.systems.potion_system import PotionSystem
        potion_bonuses = await PotionSystem.get_potion_bonuses(db, user_id)
        for stat, bonus in potion_bonuses.items():
            if stat in stats:
                stats[stat] += bonus
    
    @classmethod
    async def _apply_talisman_bonuses(cls, db, user_id: int, stats: Dict):
        talismans = await db.talismans.get_all_talismans(user_id)
        
        for talisman_data in talismans:
            talisman_id = talisman_data['talisman_id']
            
            if not db.conn:
                continue
            
            cursor = await db.conn.execute(
                'SELECT * FROM game_talisman_stats WHERE talisman_id = ?',
                (talisman_id,)
            )
            talisman_stats = await cursor.fetchone()
            
            if talisman_stats:
                stat_fields = [
                    'health', 'defense', 'strength', 'crit_chance', 'crit_damage',
                    'intelligence', 'speed', 'attack_speed', 'sea_creature_chance',
                    'magic_find', 'pet_luck', 'ferocity', 'ability_damage', 'true_defense',
                    'mining_speed', 'mining_fortune', 'farming_fortune', 'foraging_fortune',
                    'fishing_speed', 'health_regen'
                ]
                
                for stat in stat_fields:
                    value = talisman_stats[stat]
                    if value and value != 0 and stat in stats:
                        stats[stat] += value
    
    @classmethod
    async def _apply_bestiary_bonuses(cls, db, user_id: int, stats: Dict):
        bestiary_bonuses = await db.bestiary.get_total_bestiary_stats(user_id)
        for stat, bonus in bestiary_bonuses.items():
            if stat in stats:
                stats[stat] += bonus
    
    @staticmethod
    def apply_combat_effects(stats: Dict, item: Optional[Dict], enchants: Optional[List] = None) -> Dict[str, Any]:
        weapon_damage = 0
        if item and item.get('stats', {}).get('damage'):
            weapon_damage = item['stats']['damage']
        
        damage = StatCalculator.calculate_damage(stats, weapon_damage, False)
        crit_damage = StatCalculator.calculate_damage(stats, weapon_damage, True)
        
        return {
            'base_damage': damage,
            'crit_chance': StatCalculator.get_crit_chance(stats),
            'crit_damage_multiplier': crit_damage / damage if damage > 0 else 1.0,
            'attack_speed': StatCalculator.calculate_attack_speed(stats),
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
        return StatCalculator.calculate_drop_multiplier(stats)

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

    
    @classmethod
    def calculate_damage(cls, stats: Dict, weapon_damage: int, is_crit: bool = False) -> float:
        base_damage = 5 + weapon_damage
        strength_bonus = stats.get('strength', 0)
        
        total_damage = (base_damage + strength_bonus / 5) * (1 + strength_bonus / 100)
        
        if is_crit:
            crit_damage_percent = stats.get('crit_damage', 50)
            total_damage *= (1 + crit_damage_percent / 100)
        
        ability_multiplier = 1 + (stats.get('ability_damage', 0) / 100)
        total_damage *= ability_multiplier
        
        return total_damage
    
    @classmethod
    def calculate_effective_health(cls, stats: Dict) -> float:
        health = stats.get('health', 100)
        defense = stats.get('defense', 0)
        
        damage_reduction = defense / (defense + 100)
        damage_reduction = min(0.75, damage_reduction)
        
        true_def = stats.get('true_defense', 0)
        true_def_reduction = true_def / (true_def + 100)
        
        total_reduction = damage_reduction + (true_def_reduction * (1 - damage_reduction))
        
        if total_reduction >= 0.99:
            total_reduction = 0.99
        
        effective_hp = health / (1 - total_reduction)
        return effective_hp
    
    @classmethod
    def calculate_drop_multiplier(cls, stats: Dict) -> float:
        magic_find = stats.get('magic_find', 0)
        pet_luck = stats.get('pet_luck', 0)
        return 1 + ((magic_find + pet_luck) / 100)
    
    @classmethod
    def calculate_mining_yield(cls, stats: Dict, base_yield: int) -> int:
        fortune = stats.get('mining_fortune', 0)
        yield_multiplier = 1 + (fortune / 100)
        return int(base_yield * yield_multiplier)
    
    @classmethod
    def calculate_farming_yield(cls, stats: Dict, base_yield: int) -> int:
        fortune = stats.get('farming_fortune', 0)
        yield_multiplier = 1 + (fortune / 100)
        return int(base_yield * yield_multiplier)
    
    @classmethod
    def calculate_foraging_yield(cls, stats: Dict, base_yield: int) -> int:
        fortune = stats.get('foraging_fortune', 0)
        yield_multiplier = 1 + (fortune / 100)
        return int(base_yield * yield_multiplier)
    
    @classmethod
    def calculate_mining_speed(cls, stats: Dict, base_speed: float) -> float:
        mining_speed = stats.get('mining_speed', 0)
        speed_multiplier = 1 + (mining_speed / 100)
        return base_speed * speed_multiplier
    
    @classmethod
    def calculate_fishing_speed(cls, stats: Dict, base_speed: float) -> float:
        fishing_speed = stats.get('fishing_speed', 0)
        speed_multiplier = 1 + (fishing_speed / 100)
        return base_speed * speed_multiplier
    
    @classmethod
    def calculate_sea_creature_chance(cls, stats: Dict) -> float:
        return stats.get('sea_creature_chance', 0)
    
    @classmethod
    def calculate_attack_speed(cls, stats: Dict) -> float:
        return 100 + stats.get('attack_speed', 0)
    
    @classmethod
    def get_crit_chance(cls, stats: Dict) -> float:
        return min(100, max(0, stats.get('crit_chance', 30)))
    
    @classmethod
    async def get_detailed_breakdown(cls, db, user_id: int) -> Dict[str, Any]:
        base_stats = cls.BASE_STATS.copy()
        
        breakdown = {
            'base': base_stats.copy(),
            'fairy_souls': {},
            'skills': {},
            'armor': {},
            'weapon': {},
            'accessories': {},
            'pet': {},
            'reforges': {},
            'enchantments': {},
            'total': {}
        }
        
        temp_stats = cls.BASE_STATS.copy()
        await cls._apply_fairy_souls(db, user_id, temp_stats)
        breakdown['fairy_souls'] = {k: temp_stats[k] - base_stats[k] for k in base_stats}
        
        temp_stats = cls.BASE_STATS.copy()
        await cls._apply_skill_bonuses(db, user_id, temp_stats)
        breakdown['skills'] = {k: temp_stats[k] - base_stats[k] for k in base_stats}
        
        breakdown['total'] = await cls.calculate_full_stats(db, user_id)
        
        return breakdown


async def get_enchantment(game_data, enchant_name: str) -> Optional[Dict]:
    return await game_data.get_enchantment(enchant_name.lower())


async def get_reforge_stats(game_data, reforge_name: str, item_type: str) -> Dict[str, int]:
    reforge = await game_data.get_reforge(reforge_name.lower())
    if not reforge:
        return {}
    
    if item_type.upper() in reforge.get('applies_to', []):
        return reforge.get('stat_bonuses', {})
    return {}

