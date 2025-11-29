import asyncio
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from database import GameDatabase
from utils.data.all_items import ALL_ITEMS
from utils.data.enchants import ENCHANTMENTS, REFORGES
from utils.data.loot_tables import (
    MOB_LOOT_TABLES, FISHING_LOOT_TABLES, MINING_LOOT_TABLES,
    FARMING_LOOT_TABLES, FORAGING_LOOT_TABLES, DUNGEON_LOOT_TABLES
)
from utils.data.skills import SKILL_XP_REQUIREMENTS, RUNECRAFTING_XP_REQUIREMENTS, SOCIAL_XP_REQUIREMENTS
from utils.data.game_constants import PET_STATS, EVENTS, QUEST_DATA

try:
    from cogs.commands.minions import MINION_DATA
except ImportError:
    MINION_DATA = {}

async def migrate_collection_items(db: GameDatabase):
    print("Migrating collection items...")
    
    farming_items = [
        ('wheat', 'Wheat', '🌾'),
        ('carrot', 'Carrot', '🥕'),
        ('potato', 'Potato', '🥔'),
        ('sugar_cane', 'Sugar Cane', '🎋'),
        ('pumpkin', 'Pumpkin', '🎃'),
        ('melon', 'Melon', '🍉')
    ]
    
    mining_items = [
        ('cobblestone', 'Cobblestone', '🪨'),
        ('coal', 'Coal', '⚫'),
        ('iron_ingot', 'Iron Ingot', '⚙️'),
        ('gold_ingot', 'Gold Ingot', '🥇'),
        ('diamond', 'Diamond', '💎')
    ]
    
    combat_items = [
        ('rotten_flesh', 'Rotten Flesh', '🧟'),
        ('bone', 'Bone', '🦴'),
        ('string', 'String', '🕸️'),
        ('spider_eye', 'Spider Eye', '👁️'),
        ('ender_pearl', 'Ender Pearl', '🔮')
    ]
    
    foraging_items = [
        ('oak_wood', 'Oak Wood', '🪵'),
        ('jungle_wood', 'Jungle Wood', '🌴'),
        ('dark_oak_wood', 'Dark Oak Wood', '🪵')
    ]
    
    count = 0
    for item_id, display_name, emoji in farming_items:
        await db.add_collection_items('farming', item_id, display_name, emoji)
        count += 1
    
    for item_id, display_name, emoji in mining_items:
        await db.add_collection_items('mining', item_id, display_name, emoji)
        count += 1
    
    for item_id, display_name, emoji in combat_items:
        await db.add_collection_items('combat', item_id, display_name, emoji)
        count += 1
    
    for item_id, display_name, emoji in foraging_items:
        await db.add_collection_items('foraging', item_id, display_name, emoji)
        count += 1
    
    print(f"Migrated {count} collection items")

async def migrate_mob_locations(db: GameDatabase):
    print("Migrating mob locations...")
    
    mobs_data = {
        'hub': [
            ('zombie', 'Zombie', 50, 5, 50, 10),
            ('skeleton', 'Skeleton', 40, 8, 60, 12),
            ('spider', 'Spider', 35, 6, 55, 11),
            ('lapis_zombie', 'Lapis Zombie', 75, 9, 100, 15),
        ],
        'spiders_den': [
            ('cave_spider', 'Cave Spider', 60, 10, 80, 15),
            ('spider', 'Spider', 50, 9, 70, 13),
            ('spider_jockey', 'Spider Jockey', 150, 25, 150, 25),
            ('broodfather', 'Broodfather', 350, 35, 500, 100),
        ],
        'crimson_isle': [
            ('blaze', 'Blaze', 100, 18, 200, 30),
            ('magma_cube', 'Magma Cube', 90, 15, 180, 28),
            ('wither_skeleton', 'Wither Skeleton', 125, 20, 250, 35),
        ],
        'end': [
            ('enderman', 'Enderman', 150, 23, 300, 40),
            ('zealot', 'Zealot', 400, 40, 600, 80),
            ('ender_dragon', 'Ender Dragon', 7000, 150, 5000, 500),
        ],
        'nether': [
            ('ghast', 'Ghast', 200, 28, 400, 50),
            ('piglin_brute', 'Piglin Brute', 225, 30, 450, 55),
            ('wither', 'Wither', 10000, 180, 10000, 1000),
        ],
        'deep_caverns': [
            ('lapis_zombie', 'Lapis Zombie', 75, 13, 120, 20),
            ('redstone_pigman', 'Redstone Pigman', 90, 14, 150, 22),
            ('emerald_slime', 'Emerald Slime', 150, 15, 180, 25),
        ],
    }
    
    count = 0
    for location_id, mobs in mobs_data.items():
        for mob_id, mob_name, health, damage, coins, xp in mobs:
            await db.add_mob_location(location_id, mob_id, mob_name, health, damage, coins, xp)
            count += 1
    
    print(f"Migrated {count} mob locations")

