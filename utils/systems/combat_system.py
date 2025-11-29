import random
import json
from typing import Dict, List, Tuple, Optional, Any
from ..comprehensive_stat_calculator import ComprehensiveStatCalculator


class CombatSystem:
    
    @classmethod
    async def calculate_player_damage(cls, db, user_id: int, target_defense: int = 0) -> Dict[str, float]:
        stats = await ComprehensiveStatCalculator.calculate_full_stats(db, user_id)
        
        weapon_damage = await cls._get_equipped_weapon_damage(db, user_id)
        
        is_crit = random.random() * 100 < ComprehensiveStatCalculator.get_crit_chance(stats)
        
        base_damage = ComprehensiveStatCalculator.calculate_damage(stats, weapon_damage, is_crit)
        
        defense_multiplier = 1.0 - (target_defense / (target_defense + 100))
        final_damage = base_damage * defense_multiplier
        
        return {
            'damage': final_damage,
            'is_crit': is_crit,
            'base_damage': base_damage,
            'weapon_damage': weapon_damage,
            'defense_reduction': 1.0 - defense_multiplier
        }
    
    @classmethod
    async def _get_equipped_weapon_damage(cls, db, user_id: int) -> int:
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
                    return item_stats.get('damage', 0)
        
        return 0
    
    @classmethod
    async def fight_mob(cls, db, user_id: int, mob_id: str, location: str = 'hub') -> Dict[str, Any]:
        if not db.conn:
            return {'success': False, 'error': 'Database not connected'}
        
        cursor = await db.conn.execute('''
            SELECT * FROM mob_locations WHERE mob_id = ? AND location_id = ?
        ''', (mob_id, location))
        mob_data = await cursor.fetchone()
        
        if not mob_data:
            return {'success': False, 'error': 'Mob not found'}
        
        mob_health = mob_data['health']
        mob_damage = mob_data['damage']
        mob_defense = 0
        
        player_stats = await ComprehensiveStatCalculator.calculate_full_stats(db, user_id)
        player_health = player_stats['health']
        
        turns = 0
        combat_log = []
        
        while mob_health > 0 and player_health > 0 and turns < 100:
            turns += 1
            
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
        
        return {
            'success': True,
            'victory': victory,
            'turns': turns,
            'rewards': rewards,
            'combat_log': combat_log,
            'final_player_health': max(0, player_health),
            'final_mob_health': max(0, mob_health)
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
        
        player_stats = await ComprehensiveStatCalculator.calculate_full_stats(db, user_id)
        drop_multiplier = ComprehensiveStatCalculator.calculate_drop_multiplier(player_stats)
        
        coins = int(base_coins * drop_multiplier * random.uniform(0.8, 1.2))
        xp = int(base_xp * random.uniform(0.9, 1.1))
        
        drops = await cls._roll_mob_drops(db, mob_data['mob_id'], drop_multiplier)
        
        return {
            'coins': coins,
            'xp': xp,
            'drops': drops
        }
    
    @classmethod
    async def _roll_mob_drops(cls, db, mob_id: str, drop_multiplier: float) -> List[Dict[str, Any]]:
        if not db.conn:
            return []
        
        cursor = await db.conn.execute('''
            SELECT * FROM loot_tables WHERE table_id = ? AND category = 'mob'
        ''', (mob_id,))
        loot_tables = await cursor.fetchall()
        
        drops = []
        
        for loot_table in loot_tables:
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
                    else:
                        item_id = item_entry
                        amount = 1
                    
                    drops.append({
                        'item_id': item_id,
                        'amount': amount,
                        'rarity': rarity
                    })
        
        return drops
    
    @classmethod
    async def calculate_slayer_damage(cls, db, user_id: int, boss_id: str, tier: int) -> Dict[str, Any]:
        if not db.conn:
            return {'success': False, 'error': 'Database not connected'}
        
        cursor = await db.conn.execute('''
            SELECT * FROM slayer_bosses WHERE boss_id = ?
        ''', (boss_id,))
        boss_data = await cursor.fetchone()
        
        if not boss_data:
            return {'success': False, 'error': 'Boss not found'}
        
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
        await db.update_skill(user_id, 'combat', xp=xp_amount)
    
    @classmethod
    async def calculate_ability_damage(cls, db, user_id: int, ability_multiplier: float) -> float:
        stats = await ComprehensiveStatCalculator.calculate_full_stats(db, user_id)
        weapon_damage = await cls._get_equipped_weapon_damage(db, user_id)
        
        base_damage = ComprehensiveStatCalculator.calculate_damage(stats, weapon_damage, False)
        ability_damage = base_damage * ability_multiplier * (1 + stats.get('ability_damage', 0) / 100)
        
        return ability_damage
