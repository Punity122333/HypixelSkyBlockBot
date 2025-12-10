from typing import Dict, List, Optional, Any
import time
import json
from .core import DatabaseCore

class MinionUpgradeDB(DatabaseCore):
    
    async def apply_fuel(self, minion_id: int, fuel_id: str) -> bool:
        fuel_data = await self.fetchone(
            'SELECT * FROM game_minion_fuels WHERE fuel_id = ?',
            (fuel_id,)
        )
        
        if not fuel_data:
            return False
        
        minion = await self.fetchone(
            'SELECT user_id FROM user_minions WHERE id = ?',
            (minion_id,)
        )
        
        if not minion:
            return False
        
        user_id = minion['user_id']
        
        has_fuel = await self.fetchone(
            'SELECT amount FROM inventory_items WHERE user_id = ? AND item_id = ?',
            (user_id, fuel_id)
        )
        
        if not has_fuel or has_fuel['amount'] < 1:
            return False
        
        await self.execute(
            'UPDATE inventory_items SET amount = amount - 1 WHERE user_id = ? AND item_id = ?',
            (user_id, fuel_id)
        )
        
        fuel_info = {
            'fuel_id': fuel_id,
            'speed_boost': fuel_data['speed_boost'],
            'expires_at': int(time.time()) + fuel_data['duration']
        }
        
        await self.execute(
            '''INSERT INTO minion_upgrades (minion_id, upgrade_type, upgrade_value, applied_at)
               VALUES (?, 'fuel', ?, ?)''',
            (minion_id, json.dumps(fuel_info), int(time.time()))
        )
        await self.commit()
        
        return True
    
    async def apply_skin(self, minion_id: int, skin_id: str) -> bool:
        skin_data = await self.fetchone(
            'SELECT * FROM game_minion_skins WHERE skin_id = ?',
            (skin_id,)
        )
        
        if not skin_data:
            return False
        
        minion = await self.fetchone(
            'SELECT user_id, minion_type FROM user_minions WHERE id = ?',
            (minion_id,)
        )
        
        if not minion:
            return False
        
        user_id = minion['user_id']
        minion_type = minion['minion_type']
        
        if skin_data['minion_type'] != minion_type:
            return False
        
        has_skin = await self.fetchone(
            'SELECT amount FROM inventory_items WHERE user_id = ? AND item_id = ?',
            (user_id, skin_id)
        )
        
        if not has_skin or has_skin['amount'] < 1:
            return False
        
        await self.execute(
            'UPDATE inventory_items SET amount = amount - 1 WHERE user_id = ? AND item_id = ?',
            (user_id, skin_id)
        )
        
        await self.execute(
            'DELETE FROM minion_upgrades WHERE minion_id = ? AND upgrade_type = ?',
            (minion_id, 'skin')
        )
        
        skin_info = {
            'skin_id': skin_id,
            'skin_name': skin_data['name']
        }
        
        await self.execute(
            '''INSERT INTO minion_upgrades (minion_id, upgrade_type, upgrade_value, applied_at)
               VALUES (?, 'skin', ?, ?)''',
            (minion_id, json.dumps(skin_info), int(time.time()))
        )
        await self.commit()
        
        return True
    
    async def apply_compactor(self, minion_id: int, compactor_id: str) -> bool:
        compactor_data = await self.fetchone(
            'SELECT * FROM game_compactors WHERE compactor_id = ?',
            (compactor_id,)
        )
        
        if not compactor_data:
            return False
        
        minion = await self.fetchone(
            'SELECT user_id FROM user_minions WHERE id = ?',
            (minion_id,)
        )
        
        if not minion:
            return False
        
        user_id = minion['user_id']
        
        has_compactor = await self.fetchone(
            'SELECT amount FROM inventory_items WHERE user_id = ? AND item_id = ?',
            (user_id, compactor_id)
        )
        
        if not has_compactor or has_compactor['amount'] < 1:
            return False
        
        await self.execute(
            'UPDATE inventory_items SET amount = amount - 1 WHERE user_id = ? AND item_id = ?',
            (user_id, compactor_id)
        )
        
        await self.execute(
            'DELETE FROM minion_upgrades WHERE minion_id = ? AND upgrade_type = ?',
            (minion_id, 'compactor')
        )
        
        compactor_info = {
            'compactor_id': compactor_id,
            'compactor_type': compactor_data['compactor_type'],
            'compression_ratio': compactor_data['compression_ratio']
        }
        
        await self.execute(
            '''INSERT INTO minion_upgrades (minion_id, upgrade_type, upgrade_value, applied_at)
               VALUES (?, 'compactor', ?, ?)''',
            (minion_id, json.dumps(compactor_info), int(time.time()))
        )
        await self.commit()
        
        return True
    
    async def apply_storage_upgrade(self, minion_id: int) -> bool:
        minion = await self.fetchone(
            'SELECT storage_slots FROM user_minions WHERE id = ?',
            (minion_id,)
        )
        
        if not minion:
            return False
        
        current_storage = minion['storage_slots'] or 9
        
        if current_storage >= 21:
            return False
        
        new_storage = current_storage + 3
        
        await self.execute(
            'UPDATE user_minions SET storage_slots = ? WHERE id = ?',
            (new_storage, minion_id)
        )
        
        upgrade_info = {
            'old_slots': current_storage,
            'new_slots': new_storage
        }
        
        await self.execute(
            '''INSERT INTO minion_upgrades (minion_id, upgrade_type, upgrade_value, applied_at)
               VALUES (?, 'storage', ?, ?)''',
            (minion_id, json.dumps(upgrade_info), int(time.time()))
        )
        await self.commit()
        
        return True
    
    async def get_minion_upgrades(self, minion_id: int) -> Dict[str, Any]:
        rows = await self.fetchall(
            'SELECT * FROM minion_upgrades WHERE minion_id = ? ORDER BY applied_at DESC',
            (minion_id,)
        )
        
        upgrades: Dict[str, Any] = {}
        
        for row in rows:
            upgrade_type = row['upgrade_type']
            upgrade_value = json.loads(row['upgrade_value']) if row['upgrade_value'] else {}
            
            if upgrade_type == 'fuel':
                if upgrade_value.get('expires_at', 0) > time.time():
                    upgrades['fuel'] = upgrade_value
            elif upgrade_type == 'skin':
                upgrades['skin'] = upgrade_value
            elif upgrade_type == 'compactor':
                upgrades['compactor'] = upgrade_value
        
        return upgrades
    
    async def calculate_minion_speed(self, minion_id: int, base_speed: int) -> float:
        upgrades = await self.get_minion_upgrades(minion_id)
        
        speed_multiplier = 1.0
        
        if 'fuel' in upgrades and upgrades['fuel'].get('expires_at', 0) > time.time():
            speed_boost = upgrades['fuel'].get('speed_boost', 0)
            speed_multiplier += speed_boost / 100.0
        
        final_speed = base_speed / speed_multiplier
        
        return final_speed
    
    async def process_minion_collection(self, minion_id: int, items_collected: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        upgrades = await self.get_minion_upgrades(minion_id)
        
        if 'compactor' not in upgrades:
            return items_collected
        
        compactor_type = upgrades['compactor'].get('compactor_type', 'none')
        compression_ratio = upgrades['compactor'].get('compression_ratio', 1)
        
        if compactor_type == 'none':
            return items_collected
        
        processed_items = []
        
        for item in items_collected:
            item_id = item.get('item_id', '')
            amount = item.get('amount', 1)
            
            if compactor_type == 'super_compactor':
                if amount >= compression_ratio:
                    compressed_amount = amount // compression_ratio
                    remainder = amount % compression_ratio
                    
                    compressed_item_id = f"enchanted_{item_id}"
                    
                    if compressed_amount > 0:
                        processed_items.append({
                            'item_id': compressed_item_id,
                            'amount': compressed_amount
                        })
                    
                    if remainder > 0:
                        processed_items.append({
                            'item_id': item_id,
                            'amount': remainder
                        })
                else:
                    processed_items.append(item)
            else:
                processed_items.append(item)
        
        return processed_items
    
    async def remove_upgrade(self, minion_id: int, upgrade_type: str) -> bool:
        await self.execute(
            'DELETE FROM minion_upgrades WHERE minion_id = ? AND upgrade_type = ?',
            (minion_id, upgrade_type)
        )
        await self.commit()
        
        return True
