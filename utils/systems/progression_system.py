class ProgressionSystem:
    
    COMBAT_UNLOCKS = {
        'hub': {'min_level': 0, 'min_coins': 0, 'name': 'Hub', 'difficulty': 1},
        'spiders_den': {'min_level': 3, 'min_coins': 5000, 'name': 'Spider\'s Den', 'difficulty': 2},
        'crimson_isle': {'min_level': 8, 'min_coins': 50000, 'name': 'Crimson Isle', 'difficulty': 3},
        'end': {'min_level': 12, 'min_coins': 150000, 'name': 'The End', 'difficulty': 4},
        'nether': {'min_level': 15, 'min_coins': 500000, 'name': 'Nether', 'difficulty': 5},
        'deep_caverns': {'min_level': 5, 'min_coins': 15000, 'name': 'Deep Caverns', 'difficulty': 2},
    }
    
    SLAYER_UNLOCKS = {
        'revenant': {
            'min_combat_level': 5,
            'min_coins': 2000,
            'tiers': {
                1: {'cost': 2000, 'min_level': 5, 'xp': 5},
                2: {'cost': 7500, 'min_level': 10, 'xp': 25},
                3: {'cost': 20000, 'min_level': 15, 'xp': 100},
                4: {'cost': 50000, 'min_level': 20, 'xp': 500},
                5: {'cost': 100000, 'min_level': 25, 'xp': 1500}
            }
        },
        'tarantula': {
            'min_combat_level': 5,
            'min_coins': 2000,
            'tiers': {
                1: {'cost': 2000, 'min_level': 5, 'xp': 5},
                2: {'cost': 7500, 'min_level': 10, 'xp': 25},
                3: {'cost': 20000, 'min_level': 15, 'xp': 100},
                4: {'cost': 50000, 'min_level': 20, 'xp': 500},
                5: {'cost': 100000, 'min_level': 25, 'xp': 1000}
            }
        },
        'sven': {
            'min_combat_level': 10,
            'min_coins': 2000,
            'tiers': {
                1: {'cost': 2000, 'min_level': 10, 'xp': 10},
                2: {'cost': 7500, 'min_level': 15, 'xp': 30},
                3: {'cost': 20000, 'min_level': 20, 'xp': 120},
                4: {'cost': 50000, 'min_level': 25, 'xp': 600},
                5: {'cost': 100000, 'min_level': 30, 'xp': 1800}
            }
        },
        'voidgloom': {
            'min_combat_level': 15,
            'min_coins': 2000,
            'tiers': {
                1: {'cost': 2000, 'min_level': 15, 'xp': 10},
                2: {'cost': 10000, 'min_level': 20, 'xp': 50},
                3: {'cost': 30000, 'min_level': 25, 'xp': 200},
                4: {'cost': 75000, 'min_level': 30, 'xp': 1000},
                5: {'cost': 150000, 'min_level': 35, 'xp': 2500}
            }
        },
        'inferno': {
            'min_combat_level': 20,
            'min_coins': 2000,
            'tiers': {
                1: {'cost': 2000, 'min_level': 20, 'xp': 10},
                2: {'cost': 10000, 'min_level': 25, 'xp': 50},
                3: {'cost': 30000, 'min_level': 30, 'xp': 250},
                4: {'cost': 75000, 'min_level': 35, 'xp': 1200},
                5: {'cost': 150000, 'min_level': 40, 'xp': 3000}
            }
        }
    }
    
    DUNGEON_UNLOCKS = {
        'entrance': {'min_level': 0, 'min_coins': 0, 'name': 'Entrance'},
        'floor1': {'min_level': 5, 'min_coins': 5000, 'name': 'Floor 1'},
        'floor2': {'min_level': 8, 'min_coins': 15000, 'name': 'Floor 2'},
        'floor3': {'min_level': 10, 'min_coins': 30000, 'name': 'Floor 3'},
        'floor4': {'min_level': 13, 'min_coins': 60000, 'name': 'Floor 4'},
        'floor5': {'min_level': 16, 'min_coins': 120000, 'name': 'Floor 5'},
        'floor6': {'min_level': 19, 'min_coins': 250000, 'name': 'Floor 6'},
        'floor7': {'min_level': 22, 'min_coins': 500000, 'name': 'Floor 7'},
        'm1': {'min_level': 25, 'min_coins': 1000000, 'name': 'Master Mode 1'},
        'm2': {'min_level': 28, 'min_coins': 1500000, 'name': 'Master Mode 2'},
        'm3': {'min_level': 30, 'min_coins': 2500000, 'name': 'Master Mode 3'},
        'm4': {'min_level': 33, 'min_coins': 4000000, 'name': 'Master Mode 4'},
        'm5': {'min_level': 36, 'min_coins': 6000000, 'name': 'Master Mode 5'},
        'm6': {'min_level': 39, 'min_coins': 9000000, 'name': 'Master Mode 6'},
        'm7': {'min_level': 42, 'min_coins': 15000000, 'name': 'Master Mode 7'},
    }
    
    GATHERING_REQUIREMENTS = {
        'mine': {'min_level': 0, 'required_tool': None},
        'farm': {'min_level': 0, 'required_tool': None},
        'fish': {'min_level': 0, 'required_tool': None},
        'forage': {'min_level': 0, 'required_tool': None},
    }
    
    @staticmethod
    def can_access_combat_location(location: str, combat_level: int, coins: int) -> tuple[bool, str]:
        if location not in ProgressionSystem.COMBAT_UNLOCKS:
            return False, "Invalid location"
        
        req = ProgressionSystem.COMBAT_UNLOCKS[location]
        
        if combat_level < req['min_level']:
            return False, f"❌ Requires Combat Level {req['min_level']} (you have {combat_level})"
        
        if coins < req['min_coins']:
            return False, f"❌ Requires {req['min_coins']:,} total coins earned (you have {coins:,})"
        
        return True, "✅ Unlocked"
    
    @staticmethod
    def can_access_slayer(boss: str, tier: int, combat_level: int, slayer_xp: int, coins: int) -> tuple[bool, str]:
        if boss not in ProgressionSystem.SLAYER_UNLOCKS:
            return False, "Invalid slayer boss"
        
        boss_data = ProgressionSystem.SLAYER_UNLOCKS[boss]
        
        if combat_level < boss_data['min_combat_level']:
            return False, f"❌ Requires Combat Level {boss_data['min_combat_level']} (you have {combat_level})"
        
        if tier not in boss_data['tiers']:
            return False, f"Invalid tier {tier}"
        
        tier_data = boss_data['tiers'][tier]
        
        if combat_level < tier_data['min_level']:
            return False, f"❌ Tier {tier} requires Combat Level {tier_data['min_level']} (you have {combat_level})"
        
        if coins < tier_data['cost']:
            return False, f"❌ Costs {tier_data['cost']:,} coins (you have {coins:,})"
        
        return True, "✅ Unlocked"
    
    @staticmethod
    def can_access_dungeon(floor: str, catacombs_level: int, total_earned: int) -> tuple[bool, str]:
        if floor not in ProgressionSystem.DUNGEON_UNLOCKS:
            return False, "Invalid dungeon floor"
        
        req = ProgressionSystem.DUNGEON_UNLOCKS[floor]
        
        if catacombs_level < req['min_level']:
            return False, f"❌ Requires Catacombs Level {req['min_level']} (you have {catacombs_level})"
        
        if total_earned < req['min_coins']:
            return False, f"❌ Requires {req['min_coins']:,} total coins earned (you have {total_earned:,})"
        
        return True, "✅ Unlocked"
    
    @staticmethod
    def get_available_combat_locations(combat_level: int, total_earned: int) -> list:
        available = []
        for location, req in ProgressionSystem.COMBAT_UNLOCKS.items():
            can_access, msg = ProgressionSystem.can_access_combat_location(location, combat_level, total_earned)
            available.append({
                'location': location,
                'name': req['name'],
                'difficulty': req['difficulty'],
                'unlocked': can_access,
                'message': msg,
                'required_level': req['min_level'],
                'required_coins': req['min_coins']
            })
        return sorted(available, key=lambda x: x['difficulty'])
    
    @staticmethod
    def get_available_dungeons(catacombs_level: int, total_earned: int) -> list:
        available = []
        for floor, req in ProgressionSystem.DUNGEON_UNLOCKS.items():
            can_access, msg = ProgressionSystem.can_access_dungeon(floor, catacombs_level, total_earned)
            available.append({
                'floor': floor,
                'name': req['name'],
                'unlocked': can_access,
                'message': msg,
                'required_level': req['min_level'],
                'required_coins': req['min_coins']
            })
        return available
    
    @staticmethod
    def get_slayer_info(boss: str, combat_level: int, slayer_xp: int) -> dict:
        if boss not in ProgressionSystem.SLAYER_UNLOCKS:
            return {}
        
        boss_data = ProgressionSystem.SLAYER_UNLOCKS[boss]
        tiers = []
        
        for tier, tier_data in boss_data['tiers'].items():
            can_access, msg = ProgressionSystem.can_access_slayer(boss, tier, combat_level, slayer_xp, tier_data['cost'])
            tiers.append({
                'tier': tier,
                'unlocked': can_access,
                'cost': tier_data['cost'],
                'xp': tier_data['xp'],
                'required_level': tier_data['min_level'],
                'message': msg
            })
        
        return {
            'boss': boss,
            'min_combat_level': boss_data['min_combat_level'],
            'tiers': tiers
        }
