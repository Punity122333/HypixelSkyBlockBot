from .core import DatabaseCore
from typing import Optional, Dict, Any

class WeaponAbilitiesDB(DatabaseCore):
    
    async def get_weapon_ability(self, item_id: str) -> Optional[Dict[str, Any]]:
        row = await self.fetchone(
            'SELECT * FROM weapon_abilities WHERE item_id = ?',
            (item_id,)
        )
        return dict(row) if row else None
    
    async def get_all_weapon_abilities(self) -> list[Dict[str, Any]]:
        rows = await self.fetchall('SELECT * FROM weapon_abilities')
        return [dict(row) for row in rows]
    
    async def has_ability(self, item_id: str) -> bool:
        row = await self.fetchone(
            'SELECT 1 FROM weapon_abilities WHERE item_id = ?',
            (item_id,)
        )
        return row is not None
    
    async def add_weapon_ability(
        self,
        item_id: str,
        ability_name: str,
        mana_cost: int,
        cooldown: float,
        description: str,
        **kwargs
    ) -> None:
        fields = ['item_id', 'ability_name', 'mana_cost', 'cooldown', 'description']
        values = [item_id, ability_name, mana_cost, cooldown, description]
        
        for key, value in kwargs.items():
            fields.append(key)
            values.append(value)
        
        placeholders = ', '.join(['?' for _ in values])
        field_names = ', '.join(fields)
        
        await self.execute(
            f'INSERT OR REPLACE INTO weapon_abilities ({field_names}) VALUES ({placeholders})',
            tuple(values)
        )
        await self.commit()
    
    async def update_weapon_ability(self, item_id: str, **kwargs) -> None:
        if not kwargs:
            return
        
        set_clause = ', '.join([f'{key} = ?' for key in kwargs.keys()])
        values = list(kwargs.values()) + [item_id]
        
        await self.execute(
            f'UPDATE weapon_abilities SET {set_clause} WHERE item_id = ?',
            tuple(values)
        )
        await self.commit()
    
    async def delete_weapon_ability(self, item_id: str) -> None:
        await self.execute(
            'DELETE FROM weapon_abilities WHERE item_id = ?',
            (item_id,)
        )
        await self.commit()
    
    async def get_abilities_by_type(self, weapon_type: str) -> list[Dict[str, Any]]:
        rows = await self.fetchall(
            '''SELECT wa.* FROM weapon_abilities wa
               JOIN game_items gi ON wa.item_id = gi.item_id
               WHERE gi.item_type = ?''',
            (weapon_type,)
        )
        return [dict(row) for row in rows]
