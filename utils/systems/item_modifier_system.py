from typing import Dict, Optional, List, Any

class ItemModifierSystem:
    
    @staticmethod
    async def apply_random_modifier(db, user_id: int, inventory_item_id: int, item_id: str) -> Optional[Dict[str, Any]]:
        return await db.item_modifiers.apply_random_modifier(user_id, inventory_item_id, item_id)
    
    @staticmethod
    async def get_item_modifiers(db, inventory_item_id: int) -> Optional[Dict[str, Any]]:
        return await db.item_modifiers.get_item_modifiers(inventory_item_id)
    
    @staticmethod
    async def calculate_modifier_stats(db, modifiers: Optional[Dict[str, Any]]) -> Dict[str, int]:
        return await db.item_modifiers.calculate_modifier_stats(modifiers)
    
    @staticmethod
    def format_modifier_display(db, modifiers: Optional[Dict[str, Any]]) -> str:
        return db.item_modifiers.format_modifier_display(modifiers)
