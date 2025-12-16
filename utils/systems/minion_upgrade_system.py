import time
import json
from typing import Dict, List, Any

class MinionUpgradeSystem:
    
    @staticmethod
    async def apply_fuel(db, minion_id: int, fuel_id: str) -> bool:
        fuel_data = await db.fetchone(
            'SELECT * FROM game_minion_fuels WHERE fuel_id = ?',
            (fuel_id,)
        )
        
        if not fuel_data:
            return False
        
        minion = await db.fetchone(
            'SELECT user_id FROM user_minions WHERE id = ?',
            (minion_id,)
        )
        
        if not minion:
            return False
        
        user_id = minion[0]
        
        has_fuel = await db.fetchone(
            'SELECT amount FROM inventory_items WHERE user_id = ? AND item_id = ?',
            (user_id, fuel_id)
        )
        
        if not has_fuel or has_fuel[0] < 1:
            return False
        
        await db.execute(
            'UPDATE inventory_items SET amount = amount - 1 WHERE user_id = ? AND item_id = ?',
            (user_id, fuel_id)
        )
        
        fuel_info = {
            'fuel_id': fuel_id,
            'speed_boost': fuel_data[2],
            'expires_at': int(time.time()) + fuel_data[3]
        }
        
        await db.execute(
            '''INSERT INTO minion_upgrades (minion_id, upgrade_type, upgrade_value, applied_at)
               VALUES (?, 'fuel', ?, ?)''',
            (minion_id, json.dumps(fuel_info), int(time.time()))
        )
        await db.commit()
        
        return True
    
    @staticmethod
    async def apply_skin(db, minion_id: int, skin_id: str) -> bool:
        skin_data = await db.fetchone(
            'SELECT * FROM game_minion_skins WHERE skin_id = ?',
            (skin_id,)
        )
        
        if not skin_data:
            return False
        
        minion = await db.fetchone(
            'SELECT user_id, minion_type FROM user_minions WHERE id = ?',
            (minion_id,)
        )
        
        if not minion:
            return False
        
        user_id = minion[0]
        minion_type = minion[1]
        
        if skin_data[2] != minion_type:
            return False
        
        has_skin = await db.fetchone(
            'SELECT amount FROM inventory_items WHERE user_id = ? AND item_id = ?',
            (user_id, skin_id)
        )
        
        if not has_skin or has_skin[0] < 1:
            return False
        
        await db.execute(
            'UPDATE inventory_items SET amount = amount - 1 WHERE user_id = ? AND item_id = ?',
            (user_id, skin_id)
        )
        
        await db.execute(
            'DELETE FROM minion_upgrades WHERE minion_id = ? AND upgrade_type = ?',
            (minion_id, 'skin')
        )
        
        skin_info = {
            'skin_id': skin_id,
            'skin_name': skin_data[1]
        }
        
        await db.execute(
            '''INSERT INTO minion_upgrades (minion_id, upgrade_type, upgrade_value, applied_at)
               VALUES (?, 'skin', ?, ?)''',
            (minion_id, json.dumps(skin_info), int(time.time()))
        )
        await db.commit()
        
        return True
    
    @staticmethod
    async def apply_compactor(db, minion_id: int, compactor_id: str) -> bool:
        compactor_data = await db.fetchone(
            'SELECT * FROM game_compactors WHERE compactor_id = ?',
            (compactor_id,)
        )
        
        if not compactor_data:
            return False
        
        minion = await db.fetchone(
            'SELECT user_id FROM user_minions WHERE id = ?',
            (minion_id,)
        )
        
        if not minion:
            return False
        
        user_id = minion[0]
        
        has_compactor = await db.fetchone(
            'SELECT amount FROM inventory_items WHERE user_id = ? AND item_id = ?',
            (user_id, compactor_id)
        )
        
        if not has_compactor or has_compactor[0] < 1:
            return False
        
        await db.execute(
            'UPDATE inventory_items SET amount = amount - 1 WHERE user_id = ? AND item_id = ?',
            (user_id, compactor_id)
        )
        
        await db.execute(
            'DELETE FROM minion_upgrades WHERE minion_id = ? AND upgrade_type = ?',
            (minion_id, 'compactor')
        )
        
        compactor_info = {
            'compactor_id': compactor_id,
            'compactor_name': compactor_data[1],
            'tier': compactor_data[2],
            'multiplier': compactor_data[3]
        }
        
        await db.execute(
            '''INSERT INTO minion_upgrades (minion_id, upgrade_type, upgrade_value, applied_at)
               VALUES (?, 'compactor', ?, ?)''',
            (minion_id, json.dumps(compactor_info), int(time.time()))
        )
        await db.commit()
        
        return True
    
    @staticmethod
    async def apply_storage_upgrade(db, minion_id: int) -> bool:
        minion = await db.fetchone(
            'SELECT storage_slots FROM user_minions WHERE id = ?',
            (minion_id,)
        )
        
        if not minion:
            return False
        
        current_storage = minion[0] or 9
        
        if current_storage >= 21:
            return False
        
        new_storage = current_storage + 3
        
        await db.execute(
            'UPDATE user_minions SET storage_slots = ? WHERE id = ?',
            (new_storage, minion_id)
        )
        
        upgrade_info = {
            'old_slots': current_storage,
            'new_slots': new_storage
        }
        
        await db.execute(
            '''INSERT INTO minion_upgrades (minion_id, upgrade_type, upgrade_value, applied_at)
               VALUES (?, 'storage', ?, ?)''',
            (minion_id, json.dumps(upgrade_info), int(time.time()))
        )
        await db.commit()
        
        return True
    
    @staticmethod
    async def get_minion_upgrades(db, minion_id: int) -> Dict[str, Any]:
        rows = await db.fetchall(
            'SELECT upgrade_type, upgrade_value FROM minion_upgrades WHERE minion_id = ?',
            (minion_id,)
        )
        
        upgrades = {}
        for row in rows:
            upgrade_type = row[0]
            upgrade_value = json.loads(row[1]) if row[1] else {}
            
            if upgrade_type == 'fuel':
                if upgrade_value.get('expires_at', 0) > time.time():
                    upgrades['fuel'] = upgrade_value
            else:
                upgrades[upgrade_type] = upgrade_value
        
        return upgrades
    
    @staticmethod
    async def calculate_minion_speed(db, minion_id: int, base_speed: int) -> float:
        upgrades = await MinionUpgradeSystem.get_minion_upgrades(db, minion_id)
        
        speed = base_speed
        
        if 'fuel' in upgrades:
            fuel_boost = upgrades['fuel'].get('speed_boost', 1.0)
            speed = int(speed * fuel_boost)
        
        return speed
    
    @staticmethod
    async def process_minion_collection(db, minion_id: int, items_collected: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        upgrades = await MinionUpgradeSystem.get_minion_upgrades(db, minion_id)
        
        if 'compactor' not in upgrades:
            return items_collected
        
        compactor = upgrades['compactor']
        multiplier = compactor.get('multiplier', 1)
        
        processed_items = []
        for item in items_collected:
            item_id = item['item_id']
            amount = item['amount']
            
            if 'enchanted' not in item_id and amount >= multiplier:
                enchanted_count = amount // multiplier
                remaining = amount % multiplier
                
                enchanted_id = f'enchanted_{item_id}'
                if enchanted_count > 0:
                    processed_items.append({
                        'item_id': enchanted_id,
                        'amount': enchanted_count
                    })
                
                if remaining > 0:
                    processed_items.append({
                        'item_id': item_id,
                        'amount': remaining
                    })
            else:
                processed_items.append(item)
        
        return processed_items
    
    @staticmethod
    async def remove_upgrade(db, minion_id: int, upgrade_type: str) -> bool:
        await db.execute(
            'DELETE FROM minion_upgrades WHERE minion_id = ? AND upgrade_type = ?',
            (minion_id, upgrade_type)
        )
        await db.commit()
        return True
