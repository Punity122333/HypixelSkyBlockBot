import json
import aiosqlite
from typing import Dict, List, Optional

_db_path = 'skyblock.db'
_cache = {}

async def _get_db():
    conn = await aiosqlite.connect(_db_path)
    conn.row_factory = aiosqlite.Row
    return conn

PET_STATS = {
    'wolf': {
        'COMMON': {'strength': 5, 'crit_damage': 10},
        'UNCOMMON': {'strength': 10, 'crit_damage': 15},
        'RARE': {'strength': 15, 'crit_damage': 25},
        'EPIC': {'strength': 25, 'crit_damage': 35},
        'LEGENDARY': {'strength': 40, 'crit_damage': 50}
    },
    'enderman': {
        'COMMON': {'crit_damage': 5},
        'UNCOMMON': {'crit_damage': 10},
        'RARE': {'crit_damage': 15},
        'EPIC': {'crit_damage': 25, 'intelligence': 10},
        'LEGENDARY': {'crit_damage': 35, 'intelligence': 15}
    },
    'phoenix': {
        'EPIC': {'strength': 20, 'intelligence': 30},
        'LEGENDARY': {'strength': 35, 'intelligence': 50, 'health': 50}
    },
    'dragon': {
        'LEGENDARY': {'strength': 50, 'crit_damage': 50, 'crit_chance': 10, 'health': 100}
    },
    'bee': {
        'COMMON': {'farming_fortune': 5},
        'UNCOMMON': {'farming_fortune': 10},
        'RARE': {'farming_fortune': 20, 'speed': 5},
        'EPIC': {'farming_fortune': 30, 'speed': 10}
    },
    'elephant': {
        'COMMON': {'mining_fortune': 5, 'defense': 5},
        'UNCOMMON': {'mining_fortune': 10, 'defense': 10},
        'RARE': {'mining_fortune': 20, 'defense': 15},
        'EPIC': {'mining_fortune': 30, 'defense': 25, 'health': 25}
    },
    'giraffe': {
        'COMMON': {'foraging_fortune': 5},
        'UNCOMMON': {'foraging_fortune': 10},
        'RARE': {'foraging_fortune': 20, 'health': 10},
        'EPIC': {'foraging_fortune': 30, 'health': 20}
    },
    'dolphin': {
        'COMMON': {'fishing_speed': 5},
        'UNCOMMON': {'fishing_speed': 10},
        'RARE': {'fishing_speed': 15},
        'EPIC': {'fishing_speed': 25, 'sea_creature_chance': 5}
    },
    'rabbit': {
        'COMMON': {'speed': 10},
        'UNCOMMON': {'speed': 20},
        'RARE': {'speed': 30, 'health': 10},
        'EPIC': {'speed': 40, 'health': 20}
    },
    'sheep': {
        'COMMON': {'intelligence': 5},
        'UNCOMMON': {'intelligence': 10, 'ability_damage': 5},
        'RARE': {'intelligence': 15, 'ability_damage': 10},
        'EPIC': {'intelligence': 25, 'ability_damage': 15}
    },
    'pigman': {
        'EPIC': {'strength': 20, 'defense': 10, 'ferocity': 10},
        'LEGENDARY': {'strength': 35, 'defense': 20, 'ferocity': 20}
    },
    'bal': {
        'EPIC': {'mining_speed': 20, 'mining_fortune': 15},
        'LEGENDARY': {'mining_speed': 30, 'mining_fortune': 25}
    },
    'blaze': {
        'RARE': {'strength': 10, 'defense': 5},
        'EPIC': {'strength': 20, 'defense': 10, 'intelligence': 10},
        'LEGENDARY': {'strength': 30, 'defense': 20, 'intelligence': 20}
    },
    'silverfish': {
        'COMMON': {'mining_speed': 5},
        'UNCOMMON': {'mining_speed': 10, 'defense': 5},
        'RARE': {'mining_speed': 15, 'defense': 10}
    },
    'tiger': {
        'LEGENDARY': {'strength': 30, 'ferocity': 25, 'crit_chance': 5}
    },
    'lion': {
        'LEGENDARY': {'strength': 50, 'speed': 25, 'ferocity': 20}
    },
    'monkey': {
        'RARE': {'intelligence': 20, 'speed': 10},
        'EPIC': {'intelligence': 30, 'speed': 15, 'ability_damage': 10}
    },
    'parrot': {
        'EPIC': {'intelligence': 25, 'crit_damage': 15},
        'LEGENDARY': {'intelligence': 40, 'crit_damage': 25}
    },
    'turtle': {
        'RARE': {'defense': 30, 'health': 20},
        'EPIC': {'defense': 50, 'health': 40},
        'LEGENDARY': {'defense': 75, 'health': 60}
    },
    'zombie': {
        'COMMON': {'health': 10, 'strength': 3},
        'UNCOMMON': {'health': 15, 'strength': 5},
        'RARE': {'health': 25, 'strength': 10},
        'EPIC': {'health': 40, 'strength': 15}
    },
    'skeleton': {
        'COMMON': {'crit_chance': 5, 'crit_damage': 5},
        'UNCOMMON': {'crit_chance': 7, 'crit_damage': 10},
        'RARE': {'crit_chance': 10, 'crit_damage': 15},
        'EPIC': {'crit_chance': 15, 'crit_damage': 25}
    }
}


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

