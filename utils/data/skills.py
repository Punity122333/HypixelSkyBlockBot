SKILL_XP_REQUIREMENTS = {
    0: 0, 1: 50, 2: 125, 3: 200, 4: 300, 5: 500,
    6: 750, 7: 1000, 8: 1500, 9: 2000, 10: 3500,
    11: 5000, 12: 7500, 13: 10000, 14: 15000, 15: 20000,
    16: 30000, 17: 50000, 18: 75000, 19: 100000, 20: 200000,
    21: 300000, 22: 400000, 23: 500000, 24: 600000, 25: 700000,
    26: 800000, 27: 900000, 28: 1000000, 29: 1100000, 30: 1200000,
    31: 1300000, 32: 1400000, 33: 1500000, 34: 1600000, 35: 1700000,
    36: 1800000, 37: 1900000, 38: 2000000, 39: 2100000, 40: 2200000,
    41: 2300000, 42: 2400000, 43: 2500000, 44: 2600000, 45: 2750000,
    46: 2900000, 47: 3100000, 48: 3400000, 49: 3700000, 50: 4000000
}

RUNECRAFTING_XP_REQUIREMENTS = {
    0: 0, 1: 50, 2: 100, 3: 125, 4: 160, 5: 200,
    6: 250, 7: 315, 8: 400, 9: 500, 10: 625,
    11: 785, 12: 1000, 13: 1250, 14: 1600, 15: 2000,
    16: 2465, 17: 3125, 18: 4000, 19: 5000, 20: 6200,
    21: 7800, 22: 9800, 23: 12200, 24: 15300, 25: 19050
}

SOCIAL_XP_REQUIREMENTS = {
    0: 0, 1: 50, 2: 100, 3: 150, 4: 250, 5: 500,
    6: 750, 7: 1000, 8: 1250, 9: 1500, 10: 2000,
    11: 2500, 12: 3000, 13: 3750, 14: 4500, 15: 6000,
    16: 8000, 17: 10000, 18: 12500, 19: 15000, 20: 20000,
    21: 25000, 22: 30000, 23: 35000, 24: 40000, 25: 50000
}

def get_xp_for_level(skill: str, level: int) -> int:
    if skill == 'runecrafting':
        return RUNECRAFTING_XP_REQUIREMENTS.get(level, 0)
    elif skill == 'social':
        return SOCIAL_XP_REQUIREMENTS.get(level, 0)
    else:
        return SKILL_XP_REQUIREMENTS.get(level, 0)

def calculate_level_from_xp(skill: str, xp: int) -> int:
    requirements = SKILL_XP_REQUIREMENTS
    if skill == 'runecrafting':
        requirements = RUNECRAFTING_XP_REQUIREMENTS
    elif skill == 'social':
        requirements = SOCIAL_XP_REQUIREMENTS
    
    level = 0
    for lvl, req_xp in sorted(requirements.items()):
        if xp >= req_xp:
            level = lvl
        else:
            break
    return level