async def migrate_dungeon_floors(db: GameDatabase):
    print("Migrating dungeon floors...")
    
    floors = [
        ('entrance', 'Entrance', 500, 180),
        ('floor1', 'Floor 1', 1000, 240),
        ('floor2', 'Floor 2', 2000, 300),
        ('floor3', 'Floor 3', 4000, 360),
        ('floor4', 'Floor 4', 8000, 420),
        ('floor5', 'Floor 5', 15000, 480),
        ('floor6', 'Floor 6', 30000, 540),
        ('floor7', 'Floor 7', 60000, 600),
        ('m1', 'Master Mode 1', 100000, 300),
        ('m2', 'Master Mode 2', 150000, 360),
        ('m3', 'Master Mode 3', 250000, 420),
        ('m4', 'Master Mode 4', 400000, 480),
        ('m5', 'Master Mode 5', 600000, 540),
        ('m6', 'Master Mode 6', 900000, 600),
        ('m7', 'Master Mode 7', 1500000, 660),
    ]
    
    count = 0
    for floor_id, name, rewards, time in floors:
        await db.add_dungeon_floor(floor_id, name, rewards, time)
        count += 1
    
    print(f"Migrated {count} dungeon floors")

async def migrate_slayer_bosses(db: GameDatabase):
    print("Migrating slayer bosses...")
    
    slayer_data = {
        'revenant': {
            'name': 'Revenant Horror',
            'emoji': '🧟',
            'tier_data': {
                'tier_1': {'xp': [5], 'cost': [2000]},
                'tier_2': {'xp': [25], 'cost': [7500]},
                'tier_3': {'xp': [100], 'cost': [20000]},
                'tier_4': {'xp': [500], 'cost': [50000]},
                'tier_5': {'xp': [1500], 'cost': [100000]}
            }
        },
        'tarantula': {
            'name': 'Tarantula Broodfather',
            'emoji': '🕷️',
            'tier_data': {
                'tier_1': {'xp': [5], 'cost': [2000]},
                'tier_2': {'xp': [25], 'cost': [7500]},
                'tier_3': {'xp': [100], 'cost': [20000]},
                'tier_4': {'xp': [500], 'cost': [50000]},
                'tier_5': {'xp': [1000], 'cost': [100000]}
            }
        },
        'sven': {
            'name': 'Sven Packmaster',
            'emoji': '🐺',
            'tier_data': {
                'tier_1': {'xp': [10], 'cost': [2000]},
                'tier_2': {'xp': [30], 'cost': [7500]},
                'tier_3': {'xp': [120], 'cost': [20000]},
                'tier_4': {'xp': [600], 'cost': [50000]},
                'tier_5': {'xp': [1800], 'cost': [100000]}
            }
        },
        'voidgloom': {
            'name': 'Voidgloom Seraph',
            'emoji': '👾',
            'tier_data': {
                'tier_1': {'xp': [10], 'cost': [2000]},
                'tier_2': {'xp': [50], 'cost': [10000]},
                'tier_3': {'xp': [200], 'cost': [30000]},
                'tier_4': {'xp': [1000], 'cost': [75000]},
                'tier_5': {'xp': [2500], 'cost': [150000]}
            }
        },
        'inferno': {
            'name': 'Inferno Demonlord',
            'emoji': '🔥',
            'tier_data': {
                'tier_1': {'xp': [10], 'cost': [2000]},
                'tier_2': {'xp': [50], 'cost': [10000]},
                'tier_3': {'xp': [250], 'cost': [30000]},
                'tier_4': {'xp': [1200], 'cost': [75000]},
                'tier_5': {'xp': [3000], 'cost': [150000]}
            }
        }
    }
    
    count = 0
    for boss_id, data in slayer_data.items():
        await db.add_slayer_boss(boss_id, data['name'], data['emoji'], data['tier_data'])
        count += 1
    
    print(f"Migrated {count} slayer bosses")

