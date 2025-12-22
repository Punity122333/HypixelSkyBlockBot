from typing import Dict, List, Any
from .core import DatabaseCore
import time

class IslandDB(DatabaseCore):
    
    async def get_or_create_island(self, user_id: int) -> Dict:
        row = await self.fetchone(
            'SELECT * FROM player_islands WHERE user_id = ?',
            (user_id,)
        )
        
        if not row:
            await self.execute(
                '''INSERT INTO player_islands (user_id, last_modified)
                   VALUES (?, ?)''',
                (user_id, int(time.time()))
            )
            await self.commit()
            
            row = await self.fetchone(
                'SELECT * FROM player_islands WHERE user_id = ?',
                (user_id,)
            )
        
        return dict(row) if row else {}
    
    async def update_island(self, user_id: int, **kwargs):
        valid_fields = ['island_name', 'island_level', 'visitors_enabled', 'theme', 'upgrade_points']
        updates = {k: v for k, v in kwargs.items() if k in valid_fields}
        
        if not updates:
            return
        
        updates['last_modified'] = int(time.time())
        
        set_clause = ', '.join([f'{k} = ?' for k in updates.keys()])
        values = list(updates.values()) + [user_id]
        
        await self.execute(
            f'UPDATE player_islands SET {set_clause} WHERE user_id = ?',
            tuple(values)
        )
        await self.commit()
    
    async def add_decoration(self, user_id: int, decoration_id: str, position_x: int, position_y: int, rotation: int = 0) -> bool:
        decoration = await self.fetchone(
            'SELECT * FROM game_island_decorations WHERE decoration_id = ?',
            (decoration_id,)
        )
        
        if not decoration:
            return False
        
        island = await self.get_or_create_island(user_id)
        
        if island.get('island_level', 1) < decoration['required_level']:
            return False
        
        player = await self.fetchone(
            'SELECT coins FROM player_economy WHERE user_id = ?',
            (user_id,)
        )
        
        if not player or player['coins'] < decoration['cost']:
            return False
        
        existing = await self.fetchone(
            '''SELECT COUNT(*) as count FROM island_decorations 
               WHERE user_id = ? AND position_x = ? AND position_y = ?''',
            (user_id, position_x, position_y)
        )
        
        if existing and existing['count'] > 0:
            return False
        
        await self.execute(
            'UPDATE player_economy SET coins = coins - ? WHERE user_id = ?',
            (decoration['cost'], user_id)
        )
        
        await self.execute(
            '''INSERT INTO island_decorations (user_id, decoration_id, position_x, position_y, rotation, placed_at)
               VALUES (?, ?, ?, ?, ?, ?)''',
            (user_id, decoration_id, position_x, position_y, rotation, int(time.time()))
        )
        await self.commit()
        return True
    
    async def remove_decoration(self, user_id: int, decoration_id: int):
        await self.execute(
            'DELETE FROM island_decorations WHERE id = ? AND user_id = ?',
            (decoration_id, user_id)
        )
        await self.commit()
    
    async def get_decorations(self, user_id: int) -> List[Dict]:
        rows = await self.fetchall(
            '''SELECT d.*, g.decoration_name, g.decoration_type, g.rarity 
               FROM island_decorations d
               JOIN game_island_decorations g ON d.decoration_id = g.decoration_id
               WHERE d.user_id = ?
               ORDER BY d.placed_at DESC''',
            (user_id,)
        )
        return [dict(row) for row in rows]
    
    async def place_block(self, user_id: int, block_type: str, position_x: int, position_y: int, position_z: int):
        await self.execute(
            '''INSERT INTO island_blocks (user_id, block_type, position_x, position_y, position_z, placed_at)
               VALUES (?, ?, ?, ?, ?, ?)''',
            (user_id, block_type, position_x, position_y, position_z, int(time.time()))
        )
        await self.commit()
    
    async def remove_block(self, user_id: int, position_x: int, position_y: int, position_z: int):
        await self.execute(
            '''DELETE FROM island_blocks 
               WHERE user_id = ? AND position_x = ? AND position_y = ? AND position_z = ?''',
            (user_id, position_x, position_y, position_z)
        )
        await self.commit()
    
    async def get_blocks(self, user_id: int) -> List[Dict]:
        rows = await self.fetchall(
            'SELECT * FROM island_blocks WHERE user_id = ? ORDER BY placed_at DESC',
            (user_id,)
        )
        return [dict(row) for row in rows]
    
    async def get_available_decorations(self, user_id: int) -> List[Dict]:
        island = await self.get_or_create_island(user_id)
        island_level = island.get('island_level', 1)
        
        rows = await self.fetchall(
            'SELECT * FROM game_island_decorations WHERE required_level <= ? ORDER BY required_level, cost',
            (island_level,)
        )
        return [dict(row) for row in rows]
    
    async def get_available_themes(self, user_id: int) -> List[Dict]:
        island = await self.get_or_create_island(user_id)
        island_level = island.get('island_level', 1)
        
        rows = await self.fetchall(
            'SELECT * FROM game_island_themes WHERE required_level <= ? ORDER BY required_level',
            (island_level,)
        )
        return [dict(row) for row in rows]
    
    async def set_theme(self, user_id: int, theme_id: str) -> bool:
        theme = await self.fetchone(
            'SELECT * FROM game_island_themes WHERE theme_id = ?',
            (theme_id,)
        )
        
        if not theme:
            return False
        
        island = await self.get_or_create_island(user_id)
        
        if island.get('island_level', 1) < theme['required_level']:
            return False
        
        player = await self.fetchone(
            'SELECT coins FROM player_economy WHERE user_id = ?',
            (user_id,)
        )
        
        if not player or player['coins'] < theme['cost']:
            return False
        
        await self.execute(
            'UPDATE player_economy SET coins = coins - ? WHERE user_id = ?',
            (theme['cost'], user_id)
        )
        
        await self.update_island(user_id, theme=theme_id)
        return True
    
    async def get_island_stats(self, user_id: int) -> Dict[str, Any]:
        island = await self.get_or_create_island(user_id)
        
        decoration_count = await self.fetchone(
            'SELECT COUNT(*) as count FROM island_decorations WHERE user_id = ?',
            (user_id,)
        )
        
        block_count = await self.fetchone(
            'SELECT COUNT(*) as count FROM island_blocks WHERE user_id = ?',
            (user_id,)
        )
        
        minion_count = await self.fetchone(
            'SELECT COUNT(*) as count FROM player_minions WHERE user_id = ?',
            (user_id,)
        )
        
        return {
            'island_name': island.get('island_name', 'My Island'),
            'island_level': island.get('island_level', 1),
            'theme': island.get('theme', 'default'),
            'visitors_enabled': island.get('visitors_enabled', 1),
            'decoration_count': decoration_count['count'] if decoration_count else 0,
            'block_count': block_count['count'] if block_count else 0,
            'minion_count': minion_count['count'] if minion_count else 0,
            'upgrade_points': island.get('upgrade_points', 0)
        }
