import asyncio
import aiosqlite
import json

async def populate_all_stats(db_path: str):
    conn = await aiosqlite.connect(db_path)
    conn.row_factory = aiosqlite.Row
    
    await populate_armor_stats_from_items(conn)
    await populate_weapon_stats_from_items(conn)
    await populate_tool_stats_from_items(conn)
    
    await conn.close()
    print("All equipment stats populated!")

async def populate_armor_stats_from_items(conn):
    print("Populating armor stats...")
    
    cursor = await conn.execute("SELECT * FROM game_items WHERE item_type IN ('HELMET', 'CHESTPLATE', 'LEGGINGS', 'BOOTS')")
    armor_items = await cursor.fetchall()
    
    for item in armor_items:
        item_id = item['item_id']
        stats = json.loads(item['stats']) if item['stats'] else {}
        
        await conn.execute('''
            INSERT OR REPLACE INTO armor_stats 
            (item_id, defense, health, strength, crit_chance, crit_damage, intelligence, speed, magic_find, pet_luck, true_defense)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            item_id,
            stats.get('defense', 0),
            stats.get('health', 0),
            stats.get('strength', 0),
            stats.get('crit_chance', 0),
            stats.get('crit_damage', 0),
            stats.get('intelligence', 0),
            stats.get('speed', 0),
            stats.get('magic_find', 0),
            stats.get('pet_luck', 0),
            stats.get('true_defense', 0)
        ))
    
    await conn.commit()
    print(f"Populated stats for {len(armor_items)} armor items")

async def populate_weapon_stats_from_items(conn):
    print("Populating weapon stats...")
    
    cursor = await conn.execute("SELECT * FROM game_items WHERE item_type IN ('SWORD', 'BOW')")
    weapon_items = await cursor.fetchall()
    
    for item in weapon_items:
        item_id = item['item_id']
        stats = json.loads(item['stats']) if item['stats'] else {}
        
        await conn.execute('''
            INSERT OR REPLACE INTO weapon_stats 
            (item_id, damage, strength, crit_chance, crit_damage, attack_speed, ability_damage, ferocity, bonus_attack_speed)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            item_id,
            stats.get('damage', 0),
            stats.get('strength', 0),
            stats.get('crit_chance', 0),
            stats.get('crit_damage', 0),
            stats.get('attack_speed', 0),
            stats.get('ability_damage', 0),
            stats.get('ferocity', 0),
            stats.get('bonus_attack_speed', 0)
        ))
    
    await conn.commit()
    print(f"Populated stats for {len(weapon_items)} weapon items")

async def populate_tool_stats_from_items(conn):
    print("Populating tool stats...")
    
    cursor = await conn.execute("SELECT * FROM game_items WHERE item_type IN ('PICKAXE', 'AXE', 'HOE', 'SHOVEL', 'FISHING_ROD')")
    tool_items = await cursor.fetchall()
    
    for item in tool_items:
        item_id = item['item_id']
        item_type = item['item_type']
        stats = json.loads(item['stats']) if item['stats'] else {}
        
        tool_type_map = {
            'PICKAXE': 'pickaxe',
            'AXE': 'axe',
            'HOE': 'hoe',
            'SHOVEL': 'shovel',
            'FISHING_ROD': 'fishing_rod'
        }
        
        await conn.execute('''
            INSERT OR REPLACE INTO tool_stats 
            (item_id, tool_type, damage, breaking_power, mining_speed, mining_fortune, 
             farming_fortune, foraging_fortune, fishing_speed, sea_creature_chance,
             crop_yield_multiplier, wood_yield_multiplier, ore_yield_multiplier, durability)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            item_id,
            tool_type_map.get(item_type, 'unknown'),
            stats.get('damage', 0),
            stats.get('breaking_power', 0),
            stats.get('mining_speed', 0),
            stats.get('mining_fortune', 0),
            stats.get('farming_fortune', 0),
            stats.get('foraging_fortune', 0),
            stats.get('fishing_speed', 0),
            stats.get('sea_creature_chance', 0),
            stats.get('crop_yield_multiplier', 1.0),
            stats.get('wood_yield_multiplier', 1.0),
            stats.get('ore_yield_multiplier', 1.0),
            stats.get('durability', 100)
        ))
    
    await conn.commit()
    print(f"Populated stats for {len(tool_items)} tool items")

if __name__ == '__main__':
    asyncio.run(populate_all_stats('skyblock.db'))
