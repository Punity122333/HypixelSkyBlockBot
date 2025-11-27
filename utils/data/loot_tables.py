import random
from typing import List, Tuple, Dict

MOB_LOOT_TABLES = {
    'Zombie': {
        'common': [('rotten_flesh', 1, 3), ('bone', 0, 2)],
        'uncommon': [('enchanted_rotten_flesh', 1, 1), ('revenant_flesh', 1, 1)],
        'rare': [('zombie_pet', 1, 1), ('beheaded_horror', 1, 1)],
        'epic': [('zombie_sword', 1, 1)],
        'coins': (10, 50),
        'xp': 20
    },
    'Spider': {
        'common': [('string', 1, 3), ('spider_eye', 1, 2)],
        'uncommon': [('enchanted_string', 1, 1), ('tarantula_web', 1, 1)],
        'rare': [('spider_pet', 1, 1), ('fly_swatter', 1, 1)],
        'epic': [('aspect_of_the_end', 1, 1)],
        'coins': (15, 60),
        'xp': 25
    },
    'Skeleton': {
        'common': [('bone', 2, 4), ('arrow', 1, 5)],
        'uncommon': [('enchanted_bone', 1, 1)],
        'rare': [('skeleton_pet', 1, 1)],
        'epic': [('skeleton_master_helmet', 1, 1)],
        'coins': (20, 70),
        'xp': 30
    },
    'Enderman': {
        'common': [('ender_pearl', 1, 2)],
        'uncommon': [('enchanted_ender_pearl', 1, 1)],
        'rare': [('enderman_pet', 1, 1), ('enchanted_eye_of_ender', 1, 1)],
        'epic': [('aspect_of_the_end', 1, 1)],
        'legendary': [('summoning_eye', 1, 1)],
        'coins': (50, 150),
        'xp': 100
    },
    'Blaze': {
        'common': [('blaze_rod', 1, 2)],
        'uncommon': [('magma_cream', 1, 2)],
        'rare': [('blaze_pet', 1, 1)],
        'epic': [('blaze_helmet', 1, 1)],
        'coins': (100, 300),
        'xp': 150
    },
    'Wolf': {
        'common': [('bone', 1, 2)],
        'uncommon': [('wolf_tooth', 1, 2), ('hamster_wheel', 1, 1)],
        'rare': [('wolf_pet', 1, 1)],
        'epic': [('overflux_capacitor', 1, 1)],
        'coins': (80, 200),
        'xp': 120
    },
    'Dragon': {
        'uncommon': [('dragon_scale', 2, 5), ('enchanted_ender_pearl', 3, 8)],
        'rare': [('dragon_fragment', 5, 15)],
        'epic': [('dragon_helmet', 1, 1), ('dragon_chestplate', 1, 1)],
        'legendary': [('ender_dragon_pet', 1, 1), ('aspect_of_the_dragons', 1, 1)],
        'coins': (1000, 5000),
        'xp': 1000
    },
}

FISHING_LOOT_TABLES = {
    'normal': {
        'common': [('raw_fish', 1, 3), ('raw_salmon', 1, 2)],
        'uncommon': [('clownfish', 1, 1), ('pufferfish', 1, 1)],
        'rare': [('sponge', 1, 1), ('lily_pad', 2, 5)],
    },
    'sea_creature': {
        'common': [('squid', 1, 1)],
        'uncommon': [('sea_guardian', 1, 1)],
        'rare': [('sea_witch', 1, 1), ('night_squid', 1, 1)],
        'epic': [('sea_emperor', 1, 1)],
        'legendary': [('great_white_shark', 1, 1)],
    }
}

MINING_LOOT_TABLES = {
    'cobblestone': {
        'common': [('cobblestone', 3, 8)],
        'uncommon': [('enchanted_cobblestone', 1, 2)],
    },
    'coal': {
        'common': [('coal', 2, 5)],
        'uncommon': [('enchanted_coal', 1, 1)],
        'rare': [('enchanted_coal_block', 1, 1)],
    },
    'iron': {
        'common': [('iron_ingot', 1, 3)],
        'uncommon': [('enchanted_iron', 1, 1)],
        'rare': [('enchanted_iron_block', 1, 1)],
    },
    'gold': {
        'common': [('gold_ingot', 1, 2)],
        'uncommon': [('enchanted_gold', 1, 1)],
        'rare': [('enchanted_gold_block', 1, 1)],
    },
    'diamond': {
        'uncommon': [('diamond', 1, 1)],
        'rare': [('enchanted_diamond', 1, 1)],
        'epic': [('enchanted_diamond_block', 1, 1)],
    },
    'emerald': {
        'uncommon': [('emerald', 1, 1)],
        'rare': [('enchanted_emerald', 1, 1)],
    },
    'mithril': {
        'rare': [('mithril_ore', 1, 3)],
        'epic': [('titanium', 1, 1)],
    },
}

