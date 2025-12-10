from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class Item:
    id: str
    name: str
    rarity: str
    type: str
    stats: Dict[str, int]
    lore: List[str]
    
RARITIES = ['COMMON', 'UNCOMMON', 'RARE', 'EPIC', 'LEGENDARY', 'MYTHIC', 'DIVINE', 'SPECIAL', 'VERY SPECIAL']

RARITY_COLORS = {
    'COMMON': '⬜',
    'UNCOMMON': '🟩',
    'RARE': '🟦',
    'EPIC': '🟪',
    'LEGENDARY': '🟧',
    'MYTHIC': '🟥',
    'DIVINE': '🌟',
    'SPECIAL': '🔴',
    'VERY SPECIAL': '⭐'
}

ITEMS_DATABASE = {
    'aspect_of_the_end': Item(
        id='aspect_of_the_end',
        name='Aspect of the End',
        rarity='RARE',
        type='SWORD',
        stats={'damage': 100, 'strength': 100},
        lore=['Instantly teleport 8 blocks ahead', 'of where you are looking']
    ),
    'raider_axe': Item(
        id='raider_axe',
        name='Raider Axe',
        rarity='RARE',
        type='AXE',
        stats={'damage': 80, 'strength': 50},
        lore=['Gain +1 damage per 50 wood', 'in your collections']
    ),
    'aspect_of_the_dragons': Item(
        id='aspect_of_the_dragons',
        name='Aspect of the Dragons',
        rarity='LEGENDARY',
        type='SWORD',
        stats={'damage': 225, 'strength': 100},
        lore=['Shoot a fireball dealing 300 damage']
    ),
    'strong_dragon_helmet': Item(
        id='strong_dragon_helmet',
        name='Strong Dragon Helmet',
        rarity='LEGENDARY',
        type='HELMET',
        stats={'health': 130, 'defense': 90, 'strength': 25},
        lore=['Strong Dragon Armor']
    ),
    'strong_dragon_chestplate': Item(
        id='strong_dragon_chestplate',
        name='Strong Dragon Chestplate',
        rarity='LEGENDARY',
        type='CHESTPLATE',
        stats={'health': 200, 'defense': 140, 'strength': 25},
        lore=['Strong Dragon Armor']
    ),
    'strong_dragon_leggings': Item(
        id='strong_dragon_leggings',
        name='Strong Dragon Leggings',
        rarity='LEGENDARY',
        type='LEGGINGS',
        stats={'health': 170, 'defense': 115, 'strength': 25},
        lore=['Strong Dragon Armor']
    ),
    'strong_dragon_boots': Item(
        id='strong_dragon_boots',
        name='Strong Dragon Boots',
        rarity='LEGENDARY',
        type='BOOTS',
        stats={'health': 100, 'defense': 70, 'strength': 25},
        lore=['Strong Dragon Armor']
    ),
    'young_dragon_helmet': Item(
        id='young_dragon_helmet',
        name='Young Dragon Helmet',
        rarity='LEGENDARY',
        type='HELMET',
        stats={'health': 130, 'defense': 90, 'speed': 20},
        lore=['Young Dragon Armor', '+100 Speed']
    ),
    'ender_pearl': Item(
        id='ender_pearl',
        name='Ender Pearl',
        rarity='COMMON',
        type='ITEM',
        stats={},
        lore=['A crafting material']
    ),
    'enchanted_eye_of_ender': Item(
        id='enchanted_eye_of_ender',
        name='Enchanted Eye of Ender',
        rarity='RARE',
        type='ITEM',
        stats={},
        lore=['Used to craft powerful items']
    )
}

def get_item(item_id: str) -> Optional[Item]:
    return ITEMS_DATABASE.get(item_id)

def format_item_display(item: Item, count: int = 1) -> str:
    rarity_emoji = RARITY_COLORS.get(item.rarity, '⬜')
    stats_str = '\n'.join([f'+{value} {stat.title()}' for stat, value in item.stats.items()])
    lore_str = '\n'.join(item.lore) if item.lore else ''
    
    display = f"{rarity_emoji} **{item.name}** {rarity_emoji}\n"
    if count > 1:
        display += f"Amount: {count}\n"
    if stats_str:
        display += f"\n{stats_str}\n"
    if lore_str:
        display += f"\n*{lore_str}*\n"
    display += f"\n{item.rarity} {item.type}"
    
    return display