async def migrate_slayer_drops(db: GameDatabase):
    print("Migrating slayer drops...")
    
    drops_data = {
        'revenant': [
            ('revenant_flesh', 2, 10, 1.0),
            ('revenant_viscera', 1, 3, 0.7),
            ('beheaded_horror', 0, 1, 0.3)
        ],
        'tarantula': [
            ('tarantula_web', 2, 8, 1.0),
            ('toxic_arrow_poison', 1, 4, 0.7),
            ('digested_mosquito', 0, 1, 0.3)
        ],
        'sven': [
            ('wolf_tooth', 2, 8, 1.0),
            ('hamster_wheel', 1, 3, 0.7),
            ('overflux_capacitor', 0, 1, 0.3)
        ],
        'voidgloom': [
            ('null_sphere', 2, 6, 1.0),
            ('void_conqueror_enderman_skin', 1, 2, 0.7),
            ('summoning_eye', 0, 1, 0.3)
        ],
        'inferno': [
            ('inferno_fuel', 3, 10, 1.0),
            ('blaze_rod', 2, 5, 0.8),
            ('fire_stone', 1, 2, 0.5)
        ]
    }
    
    count = 0
    for boss_id, drops in drops_data.items():
        for item_id, min_amt, max_amt, drop_chance in drops:
            await db.add_slayer_drop(boss_id, item_id, min_amt, max_amt, drop_chance)
            count += 1
    
    print(f"Migrated {count} slayer drops")

async def migrate_seasons_mayors(db: GameDatabase):
    print("Migrating seasons and mayors...")
    
    seasons = [
        'Early Spring', 'Spring', 'Late Spring',
        'Early Summer', 'Summer', 'Late Summer',
        'Early Autumn', 'Autumn', 'Late Autumn',
        'Early Winter', 'Winter', 'Late Winter'
    ]
    
    for idx, season in enumerate(seasons):
        await db.add_season(idx, season)
    
    mayors = [
        ('diana', 'Diana', '🏹 +50% Pet XP\n🎯 Better pet drops'),
        ('derpy', 'Derpy', '📚 +50% Skill XP\n💰 +50% Shop prices'),
        ('paul', 'Paul', '💰 -10% Shop prices\n📦 +1 Minion slot'),
        ('jerry', 'Jerry', '🎁 Random perks\n🎲 Mystery bonuses'),
        ('marina', 'Marina', '🎣 +100% Fishing XP\n🐟 Better sea creatures'),
        ('aatrox', 'Aatrox', '⚔️ +100% Slayer XP\n👹 Better slayer drops')
    ]
    
    for mayor_id, name, perks in mayors:
        await db.add_mayor(mayor_id, name, perks)
    
    print(f"Migrated {len(seasons)} seasons and {len(mayors)} mayors")

async def migrate_gathering_drops(db: GameDatabase):
    print("Migrating gathering drops...")
    
    wood_drops = [
        ('foraging', 'wood', 'oak_wood', 1.0, 4, 12),
        ('foraging', 'wood', 'jungle_wood', 1.0, 3, 8),
        ('foraging', 'wood', 'dark_oak_wood', 1.0, 2, 6),
    ]
    
    combat_drops = [
        ('combat', 'mob_drops', 'rotten_flesh', 1.0, 3, 8),
        ('combat', 'mob_drops', 'bone', 1.0, 2, 5),
        ('combat', 'mob_drops', 'string', 1.0, 1, 4),
        ('combat', 'mob_drops', 'spider_eye', 0.8, 1, 3),
        ('combat', 'mob_drops', 'gunpowder', 0.6, 1, 2),
        ('combat', 'mob_drops', 'ender_pearl', 0.3, 1, 1),
    ]
    
    count = 0
    for gathering_type, resource_type, item_id, drop_chance, min_amt, max_amt in wood_drops + combat_drops:
        await db.add_gathering_drop(gathering_type, resource_type, item_id, drop_chance, min_amt, max_amt)
        count += 1
    
    print(f"Migrated {count} gathering drops")