FARMING_LOOT_TABLES = {
    'wheat': {
        'common': [('wheat', 5, 15)],
        'uncommon': [('enchanted_bread', 1, 2)],
    },
    'carrot': {
        'common': [('carrot', 5, 15)],
        'uncommon': [('enchanted_carrot', 1, 2)],
        'rare': [('golden_carrot', 1, 1)],
    },
    'potato': {
        'common': [('potato', 5, 15)],
        'uncommon': [('enchanted_potato', 1, 2)],
        'rare': [('enchanted_baked_potato', 1, 1)],
    },
    'sugar_cane': {
        'common': [('sugar_cane', 5, 15)],
        'uncommon': [('enchanted_sugar', 1, 2)],
    },
    'pumpkin': {
        'common': [('pumpkin', 3, 10)],
        'uncommon': [('enchanted_pumpkin', 1, 1)],
    },
    'melon': {
        'common': [('melon', 5, 15)],
        'uncommon': [('enchanted_melon', 1, 2)],
        'rare': [('enchanted_melon_block', 1, 1)],
    },
}

FORAGING_LOOT_TABLES = {
    'oak': {
        'common': [('oak_wood', 3, 8), ('stick', 1, 4)],
        'uncommon': [('enchanted_oak_wood', 1, 1)],
    },
    'jungle': {
        'common': [('jungle_wood', 3, 8)],
        'uncommon': [('enchanted_jungle_wood', 1, 1)],
    },
    'dark_oak': {
        'common': [('dark_oak_wood', 3, 8)],
        'uncommon': [('enchanted_dark_oak_wood', 1, 1)],
    },
}

DUNGEON_LOOT_TABLES = {
    'floor_1': {
        'common': [('bone', 5, 15), ('rotten_flesh', 5, 15)],
        'uncommon': [('enchanted_bone', 1, 3), ('skeleton_master_boots', 1, 1)],
        'rare': [('adaptive_helmet', 1, 1), ('zombie_soldier_helmet', 1, 1)],
        'epic': [('shadow_assassin_helmet', 1, 1)],
        'coins': (100, 500),
        'keys': (0, 2),
    },
    'floor_3': {
        'uncommon': [('skeleton_master_helmet', 1, 1), ('zombie_soldier_chestplate', 1, 1)],
        'rare': [('adaptive_chestplate', 1, 1), ('zombie_knight_helmet', 1, 1)],
        'epic': [('shadow_assassin_chestplate', 1, 1), ('fancy_sword', 1, 1)],
        'legendary': [('necron_helmet', 1, 1)],
        'coins': (500, 2000),
        'keys': (1, 3),
    },
    'floor_5': {
        'rare': [('zombie_lord_helmet', 1, 1), ('shadow_fury', 1, 1)],
        'epic': [('necron_chestplate', 1, 1), ('livid_dagger', 1, 1)],
        'legendary': [('hyperion', 1, 1), ('valkyrie', 1, 1), ('necron_helmet', 1, 1)],
        'coins': (2000, 10000),
        'keys': (2, 5),
    },
    'floor_7': {
        'epic': [('necron_leggings', 1, 1), ('necron_boots', 1, 1)],
        'legendary': [('hyperion', 1, 1), ('astraea', 1, 1), ('scylla', 1, 1), ('valkyrie', 1, 1)],
        'mythic': [('giants_sword', 1, 1), ('terminator', 1, 1)],
        'coins': (10000, 50000),
        'keys': (3, 7),
    },
}

def roll_loot(loot_table: Dict, magic_find: float = 0, fortune: int = 0) -> List[Tuple[str, int]]:
    drops = []
    
    rarity_chances = {
        'common': 1.0,
        'uncommon': 0.25 + (magic_find * 0.01),
        'rare': 0.05 + (magic_find * 0.005),
        'epic': 0.01 + (magic_find * 0.002),
        'legendary': 0.001 + (magic_find * 0.0005),
        'mythic': 0.0001 + (magic_find * 0.0001),
    }
    
    for rarity, chance in rarity_chances.items():
        if rarity in loot_table and random.random() < chance:
            rarity_drops = loot_table[rarity]
            item_id, min_amt, max_amt = random.choice(rarity_drops)
            
            amount = random.randint(min_amt, max_amt)
            fortune_bonus = int((fortune / 100) * amount)
            total_amount = amount + fortune_bonus
            
            if total_amount > 0:
                drops.append((item_id, total_amount))
    
    if not drops and 'common' in loot_table:
        item_id, min_amt, max_amt = random.choice(loot_table['common'])
        amount = random.randint(min_amt, max_amt)
        fortune_bonus = int((fortune / 100) * amount)
        drops.append((item_id, amount + fortune_bonus))
    
    return drops

def get_coins_reward(loot_table: Dict) -> int:
    if 'coins' in loot_table:
        min_coins, max_coins = loot_table['coins']
        return random.randint(min_coins, max_coins)
    return 0

def get_xp_reward(loot_table: Dict) -> int:
    return loot_table.get('xp', 0)

def check_sea_creature_spawn(sea_creature_chance: float) -> bool:
    base_chance = 0.02
    total_chance = base_chance + (sea_creature_chance / 100)
    return random.random() < total_chance
