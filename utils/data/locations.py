MINING_LOCATIONS = {
    'coal_mine': {
        'name': 'Coal Mine',
        'drops': ['coal', 'cobblestone'],
        'xp_range': (5, 15)
    },
    'gold_mine': {
        'name': 'Gold Mine',
        'drops': ['gold_ore', 'cobblestone'],
        'xp_range': (10, 25)
    },
    'diamond_reserve': {
        'name': 'Diamond Reserve',
        'drops': ['diamond', 'gold_ore', 'iron_ore'],
        'xp_range': (25, 50)
    },
    'obsidian_sanctuary': {
        'name': 'Obsidian Sanctuary',
        'drops': ['obsidian', 'diamond'],
        'xp_range': (40, 80)
    },
    'dwarven_mines': {
        'name': 'Dwarven Mines',
        'drops': ['mithril', 'titanium', 'diamond'],
        'xp_range': (50, 100)
    },
    'crystal_hollows': {
        'name': 'Crystal Hollows',
        'drops': ['gemstone', 'mithril', 'diamond'],
        'xp_range': (75, 150)
    }
}

FARMING_LOCATIONS = {
    'barn': {
        'name': 'The Barn',
        'crops': ['wheat', 'carrot', 'potato'],
        'xp_range': (5, 20)
    },
    'mushroom_desert': {
        'name': 'Mushroom Desert',
        'crops': ['mushroom', 'cactus'],
        'xp_range': (10, 30)
    },
    'garden': {
        'name': 'The Garden',
        'crops': ['wheat', 'carrot', 'potato', 'pumpkin', 'melon'],
        'xp_range': (15, 40)
    }
}

COMBAT_LOCATIONS = {
    'spiders_den': {
        'name': "Spider's Den",
        'mobs': ['spider', 'cave_spider', 'broodfather'],
        'xp_range': (10, 30)
    },
    'end': {
        'name': 'The End',
        'mobs': ['enderman', 'zealot', 'dragon'],
        'xp_range': (25, 60)
    },
    'crimson_isle': {
        'name': 'Crimson Isle',
        'mobs': ['blaze', 'magma_cube', 'wither_skeleton'],
        'xp_range': (30, 75)
    },
    'deep_caverns': {
        'name': 'Deep Caverns',
        'mobs': ['zombie', 'skeleton', 'creeper'],
        'xp_range': (5, 20)
    }
}

FISHING_LOCATIONS = {
    'pond': {
        'name': 'Pond',
        'catches': ['raw_fish', 'lily_pad'],
        'xp_range': (5, 15)
    },
    'barn_fishing': {
        'name': 'Barn Fishing',
        'catches': ['raw_fish', 'sponge'],
        'xp_range': (10, 25)
    },
    'mushroom_desert_fishing': {
        'name': 'Mushroom Desert Fishing',
        'catches': ['pufferfish', 'clownfish'],
        'xp_range': (15, 35)
    },
    'spider_den_fishing': {
        'name': "Spider's Den Fishing",
        'catches': ['raw_fish', 'string'],
        'xp_range': (20, 45)
    },
    'crimson_isle_fishing': {
        'name': 'Crimson Isle Fishing',
        'catches': ['magmafish', 'sulfur'],
        'xp_range': (30, 70)
    }
}

FORAGING_LOCATIONS = {
    'park': {
        'name': 'The Park',
        'trees': ['oak', 'birch'],
        'xp_range': (5, 15)
    },
    'floating_islands': {
        'name': 'Floating Islands',
        'trees': ['spruce', 'dark_oak'],
        'xp_range': (10, 25)
    },
    'jungle': {
        'name': 'Jungle',
        'trees': ['jungle', 'acacia'],
        'xp_range': (15, 35)
    }
}

def get_location_data(location_type: str, location_name: str):
    locations = {
        'mining': MINING_LOCATIONS,
        'farming': FARMING_LOCATIONS,
        'combat': COMBAT_LOCATIONS,
        'fishing': FISHING_LOCATIONS,
        'foraging': FORAGING_LOCATIONS
    }
    return locations.get(location_type, {}).get(location_name)
