from typing import Dict, Any, List
import json
from .base import DatabaseBase


class InventoryDatabase(DatabaseBase):
    """Database operations for inventory and item management."""
    
    async def get_inventory(self, user_id: int) -> List[Dict]:
        """Get user's inventory."""
        async with self.conn.execute(
            'SELECT * FROM inventories WHERE user_id = ? ORDER BY slot', (user_id,)
        ) as cursor:
            rows = await cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in rows]

    async def add_item(self, user_id: int, item_id: str, item_data: Dict[str, Any]):
        """Add an item to inventory."""
        async with self.conn.execute(
            'SELECT MAX(slot) FROM inventories WHERE user_id = ?', (user_id,)
        ) as cursor:
            result = await cursor.fetchone()
            if result and result[0] is not None:
                next_slot = result[0] + 1
            else:
                next_slot = 0
        
        await self.conn.execute(
            'INSERT INTO inventories (user_id, slot, item_id, item_data) VALUES (?, ?, ?, ?)',
            (user_id, next_slot, item_id, json.dumps(item_data))
        )
        await self.conn.commit()

    async def remove_item(self, user_id: int, slot: int):
        """Remove an item from inventory by slot."""
        await self.conn.execute(
            'DELETE FROM inventories WHERE user_id = ? AND slot = ?',
            (user_id, slot)
        )
        await self.conn.commit()

    async def get_item_count(self, user_id: int, item_id: str) -> int:
        """Count how many of a specific item a user has."""
        inventory = await self.get_inventory(user_id)
        count = 0
        for item in inventory:
            if item['item_id'] == item_id:
                count += 1
        return count

    async def add_item_to_inventory(self, user_id: int, item_id: str, amount: int = 1):
        """Add multiple items to inventory."""
        for _ in range(amount):
            await self.add_item(user_id, item_id, {})

    async def remove_item_from_inventory(self, user_id: int, item_id: str, amount: int = 1):
        """Remove multiple items from inventory."""
        inventory = await self.get_inventory(user_id)
        removed = 0
        for item in inventory:
            if item['item_id'] == item_id and removed < amount:
                await self.remove_item(user_id, item['slot'])
                removed += 1
        return removed

    async def has_tool(self, user_id: int, tool_type: str) -> tuple[bool, str]:
        """Check if user has a tool and return the best one."""
        inventory = await self.get_inventory(user_id)
        tool_tiers = {
            'pickaxe': ['wooden_pickaxe', 'stone_pickaxe', 'iron_pickaxe', 'gold_pickaxe', 'diamond_pickaxe'],
            'axe': ['wooden_axe', 'stone_axe', 'iron_axe', 'diamond_axe'],
            'hoe': ['wooden_hoe', 'stone_hoe', 'iron_hoe', 'diamond_hoe'],
            'sword': ['wooden_sword', 'stone_sword', 'iron_sword', 'diamond_sword'],
            'fishing_rod': ['wooden_fishing_rod', 'iron_fishing_rod', 'diamond_fishing_rod']
        }
        
        tools = tool_tiers.get(tool_type, [])
        best_tool = None
        for item in inventory:
            if item['item_id'] in tools:
                if best_tool is None or tools.index(item['item_id']) > tools.index(best_tool):
                    best_tool = item['item_id']
        
        return (best_tool is not None, best_tool if best_tool else "")

    async def get_tool_multiplier(self, user_id: int, tool_type: str) -> float:
        """Get the multiplier for the best tool of a type."""
        has_it, tool_id = await self.has_tool(user_id, tool_type)
        if not has_it:
            return 0.0
        
        multipliers = {
            'wooden_pickaxe': 1.0, 'stone_pickaxe': 1.2, 'iron_pickaxe': 1.5, 'gold_pickaxe': 1.8, 'diamond_pickaxe': 2.2,
            'wooden_axe': 1.0, 'stone_axe': 1.2, 'iron_axe': 1.5, 'diamond_axe': 2.0,
            'wooden_hoe': 1.0, 'stone_hoe': 1.2, 'iron_hoe': 1.5, 'diamond_hoe': 2.0,
            'wooden_sword': 1.0, 'stone_sword': 1.2, 'iron_sword': 1.5, 'diamond_sword': 2.0,
            'wooden_fishing_rod': 1.0, 'iron_fishing_rod': 1.3, 'diamond_fishing_rod': 1.7
        }
        
        return multipliers.get(tool_id, 1.0)
