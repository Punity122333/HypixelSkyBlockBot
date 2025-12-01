import random
from typing import List, Tuple, Dict

default_loot = {
            'entrance': [
                {'item_id': 'wither_essence', 'drop_chance': 0.3, 'min_amount': 1, 'max_amount': 3},
                {'item_id': 'undead_essence', 'drop_chance': 0.4, 'min_amount': 1, 'max_amount': 5},
            ],
            'floor_1': [
                {'item_id': 'wither_essence', 'drop_chance': 0.4, 'min_amount': 2, 'max_amount': 5},
                {'item_id': 'undead_essence', 'drop_chance': 0.5, 'min_amount': 2, 'max_amount': 8},
                {'item_id': 'bonzo_staff_fragment', 'drop_chance': 0.05, 'min_amount': 1, 'max_amount': 1},
            ],
            'floor_2': [
                {'item_id': 'wither_essence', 'drop_chance': 0.5, 'min_amount': 3, 'max_amount': 8},
                {'item_id': 'undead_essence', 'drop_chance': 0.6, 'min_amount': 3, 'max_amount': 10},
                {'item_id': 'scarf_fragment', 'drop_chance': 0.05, 'min_amount': 1, 'max_amount': 1},
            ],
            'floor_3': [
                {'item_id': 'wither_essence', 'drop_chance': 0.6, 'min_amount': 5, 'max_amount': 12},
                {'item_id': 'undead_essence', 'drop_chance': 0.7, 'min_amount': 5, 'max_amount': 15},
                {'item_id': 'professor_fragment', 'drop_chance': 0.05, 'min_amount': 1, 'max_amount': 1},
            ],
            'floor_4': [
                {'item_id': 'wither_essence', 'drop_chance': 0.7, 'min_amount': 8, 'max_amount': 16},
                {'item_id': 'undead_essence', 'drop_chance': 0.8, 'min_amount': 8, 'max_amount': 20},
                {'item_id': 'spirit_bone', 'drop_chance': 0.08, 'min_amount': 1, 'max_amount': 1},
            ],
            'floor_5': [
                {'item_id': 'wither_essence', 'drop_chance': 0.8, 'min_amount': 10, 'max_amount': 25},
                {'item_id': 'undead_essence', 'drop_chance': 0.9, 'min_amount': 10, 'max_amount': 30},
                {'item_id': 'livid_dagger', 'drop_chance': 0.02, 'min_amount': 1, 'max_amount': 1},
                {'item_id': 'shadow_fury', 'drop_chance': 0.01, 'min_amount': 1, 'max_amount': 1},
            ],
            'floor_6': [
                {'item_id': 'wither_essence', 'drop_chance': 0.9, 'min_amount': 15, 'max_amount': 35},
                {'item_id': 'undead_essence', 'drop_chance': 1.0, 'min_amount': 15, 'max_amount': 40},
                {'item_id': 'giant_sword', 'drop_chance': 0.01, 'min_amount': 1, 'max_amount': 1},
                {'item_id': 'necromancer_lord_armor_piece', 'drop_chance': 0.03, 'min_amount': 1, 'max_amount': 1},
            ],
            'floor_7': [
                {'item_id': 'wither_essence', 'drop_chance': 1.0, 'min_amount': 20, 'max_amount': 50},
                {'item_id': 'undead_essence', 'drop_chance': 1.0, 'min_amount': 20, 'max_amount': 60},
                {'item_id': 'necron_blade', 'drop_chance': 0.005, 'min_amount': 1, 'max_amount': 1},
                {'item_id': 'wither_armor_piece', 'drop_chance': 0.02, 'min_amount': 1, 'max_amount': 1},
            ],
            'm1': [
                {'item_id': 'wither_essence', 'drop_chance': 1.0, 'min_amount': 30, 'max_amount': 60},
                {'item_id': 'master_star', 'drop_chance': 0.1, 'min_amount': 1, 'max_amount': 1},
            ],
            'm2': [
                {'item_id': 'wither_essence', 'drop_chance': 1.0, 'min_amount': 35, 'max_amount': 70},
                {'item_id': 'master_star', 'drop_chance': 0.12, 'min_amount': 1, 'max_amount': 1},
            ],
            'm3': [
                {'item_id': 'wither_essence', 'drop_chance': 1.0, 'min_amount': 40, 'max_amount': 80},
                {'item_id': 'master_star', 'drop_chance': 0.15, 'min_amount': 1, 'max_amount': 1},
            ],
            'm4': [
                {'item_id': 'wither_essence', 'drop_chance': 1.0, 'min_amount': 45, 'max_amount': 90},
                {'item_id': 'master_star', 'drop_chance': 0.18, 'min_amount': 1, 'max_amount': 1},
            ],
            'm5': [
                {'item_id': 'wither_essence', 'drop_chance': 1.0, 'min_amount': 50, 'max_amount': 100},
                {'item_id': 'master_star', 'drop_chance': 0.2, 'min_amount': 1, 'max_amount': 1},
                {'item_id': 'shadow_fury', 'drop_chance': 0.02, 'min_amount': 1, 'max_amount': 1},
            ],
            'm6': [
                {'item_id': 'wither_essence', 'drop_chance': 1.0, 'min_amount': 60, 'max_amount': 120},
                {'item_id': 'master_star', 'drop_chance': 0.25, 'min_amount': 1, 'max_amount': 1},
                {'item_id': 'giant_sword', 'drop_chance': 0.02, 'min_amount': 1, 'max_amount': 1},
            ],
            'm7': [
                {'item_id': 'wither_essence', 'drop_chance': 1.0, 'min_amount': 80, 'max_amount': 150},
                {'item_id': 'master_star', 'drop_chance': 0.3, 'min_amount': 1, 'max_amount': 1},
                {'item_id': 'claymore', 'drop_chance': 0.01, 'min_amount': 1, 'max_amount': 1},
                {'item_id': 'hyperion', 'drop_chance': 0.001, 'min_amount': 1, 'max_amount': 1},
            ],
        }

