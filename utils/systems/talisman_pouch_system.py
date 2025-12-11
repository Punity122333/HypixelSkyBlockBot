from typing import Dict, List

class TalismanPouchSystem:
    MAX_TALISMANS = 24
    
    @staticmethod
    async def add_talisman_to_pouch(db, user_id: int, talisman_id: str) -> Dict:
        current_count = await db.talismans.get_talisman_count(user_id)
        
        if current_count >= TalismanPouchSystem.MAX_TALISMANS:
            return {'success': False, 'message': 'Talisman pouch is full!'}
        
        item_count = await db.get_item_count(user_id, talisman_id)
        if item_count < 1:
            return {'success': False, 'message': "You don't have this talisman!"}
        
        item = await db.game_data.get_game_item(talisman_id)
        if not item:
            return {'success': False, 'message': 'Invalid item!'}
        
        # Handle both dict and object formats
        item_type = item.get('item_type') or item.get('type') if isinstance(item, dict) else getattr(item, 'type', None)
        item_name = item.get('name') if isinstance(item, dict) else getattr(item, 'name', talisman_id)
        
        if item_type != 'TALISMAN':
            return {'success': False, 'message': 'This is not a talisman!'}
        
        existing = await db.talismans.get_talisman_by_id(user_id, talisman_id)
        
        if existing:
            return {'success': False, 'message': 'You already have this talisman in your pouch!'}
        
        next_slot = current_count
        
        await db.talismans.add_talisman(user_id, talisman_id, next_slot)
        
        await db.remove_item_from_inventory(user_id, talisman_id, 1)
        
        return {'success': True, 'message': f'Added {item_name} to talisman pouch!'}
    
    @staticmethod
    async def remove_talisman_from_pouch(db, user_id: int, slot: int) -> Dict:
        talisman = await db.talismans.get_talisman_by_slot(user_id, slot)
        
        if not talisman:
            return {'success': False, 'message': 'No talisman in this slot!'}
        
        talisman_id = talisman['talisman_id']
        
        await db.talismans.remove_talisman(user_id, slot)
        
        await db.talismans.shift_talismans_down(user_id, slot)
        
        await db.add_item_to_inventory(user_id, talisman_id, 1)
        
        return {'success': True, 'talisman_id': talisman_id}
    
    @staticmethod
    async def get_talisman_pouch(db, user_id: int) -> List[Dict]:
        return await db.talismans.get_all_talismans(user_id)
    
    @staticmethod
    async def get_talisman_bonuses(db, user_id: int) -> Dict[str, int]:
        talismans = await TalismanPouchSystem.get_talisman_pouch(db, user_id)
        bonuses = {}
        
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
                    'fishing_speed'
                ]
                
                for stat in stat_fields:
                    value = talisman_stats[stat]
                    if value and value != 0:
                        bonuses[stat] = bonuses.get(stat, 0) + value
        
        return bonuses

