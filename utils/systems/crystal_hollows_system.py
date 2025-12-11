from typing import Dict, Any, List
import random


class CrystalHollowsSystem:
    
    ZONES = {
        'magma_fields': {
            'name': 'Magma Fields',
            'unlock_reputation': 0,
            'resources': ['magma_cream', 'blaze_rod', 'netherrack'],
            'mobs': ['magma_cube', 'blaze']
        },
        'jungle': {
            'name': 'Jungle',
            'unlock_reputation': 50,
            'resources': ['jungle_wood', 'cocoa_beans', 'vines'],
            'mobs': ['ocelot', 'parrot']
        },
        'mithril_deposits': {
            'name': 'Mithril Deposits',
            'unlock_reputation': 100,
            'resources': ['mithril', 'titanium'],
            'mobs': ['yog', 'goblin']
        },
        'precursor_remnants': {
            'name': 'Precursor Remnants',
            'unlock_reputation': 200,
            'resources': ['precursor_gear', 'ancient_parts'],
            'mobs': ['automaton', 'sludge']
        },
        'goblin_holdout': {
            'name': 'Goblin Holdout',
            'unlock_reputation': 150,
            'resources': ['goblin_egg', 'amber'],
            'mobs': ['goblin_brute', 'goblin_mage']
        }
    }
    
    CRYSTALS = [
        'amber', 'amethyst', 'jade', 'sapphire', 'topaz'
    ]
    
    @classmethod
    async def get_crystal_hollows_progress(cls, db, user_id: int) -> Dict[str, Any]:
        if not db.conn:
            return cls._get_default_progress()
        
        progress = await db.crystal_hollows.get_crystal_hollows_progress(user_id)
        if not progress:
            await db.crystal_hollows.initialize_progress(user_id)
            return await cls.get_crystal_hollows_progress(db, user_id)
        
        return progress
    
    @classmethod
    async def initialize_progress(cls, db, user_id: int):
        if not db.conn:
            return
        await db.crystal_hollows.initialize_progress(user_id)
    
    @classmethod
    def _get_default_progress(cls) -> Dict[str, Any]:
        return {
            'nucleus_runs': 0,
            'crystals_found': 0,
            'jungle_unlocked': 0,
            'mithril_deposits_unlocked': 0,
            'precursor_unlocked': 0,
            'magma_fields_unlocked': 1,
            'goblin_holdout_unlocked': 0
        }
    
    @classmethod
    async def unlock_zone(cls, db, user_id: int, zone: str) -> Dict[str, Any]:
        if zone not in cls.ZONES:
            return {'success': False, 'error': 'Invalid zone'}
        
        zone_data = cls.ZONES[zone]
        
        from utils.systems.dwarven_mines_system import DwarvenMinesSystem
        dwarven_progress = await DwarvenMinesSystem.get_dwarven_progress(db, user_id)
        
        if dwarven_progress['reputation'] < zone_data['unlock_reputation']:
            return {
                'success': False,
                'error': f'Need {zone_data["unlock_reputation"]} reputation',
                'current_reputation': dwarven_progress['reputation']
            }
        
        column_map = {
            'jungle': 'jungle_unlocked',
            'mithril_deposits': 'mithril_deposits_unlocked',
            'precursor_remnants': 'precursor_unlocked',
            'magma_fields': 'magma_fields_unlocked',
            'goblin_holdout': 'goblin_holdout_unlocked'
        }
        
        column = column_map.get(zone)
        if column:
            await db.crystal_hollows.unlock_zone(user_id, column)
        
        return {
            'success': True,
            'zone': zone_data['name']
        }
    
    @classmethod
    async def explore_nucleus(cls, db, user_id: int) -> Dict[str, Any]:
        if not db.conn:
            return {'success': False}
        
        from utils.stat_calculator import StatCalculator
        stats = await StatCalculator.calculate_full_stats(db, user_id)
        
        crystal_found = random.random() < 0.15
        crystal_type = random.choice(cls.CRYSTALS) if crystal_found else None
        
        rewards = {
            'coins': random.randint(5000, 15000),
            'mithril_powder': random.randint(200, 500),
            'gemstone_powder': random.randint(100, 300)
        }
        
        if crystal_found:
            await db.crystal_hollows.increment_crystals_found(user_id)
            if crystal_type is not None:
                await db.crystal_hollows.add_crystal_to_inventory(user_id, crystal_type)
        
        await db.crystal_hollows.increment_nucleus_runs(user_id)
        
        from utils.systems.hotm_system import HeartOfTheMountainSystem
        await HeartOfTheMountainSystem.add_powder(db, user_id, 'mithril', rewards['mithril_powder'])
        await HeartOfTheMountainSystem.add_powder(db, user_id, 'gemstone', rewards['gemstone_powder'])
        
        return {
            'success': True,
            'crystal_found': crystal_found,
            'crystal_type': crystal_type,
            'rewards': rewards
        }
    
    @classmethod
    async def get_unlocked_zones(cls, db, user_id: int) -> List[str]:
        progress = await cls.get_crystal_hollows_progress(db, user_id)
        
        unlocked = []
        if progress.get('magma_fields_unlocked'):
            unlocked.append('magma_fields')
        if progress.get('jungle_unlocked'):
            unlocked.append('jungle')
        if progress.get('mithril_deposits_unlocked'):
            unlocked.append('mithril_deposits')
        if progress.get('precursor_unlocked'):
            unlocked.append('precursor_remnants')
        if progress.get('goblin_holdout_unlocked'):
            unlocked.append('goblin_holdout')
        
        return unlocked