EVENTS = [
    {
        'id': 'spooky_festival',
        'name': '🌙 Spooky Festival',
        'description': '+50% Combat XP\nSpecial mob spawns\nIncreased rare drops',
        'duration': 7200,
        'occurs_every': 86400,
        'bonuses': {'combat_xp': 0.5, 'magic_find': 10}
    },
    {
        'id': 'mining_fiesta',
        'name': '⛏️ Mining Fiesta',
        'description': 'Double mining fortune\n+100% mining XP\nRare ore spawns',
        'duration': 10800,
        'occurs_every': 129600,
        'bonuses': {'mining_fortune': 100, 'mining_xp': 1.0}
    },
    {
        'id': 'farming_festival',
        'name': '🌾 Farming Festival',
        'description': 'Double crop yield\n+75% farming XP\nBonus jacob tickets',
        'duration': 14400,
        'occurs_every': 172800,
        'bonuses': {'farming_fortune': 100, 'farming_xp': 0.75}
    },
    {
        'id': 'fishing_tournament',
        'name': '🎣 Fishing Tournament',
        'description': 'Increased sea creature spawn\n+100% fishing XP\nSpecial trophies',
        'duration': 5400,
        'occurs_every': 86400,
        'bonuses': {'sea_creature_chance': 10, 'fishing_xp': 1.0}
    },
    {
        'id': 'bank_interest',
        'name': '💰 Bank Interest Event',
        'description': '+5% extra bank interest\nBonus coins from all sources',
        'duration': 3600,
        'occurs_every': 432000,
        'bonuses': {'bank_interest': 0.05, 'coin_bonus': 0.1}
    },
    {
        'id': 'dragon_spawns',
        'name': '🐉 Dragon Spawns',
        'description': 'Dragons spawn every 15 minutes\nIncreased summoning eye drops',
        'duration': 10800,
        'occurs_every': 259200,
        'bonuses': {'dragon_spawn': True, 'summoning_eye_chance': 0.5}
    }
]

async def get_mining_locations() -> Dict[str, Dict]:
    if 'mining_locations' in _cache:
        return _cache['mining_locations']
    
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
    _cache['mining_locations'] = locations
    return locations

async def get_farming_locations() -> Dict[str, Dict]:
    if 'farming_locations' in _cache:
        return _cache['farming_locations']
    
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
    _cache['farming_locations'] = locations
    return locations

async def get_combat_locations() -> Dict[str, Dict]:
    if 'combat_locations' in _cache:
        return _cache['combat_locations']
    
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
    _cache['combat_locations'] = locations
    return locations

