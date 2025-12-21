async def is_item_bazaar_tradeable(db, item_id: str) -> tuple[bool, str]:
    cursor = await db.conn.execute('''
        SELECT item_type, rarity FROM game_items WHERE item_id = ?
    ''', (item_id,))
    item = await cursor.fetchone()
    
    if not item:
        return False, "Item not found"
    
    item_type = item['item_type']
    rarity = item.get('rarity')
    
    non_tradeable_types = {
        'SWORD', 'BOW', 'AXE', 'PICKAXE', 'HOE', 'DRILL', 'FISHING_ROD',
        'HELMET', 'CHESTPLATE', 'LEGGINGS', 'BOOTS',
        'PET', 'PET_ITEM', 'MINION', 'RUNE', 'SKIN', 'POTION'
    }
    
    if item_type in non_tradeable_types:
        return False, f"Cannot trade {item_type.lower().replace('_', ' ')}s on the bazaar"
    
    non_tradeable_rarities = {'SPECIAL', 'DIVINE', 'MYTHIC'}
    if rarity in non_tradeable_rarities:
        return False, f"Cannot trade {rarity} items on the bazaar"
    
    special_items = {
        'dragon_egg', 'nether_star', 'dragon_scale', 'dragon_claw',
        'wither_blood', 'dark_orb', 'master_skull', 'necromancer_brooch',
        'wither_essence', 'diamond_essence', 'gold_essence', 'ice_essence'
    }
    
    for special in special_items:
        if special in item_id:
            return False, "Cannot trade special/rare items on the bazaar"
    
    return True, "OK"