PET_DROP_TABLE = {
    'zombie': {'pet': 'zombie', 'base_chance': 0.002, 'rarities': ['COMMON', 'UNCOMMON', 'RARE']},
    'skeleton': {'pet': 'skeleton', 'base_chance': 0.002, 'rarities': ['COMMON', 'UNCOMMON', 'RARE']},
    'spider': {'pet': 'spider', 'base_chance': 0.002, 'rarities': ['COMMON', 'UNCOMMON', 'RARE']},
    'enderman': {'pet': 'enderman', 'base_chance': 0.001, 'rarities': ['RARE', 'EPIC', 'LEGENDARY']},
    'blaze': {'pet': 'blaze', 'base_chance': 0.001, 'rarities': ['RARE', 'EPIC', 'LEGENDARY']},
    'magma_cube': {'pet': 'magma_cube', 'base_chance': 0.0015, 'rarities': ['UNCOMMON', 'RARE', 'EPIC']},
    'wolf': {'pet': 'wolf', 'base_chance': 0.003, 'rarities': ['COMMON', 'UNCOMMON', 'RARE', 'EPIC']},
    'wither_skeleton': {'pet': 'wither_skeleton', 'base_chance': 0.0005, 'rarities': ['EPIC', 'LEGENDARY']},
    'pigman': {'pet': 'pigman', 'base_chance': 0.0008, 'rarities': ['EPIC', 'LEGENDARY']},
    'ghast': {'pet': 'ghast', 'base_chance': 0.0008, 'rarities': ['RARE', 'EPIC', 'LEGENDARY']},
    'ender_dragon': {'pet': 'dragon', 'base_chance': 0.0001, 'rarities': ['LEGENDARY']},
    'zealot': {'pet': 'enderman', 'base_chance': 0.005, 'rarities': ['EPIC', 'LEGENDARY']},
    'broodfather': {'pet': 'spider', 'base_chance': 0.01, 'rarities': ['EPIC', 'LEGENDARY']},
    'sven': {'pet': 'wolf', 'base_chance': 0.01, 'rarities': ['LEGENDARY']},
    'revenant': {'pet': 'zombie', 'base_chance': 0.008, 'rarities': ['EPIC', 'LEGENDARY']},
    'necron': {'pet': 'wither_skeleton', 'base_chance': 0.005, 'rarities': ['LEGENDARY']},
    'goldor': {'pet': 'golden_dragon', 'base_chance': 0.003, 'rarities': ['LEGENDARY']},
}

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
    'Lapis Zombie': {
        'common': [('rotten_flesh', 1, 3), ('lapis_lazuli', 1, 2)],
        'uncommon': [('enchanted_rotten_flesh', 1, 1), ('enchanted_lapis_lazuli', 1, 1)],
        'rare': [('zombie_pet', 1, 1)],
        'coins': (15, 65),
        'xp': 22
    },
    'Cave Spider': {
        'common': [('string', 1, 3), ('spider_eye', 1, 2)],
        'uncommon': [('enchanted_string', 1, 1), ('tarantula_web', 1, 1)],
        'rare': [('spider_pet', 1, 1)],
        'coins': (18, 70),
        'xp': 28
    },
    'Spider Jockey': {
        'common': [('string', 2, 4), ('bone', 1, 3), ('arrow', 2, 6)],
        'uncommon': [('enchanted_string', 1, 2), ('enchanted_bone', 1, 1)],
        'rare': [('spider_pet', 1, 1), ('skeleton_pet', 1, 1)],
        'epic': [('aspect_of_the_end', 1, 1)],
        'coins': (25, 100),
        'xp': 45
    },
    'Broodfather': {
        'common': [('string', 3, 8), ('spider_eye', 2, 5)],
        'uncommon': [('enchanted_string', 2, 4), ('tarantula_web', 2, 4)],
        'rare': [('fly_swatter', 1, 1), ('spider_pet', 1, 1)],
        'epic': [('tarantula_helmet', 1, 1), ('scorpion_foil', 1, 1)],
        'legendary': [('digested_mosquito', 1, 1)],
        'coins': (100, 500),
        'xp': 200
    },
    'Magma Cube': {
        'common': [('magma_cream', 1, 3), ('slime_ball', 1, 2)],
        'uncommon': [('enchanted_magma_cream', 1, 1)],
        'rare': [('magma_cube_pet', 1, 1)],
        'coins': (30, 120),
        'xp': 50
    },
    'Wither Skeleton': {
        'common': [('bone', 2, 4), ('coal', 1, 3)],
        'uncommon': [('enchanted_bone', 1, 2), ('wither_skeleton_skull', 1, 1)],
        'rare': [('skeleton_pet', 1, 1)],
        'epic': [('skeleton_master_helmet', 1, 1)],
        'coins': (40, 150),
        'xp': 65
    },
    'Zealot': {
        'common': [('ender_pearl', 2, 4)],
        'uncommon': [('enchanted_ender_pearl', 1, 2)],
        'rare': [('enchanted_eye_of_ender', 1, 1), ('enderman_pet', 1, 1)],
        'epic': [('aspect_of_the_end', 1, 1)],
        'legendary': [('summoning_eye', 1, 1)],
        'coins': (100, 400),
        'xp': 150
    },
    'Ender Dragon': {
        'uncommon': [('dragon_scale', 5, 12), ('enchanted_ender_pearl', 8, 15)],
        'rare': [('dragon_fragment', 10, 25)],
        'epic': [('dragon_helmet', 1, 1), ('dragon_chestplate', 1, 1), ('dragon_leggings', 1, 1), ('dragon_boots', 1, 1)],
        'legendary': [('ender_dragon_pet', 1, 1), ('aspect_of_the_dragons', 1, 1)],
        'mythic': [('dragon_egg', 1, 1)],
        'coins': (1000, 5000),
        'xp': 1000
    },
    'Ghast': {
        'common': [('ghast_tear', 1, 2), ('gunpowder', 1, 3)],
        'uncommon': [('enchanted_ghast_tear', 1, 1)],
        'rare': [('ghast_pet', 1, 1)],
        'coins': (50, 200),
        'xp': 80
    },
    'Piglin Brute': {
        'common': [('gold_ingot', 2, 5), ('pork', 1, 3)],
        'uncommon': [('enchanted_gold', 1, 2), ('enchanted_pork', 1, 1)],
        'rare': [('pigman_pet_item', 1, 1), ('golden_tooth', 1, 1)],
        'coins': (60, 220),
        'xp': 90
    },
    'Wither': {
        'uncommon': [('bone', 10, 20), ('coal', 5, 10)],
        'rare': [('wither_skeleton_skull', 2, 5)],
        'epic': [('enchanted_bone', 3, 8)],
        'legendary': [('nether_star', 1, 1)],
        'mythic': [('wither_pet', 1, 1)],
        'coins': (1500, 10000),
        'xp': 2000
    },
    'Redstone Pigman': {
        'common': [('rotten_flesh', 2, 4), ('redstone', 2, 5)],
        'uncommon': [('enchanted_rotten_flesh', 1, 1), ('enchanted_redstone', 1, 1)],
        'rare': [('zombie_pet', 1, 1)],
        'coins': (25, 90),
        'xp': 35
    },
    'Emerald Slime': {
        'common': [('slime_ball', 2, 5), ('emerald', 1, 2)],
        'uncommon': [('enchanted_slime_ball', 1, 2), ('enchanted_emerald', 1, 1)],
        'rare': [('slime_pet', 1, 1)],
        'coins': (30, 100),
        'xp': 40
    },
    'Sven': {
        'common': [('bone', 5, 10), ('wolf_tooth', 2, 5)],
        'uncommon': [('enchanted_bone', 2, 4), ('hamster_wheel', 1, 2)],
        'rare': [('wolf_pet', 1, 1), ('golden_tooth', 1, 2)],
        'epic': [('overflux_capacitor', 1, 1), ('grizzly_bait', 1, 1)],
        'legendary': [('couture_rune', 1, 1)],
        'coins': (300, 1500),
        'xp': 350
    },
    'Revenant': {
        'common': [('rotten_flesh', 5, 12), ('bone', 3, 8)],
        'uncommon': [('enchanted_rotten_flesh', 2, 5), ('revenant_flesh', 2, 4)],
        'rare': [('beheaded_horror', 1, 2), ('zombie_pet', 1, 1)],
        'epic': [('revenant_catalyst', 1, 1), ('snake_rune', 1, 1)],
        'legendary': [('scythe_blade', 1, 1)],
        'coins': (400, 2000),
        'xp': 400
    },
    'Necron': {
        'uncommon': [('bone', 10, 25), ('enchanted_bone', 3, 8)],
        'rare': [('enchanted_diamond', 5, 15), ('wither_blood', 2, 5)],
        'epic': [('shadow_assassin_helmet', 1, 1), ('shadow_assassin_chestplate', 1, 1)],
        'legendary': [('necron_helmet', 1, 1), ('necron_chestplate', 1, 1), ('necron_leggings', 1, 1), ('necron_boots', 1, 1)],
        'mythic': [('wither_shield', 1, 1), ('necron_blade', 1, 1)],
        'coins': (2000, 10000),
        'xp': 2500
    },
    'Goldor': {
        'uncommon': [('gold_ingot', 15, 30), ('enchanted_gold', 5, 12)],
        'rare': [('enchanted_gold_block', 2, 6), ('titanium', 3, 8)],
        'epic': [('shadow_assassin_leggings', 1, 1), ('shadow_assassin_boots', 1, 1)],
        'legendary': [('goldor_helmet', 1, 1), ('goldor_chestplate', 1, 1), ('goldor_leggings', 1, 1), ('goldor_boots', 1, 1)],
        'mythic': [('golden_sadan_head', 1, 1)],
        'coins': (2500, 12000),
        'xp': 3000
    },
    'Tarantula': {
        'common': [('string', 4, 10), ('spider_eye', 3, 7)],
        'uncommon': [('enchanted_string', 2, 5), ('tarantula_web', 2, 5)],
        'rare': [('toxic_arrow_poison', 1, 3), ('fly_swatter', 1, 1), ('spider_pet', 1, 1)],
        'epic': [('tarantula_helmet', 1, 1), ('digested_mosquito', 1, 1)],
        'legendary': [('fly_swatter_max', 1, 1)],
        'coins': (200, 1000),
        'xp': 250
    },
    'Voidgloom': {
        'common': [('ender_pearl', 5, 12)],
        'uncommon': [('enchanted_ender_pearl', 3, 8), ('null_sphere', 2, 5)],
        'rare': [('enchanted_eye_of_ender', 2, 4), ('void_conqueror_enderman_skin', 1, 2)],
        'epic': [('enderman_pet', 1, 1), ('summoning_eye', 1, 1)],
        'legendary': [('judgement_core', 1, 1), ('endersnake_rune', 1, 1)],
        'coins': (500, 2500),
        'xp': 450
    },
    'Inferno': {
        'common': [('blaze_rod', 4, 10), ('magma_cream', 3, 8)],
        'uncommon': [('enchanted_blaze_rod', 2, 5), ('inferno_fuel', 3, 7)],
        'rare': [('enchanted_magma_cream', 2, 4), ('fire_stone', 1, 2)],
        'epic': [('blaze_pet', 1, 1), ('molten_cube', 1, 1)],
        'legendary': [('infernal_kuudra_key', 1, 1)],
        'coins': (600, 3000),
        'xp': 550
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
