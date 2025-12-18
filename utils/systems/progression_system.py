class ProgressionSystem:
    
    COMBAT_UNLOCKS = {}
    SLAYER_UNLOCKS = {}
    DUNGEON_UNLOCKS = {}
    GATHERING_REQUIREMENTS = {}
    
    @classmethod
    async def _load_constants(cls, db):
        cls.COMBAT_UNLOCKS = await db.game_constants.get_combat_location_unlocks()
        cls.SLAYER_UNLOCKS = await db.game_constants.get_slayer_unlocks()
        cls.DUNGEON_UNLOCKS = await db.game_constants.get_dungeon_unlocks()
        cls.GATHERING_REQUIREMENTS = await db.game_constants.get_gathering_requirements()
    
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
