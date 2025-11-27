from typing import Optional, Dict, List
import json
from .base import DatabaseBase


class PetsMinionsDatabase(DatabaseBase):
    """Database operations for pets and minions."""
    
    # Pets
    async def add_pet(self, user_id: int, pet_type: str, rarity: str, level: int = 1, xp: int = 0) -> int:
        """Add a pet to a player's collection."""
        await self.conn.execute('''
            INSERT INTO pets (user_id, pet_type, rarity, level, xp, active)
            VALUES (?, ?, ?, ?, ?, 0)
        ''', (user_id, pet_type, rarity, level, xp))
        await self.conn.commit()
        async with self.conn.execute('SELECT last_insert_rowid()') as cursor:
            result = await cursor.fetchone()
            return result[0] if result else 0
    
    async def get_user_pets(self, user_id: int) -> List[Dict]:
        """Get all pets owned by a user."""
        async with self.conn.execute('''
            SELECT * FROM pets WHERE user_id = ? ORDER BY active DESC, rarity DESC, level DESC
        ''', (user_id,)) as cursor:
            rows = await cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
    
    async def get_active_pet(self, user_id: int) -> Optional[Dict]:
        """Get the currently active pet for a user."""
        async with self.conn.execute('''
            SELECT * FROM pets WHERE user_id = ? AND active = 1 LIMIT 1
        ''', (user_id,)) as cursor:
            row = await cursor.fetchone()
            if row:
                columns = [description[0] for description in cursor.description]
                return dict(zip(columns, row))
            return None
    
    async def equip_pet(self, user_id: int, pet_id: int) -> bool:
        """Equip a pet (unequip all others first)."""
        await self.conn.execute('UPDATE pets SET active = 0 WHERE user_id = ?', (user_id,))
        await self.conn.execute('UPDATE pets SET active = 1 WHERE id = ? AND user_id = ?', (pet_id, user_id))
        await self.conn.commit()
        return True
    
    async def update_pet_xp(self, pet_id: int, xp: int):
        """Add XP to a pet."""
        await self.conn.execute('UPDATE pets SET xp = xp + ? WHERE id = ?', (xp, pet_id))
        await self.conn.commit()
    
    async def level_up_pet(self, pet_id: int):
        """Level up a pet."""
        await self.conn.execute('UPDATE pets SET level = level + 1, xp = 0 WHERE id = ?', (pet_id,))
        await self.conn.commit()
    
    async def delete_pet(self, pet_id: int, user_id: int):
        """Delete a pet."""
        await self.conn.execute('DELETE FROM pets WHERE id = ? AND user_id = ?', (pet_id, user_id))
        await self.conn.commit()
    
    # Minions
    async def add_minion(self, user_id: int, minion_type: str, tier: int, island_slot: int) -> int:
        """Add a minion to a player's island."""
        storage_data = json.dumps([])
        await self.conn.execute('''
            INSERT INTO minions (user_id, minion_type, tier, island_slot, fuel, storage)
            VALUES (?, ?, ?, ?, 0, ?)
        ''', (user_id, minion_type, tier, island_slot, storage_data))
        await self.conn.commit()
        async with self.conn.execute('SELECT last_insert_rowid()') as cursor:
            result = await cursor.fetchone()
            return result[0] if result else 0
    
    async def get_user_minions(self, user_id: int) -> List[Dict]:
        """Get all minions owned by a user."""
        async with self.conn.execute('''
            SELECT * FROM minions WHERE user_id = ? ORDER BY island_slot
        ''', (user_id,)) as cursor:
            rows = await cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            minions = []
            for row in rows:
                minion_dict = dict(zip(columns, row))
                minion_dict['storage'] = json.loads(minion_dict['storage'])
                minions.append(minion_dict)
            return minions
    
    async def get_minion(self, minion_id: int) -> Optional[Dict]:
        """Get a specific minion."""
        async with self.conn.execute('SELECT * FROM minions WHERE id = ?', (minion_id,)) as cursor:
            row = await cursor.fetchone()
            if row:
                columns = [description[0] for description in cursor.description]
                minion_dict = dict(zip(columns, row))
                minion_dict['storage'] = json.loads(minion_dict['storage'])
                return minion_dict
            return None
    
    async def update_minion_storage(self, minion_id: int, storage: List[Dict]):
        """Update minion storage contents."""
        await self.conn.execute('UPDATE minions SET storage = ? WHERE id = ?', (json.dumps(storage), minion_id))
        await self.conn.commit()
    
    async def update_minion_fuel(self, minion_id: int, fuel: int):
        """Update minion fuel."""
        await self.conn.execute('UPDATE minions SET fuel = ? WHERE id = ?', (fuel, minion_id))
        await self.conn.commit()
    
    async def upgrade_minion(self, minion_id: int):
        """Upgrade minion tier."""
        await self.conn.execute('UPDATE minions SET tier = tier + 1 WHERE id = ?', (minion_id,))
        await self.conn.commit()
    
    async def delete_minion(self, minion_id: int, user_id: int):
        """Delete a minion."""
        await self.conn.execute('DELETE FROM minions WHERE id = ? AND user_id = ?', (minion_id, user_id))
        await self.conn.commit()
