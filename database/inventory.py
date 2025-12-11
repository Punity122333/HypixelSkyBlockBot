from typing import Dict, List, Optional
from .core import DatabaseCore
import random


class InventoryDB(DatabaseCore):
    async def get_inventory(self, user_id: int) -> List[Dict]:
        rows = await self.fetchall(
            'SELECT * FROM inventory_items WHERE user_id = ? ORDER BY slot',
            (user_id,)
        )
        return [dict(row) for row in rows]

    async def add_item(self, user_id: int, item_id: str, amount: int = 1):
        row = await self.fetchone(
            'SELECT MAX(slot) as max_slot FROM inventory_items WHERE user_id = ?',
            (user_id,)
        )
        next_slot = (row['max_slot'] + 1) if row and row['max_slot'] is not None else 0
        
        cursor = await self.execute(
            'INSERT INTO inventory_items (user_id, item_id, amount, slot) VALUES (?, ?, ?, ?)',
            (user_id, item_id, amount, next_slot)
        )
        await self.commit()
        
        inventory_item_id = cursor.lastrowid if cursor.lastrowid else 0
        
        if inventory_item_id and random.random() < 0.25:
            item_row = await self.fetchone(
                'SELECT item_type FROM game_items WHERE item_id = ?',
                (item_id,)
            )
            
            if item_row:
                item_type = item_row['item_type']
                modifier_item_types = ['SWORD', 'BOW', 'PICKAXE', 'AXE', 'HOE', 'FISHING_ROD', 
                                      'HELMET', 'CHESTPLATE', 'LEGGINGS', 'BOOTS']
                
                if item_type in modifier_item_types:
                    from .item_modifiers import ItemModifierDB
                    modifier_db = ItemModifierDB(self.db_path)
                    modifier_db.conn = self.conn
                    await modifier_db.apply_random_modifier(user_id, inventory_item_id, item_id)

    async def remove_item(self, user_id: int, item_id: str, amount: int = 1):
        rows = await self.fetchall(
            'SELECT id, amount FROM inventory_items WHERE user_id = ? AND item_id = ? ORDER BY slot',
            (user_id, item_id)
        )
        
        removed = 0
        for row in rows:
            if removed >= amount:
                break
            
            item_amount = row['amount']
            if item_amount <= (amount - removed):
                await self.execute(
                    'DELETE FROM inventory_items WHERE id = ?',
                    (row['id'],)
                )
                removed += item_amount
            else:
                await self.execute(
                    'UPDATE inventory_items SET amount = amount - ? WHERE id = ?',
                    (amount - removed, row['id'])
                )
                removed = amount
        
        await self.commit()
        return removed >= amount

    async def get_item_count(self, user_id: int, item_id: str) -> int:
        row = await self.fetchone(
            'SELECT SUM(amount) as total FROM inventory_items WHERE user_id = ? AND item_id = ?',
            (user_id, item_id)
        )
        return row['total'] if row and row['total'] else 0

    async def add_item_to_inventory(self, user_id: int, item_id: str, amount: int = 1):
        for _ in range(amount):
            await self.add_item(user_id, item_id, 1)

    async def remove_item_from_inventory(self, user_id: int, item_id: str, amount: int = 1):
        return await self.remove_item(user_id, item_id, amount)

    async def has_tool(self, user_id: int, tool_type: str) -> tuple[bool, Optional[str]]:
        rows = await self.fetchall(
            'SELECT item_id FROM inventory_items WHERE user_id = ?',
            (user_id,)
        )
        
        for row in rows:
            if tool_type in row['item_id'].lower():
                return True, row['item_id']
        
        return False, None

    async def get_tool_multiplier(self, user_id: int, tool_type: str) -> float:
        has_tool, tool_id = await self.has_tool(user_id, tool_type)
        if not has_tool or not tool_id:
            return 1.0
        
        if 'wooden' in tool_id:
            return 1.0
        elif 'stone' in tool_id:
            return 1.5
        elif 'iron' in tool_id:
            return 2.0
        elif 'golden' in tool_id:
            return 2.5
        elif 'diamond' in tool_id:
            return 3.0
        else:
            return 1.0

    async def equip_item(self, user_id: int, slot_id: int, equipment_slot: str) -> bool:
        row = await self.fetchone(
            'SELECT * FROM inventory_items WHERE user_id = ? AND slot = ?',
            (user_id, slot_id)
        )
        
        if not row:
            return False
        
        item_id = row['item_id']
        
        item_row = await self.fetchone(
            'SELECT * FROM game_items WHERE item_id = ?',
            (item_id,)
        )
        
        if not item_row:
            return False
        
        item_type = item_row['item_type']
        
        valid_equipment = {
            'helmet': ['HELMET'],
            'chestplate': ['CHESTPLATE'],
            'leggings': ['LEGGINGS'],
            'boots': ['BOOTS'],
            'sword': ['SWORD'],
            'bow': ['BOW'],
            'pickaxe': ['PICKAXE'],
            'axe': ['AXE'],
            'hoe': ['HOE'],
            'fishing_rod': ['FISHING_ROD']
        }
        
        if equipment_slot not in valid_equipment or item_type not in valid_equipment[equipment_slot]:
            return False
        
        await self.execute(
            'INSERT OR IGNORE INTO player_equipment (user_id) VALUES (?)',
            (user_id,)
        )
        
        old_equipment_row = await self.fetchone(
            'SELECT {}_slot FROM player_equipment WHERE user_id = ?'.format(equipment_slot),
            (user_id,)
        )
        
        old_slot_id = old_equipment_row[f'{equipment_slot}_slot'] if old_equipment_row else None
        
        if old_slot_id is not None:
            await self.execute(
                'UPDATE inventory_items SET equipped = 0 WHERE user_id = ? AND slot = ?',
                (user_id, old_slot_id)
            )
        
        await self.execute(
            'UPDATE player_equipment SET {}_slot = ? WHERE user_id = ?'.format(equipment_slot),
            (slot_id, user_id)
        )
        
        await self.execute(
            'UPDATE inventory_items SET equipped = 1 WHERE user_id = ? AND slot = ?',
            (user_id, slot_id)
        )
        
        await self.commit()
        return True

    async def unequip_item(self, user_id: int, equipment_slot: str) -> bool:
        await self.execute(
            'UPDATE player_equipment SET {}_slot = NULL WHERE user_id = ?'.format(equipment_slot),
            (user_id,)
        )
        await self.commit()
        return True

    async def get_equipped_items(self, user_id: int):
        row = await self.fetchone(
            'SELECT * FROM player_equipment WHERE user_id = ?',
            (user_id,)
        )
        
        if not row:
            await self.execute(
                'INSERT INTO player_equipment (user_id) VALUES (?)',
                (user_id,)
            )
            await self.commit()
            return {
                'helmet': None,
                'chestplate': None,
                'leggings': None,
                'boots': None,
                'sword': None,
                'bow': None,
                'pickaxe': None,
                'axe': None,
                'hoe': None,
                'fishing_rod': None
            }
        
        equipment = {}
        for slot in ['helmet', 'chestplate', 'leggings', 'boots', 'sword', 'bow', 'pickaxe', 'axe', 'hoe', 'fishing_rod']:
            slot_id = row[f'{slot}_slot']
            if slot_id is not None:
                item_row = await self.fetchone(
                    'SELECT i.*, g.* FROM inventory_items i JOIN game_items g ON i.item_id = g.item_id WHERE i.user_id = ? AND i.slot = ?',
                    (user_id, slot_id)
                )
                equipment[slot] = dict(item_row) if item_row else None
            else:
                equipment[slot] = None
        
        return equipment
