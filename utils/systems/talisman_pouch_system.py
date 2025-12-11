from typing import Dict, List

class TalismanPouchSystem:
    MAX_TALISMANS = 24
    
    @staticmethod
    async def add_talisman_to_pouch(db, user_id: int, talisman_id: str) -> Dict:
        count = await db.fetchone(
            'SELECT COUNT(*) as count FROM player_talisman_pouch WHERE user_id = ?',
            (user_id,)
        )
        current_count = count['count'] if count else 0
        
        if current_count >= TalismanPouchSystem.MAX_TALISMANS:
            return {'success': False, 'message': 'Talisman pouch is full!'}
        
        item_count = await db.get_item_count(user_id, talisman_id)
        if item_count < 1:
            return {'success': False, 'message': "You don't have this talisman!"}
        
        item = await db.game_data.get_item(talisman_id)
        if not item or item.type != 'TALISMAN':
            return {'success': False, 'message': 'This is not a talisman!'}
        
        existing = await db.fetchone(
            'SELECT * FROM player_talisman_pouch WHERE user_id = ? AND talisman_id = ?',
            (user_id, talisman_id)
        )
        
        if existing:
            return {'success': False, 'message': 'You already have this talisman in your pouch!'}
        
        next_slot = current_count
        
        await db.execute(
            '''INSERT INTO player_talisman_pouch (user_id, talisman_id, slot, equipped)
               VALUES (?, ?, ?, 1)''',
            (user_id, talisman_id, next_slot)
        )
        await db.commit()
        
        await db.remove_item_from_inventory(user_id, talisman_id, 1)
        
        return {'success': True, 'message': f'Added {item.name} to talisman pouch!'}
    
    @staticmethod
    async def remove_talisman_from_pouch(db, user_id: int, slot: int) -> Dict:
        talisman = await db.fetchone(
            'SELECT * FROM player_talisman_pouch WHERE user_id = ? AND slot = ?',
            (user_id, slot)
        )
        
        if not talisman:
            return {'success': False, 'message': 'No talisman in this slot!'}
        
        talisman_id = talisman['talisman_id']
        
        await db.execute(
            'DELETE FROM player_talisman_pouch WHERE user_id = ? AND slot = ?',
            (user_id, slot)
        )
        await db.commit()
        
        await db.execute(
            '''UPDATE player_talisman_pouch 
               SET slot = slot - 1 
               WHERE user_id = ? AND slot > ?''',
            (user_id, slot)
        )
        await db.commit()
        
        await db.add_item_to_inventory(user_id, talisman_id, 1)
        
        return {'success': True, 'talisman_id': talisman_id}
    
    @staticmethod
    async def get_talisman_pouch(db, user_id: int) -> List[Dict]:
        rows = await db.fetchall(
            'SELECT * FROM player_talisman_pouch WHERE user_id = ? AND equipped = 1 ORDER BY slot',
            (user_id,)
        )
        
        return [dict(row) for row in rows]
    
    @staticmethod
    async def get_talisman_bonuses(db, user_id: int) -> Dict[str, int]:
        talismans = await TalismanPouchSystem.get_talisman_pouch(db, user_id)
        bonuses = {}
        
        for talisman_data in talismans:
            talisman_id = talisman_data['talisman_id']
            item = await db.game_data.get_item(talisman_id)
            
            if item and item.stats:
                for stat, value in item.stats.items():
                    bonuses[stat] = bonuses.get(stat, 0) + value
        
        return bonuses
