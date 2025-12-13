import time
from typing import Dict, List, Optional

class PotionSystem:
    POTION_EFFECTS = {
        'speed_potion_1': {'stat': 'speed', 'amount': 10, 'duration': 180},
        'speed_potion_2': {'stat': 'speed', 'amount': 20, 'duration': 180},
        'speed_potion_3': {'stat': 'speed', 'amount': 30, 'duration': 180},
        'strength_potion_1': {'stat': 'strength', 'amount': 10, 'duration': 180},
        'strength_potion_2': {'stat': 'strength', 'amount': 20, 'duration': 180},
        'strength_potion_3': {'stat': 'strength', 'amount': 30, 'duration': 180},
        'regeneration_potion_1': {'stat': 'health_regen', 'amount': 5, 'duration': 180},
        'regeneration_potion_2': {'stat': 'health_regen', 'amount': 10, 'duration': 180},
        'regeneration_potion_3': {'stat': 'health_regen', 'amount': 15, 'duration': 180},
        'defense_potion_1': {'stat': 'defense', 'amount': 15, 'duration': 180},
        'defense_potion_2': {'stat': 'defense', 'amount': 30, 'duration': 180},
        'defense_potion_3': {'stat': 'defense', 'amount': 45, 'duration': 180},
        'critical_potion_1': {'stat': 'crit_chance', 'amount': 5, 'duration': 180},
        'critical_potion_2': {'stat': 'crit_chance', 'amount': 10, 'duration': 180},
        'critical_potion_3': {'stat': 'crit_chance', 'amount': 15, 'duration': 180},
        'magic_find_potion_1': {'stat': 'magic_find', 'amount': 10, 'duration': 180},
        'magic_find_potion_2': {'stat': 'magic_find', 'amount': 20, 'duration': 180},
        'magic_find_potion_3': {'stat': 'magic_find', 'amount': 30, 'duration': 180},
        'fishing_potion_1': {'stat': 'sea_creature_chance', 'amount': 5, 'duration': 180},
        'fishing_potion_2': {'stat': 'sea_creature_chance', 'amount': 10, 'duration': 180},
        'fishing_potion_3': {'stat': 'sea_creature_chance', 'amount': 15, 'duration': 180},
        'mining_potion_1': {'stat': 'mining_speed', 'amount': 10, 'duration': 180},
        'mining_potion_2': {'stat': 'mining_speed', 'amount': 20, 'duration': 180},
        'mining_potion_3': {'stat': 'mining_speed', 'amount': 30, 'duration': 180},
        'farming_potion_1': {'stat': 'farming_fortune', 'amount': 10, 'duration': 180},
        'farming_potion_2': {'stat': 'farming_fortune', 'amount': 20, 'duration': 180},
        'farming_potion_3': {'stat': 'farming_fortune', 'amount': 30, 'duration': 180},
        'combat_potion_1': {'stat': 'combat_xp_boost', 'amount': 10, 'duration': 180},
        'combat_potion_2': {'stat': 'combat_xp_boost', 'amount': 20, 'duration': 180},
        'combat_potion_3': {'stat': 'combat_xp_boost', 'amount': 30, 'duration': 180},
        'intelligence_potion_1': {'stat': 'intelligence', 'amount': 15, 'duration': 180},
        'intelligence_potion_2': {'stat': 'intelligence', 'amount': 30, 'duration': 180},
        'intelligence_potion_3': {'stat': 'intelligence', 'amount': 50, 'duration': 180},
        'true_defense_potion_1': {'stat': 'true_defense', 'amount': 10, 'duration': 180},
        'true_defense_potion_2': {'stat': 'true_defense', 'amount': 20, 'duration': 180},
        'true_defense_potion_3': {'stat': 'true_defense', 'amount': 30, 'duration': 180},
        'crit_damage_potion_1': {'stat': 'crit_damage', 'amount': 15, 'duration': 180},
        'crit_damage_potion_2': {'stat': 'crit_damage', 'amount': 30, 'duration': 180},
        'crit_damage_potion_3': {'stat': 'crit_damage', 'amount': 50, 'duration': 180},
        'ability_damage_potion_1': {'stat': 'ability_damage', 'amount': 10, 'duration': 180},
        'ability_damage_potion_2': {'stat': 'ability_damage', 'amount': 20, 'duration': 180},
        'ability_damage_potion_3': {'stat': 'ability_damage', 'amount': 30, 'duration': 180},
        'ferocity_potion_1': {'stat': 'ferocity', 'amount': 5, 'duration': 180},
        'ferocity_potion_2': {'stat': 'ferocity', 'amount': 10, 'duration': 180},
        'ferocity_potion_3': {'stat': 'ferocity', 'amount': 15, 'duration': 180},
        'pet_luck_potion_1': {'stat': 'pet_luck', 'amount': 5, 'duration': 180},
        'pet_luck_potion_2': {'stat': 'pet_luck', 'amount': 10, 'duration': 180},
        'pet_luck_potion_3': {'stat': 'pet_luck', 'amount': 15, 'duration': 180},
        'foraging_potion_1': {'stat': 'foraging_fortune', 'amount': 10, 'duration': 180},
        'foraging_potion_2': {'stat': 'foraging_fortune', 'amount': 20, 'duration': 180},
        'foraging_potion_3': {'stat': 'foraging_fortune', 'amount': 30, 'duration': 180},
        'attack_speed_potion_1': {'stat': 'attack_speed', 'amount': 5, 'duration': 180},
        'attack_speed_potion_2': {'stat': 'attack_speed', 'amount': 10, 'duration': 180},
        'attack_speed_potion_3': {'stat': 'attack_speed', 'amount': 15, 'duration': 180},
        'health_potion': {'type': 'instant_heal', 'amount': 100},
        'greater_health_potion': {'type': 'instant_heal', 'amount': 250},
        'super_health_potion': {'type': 'instant_heal', 'amount': 500},
        'ultimate_health_potion': {'type': 'instant_heal', 'amount': 1000},
        'god_potion': {'type': 'god', 'duration': 1200, 'effects': {
            'strength': 50,
            'defense': 50,
            'speed': 50,
            'crit_chance': 15,
            'crit_damage': 50,
            'intelligence': 50,
            'magic_find': 25,
            'pet_luck': 15,
            'ferocity': 15,
            'ability_damage': 30,
            'true_defense': 25,
            'mining_speed': 50,
            'mining_fortune': 50,
            'farming_fortune': 50,
            'foraging_fortune': 50,
            'fishing_speed': 50,
            'sea_creature_chance': 15,
            'attack_speed': 15,
            'health_regen': 25
        }}
    }
    
    @staticmethod
    async def use_potion(db, user_id: int, potion_id: str) -> Dict:
        if potion_id not in PotionSystem.POTION_EFFECTS:
            return {'success': False, 'message': 'Invalid potion!'}
        
        item_count = await db.get_item_count(user_id, potion_id)
        if item_count < 1:
            return {'success': False, 'message': "You don't have this potion!"}
        
        potion_effect = PotionSystem.POTION_EFFECTS[potion_id]
        
        if potion_effect.get('type') == 'instant_heal':
            await db.remove_item_from_inventory(user_id, potion_id, 1)
            return {
                'success': True,
                'type': 'instant_heal',
                'amount': potion_effect['amount']
            }
        elif potion_effect.get('type') == 'god':
            for stat, amount in potion_effect['effects'].items():
                await db.potions.add_active_potion(user_id, f"god_potion_{stat}", 1, potion_effect['duration'])
            
            await db.remove_item_from_inventory(user_id, potion_id, 1)
            
            return {
                'success': True,
                'type': 'god',
                'duration': potion_effect['duration']
            }
        else:
            await db.potions.add_active_potion(user_id, potion_id, 1, potion_effect['duration'])
            
            await db.remove_item_from_inventory(user_id, potion_id, 1)
            
            return {
                'success': True,
                'stat': potion_effect['stat'],
                'amount': potion_effect['amount'],
                'duration': potion_effect['duration']
            }
    
    @staticmethod
    async def use_health_potion_in_combat(db, user_id: int, potion_id: str, current_health: int, max_health: int) -> Dict:
        if potion_id not in PotionSystem.POTION_EFFECTS:
            return {'success': False, 'message': 'Invalid potion!'}
        
        potion_effect = PotionSystem.POTION_EFFECTS[potion_id]
        if potion_effect.get('type') != 'instant_heal':
            return {'success': False, 'message': 'This is not a health potion!'}
        
        item_count = await db.get_item_count(user_id, potion_id)
        if item_count < 1:
            return {'success': False, 'message': "You don't have this potion!"}
        
        heal_amount = potion_effect['amount']
        new_health = min(current_health + heal_amount, max_health)
        actual_heal = new_health - current_health
        
        await db.remove_item_from_inventory(user_id, potion_id, 1)
        
        return {
            'success': True,
            'new_health': new_health,
            'heal_amount': actual_heal
        }
    
    @staticmethod
    @staticmethod
    async def get_active_potions(db, user_id: int) -> List[Dict]:
        await db.potions.remove_expired_potions(user_id)
        
        return await db.potions.get_active_potions(user_id)
    
    @staticmethod
    async def get_potion_bonuses(db, user_id: int) -> Dict[str, int]:
        active_potions = await PotionSystem.get_active_potions(db, user_id)
        bonuses = {}
        
        for potion_data in active_potions:
            potion_id = potion_data['potion_id']
            
            if potion_id.startswith('god_potion_'):
                stat = potion_id.replace('god_potion_', '')
                god_potion_effect = PotionSystem.POTION_EFFECTS['god_potion']
                if stat in god_potion_effect['effects']:
                    amount = god_potion_effect['effects'][stat]
                    bonuses[stat] = bonuses.get(stat, 0) + amount
            elif potion_id in PotionSystem.POTION_EFFECTS:
                effect = PotionSystem.POTION_EFFECTS[potion_id]
                if 'stat' in effect:
                    stat = effect['stat']
                    amount = effect['amount']
                    bonuses[stat] = bonuses.get(stat, 0) + amount
        
        return bonuses