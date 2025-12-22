COLLECTION_TIERS = {}
_db_instance = None

async def _load_xp_requirements(db):
    global _db_instance
    _db_instance = db

async def _load_collection_tiers(db):
    global COLLECTION_TIERS
    COLLECTION_TIERS = await db.game_constants.get_collection_tiers()

async def get_xp_for_level(skill: str, level: int) -> int:
    if _db_instance:
        return await _db_instance.game_constants.get_xp_for_level(skill, level)
    return 0

async def calculate_level_from_xp(skill: str, xp: int) -> int:
    if _db_instance:
        return await _db_instance.game_constants.calculate_level_from_xp(skill, xp)
    return 0

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

SKILL_BONUSES = {}

async def _load_skill_bonuses(db):
    global SKILL_BONUSES
    skills = ['farming', 'mining', 'combat', 'foraging', 'fishing', 'enchanting', 'alchemy', 'taming', 'carpentry', 'runecrafting', 'social']
    for skill in skills:
        SKILL_BONUSES[skill] = await db.game_constants.get_skill_bonuses(skill)

def get_skill_stat_bonus(skill: str, level: int) -> dict:
    bonus_info = SKILL_BONUSES.get(skill, {'stat': 'none', 'per_level': 0})
    return {
        'stat': bonus_info['stat'],
        'value': level * bonus_info['per_level']
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