async def migrate_rarity_colors(db: GameDatabase):
    print("Migrating rarity colors...")
    
    colors = {
        'COMMON': '#999999',
        'UNCOMMON': '#55FF55',
        'RARE': '#5555FF',
        'EPIC': '#AA00AA',
        'LEGENDARY': '#FFAA00',
        'MYTHIC': '#FF55FF'
    }
    
    count = 0
    for rarity, color_hex in colors.items():
        await db.add_rarity_color(rarity, color_hex)
        count += 1
    
    print(f"Migrated {count} rarity colors")

async def migrate_tool_tiers(db: GameDatabase):
    print("Migrating tool tiers...")
    
    tool_data = {
        'pickaxe': [
            ('wooden_pickaxe', 'Wooden Pickaxe', 0, {'mining_speed': 0}, {}),
            ('stone_pickaxe', 'Stone Pickaxe', 1, {'mining_speed': 10}, {'cobblestone': 3, 'stick': 2}),
            ('iron_pickaxe', 'Iron Pickaxe', 2, {'mining_speed': 25}, {'iron_ingot': 3, 'stick': 2}),
            ('gold_pickaxe', 'Gold Pickaxe', 3, {'mining_speed': 40}, {'gold_ingot': 3, 'stick': 2}),
            ('diamond_pickaxe', 'Diamond Pickaxe', 4, {'mining_speed': 60}, {'diamond': 3, 'stick': 2}),
        ],
        'axe': [
            ('wooden_axe', 'Wooden Axe', 0, {'foraging_speed': 0}, {}),
            ('stone_axe', 'Stone Axe', 1, {'foraging_speed': 10}, {'cobblestone': 3, 'stick': 2}),
            ('iron_axe', 'Iron Axe', 2, {'foraging_speed': 25}, {'iron_ingot': 3, 'stick': 2}),
            ('diamond_axe', 'Diamond Axe', 3, {'foraging_speed': 50}, {'diamond': 3, 'stick': 2}),
        ],
        'sword': [
            ('wooden_sword', 'Wooden Sword', 0, {'damage': 20}, {}),
            ('stone_sword', 'Stone Sword', 1, {'damage': 30}, {'cobblestone': 2, 'stick': 1}),
            ('iron_sword', 'Iron Sword', 2, {'damage': 40}, {'iron_ingot': 2, 'stick': 1}),
            ('diamond_sword', 'Diamond Sword', 3, {'damage': 60}, {'diamond': 2, 'stick': 1}),
        ],
        'hoe': [
            ('wooden_hoe', 'Wooden Hoe', 0, {'farming_speed': 0}, {'oak_wood': 2, 'stick': 2}),
            ('stone_hoe', 'Stone Hoe', 1, {'farming_speed': 10}, {'cobblestone': 2, 'stick': 2}),
            ('iron_hoe', 'Iron Hoe', 2, {'farming_speed': 25}, {'iron_ingot': 2, 'stick': 2}),
            ('diamond_hoe', 'Diamond Hoe', 3, {'farming_speed': 50}, {'diamond': 2, 'stick': 2}),
        ],
        'fishing_rod': [
            ('wooden_fishing_rod', 'Wooden Fishing Rod', 0, {'fishing_speed': 0}, {'stick': 3, 'string': 2}),
            ('iron_fishing_rod', 'Iron Fishing Rod', 1, {'fishing_speed': 15}, {'iron_ingot': 3, 'string': 2}),
            ('diamond_fishing_rod', 'Diamond Fishing Rod', 2, {'fishing_speed': 35}, {'diamond': 2, 'iron_ingot': 1, 'string': 2}),
        ]
    }
    
    count = 0
    for tool_type, tiers in tool_data.items():
        for item_id, name, tier, stats, recipe in tiers:
            await db.add_tool_tier(tool_type, tier, item_id, name, stats, recipe)
            count += 1
    
    print(f"Migrated {count} tool tiers")

async def migrate_crafting_recipes(db: GameDatabase):
    print("Migrating crafting recipes...")
    
    count = 0
    for item_id, item in ALL_ITEMS.items():
        if item.craft_recipe:
            await db.add_crafting_recipe(item_id, item_id, item.craft_recipe)
            count += 1
    
    print(f"Migrated {count} crafting recipes from ALL_ITEMS")

