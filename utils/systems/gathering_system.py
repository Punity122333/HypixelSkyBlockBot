import random
import json
from typing import Dict, List, Optional, Any
from ..stat_calculator import ComprehensiveStatCalculator


class GatheringSystem:
    
    GATHERING_CATEGORIES = {
        'mining': ['pickaxe'],
        'farming': ['hoe'],
        'foraging': ['axe'],
        'fishing': ['fishing_rod']
    }
    
    @classmethod
    async def gather_resource(cls, db, user_id: int, resource_type: str, tool_type: str, 
                             base_time: float = 1.0) -> Dict[str, Any]:
        if not await cls._has_required_tool(db, user_id, tool_type):
            return {
                'success': False,
                'error': f'Missing required tool: {tool_type}'
            }
        
        stats = await ComprehensiveStatCalculator.calculate_full_stats(db, user_id)
        
        gathering_skill = cls._get_gathering_skill(tool_type)
        
        if gathering_skill == 'mining':
            yield_amount = ComprehensiveStatCalculator.calculate_mining_yield(stats, 1)
            gather_speed = ComprehensiveStatCalculator.calculate_mining_speed(stats, base_time)
        elif gathering_skill == 'farming':
            yield_amount = ComprehensiveStatCalculator.calculate_farming_yield(stats, 1)
            gather_speed = base_time
        elif gathering_skill == 'foraging':
            yield_amount = ComprehensiveStatCalculator.calculate_foraging_yield(stats, 1)
            gather_speed = base_time
        elif gathering_skill == 'fishing':
            yield_amount = 1
            gather_speed = ComprehensiveStatCalculator.calculate_fishing_speed(stats, base_time)
        else:
            yield_amount = 1
            gather_speed = base_time
        
        drops = await cls._generate_gathering_drops(db, gathering_skill, resource_type, yield_amount, stats)
        
        xp_gained = cls._calculate_gathering_xp(yield_amount, resource_type)
        
        return {
            'success': True,
            'drops': drops,
            'xp': xp_gained,
            'time_taken': gather_speed,
            'skill': gathering_skill
        }
    
    @classmethod
    async def _has_required_tool(cls, db, user_id: int, tool_type: str) -> bool:
        return await db.has_tool(user_id, tool_type)
    
    @classmethod
    def _get_gathering_skill(cls, tool_type: str) -> str:
        for skill, tools in cls.GATHERING_CATEGORIES.items():
            if tool_type in tools:
                return skill
        return 'mining'
    
    @classmethod
    async def _generate_gathering_drops(cls, db, gathering_type: str, resource_type: str, 
                                       base_amount: int, stats: Dict) -> List[Dict[str, Any]]:
        drops = []
        
        drops.append({
            'item_id': resource_type,
            'amount': base_amount,
            'type': 'primary'
        })
        
        if not db.conn:
            return drops
        
        cursor = await db.conn.execute('''
            SELECT * FROM gathering_drops WHERE gathering_type = ? AND resource_type = ?
        ''', (gathering_type, resource_type))
        drop_configs = await cursor.fetchall()
        
        drop_multiplier = ComprehensiveStatCalculator.calculate_drop_multiplier(stats)
        
        for drop_config in drop_configs:
            drop_chance = drop_config['drop_chance'] * drop_multiplier
            
            if random.random() < drop_chance:
                min_amt = drop_config['min_amt']
                max_amt = drop_config['max_amt']
                amount = random.randint(min_amt, max_amt)
                
                drops.append({
                    'item_id': drop_config['item_id'],
                    'amount': amount,
                    'type': 'bonus'
                })
        
        return drops
    
    @classmethod
    def _calculate_gathering_xp(cls, amount: int, resource_type: str) -> int:
        base_xp_map = {
            'cobblestone': 2,
            'coal': 5,
            'iron_ingot': 10,
            'gold_ingot': 20,
            'diamond': 50,
            'wheat': 3,
            'carrot': 3,
            'potato': 3,
            'sugar_cane': 4,
            'pumpkin': 5,
            'melon': 5,
            'oak_wood': 5,
            'jungle_wood': 6,
            'dark_oak_wood': 7
        }
        
        base_xp = base_xp_map.get(resource_type, 1)
        return base_xp * amount
    
    @classmethod
    async def mine_block(cls, db, user_id: int, block_type: str) -> Dict[str, Any]:
        return await cls.gather_resource(db, user_id, block_type, 'pickaxe', 1.0)
    
    @classmethod
    async def chop_tree(cls, db, user_id: int, tree_type: str = 'oak_wood') -> Dict[str, Any]:
        return await cls.gather_resource(db, user_id, tree_type, 'axe', 1.5)
    
    @classmethod
    async def harvest_crop(cls, db, user_id: int, crop_type: str) -> Dict[str, Any]:
        return await cls.gather_resource(db, user_id, crop_type, 'hoe', 0.5)
    
    @classmethod
    async def fish(cls, db, user_id: int) -> Dict[str, Any]:
        stats = await ComprehensiveStatCalculator.calculate_full_stats(db, user_id)
        
        base_time = 20.0
        fishing_time = ComprehensiveStatCalculator.calculate_fishing_speed(stats, base_time)
        
        sea_creature_chance = ComprehensiveStatCalculator.calculate_sea_creature_chance(stats)
        
        is_sea_creature = random.random() * 100 < sea_creature_chance
        
        if is_sea_creature:
            catch = await cls._generate_sea_creature(db, stats)
        else:
            catch = await cls._generate_fish_drop(db, stats)
        
        xp_gained = catch.get('xp', 10)
        
        return {
            'success': True,
            'catch': catch,
            'xp': xp_gained,
            'time_taken': fishing_time,
            'is_sea_creature': is_sea_creature,
            'skill': 'fishing'
        }
    
    @classmethod
    async def _generate_fish_drop(cls, db, stats: Dict) -> Dict[str, Any]:
        drop_multiplier = ComprehensiveStatCalculator.calculate_drop_multiplier(stats)
        
        rarity_roll = random.random()
        
        if rarity_roll < 0.01 * drop_multiplier:
            rarity = 'legendary'
            item_id = 'legendary_fish'
            xp = 500
        elif rarity_roll < 0.05 * drop_multiplier:
            rarity = 'epic'
            item_id = 'epic_fish'
            xp = 200
        elif rarity_roll < 0.15 * drop_multiplier:
            rarity = 'rare'
            item_id = 'rare_fish'
            xp = 75
        elif rarity_roll < 0.40:
            rarity = 'uncommon'
            item_id = 'uncommon_fish'
            xp = 30
        else:
            rarity = 'common'
            item_id = 'common_fish'
            xp = 10
        
        return {
            'item_id': item_id,
            'amount': 1,
            'rarity': rarity,
            'xp': xp
        }
    
    @classmethod
    async def _generate_sea_creature(cls, db, stats: Dict) -> Dict[str, Any]:
        creatures = [
            {'id': 'squid', 'health': 50, 'xp': 100, 'coins': 50},
            {'id': 'sea_guardian', 'health': 150, 'xp': 300, 'coins': 200},
            {'id': 'sea_witch', 'health': 500, 'xp': 1000, 'coins': 1000}
        ]
        
        creature = random.choice(creatures)
        
        return {
            'creature_id': creature['id'],
            'health': creature['health'],
            'xp': creature['xp'],
            'coins': creature['coins'],
            'type': 'sea_creature'
        }
    
    @classmethod
    async def apply_gathering_xp(cls, db, user_id: int, skill: str, xp_amount: int):
        await db.update_skill(user_id, skill, xp=xp_amount)
    
    @classmethod
    async def get_tool_efficiency(cls, db, user_id: int, tool_type: str) -> float:
        multiplier = await db.get_tool_multiplier(user_id, tool_type)
        return 1.0 + (multiplier / 100)
