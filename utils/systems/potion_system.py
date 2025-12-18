
from typing import Dict, List

class PotionSystem:
    POTION_EFFECTS = {}
    
    @classmethod
    async def _load_constants(cls, db):
        cls.POTION_EFFECTS = await db.game_constants.get_all_potion_effects()
    
    @staticmethod
    async def use_potion(db, user_id: int, potion_id: str) -> Dict:
        if not PotionSystem.POTION_EFFECTS:
            await PotionSystem._load_constants(db)
        
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