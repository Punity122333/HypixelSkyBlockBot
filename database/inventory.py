from typing import Dict, List, Optional
from .core import DatabaseCore


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
        
        await self.execute(
            'INSERT INTO inventory_items (user_id, item_id, amount, slot) VALUES (?, ?, ?, ?)',
            (user_id, item_id, amount, next_slot)
        )
        await self.commit()

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
