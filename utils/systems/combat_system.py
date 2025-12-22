import random
import json
from typing import Dict, List, Any, Optional
from ..stat_calculator import StatCalculator
from .weapon_abilities import WeaponAbilities

class CombatSystem:
    
    @classmethod
    async def apply_health_regeneration(cls, db, user_id: int, current_health: int, max_health: int) -> int:
        stats = await StatCalculator.calculate_full_stats(db, user_id)
        health_regen = stats.get('health_regen', 0)
        
        if health_regen > 0:
            regen_amount = int(max_health * (health_regen / 100))
            new_health = min(current_health + regen_amount, max_health)
            return new_health
        
        return current_health
    
    @classmethod
    async def _get_equipped_armor_defense(cls, db, user_id: int) -> int:
        """Get total defense from all equipped armor pieces"""
        if not db.conn:
            return 0
        
        cursor = await db.conn.execute('''
            SELECT * FROM player_equipment WHERE user_id = ?
        ''', (user_id,))
        row = await cursor.fetchone()
        
        if not row:
            return 0
        
        equipment = dict(row)
        total_defense = 0
        slots = ['helmet_slot', 'chestplate_slot', 'leggings_slot', 'boots_slot']
        
        for slot in slots:
            item_id = equipment.get(slot)
            if item_id:
                armor_stats = await db.get_armor_stats(item_id)
                if armor_stats:
                    total_defense += armor_stats.get('defense', 0)
        
        return total_defense
    
    @classmethod
    async def _get_combat_drop_yield_multiplier(cls, db, user_id: int) -> float:
        if not db.conn:
            return 1.0
        
        multiplier = 1.0
        
        cursor = await db.conn.execute('''
            SELECT * FROM player_equipment WHERE user_id = ?
        ''', (user_id,))
        row = await cursor.fetchone()
        
        if not row:
            return multiplier
            
        equipment = dict(row)

        sword_slot_id = equipment.get('sword_slot')
        if sword_slot_id:
            cursor = await db.conn.execute('''
                SELECT i.item_id FROM inventory_items i
                WHERE i.user_id = ? AND i.slot = ?
            ''', (user_id, sword_slot_id))
            inv_row = await cursor.fetchone()
            if inv_row:
                item_id = inv_row['item_id']
                cursor = await db.conn.execute('''
                    SELECT combat_drop_yield_multiplier FROM weapon_stats WHERE item_id = ?
                ''', (item_id,))
                weapon_row = await cursor.fetchone()
                if weapon_row:
                    weapon_stats = dict(weapon_row)
                    if weapon_stats.get('combat_drop_yield_multiplier'):
                        multiplier *= weapon_stats['combat_drop_yield_multiplier']

        bow_slot_id = equipment.get('bow_slot')
        if bow_slot_id:
            cursor = await db.conn.execute('''
                SELECT i.item_id FROM inventory_items i
                WHERE i.user_id = ? AND i.slot = ?
            ''', (user_id, bow_slot_id))
            inv_row = await cursor.fetchone()
            if inv_row:
                item_id = inv_row['item_id']
                cursor = await db.conn.execute('''
                    SELECT combat_drop_yield_multiplier FROM weapon_stats WHERE item_id = ?
                ''', (item_id,))
                weapon_row = await cursor.fetchone()
                if weapon_row:
                    weapon_stats = dict(weapon_row)
                    if weapon_stats.get('combat_drop_yield_multiplier'):
                        multiplier = max(multiplier, weapon_stats['combat_drop_yield_multiplier'])

        armor_slots = ['helmet_slot', 'chestplate_slot', 'leggings_slot', 'boots_slot']
        armor_count = 0
        armor_multiplier_sum = 0.0
        
        for slot in armor_slots:
            armor_slot_id = equipment.get(slot)
            if armor_slot_id:
                cursor = await db.conn.execute('''
                    SELECT i.item_id FROM inventory_items i
                    WHERE i.user_id = ? AND i.slot = ?
                ''', (user_id, armor_slot_id))
                inv_row = await cursor.fetchone()
                if inv_row:
                    item_id = inv_row['item_id']
                    cursor = await db.conn.execute('''
                        SELECT combat_drop_yield_multiplier FROM armor_stats WHERE item_id = ?
                    ''', (item_id,))
                    armor_row = await cursor.fetchone()
                    if armor_row:
                        armor_stats = dict(armor_row)
                        if armor_stats.get('combat_drop_yield_multiplier'):
                            armor_count += 1
                            armor_multiplier_sum += armor_stats['combat_drop_yield_multiplier']
        
        if armor_count > 0:
            avg_armor_multiplier = armor_multiplier_sum / armor_count
            multiplier *= avg_armor_multiplier
        
        return multiplier
    
    @classmethod
    async def roll_combat_loot(cls, game_data, db, user_id: int, loot_table: Dict[str, Any], magic_find: float = 0, fortune: int = 0) -> List[tuple[str, int]]:
        from ..compat import roll_loot as compat_roll_loot
        
        drops = await compat_roll_loot(game_data, loot_table, magic_find, fortune)
        
        combat_drop_yield = await cls._get_combat_drop_yield_multiplier(db, user_id)
        
        drops = [
            (
                item_id,
                max(
                    1,
                    int(amount * (combat_drop_yield if "pet" not in item_id.lower() and "enchanted" not in item_id.lower()
                                else combat_drop_yield / 2))
                )
            )
            for item_id, amount in drops
        ]

        
        return drops
    
    @classmethod
    async def calculate_player_damage(cls, db, user_id: int, target_defense: int = 0) -> Dict[str, Any]:
        stats = await StatCalculator.calculate_full_stats(db, user_id)
        
        weapon_damage, weapon_tier = await cls._get_equipped_weapon_damage_and_tier(db, user_id)
        
        is_crit = random.random() * 100 < StatCalculator.get_crit_chance(stats)
        
        base_damage = StatCalculator.calculate_damage(stats, weapon_damage, is_crit, weapon_tier)
        
        skills = await db.get_skills(user_id)
        combat_skill = next((s for s in skills if s['skill_name'] == 'combat'), None)
        combat_level = combat_skill['level'] if combat_skill else 0
        
        skill_multiplier = 1.0 + (combat_level * 0.05)
        base_damage *= skill_multiplier
        
        defense_multiplier = 1.0 - (target_defense / (target_defense + 100))
        final_damage = base_damage * defense_multiplier
        
        return {
            'damage': final_damage,
            'is_crit': is_crit,
            'base_damage': base_damage,
            'weapon_damage': weapon_damage,
            'defense_reduction': 1.0 - defense_multiplier,
            'combat_level': combat_level,
            'skill_multiplier': skill_multiplier,
            'weapon_tier': weapon_tier
        }
    
    @classmethod
    async def _get_equipped_weapon_damage(cls, db, user_id: int) -> int:
        damage, _ = await cls._get_equipped_weapon_damage_and_tier(db, user_id)
        return damage
    
    @classmethod
    async def _get_equipped_weapon_damage_and_tier(cls, db, user_id: int) -> tuple[int, str]:
        equipped_items = await db.get_equipped_items(user_id)
        total_damage = 0
        weapon_tier = 'COMMON'
        
        sword_item = equipped_items.get('sword')
        if sword_item and 'item_id' in sword_item:
            item_id = sword_item['item_id']
            item_type = sword_item.get('item_type')
            
            if item_type == 'SWORD':
                weapon_stats = await db.get_weapon_stats(item_id)
                if weapon_stats:
                    total_damage += weapon_stats.get('damage', 0)
                else:
                    item_stats = json.loads(sword_item.get('stats', '{}')) if sword_item.get('stats') else {}
                    total_damage += item_stats.get('damage', 0)
                
                rarity = sword_item.get('rarity', 'COMMON')
                if rarity:
                    weapon_tier = rarity
        
        bow_item = equipped_items.get('bow')
        if bow_item and 'item_id' in bow_item:
            item_id = bow_item['item_id']
            item_type = bow_item.get('item_type')
            
            if item_type == 'BOW':
                weapon_stats = await db.get_weapon_stats(item_id)
                if weapon_stats:
                    total_damage += weapon_stats.get('damage', 0)
                else:
                    item_stats = json.loads(bow_item.get('stats', '{}')) if bow_item.get('stats') else {}
                    total_damage += item_stats.get('damage', 0)
                
                rarity = bow_item.get('rarity', 'COMMON')
                if rarity:
                    weapon_tier = rarity

        if total_damage == 0:
            axe_item = equipped_items.get('axe')
            if axe_item and 'item_id' in axe_item:
                item_id = axe_item['item_id']
                weapon_stats = await db.get_weapon_stats(item_id)
                if weapon_stats:
                    total_damage += weapon_stats.get('damage', 0)
                
                rarity = axe_item.get('rarity', 'COMMON')
                if rarity:
                    weapon_tier = rarity
        
        return total_damage, weapon_tier
    
    @classmethod
    async def get_equipped_weapon_info(cls, db, user_id: int) -> Optional[Dict[str, Any]]:
        equipped_items = await db.get_equipped_items(user_id)
        
        for slot in ['sword', 'bow', 'axe']:
            item = equipped_items.get(slot)
            if item and 'item_id' in item:
                return {
                    'item_id': item['item_id'],
                    'name': item.get('name', ''),
                    'rarity': item.get('rarity', 'COMMON'),
                    'type': item.get('item_type', '')
                }
        
        return None
    
    @classmethod
    async def get_mob_level_scaling(cls, db, level: int) -> Dict[str, float]:
        if not db.conn:
            return {
                'health_multiplier': 1.0,
                'damage_multiplier': 1.0,
                'defense_multiplier': 1.0,
                'coins_multiplier': 1.0,
                'xp_multiplier': 1.0
            }
        
        cursor = await db.conn.execute('''
            SELECT * FROM mob_level_scaling WHERE level <= ? ORDER BY level DESC LIMIT 1
        ''', (level,))
        scaling_row = await cursor.fetchone()
        
        if scaling_row:
            return dict(scaling_row)
        
        return {
            'health_multiplier': 1.0 + (level - 1) * 0.1,
            'damage_multiplier': 1.0 + (level - 1) * 0.08,
            'defense_multiplier': 1.0 + (level - 1) * 0.08,
            'coins_multiplier': 1.0 + (level - 1) * 0.1,
            'xp_multiplier': 1.0 + (level - 1) * 0.1
        }
    
    @classmethod
    async def fight_mob(cls, db, user_id: int, mob_id: str, location: str = 'hub') -> Dict[str, Any]:
        if not db.conn:
            return {'success': False, 'error': 'Database not connected'}
        
        cursor = await db.conn.execute('''
            SELECT * FROM mob_locations WHERE mob_id = ? AND location_id = ?
        ''', (mob_id, location))
        mob_row = await cursor.fetchone()
        
        if not mob_row:
            return {'success': False, 'error': 'Mob not found'}
        
        mob_data = dict(mob_row)
        mob_level = mob_data.get('level', 1)
        scaling = await cls.get_mob_level_scaling(db, mob_level)
        
        mob_health = int(mob_data['health'] * scaling['health_multiplier'])
        mob_damage = int(mob_data['damage'] * scaling['damage_multiplier'])
        mob_defense = int(mob_data.get('defense', 0) * scaling['defense_multiplier'])
        
        if mob_defense == 0:
            mob_stats = await db.get_mob_stats(mob_id)
            if mob_stats:
                mob_defense = mob_stats.get('defense', 0)
        
        player_stats = await StatCalculator.calculate_full_stats(db, user_id)

        armor_defense = await cls._get_equipped_armor_defense(db, user_id)
        player_stats['defense'] = player_stats.get('defense', 0) + armor_defense
        
        player_health = player_stats['health']
        
        turns = 0
        combat_log = []
        
        while mob_health > 0 and player_health > 0 and turns < 100:
            turns += 1
            
            player_health = await cls.apply_health_regeneration(db, user_id, int(player_health), int(player_stats['max_health']))
            
            damage_result = await cls.calculate_player_damage(db, user_id, mob_defense)
            damage_dealt = damage_result['damage']
            mob_health -= damage_dealt
            
            combat_log.append({
                'turn': turns,
                'actor': 'player',
                'damage': damage_dealt,
                'is_crit': damage_result['is_crit']
            })
            
            if mob_health <= 0:
                break
            
            player_damage_taken = cls._calculate_mob_damage(mob_damage, player_stats['defense'])
            player_health -= player_damage_taken
            
            combat_log.append({
                'turn': turns,
                'actor': 'mob',
                'damage': player_damage_taken
            })
        
        victory = mob_health <= 0
        
        rewards = {}
        if victory:
            rewards = await cls._generate_mob_rewards(db, user_id, mob_data)
            
            bestiary_result = await db.bestiary.add_bestiary_kill(user_id, mob_id)
            rewards['bestiary'] = bestiary_result
        else:
            await db.bestiary.add_bestiary_death(user_id, mob_id)
        
        return {
            'success': True,
            'victory': victory,
            'turns': turns,
            'rewards': rewards,
            'combat_log': combat_log,
            'final_player_health': max(0, player_health),
            'final_mob_health': max(0, mob_health),
            'armor_defense_bonus': armor_defense
        }
    
    @classmethod
    def _calculate_mob_damage(cls, mob_base_damage: int, player_defense: float) -> float:
        defense_reduction = player_defense / (player_defense + 100)
        defense_reduction = min(0.75, defense_reduction)
        
        damage = mob_base_damage * (1 - defense_reduction)
        return max(1, damage)
    
    @classmethod
    async def _generate_mob_rewards(cls, db, user_id: int, mob_data: Dict) -> Dict[str, Any]:
        base_coins = mob_data['coins']
        base_xp = mob_data['xp']
        mob_level = mob_data.get('level', 1)
        
        scaling = await cls.get_mob_level_scaling(db, mob_level)
        
        player_stats = await StatCalculator.calculate_full_stats(db, user_id)
        drop_multiplier = StatCalculator.calculate_drop_multiplier(player_stats)
        
        museum_bonus = await db.museum.calculate_museum_drop_bonus(user_id)
        achievement_luck = await db.achievements.calculate_achievement_luck_bonus(user_id)
        
        drop_multiplier *= museum_bonus * achievement_luck
        
        combat_drop_yield = await cls._get_combat_drop_yield_multiplier(db, user_id)
        drop_multiplier *= combat_drop_yield
        
        skills = await db.get_skills(user_id)
        combat_skill = next((s for s in skills if s['skill_name'] == 'combat'), None)
        combat_level = combat_skill['level'] if combat_skill else 0
        
        coins = int(base_coins * scaling['coins_multiplier'] * drop_multiplier * random.uniform(0.8, 1.2))
        xp = int(base_xp * scaling['xp_multiplier'] * random.uniform(0.9, 1.1))
        
        drops = await cls._roll_mob_drops(db, mob_data['mob_id'], drop_multiplier, combat_level)
        
        drop_xp = await cls._calculate_drop_xp(db, drops)
        xp += drop_xp
        coins += int(drop_xp * 0.8)
        
        return {
            'coins': coins,
            'xp': xp,
            'drops': drops,
            'combat_level': combat_level,
            'mob_level': mob_level,
            'combat_drop_yield_multiplier': combat_drop_yield
        }
    
    @classmethod
    async def _roll_mob_drops(cls, db, mob_id: str, drop_multiplier: float, combat_level: int = 0) -> List[Dict[str, Any]]:
        if not db.conn:
            return []
        
        cursor = await db.conn.execute('''
            SELECT * FROM loot_tables WHERE table_id = ? AND category = 'mob'
        ''', (mob_id,))
        loot_table_rows = await cursor.fetchall()
        
        drops = []
        
        skill_drop_multiplier = 1.0 + (combat_level * 0.05)
        
        for row in loot_table_rows:
            loot_table = dict(row)
            rarity = loot_table['rarity']
            loot_data = json.loads(loot_table['loot_data']) if loot_table['loot_data'] else []
            
            rarity_chance = {
                'common': 0.7,
                'uncommon': 0.2,
                'rare': 0.08,
                'epic': 0.015,
                'legendary': 0.004,
                'mythic': 0.001
            }
            
            base_chance = rarity_chance.get(rarity.lower(), 0.5)
            actual_chance = base_chance * drop_multiplier
            
            if random.random() < actual_chance:
                for item_entry in loot_data:
                    if isinstance(item_entry, dict):
                        item_id = item_entry.get('item_id')
                        min_amt = item_entry.get('min', 1)
                        max_amt = item_entry.get('max', 1)
                        amount = random.randint(min_amt, max_amt)
                        amount = int(amount * skill_drop_multiplier)
                    else:
                        item_id = item_entry
                        amount = max(1, int(1 * skill_drop_multiplier))
                    
                    drops.append({
                        'item_id': item_id,
                        'amount': amount,
                        'rarity': rarity
                    })
        
        return drops
    
    @classmethod
    async def _calculate_drop_xp(cls, db, drops: List[Dict[str, Any]]) -> int:
        if not db.conn:
            return 0
        
        total_xp = 0
        
        for drop in drops:
            item_id = drop.get('item_id')
            amount = drop.get('amount', 1)
            
            if item_id:
                cursor = await db.conn.execute('''
                    SELECT base_xp FROM combat_drop_xp WHERE item_id = ?
                ''', (item_id,))
                row = await cursor.fetchone()
                
                if row:
                    base_xp = row['base_xp']
                    total_xp += base_xp * amount
        
        return total_xp
    
    @classmethod
    async def calculate_slayer_damage(cls, db, user_id: int, boss_id: str, tier: int) -> Dict[str, Any]:
        if not db.conn:
            return {'success': False, 'error': 'Database not connected'}
        
        cursor = await db.conn.execute('''
            SELECT * FROM slayer_bosses WHERE boss_id = ?
        ''', (boss_id,))
        boss_row = await cursor.fetchone()
        
        if not boss_row:
            return {'success': False, 'error': 'Boss not found'}
        
        boss_data = dict(boss_row)
        tier_data = json.loads(boss_data['tier_data'])
        tier_key = f'tier_{tier}'
        
        if tier_key not in tier_data:
            return {'success': False, 'error': 'Invalid tier'}
        
        tier_info = tier_data[tier_key]
        boss_health = tier_info['xp'][0] * 100
        boss_damage = tier * 50
        
        return await cls.fight_mob(db, user_id, boss_id, 'slayer')
    
    @classmethod
    async def apply_combat_xp(cls, db, user_id: int, xp_amount: int):
        achievement_bonus = await db.achievements.calculate_achievement_skill_bonus(user_id, 'combat')
        xp_amount = int(xp_amount * achievement_bonus)
        await db.update_skill(user_id, 'combat', xp=xp_amount)
    
    @classmethod
    async def calculate_ability_damage(cls, db, user_id: int, ability_multiplier: float = 3.0) -> float:
        stats = await StatCalculator.calculate_full_stats(db, user_id)
        weapon_damage = await cls._get_equipped_weapon_damage(db, user_id)
        
        weapon_info = await cls.get_equipped_weapon_info(db, user_id)
        if weapon_info and await WeaponAbilities.has_ability(db, weapon_info['item_id']):
            ability_damage = await WeaponAbilities.calculate_ability_damage(
                db, weapon_info['item_id'], stats, weapon_damage
            )
            return ability_damage
        
        base_damage = StatCalculator.calculate_damage(stats, weapon_damage, False)
        ability_damage = base_damage * ability_multiplier * (1 + stats.get('ability_damage', 0) / 100)
        
        return ability_damage