async def migrate_reforge_items(db: GameDatabase):
    print("Migrating reforge items...")
    
    reforges = {
        'sharp': {'applies_to': ['SWORD'], 'stats': {'crit_chance': 10, 'crit_damage': 20}},
        'deadly': {'applies_to': ['SWORD'], 'stats': {'crit_chance': 5, 'crit_damage': 30}},
        'fierce': {'applies_to': ['SWORD'], 'stats': {'strength': 15, 'crit_chance': 5}},
        'spicy': {'applies_to': ['SWORD'], 'stats': {'strength': 20, 'crit_damage': 25}},
        'legendary': {'applies_to': ['SWORD', 'BOW'], 'stats': {'strength': 15, 'crit_damage': 28, 'intelligence': 7}},
        'pure': {'applies_to': ['ARMOR'], 'stats': {'health': 15, 'defense': 10}},
        'smart': {'applies_to': ['ARMOR'], 'stats': {'intelligence': 30, 'health': 10}},
        'strong': {'applies_to': ['ARMOR'], 'stats': {'strength': 25}},
        'ancient': {'applies_to': ['ARMOR'], 'stats': {'strength': 8, 'crit_damage': 8, 'health': 20}},
        'renowned': {'applies_to': ['ACCESSORY'], 'stats': {'health': 5, 'defense': 5, 'strength': 5}},
    }
    
    count = 0
    for reforge_id, data in reforges.items():
        await db.add_reforge(
            reforge_id=reforge_id,
            name=reforge_id.title(),
            applies_to=data['applies_to'],
            stat_bonuses=data['stats'],
            cost_formula=None
        )
        count += 1
    
    print(f"Migrated {count} reforges")

async def migrate_enchantments(db: GameDatabase):
    print("Migrating enchantments...")
    count = 0
    for enchant_id, enchant_data in ENCHANTMENTS.items():
        stat_bonuses = {}
        if 'stat_bonuses' in enchant_data:
            stat_bonuses = enchant_data['stat_bonuses']
        
        await db.add_enchantment(
            enchant_id=enchant_id,
            name=enchant_data['name'],
            max_level=enchant_data['max_level'],
            applies_to=enchant_data['applies_to'],
            description=enchant_data['description'],
            stat_bonuses=stat_bonuses
        )
        count += 1
    print(f"Migrated {count} enchantments")

async def migrate_reforges(db: GameDatabase):
    print("Migrating reforges...")
    count = 0
    for item_type, reforges in REFORGES.items():
        for reforge_id, stats in reforges.items():
            await db.add_reforge(
                reforge_id=f"{item_type}_{reforge_id}",
                name=reforge_id.replace('_', ' ').title(),
                applies_to=[item_type.upper()],
                stat_bonuses=stats
            )
            count += 1
    print(f"Migrated {count} reforges")

async def migrate_loot_tables(db: GameDatabase):
    print("Migrating loot tables...")
    count = 0
    
    for mob_name, loot_data in MOB_LOOT_TABLES.items():
        coins_min, coins_max = loot_data.get('coins', (0, 0))
        xp = loot_data.get('xp', 0)
        
        loot_dict = {}
        for rarity, items in loot_data.items():
            if rarity in ['common', 'uncommon', 'rare', 'epic', 'legendary', 'mythic']:
                loot_dict[rarity] = items
        
        if loot_dict:
            await db.add_loot_table(
                table_id=mob_name,
                category='mob',
                loot_data=loot_dict,
                coins_min=coins_min,
                coins_max=coins_max,
                xp_reward=xp
            )
            count += 1
    
    for fish_type, loot_data in FISHING_LOOT_TABLES.items():
        loot_dict = {}
        for rarity, items in loot_data.items():
            if rarity in ['common', 'uncommon', 'rare', 'epic', 'legendary', 'mythic']:
                loot_dict[rarity] = items
        
        if loot_dict:
            await db.add_loot_table(
                table_id=fish_type,
                category='fishing',
                loot_data=loot_dict
            )
            count += 1
    
    for ore_type, loot_data in MINING_LOOT_TABLES.items():
        loot_dict = {}
        for rarity, items in loot_data.items():
            if rarity in ['common', 'uncommon', 'rare', 'epic', 'legendary']:
                loot_dict[rarity] = items
        
        if loot_dict:
            await db.add_loot_table(
                table_id=ore_type,
                category='mining',
                loot_data=loot_dict
            )
            count += 1
    
    for crop_type, loot_data in FARMING_LOOT_TABLES.items():
        loot_dict = {}
        for rarity, items in loot_data.items():
            if rarity in ['common', 'uncommon', 'rare', 'epic']:
                loot_dict[rarity] = items
        
        if loot_dict:
            await db.add_loot_table(
                table_id=crop_type,
                category='farming',
                loot_data=loot_dict
            )
            count += 1
    
    for wood_type, loot_data in FORAGING_LOOT_TABLES.items():
        loot_dict = {}
        for rarity, items in loot_data.items():
            if rarity in ['common', 'uncommon', 'rare']:
                loot_dict[rarity] = items
        
        if loot_dict:
            await db.add_loot_table(
                table_id=wood_type,
                category='foraging',
                loot_data=loot_dict
            )
            count += 1
    
    for floor, loot_data in DUNGEON_LOOT_TABLES.items():
        coins_min, coins_max = loot_data.get('coins', (0, 0))
        
        loot_dict = {}
        for rarity, items in loot_data.items():
            if rarity in ['common', 'uncommon', 'rare', 'epic', 'legendary', 'mythic']:
                loot_dict[rarity] = items
        
        if loot_dict:
            await db.add_loot_table(
                table_id=floor,
                category='dungeon',
                loot_data=loot_dict,
                coins_min=coins_min,
                coins_max=coins_max
            )
            count += 1
    
    print(f"Migrated {count} loot table entries")

