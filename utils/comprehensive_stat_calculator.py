from typing import Dict, List, Optional, Any, Tuple
import json


class ComprehensiveStatCalculator:
    
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
    }
    
    SKILL_STAT_BONUSES = {
        'farming': {
            'health': 4,
            'farming_fortune': 4
        },
        'mining': {
            'defense': 1,
            'mining_fortune': 4,
            'mining_speed': 2
        },
        'combat': {
            'crit_chance': 0.5,
            'strength': 4
        },
        'foraging': {
            'strength': 1,
            'foraging_fortune': 4
        },
        'fishing': {
            'health': 2,
            'sea_creature_chance': 0.1,
            'fishing_speed': 2
        },
        'enchanting': {
            'intelligence': 1,
            'ability_damage': 0.5
        },
        'alchemy': {
            'intelligence': 1
        },
        'taming': {
            'pet_luck': 1
        }
    }
    
    FAIRY_SOUL_BONUSES = {
        'health': 3,
        'intelligence': 2
    }
    
    @classmethod
    async def calculate_full_stats(cls, db, user_id: int, context: str = 'general') -> Dict[str, float]:
        stats = cls.BASE_STATS.copy()
        
        await cls._apply_fairy_souls(db, user_id, stats)
        await cls._apply_skill_bonuses(db, user_id, stats)
        await cls._apply_armor_stats(db, user_id, stats)
        await cls._apply_weapon_stats(db, user_id, stats)
        await cls._apply_accessory_stats(db, user_id, stats)
        await cls._apply_pet_stats(db, user_id, stats)
        await cls._apply_reforge_stats(db, user_id, stats)
        await cls._apply_enchantment_stats(db, user_id, stats)
        
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
    async def _apply_armor_stats(cls, db, user_id: int, stats: Dict):
        inventory = await db.get_inventory(user_id)
        equipped_armor = {}
        
        for item_row in inventory:
            if item_row.get('equipped') == 1:
                item_id = item_row['item_id']
                
                if not db.conn:
                    continue
                    
                cursor = await db.conn.execute('''
                    SELECT * FROM game_items WHERE item_id = ?
                ''', (item_id,))
                item_data = await cursor.fetchone()
                
                if not item_data:
                    continue
                
                item_type = item_data['item_type']
                if item_type in ['HELMET', 'CHESTPLATE', 'LEGGINGS', 'BOOTS']:
                    equipped_armor[item_type] = item_data
                    
                    item_stats = json.loads(item_data['stats']) if item_data['stats'] else {}
                    for stat, value in item_stats.items():
                        if stat in stats:
                            stats[stat] += value
        
        if len(equipped_armor) == 4:
            await cls._apply_armor_set_bonus(equipped_armor, stats)
    
    @classmethod
    async def _apply_armor_set_bonus(cls, equipped_armor: Dict, stats: Dict):
        armor_names = [item['name'] for item in equipped_armor.values()]
        
        if all('Ender' in name for name in armor_names):
            stats['health'] += 100
            stats['defense'] += 100
        elif all('Diamond' in name for name in armor_names):
            stats['health'] += 50
            stats['defense'] += 50
        elif all('Wise' in name for name in armor_names):
            stats['intelligence'] += 200
        elif all('Strong' in name for name in armor_names):
            stats['strength'] += 100
        elif all('Superior' in name for name in armor_names):
            stats['health'] += 100
            stats['strength'] += 50
            stats['crit_damage'] += 50
            stats['intelligence'] += 50
            stats['defense'] += 50
    
    @classmethod
    async def _apply_weapon_stats(cls, db, user_id: int, stats: Dict):
        inventory = await db.get_inventory(user_id)
        
        for item_row in inventory:
            if item_row.get('equipped') == 1:
                item_id = item_row['item_id']
                
                if not db.conn:
                    continue
                    
                cursor = await db.conn.execute('''
                    SELECT * FROM game_items WHERE item_id = ?
                ''', (item_id,))
                item_data = await cursor.fetchone()
                
                if not item_data:
                    continue
                
                item_type = item_data['item_type']
                if item_type in ['SWORD', 'BOW']:
                    item_stats = json.loads(item_data['stats']) if item_data['stats'] else {}
                    for stat, value in item_stats.items():
                        if stat in stats:
                            stats[stat] += value
    
    @classmethod
    async def _apply_accessory_stats(cls, db, user_id: int, stats: Dict):
        inventory = await db.get_inventory(user_id)
        seen_accessories = set()
        
        for item_row in inventory:
            if item_row.get('equipped') == 1:
                item_id = item_row['item_id']
                
                if not db.conn:
                    continue
                    
                cursor = await db.conn.execute('''
                    SELECT * FROM game_items WHERE item_id = ?
                ''', (item_id,))
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
    async def _apply_pet_stats(cls, db, user_id: int, stats: Dict):
        active_pet = await db.get_active_pet(user_id)
        if not active_pet:
            return
        
        pet_type = active_pet['pet_type']
        rarity = active_pet['rarity']
        level = active_pet.get('level', 1)
        
        if not db.conn:
            return
            
        cursor = await db.conn.execute('''
            SELECT * FROM game_pets WHERE pet_type = ? AND rarity = ?
        ''', (pet_type, rarity))
        pet_config = await cursor.fetchone()
        
        if not pet_config:
            return
        
        base_stats = json.loads(pet_config['stats']) if pet_config['stats'] else {}
        
        for stat, base_value in base_stats.items():
            scaled_value = int(base_value * (level / 100))
            if stat in stats:
                stats[stat] += scaled_value
    
    @classmethod
    async def _apply_reforge_stats(cls, db, user_id: int, stats: Dict):
        inventory = await db.get_inventory(user_id)
        
        for item_row in inventory:
            if item_row.get('equipped') == 1 and item_row.get('reforge'):
                reforge_id = item_row['reforge']
                item_id = item_row['item_id']
                
                if not db.conn:
                    continue
                
                cursor = await db.conn.execute('''
                    SELECT * FROM game_items WHERE item_id = ?
                ''', (item_id,))
                item_data = await cursor.fetchone()
                
                if not item_data:
                    continue
                
                item_type = item_data['item_type']
                
                cursor = await db.conn.execute('''
                    SELECT * FROM reforges WHERE reforge_id = ?
                ''', (reforge_id,))
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
                    
                    cursor = await db.conn.execute('''
                        SELECT * FROM enchantments WHERE enchant_id = ?
                    ''', (enchant_id,))
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