async def get_fishing_locations() -> Dict[str, Dict]:
    if 'fishing_locations' in _cache:
        return _cache['fishing_locations']
    
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
    _cache['fishing_locations'] = locations
    return locations

async def get_foraging_locations() -> Dict[str, Dict]:
    if 'foraging_locations' in _cache:
        return _cache['foraging_locations']
    
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
    _cache['foraging_locations'] = locations
    return locations

QUEST_DATA = {
    'wheat_collector': {
        'name': '🌾 Wheat Collector',
        'description': 'Collect 500 wheat',
        'requirement_type': 'collection',
        'requirement_item': 'Wheat',
        'requirement_amount': 500,
        'reward_coins': 5000,
        'reward_items': []
    },
    'coal_miner': {
        'name': '⚫ Coal Miner',
        'description': 'Mine 200 coal',
        'requirement_type': 'collection',
        'requirement_item': 'Coal',
        'requirement_amount': 200,
        'reward_coins': 3000,
        'reward_items': []
    },
    'monster_hunter': {
        'name': '⚔️ Monster Hunter',
        'description': 'Collect 100 rotten flesh',
        'requirement_type': 'collection',
        'requirement_item': 'Rotten Flesh',
        'requirement_amount': 100,
        'reward_coins': 10000,
        'reward_items': []
    },
    'wood_gatherer': {
        'name': '🌲 Wood Gatherer',
        'description': 'Collect 1000 oak wood',
        'requirement_type': 'collection',
        'requirement_item': 'Oak Wood',
        'requirement_amount': 1000,
        'reward_coins': 7500,
        'reward_items': []
    },
    'iron_enthusiast': {
        'name': '⛏️ Iron Enthusiast',
        'description': 'Collect 250 iron ingots',
        'requirement_type': 'collection',
        'requirement_item': 'Iron Ingot',
        'requirement_amount': 250,
        'reward_coins': 8000,
        'reward_items': []
    },
    'diamond_seeker': {
        'name': '💎 Diamond Seeker',
        'description': 'Collect 50 diamonds',
        'requirement_type': 'collection',
        'requirement_item': 'Diamond',
        'requirement_amount': 50,
        'reward_coins': 25000,
        'reward_items': [('diamond_sword', 1)]
    },
    'fisher_beginner': {
        'name': '🎣 Fisher Beginner',
        'description': 'Catch 100 raw fish',
        'requirement_type': 'collection',
        'requirement_item': 'Raw Fish',
        'requirement_amount': 100,
        'reward_coins': 4000,
        'reward_items': []
    },
    'farmer_expert': {
        'name': '🚜 Farmer Expert',
        'description': 'Collect 2000 wheat',
        'requirement_type': 'collection',
        'requirement_item': 'Wheat',
        'requirement_amount': 2000,
        'reward_coins': 15000,
        'reward_items': [('diamond_hoe', 1)]
    },
    'miner_professional': {
        'name': '⛏️ Miner Professional',
        'description': 'Collect 500 cobblestone',
        'requirement_type': 'collection',
        'requirement_item': 'Cobblestone',
        'requirement_amount': 500,
        'reward_coins': 6000,
        'reward_items': [('stone_pickaxe', 1)]
    },
    'combat_warrior': {
        'name': '⚔️ Combat Warrior',
        'description': 'Collect 200 bones',
        'requirement_type': 'collection',
        'requirement_item': 'Bone',
        'requirement_amount': 200,
        'reward_coins': 12000,
        'reward_items': [('iron_sword', 1)]
    },
    'gold_rusher': {
        'name': '🥇 Gold Rusher',
        'description': 'Collect 100 gold ingots',
        'requirement_type': 'collection',
        'requirement_item': 'Gold Ingot',
        'requirement_amount': 100,
        'reward_coins': 15000,
        'reward_items': []
    },
    'string_collector': {
        'name': '🕸️ String Collector',
        'description': 'Collect 300 string',
        'requirement_type': 'collection',
        'requirement_item': 'String',
        'requirement_amount': 300,
        'reward_coins': 9000,
        'reward_items': []
    }
}

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