async def migrate_skills(db: GameDatabase):
    print("Migrating skills...")
    
    skills_data = {
        'farming': {
            'display_name': 'Farming',
            'stat_bonuses': {'health': 4, 'farming_fortune': 4}
        },
        'mining': {
            'display_name': 'Mining',
            'stat_bonuses': {'defense': 1, 'mining_fortune': 4, 'mining_speed': 2}
        },
        'combat': {
            'display_name': 'Combat',
            'stat_bonuses': {'crit_chance': 0.5, 'strength': 4}
        },
        'foraging': {
            'display_name': 'Foraging',
            'stat_bonuses': {'strength': 1, 'foraging_fortune': 4}
        },
        'fishing': {
            'display_name': 'Fishing',
            'stat_bonuses': {'health': 2, 'sea_creature_chance': 0.1, 'fishing_speed': 2}
        },
        'enchanting': {
            'display_name': 'Enchanting',
            'stat_bonuses': {'intelligence': 1, 'ability_damage': 0.5}
        },
        'alchemy': {
            'display_name': 'Alchemy',
            'stat_bonuses': {'intelligence': 1}
        },
        'taming': {
            'display_name': 'Taming',
            'stat_bonuses': {'pet_luck': 1}
        },
        'carpentry': {
            'display_name': 'Carpentry',
            'stat_bonuses': {}
        },
        'runecrafting': {
            'display_name': 'Runecrafting',
            'xp_requirements': RUNECRAFTING_XP_REQUIREMENTS,
            'stat_bonuses': {}
        },
        'social': {
            'display_name': 'Social',
            'xp_requirements': SOCIAL_XP_REQUIREMENTS,
            'stat_bonuses': {}
        }
    }
    
    for skill_name, data in skills_data.items():
        xp_reqs = data.get('xp_requirements', SKILL_XP_REQUIREMENTS)
        await db.add_skill_config(
            skill_name=skill_name,
            display_name=data['display_name'],
            max_level=max(xp_reqs.keys()) if xp_reqs else 50,
            xp_requirements=xp_reqs,
            level_rewards={},
            stat_bonuses=data['stat_bonuses']
        )
    
    print(f"Migrated {len(skills_data)} skills")

async def migrate_pets(db: GameDatabase):
    print("Migrating pets...")
    count = 0
    for pet_type, rarities in PET_STATS.items():
        for rarity, stats in rarities.items():
            pet_id = f"{pet_type}_{rarity.lower()}"
            await db.add_game_pet(
                pet_id=pet_id,
                pet_type=pet_type,
                rarity=rarity,
                stats=stats,
                max_level=100,
                description=f"{rarity} {pet_type.title()} pet"
            )
            count += 1
    print(f"Migrated {count} pet variants")

async def migrate_minions(db: GameDatabase):
    print("Migrating minions...")
    count = 0
    for minion_type, data in MINION_DATA.items():
        await db.add_game_minion(
            minion_type=minion_type,
            produces=data['produces'],
            base_speed=data['speed'],
            max_tier=data.get('max_tier', 11),
            category=data.get('category', 'mining'),
            description=f"Generates {data['produces'].replace('_', ' ')}"
        )
        count += 1
    print(f"Migrated {count} minion types")