def get_skill_rewards(skill: str, level: int) -> str:
    rewards = {
        'farming': {
            1: '+4 Health',
            5: '+8 Health',
            10: 'Farming Minion Slot I',
            15: 'Farming Islands Access',
            20: 'Enchanted Hopper Recipe',
            25: 'Farming Accessories',
            30: 'Replenish Enchantment',
            35: 'Turbo-Wheat V',
            40: 'Cropie Pet',
            45: 'Turbo-Carrot V',
            50: 'Dedication IV'
        },
        'mining': {
            1: '+1 Defense',
            5: '+2 Defense',
            10: 'Mining Speed Boost I',
            12: 'Diamond Spreading',
            15: 'Dwarven Mines Access',
            20: 'Goblin Armor Recipe',
            25: 'Quick Claw',
            30: 'Crystal Hollows Access',
            35: 'Peak of the Mountain I',
            40: 'Pristine V',
            45: 'Titanium-Infused Drill',
            50: 'Gemstone Chamber'
        },
        'combat': {
            1: '+1 Crit Chance',
            5: '+2 Crit Chance',
            10: 'Revenant Slayer I',
            15: 'Hardened Diamond Armor',
            20: 'Ender Slayer VI',
            25: 'Reaper Mask Recipe',
            30: 'Voidgloom Slayer I',
            35: 'Wither Armor Recipe',
            40: 'Infernal Slayer I',
            45: 'Legion V',
            50: 'Chimera V'
        },
        'foraging': {
            1: '+1 Strength',
            5: '+2 Strength',
            10: 'Foraging Minion Slot I',
            15: 'Tree Capitator Recipe',
            20: 'Oasis Skin',
            25: 'Monkey Pet',
            30: 'Park Access',
            35: 'Treecapitator Enchantment',
            40: 'Efficiency VI',
            45: 'Cultivating X',
            50: 'Lumberjack V'
        },
        'fishing': {
            1: '+1 Health',
            5: '+2 Health',
            10: 'Fishing Minion Slot I',
            15: 'Sponge Rod Recipe',
            20: 'Challenging Rod',
            25: 'Shredder',
            30: 'Shark Scale Armor',
            35: 'Fishing Speed V',
            40: 'Squid Pet',
            45: 'Master Bait',
            50: 'Trophy Hunter V'
        },
        'enchanting': {
            1: '+1 Intelligence',
            5: '+2 Intelligence',
            10: 'Enchantment Table II',
            15: 'Grand Experience Bottle',
            20: 'Anvil Uses +5',
            25: 'Silk Edge',
            30: 'Experience Artifact',
            35: 'Titanic Bottle',
            40: 'Experiments Access',
            45: 'Chimera Enchantment',
            50: 'Power Scroll'
        },
        'alchemy': {
            1: '+1 Intelligence',
            5: '+2 Intelligence',
            10: 'Brewing Stand III',
            15: 'Critical Potion III',
            20: 'God Potion Recipe',
            25: 'Alchemy Wisdom',
            30: 'Vampire Mask',
            35: 'Transfusion',
            40: 'Refined Potion',
            45: 'Splash Potions',
            50: 'Wisp Potion'
        },
        'taming': {
            1: '+1 Pet Luck',
            5: '+2 Pet Luck',
            10: 'Pet Item Storage I',
            15: 'Pet Candy',
            20: 'Legendary Pet Drop',
            25: 'Pet Skin Recipe',
            30: 'Auto Pet Rules',
            35: 'Mythic Pet Drop',
            40: 'Pet Affinity',
            45: 'Legendary Bee',
            50: 'Kat Upgrades'
        },
        'carpentry': {
            1: 'Recipe: Oak Wood Plank',
            5: 'Workbench Efficiency I',
            10: 'Minion Slot Recipe',
            15: 'Custom Builds',
            20: 'Hardwood Recipe',
            25: 'Personal Bank Upgrade',
            30: 'Advanced Builds',
            35: 'Master Carpenter',
            40: 'Quick Craft',
            45: 'Legendary Builds',
            50: 'Ultimate Carpenter'
        },
        'runecrafting': {
            1: 'Unlock Runes',
            5: 'Basic Rune Combination',
            10: 'Rare Rune Crafting',
            15: 'Epic Rune Crafting',
            20: 'Legendary Rune Crafting',
            25: 'Mythic Rune Access'
        },
        'social': {
            1: 'Party Commands',
            5: 'Friend List Expansion I',
            10: 'Co-op Bonus I',
            15: 'Friend List Expansion II',
            20: 'Guild Access',
            25: 'Co-op Bonus II'
        }
    }
    return rewards.get(skill, {}).get(level, 'No rewards')

