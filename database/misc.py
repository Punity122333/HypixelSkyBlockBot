import json
import aiosqlite
from typing import Dict

_db_path = 'skyblock.db'
_cache = {}

async def _get_db():
    conn = await aiosqlite.connect(_db_path)
    conn.row_factory = aiosqlite.Row
    return conn

async def get_pet_stats() -> Dict:
    if 'pet_stats' in _cache:
        return _cache['pet_stats']
    
    conn = await _get_db()
    cursor = await conn.execute('SELECT pet_type, rarity, stats FROM game_pets')
    rows = await cursor.fetchall()
    await conn.close()
    
    pet_stats_dict = {}
    for row in rows:
        pet_type = row['pet_type']
        rarity = row['rarity']
        stats = json.loads(row['stats']) if row['stats'] else {}
        if pet_type not in pet_stats_dict:
            pet_stats_dict[pet_type] = {}
        pet_stats_dict[pet_type][rarity] = stats
    
    _cache['pet_stats'] = pet_stats_dict
    return pet_stats_dict

async def get_minion_data() -> Dict[str, Dict]:
    if 'minion_data' in _cache:
        return _cache['minion_data']
    
    conn = await _get_db()
    cursor = await conn.execute('SELECT * FROM game_minions')
    rows = await cursor.fetchall()
    await conn.close()
    
    minions = {}
    for row in rows:
        minions[row['minion_type']] = {
            'produces': row['produces'],
            'speed': row['base_speed'],
            'max_tier': row['max_tier'],
            'category': row['category']
        }
    _cache['minion_data'] = minions
    return minions