async def migrate_events(db: GameDatabase):
    print("Migrating events...")
    count = 0
    for idx, event in enumerate(EVENTS):
        event_id = event['name'].lower().replace(' ', '_').replace('🌙', 'spooky').replace('⛏️', 'mining').replace('🌾', 'farming').replace('🎣', 'fishing').replace('⚔️', 'combat').replace('🔥', 'fire').replace('💎', 'treasure')
        await db.add_game_event(
            event_id=event_id,
            name=event['name'],
            description=event['description'],
            duration=event['duration'],
            occurs_every=event['occurs_every'],
            bonuses={}
        )
        count += 1
    print(f"Migrated {count} events")

async def migrate_quests(db: GameDatabase):
    print("Migrating quests...")
    count = 0
    for quest_id, quest_info in QUEST_DATA.items():
        await db.add_game_quest(
            quest_id=quest_id,
            name=quest_info['name'],
            description=quest_info['description'],
            requirement_type=quest_info['requirement_type'],
            requirement_item=quest_info.get('requirement_item'),
            requirement_amount=quest_info.get('requirement_amount', 0),
            reward_coins=quest_info.get('reward_coins', 0),
            reward_items=quest_info.get('reward_items', [])
        )
        count += 1
    print(f"Migrated {count} quests")

async def migrate_items(db: GameDatabase):
    print("Migrating items...")
    count = 0
    if not db.conn:
        print("Database connection not established!")
        return
    
    for item_id, item in ALL_ITEMS.items():
        try:
            lore_str = '\n'.join(item.lore) if isinstance(item.lore, list) else (item.lore or '')
            
            await db.conn.execute('''
                INSERT OR REPLACE INTO game_items (
                    item_id, name, rarity, item_type, stats, lore, 
                    special_ability, craft_recipe, npc_sell_price, 
                    collection_req, default_bazaar_price
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                item.id,
                item.name,
                item.rarity,
                item.type,
                json.dumps(item.stats) if item.stats else '{}',
                lore_str,
                item.special_ability or '',
                json.dumps(item.craft_recipe) if item.craft_recipe else '{}',
                item.npc_sell_price or 0,
                json.dumps(item.collection_req) if item.collection_req else '{}',
                item.default_bazaar_price or 100
            ))
            count += 1
        except Exception as e:
            print(f"Error migrating item {item_id}: {e}")
    
    await db.conn.commit()
    print(f"Migrated {count} items")

async def update_default_bazaar_prices(db: GameDatabase):
    print("Updating default bazaar prices...")
    
    count = 0
    if db.conn:
        for item_id, item in ALL_ITEMS.items():
            price = item.default_bazaar_price or 100
            try:
                await db.conn.execute('''
                    INSERT OR REPLACE INTO bazaar_products (product_id, buy_price, sell_price, last_update)
                    VALUES (?, ?, ?, ?)
                ''', (item_id, price, price * 0.93, 0))
                count += 1
            except Exception as e:
                print(f"Error updating price for {item_id}: {e}")
        
        await db.conn.commit()
    print(f"Updated {count} items with default bazaar prices")

async def main():
    print("Starting game data migration...")
    db = GameDatabase('skyblock.db')
    await db.initialize()
    
    try:
        await migrate_items(db)
        await migrate_enchantments(db)
        await migrate_reforges(db)
        await migrate_loot_tables(db)
        await migrate_skills(db)
        await migrate_pets(db)
        await migrate_minions(db)
        await migrate_events(db)
        await migrate_quests(db)
        await migrate_collection_items(db)
        await migrate_mob_locations(db)
        await migrate_dungeon_floors(db)
        await migrate_slayer_bosses(db)
        await migrate_slayer_drops(db)
        await migrate_seasons_mayors(db)
        await migrate_gathering_drops(db)
        await migrate_rarity_colors(db)
        await migrate_tool_tiers(db)
        await migrate_crafting_recipes(db)
        await migrate_reforge_items(db)
        await update_default_bazaar_prices(db)
        print("\n✅ Migration completed successfully!")
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await db.close()

if __name__ == "__main__":
    asyncio.run(main())
