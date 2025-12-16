import json
import aiosqlite
from typing import Optional, Dict

_db_path = 'skyblock.db'
_location_cache = {}

async def _get_db():
    conn = await aiosqlite.connect(_db_path)
    conn.row_factory = aiosqlite.Row
    return conn

async def get_mining_locations() -> Dict[str, Dict]:
    if 'mining' in _location_cache:
        return _location_cache['mining']
    
    conn = await _get_db()
    cursor = await conn.execute('SELECT * FROM mining_locations')
    rows = await cursor.fetchall()
    await conn.close()
    
    locations = {}
    for row in rows:
        locations[row['location_id']] = {
            'name': row['name'],
            'drops': json.loads(row['drops']),
            'xp_range': (row['xp_min'], row['xp_max'])
        }
    _location_cache['mining'] = locations
    return locations

async def get_farming_locations() -> Dict[str, Dict]:
    if 'farming' in _location_cache:
        return _location_cache['farming']
    
    conn = await _get_db()
    cursor = await conn.execute('SELECT * FROM farming_locations')
    rows = await cursor.fetchall()
    await conn.close()
    
    locations = {}
    for row in rows:
        locations[row['location_id']] = {
            'name': row['name'],
            'crops': json.loads(row['crops']),
            'xp_range': (row['xp_min'], row['xp_max'])
        }
    _location_cache['farming'] = locations
    return locations

async def get_combat_locations() -> Dict[str, Dict]:
    if 'combat' in _location_cache:
        return _location_cache['combat']
    
    conn = await _get_db()
    cursor = await conn.execute('SELECT * FROM combat_locations')
    rows = await cursor.fetchall()
    await conn.close()
    
    locations = {}
    for row in rows:
        locations[row['location_id']] = {
            'name': row['name'],
            'mobs': json.loads(row['mobs']),
            'xp_range': (row['xp_min'], row['xp_max'])
        }
    _location_cache['combat'] = locations
    return locations

async def get_fishing_locations() -> Dict[str, Dict]:
    if 'fishing' in _location_cache:
        return _location_cache['fishing']
    
    conn = await _get_db()
    cursor = await conn.execute('SELECT * FROM fishing_locations')
    rows = await cursor.fetchall()
    await conn.close()
    
    locations = {}
    for row in rows:
        locations[row['location_id']] = {
            'name': row['name'],
            'catches': json.loads(row['catches']),
            'xp_range': (row['xp_min'], row['xp_max'])
        }
    _location_cache['fishing'] = locations
    return locations

async def get_foraging_locations() -> Dict[str, Dict]:
    if 'foraging' in _location_cache:
        return _location_cache['foraging']
    
    conn = await _get_db()
    cursor = await conn.execute('SELECT * FROM foraging_locations')
    rows = await cursor.fetchall()
    await conn.close()
    
    locations = {}
    for row in rows:
        locations[row['location_id']] = {
            'name': row['name'],
            'trees': json.loads(row['trees']),
            'xp_range': (row['xp_min'], row['xp_max'])
        }
    _location_cache['foraging'] = locations
    return locations

async def get_location_data(location_type: str, location_name: str) -> Optional[Dict]:
    if location_type == 'mining':
        locations = await get_mining_locations()
    elif location_type == 'farming':
        locations = await get_farming_locations()
    elif location_type == 'combat':
        locations = await get_combat_locations()
    elif location_type == 'fishing':
        locations = await get_fishing_locations()
    elif location_type == 'foraging':
        locations = await get_foraging_locations()
    else:
        return None
    
    return locations.get(location_name)