SKILL_BONUSES = {
    'farming': {
        'stat': 'health',
        'per_level': 4
    },
    'mining': {
        'stat': 'defense',
        'per_level': 1
    },
    'combat': {
        'stat': 'crit_chance',
        'per_level': 1
    },
    'foraging': {
        'stat': 'strength',
        'per_level': 1
    },
    'fishing': {
        'stat': 'health',
        'per_level': 2
    },
    'enchanting': {
        'stat': 'intelligence',
        'per_level': 1
    },
    'alchemy': {
        'stat': 'intelligence',
        'per_level': 1
    },
    'taming': {
        'stat': 'pet_luck',
        'per_level': 1
    },
    'carpentry': {
        'stat': 'none',
        'per_level': 0
    },
    'runecrafting': {
        'stat': 'none',
        'per_level': 0
    },
    'social': {
        'stat': 'none',
        'per_level': 0
    }
}

def get_skill_stat_bonus(skill: str, level: int) -> dict:
    bonus_info = SKILL_BONUSES.get(skill, {'stat': 'none', 'per_level': 0})
    return {
        'stat': bonus_info['stat'],
        'value': level * bonus_info['per_level']
    }

COLLECTION_TIERS = {
    'wheat': [50, 100, 250, 500, 1000, 2500, 5000, 10000, 25000, 50000],
    'carrot': [50, 100, 250, 500, 1000, 2500, 5000, 10000, 25000, 50000],
    'potato': [50, 100, 250, 500, 1000, 2500, 5000, 10000, 25000, 50000],
    'melon': [50, 100, 250, 500, 1000, 2500, 5000, 10000, 25000, 50000],
    'pumpkin': [50, 100, 250, 500, 1000, 2500, 5000, 10000, 25000, 50000],
    'sugar_cane': [50, 100, 250, 500, 1000, 2500, 5000, 10000, 25000, 50000],
    'cobblestone': [50, 100, 250, 1000, 2500, 5000, 10000, 25000, 50000, 100000],
    'coal': [50, 100, 250, 1000, 2500, 5000, 10000, 25000, 50000, 100000],
    'iron': [50, 100, 250, 1000, 2500, 5000, 10000, 25000, 50000, 100000],
    'gold': [50, 100, 250, 1000, 2500, 5000, 10000, 25000, 50000, 100000],
    'diamond': [50, 100, 250, 1000, 2500, 5000, 10000, 25000, 50000, 100000],
    'emerald': [50, 100, 250, 1000, 2500, 5000, 10000, 25000, 50000, 100000],
    'lapis': [50, 100, 250, 1000, 2500, 5000, 10000, 25000, 50000, 100000],
    'redstone': [50, 100, 250, 1000, 2500, 5000, 10000, 25000, 50000, 100000],
    'obsidian': [50, 100, 250, 1000, 2500, 5000, 10000, 25000, 50000, 100000],
    'oak_wood': [50, 100, 250, 1000, 2500, 5000, 10000, 25000, 50000, 100000],
    'jungle_wood': [50, 100, 250, 1000, 2500, 5000, 10000, 25000, 50000, 100000],
    'dark_oak_wood': [50, 100, 250, 1000, 2500, 5000, 10000, 25000, 50000, 100000],
    'rotten_flesh': [50, 100, 250, 1000, 2500, 5000, 10000, 25000, 50000, 100000],
    'bone': [50, 100, 250, 1000, 2500, 5000, 10000, 25000, 50000, 100000],
    'string': [50, 100, 250, 1000, 2500, 5000, 10000, 25000, 50000, 100000],
    'ender_pearl': [50, 100, 250, 1000, 2500, 5000, 10000, 25000, 50000, 100000],
    'raw_fish': [50, 100, 250, 1000, 2500, 5000, 10000, 25000, 50000, 100000],
}

def get_collection_tier(collection: str, amount: int) -> int:
    tiers = COLLECTION_TIERS.get(collection, [])
    tier = 0
    for i, requirement in enumerate(tiers):
        if amount >= requirement:
            tier = i + 1
        else:
            break
    return tier
