import random
from typing import Dict, List, Optional, Any
from ..stat_calculator import StatCalculator


class GatheringSystem:
    
    GATHERING_CATEGORIES = {}
    
    @classmethod
    async def _load_constants(cls, db):
        cls.GATHERING_CATEGORIES = await db.game_constants.get_gathering_categories()
    
    @classmethod
    async def _get_equipped_tool_stats(cls, db, user_id: int, tool_type: str) -> Dict[str, float]:
        equipped_items = await db.get_equipped_items(user_id)
  
        tool_slot_mapping = {
            'pickaxe': 'pickaxe',
            'axe': 'axe',
            'hoe': 'hoe',
            'fishing_rod': 'fishing_rod',
            'shovel': 'pickaxe' 
        }
        
        slot_name = tool_slot_mapping.get(tool_type, tool_type)
        tool_item = equipped_items.get(slot_name)
        
        if not tool_item or 'item_id' not in tool_item:
            return {}
        
        item_id = tool_item['item_id']
        tool_stats = await db.get_tool_stats(item_id)
        
        if not tool_stats:
            return {}

        return {
            'mining_speed': tool_stats.get('mining_speed', 0),
            'mining_fortune': tool_stats.get('mining_fortune', 0),
            'farming_fortune': tool_stats.get('farming_fortune', 0),
            'foraging_fortune': tool_stats.get('foraging_fortune', 0),
            'fishing_speed': tool_stats.get('fishing_speed', 0),
            'sea_creature_chance': tool_stats.get('sea_creature_chance', 0),
            'breaking_power': tool_stats.get('breaking_power', 0),
            'crop_yield_multiplier': tool_stats.get('crop_yield_multiplier', 1.0),
            'wood_yield_multiplier': tool_stats.get('wood_yield_multiplier', 1.0),
            'ore_yield_multiplier': tool_stats.get('ore_yield_multiplier', 1.0)
        }
    
    @classmethod
    async def gather_resource(cls, db, user_id: int, resource_type: str, tool_type: str, 
                             base_time: float = 1.0, event_bonuses: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if not await cls._has_required_tool(db, user_id, tool_type):
            return {
                'success': False,
                'error': f'Missing required tool: {tool_type}'
            }
        
        stats = await StatCalculator.calculate_full_stats(db, user_id)

        tool_stats = await cls._get_equipped_tool_stats(db, user_id, tool_type)

        if event_bonuses:
            for stat, value in event_bonuses.items():
                if stat in stats:
                    stats[stat] += value
        
        gathering_skill = cls._get_gathering_skill(tool_type)
        
        skills = await db.get_skills(user_id)
        skill_data = next((s for s in skills if s['skill_name'] == gathering_skill), None)
        skill_level = skill_data['level'] if skill_data else 0
        
        skill_yield_multiplier = 1.0 + (skill_level * 0.15)
        skill_speed_multiplier = max(0.5, 1.0 - (skill_level * 0.01))
        
        tool_yield_multiplier = 1.0
        tool_speed_multiplier = 1.0
        
        if gathering_skill == 'mining':

            stats['mining_fortune'] = stats.get('mining_fortune', 0) + tool_stats.get('mining_fortune', 0)
            stats['mining_speed'] = stats.get('mining_speed', 0) + tool_stats.get('mining_speed', 0)
            
            yield_amount = StatCalculator.calculate_mining_yield(stats, 1)
            gather_speed = StatCalculator.calculate_mining_speed(stats, base_time)

            tool_yield_multiplier = tool_stats.get('ore_yield_multiplier', 1.0)
            
        elif gathering_skill == 'farming':

            stats['farming_fortune'] = stats.get('farming_fortune', 0) + tool_stats.get('farming_fortune', 0)
            
            yield_amount = StatCalculator.calculate_farming_yield(stats, 1)
            gather_speed = base_time

            tool_yield_multiplier = tool_stats.get('crop_yield_multiplier', 1.0)
            
        elif gathering_skill == 'foraging':
  
            stats['foraging_fortune'] = stats.get('foraging_fortune', 0) + tool_stats.get('foraging_fortune', 0)
            
            yield_amount = StatCalculator.calculate_foraging_yield(stats, 1)
            gather_speed = base_time
            

            tool_yield_multiplier = tool_stats.get('wood_yield_multiplier', 1.0)
            
        elif gathering_skill == 'fishing':

            stats['fishing_speed'] = stats.get('fishing_speed', 0) + tool_stats.get('fishing_speed', 0)
            stats['sea_creature_chance'] = stats.get('sea_creature_chance', 0) + tool_stats.get('sea_creature_chance', 0)
            
            yield_amount = 1
            gather_speed = StatCalculator.calculate_fishing_speed(stats, base_time)
            
        else:
            yield_amount = 1
            gather_speed = base_time
        

        yield_amount = int(yield_amount * skill_yield_multiplier * tool_yield_multiplier)
        gather_speed = gather_speed * skill_speed_multiplier * tool_speed_multiplier
        
        stats['user_id'] = user_id
        drops = await cls._generate_gathering_drops(db, gathering_skill, resource_type, yield_amount, stats)
        
        xp_gained = cls._calculate_gathering_xp(yield_amount, resource_type)
        
        skill_drop_multiplier = 1.0 + (skill_level * 0.05)
        
        return {
            'success': True,
            'drops': drops,
            'xp': xp_gained,
            'time_taken': gather_speed,
            'skill': gathering_skill,
            'skill_level': skill_level,
            'skill_yield_multiplier': skill_yield_multiplier,
            'skill_drop_multiplier': skill_drop_multiplier,
            'tool_bonuses': {
                'fortune': tool_stats.get(f'{gathering_skill}_fortune', 0),
                'speed': tool_stats.get(f'{gathering_skill}_speed', 0) if gathering_skill in ['mining', 'fishing'] else 0,
                'yield_multiplier': tool_yield_multiplier,
                'breaking_power': tool_stats.get('breaking_power', 0) if gathering_skill == 'mining' else 0
            }
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
        
        user_id = stats.get('user_id', 0)
        skills = await db.get_skills(user_id) if user_id else []
        skill_data = next((s for s in skills if s['skill_name'] == gathering_type), None)
        skill_level = skill_data['level'] if skill_data else 0
        
        skill_drop_multiplier = 1.0 + (skill_level * 0.05)
        
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
        
        drop_multiplier = StatCalculator.calculate_drop_multiplier(stats)
        
        if user_id:
            museum_bonus = await db.museum.calculate_museum_drop_bonus(user_id)
            achievement_luck = await db.achievements.calculate_achievement_luck_bonus(user_id)
            drop_multiplier *= museum_bonus * achievement_luck
        
        for drop_config in drop_configs:
            drop_chance = drop_config['drop_chance'] * drop_multiplier
            
            if random.random() < drop_chance:
                min_amt = drop_config['min_amt']
                max_amt = drop_config['max_amt']
                amount = random.randint(min_amt, max_amt)
                amount = int(amount * skill_drop_multiplier)
                
                drops.append({
                    'item_id': drop_config['item_id'],
                    'amount': amount,
                    'type': 'bonus'
                })
        
        return drops
    
    @classmethod
    def _calculate_gathering_xp(cls, amount: int, resource_type: str) -> int:
        base_xp_map = {
        
            'cobblestone': 10,    
            'coal': 15,          
            'iron_ingot': 20,   
            'gold_ingot': 30,    
            'diamond': 50,       

            'wheat': 15,         
            'carrot': 15,
            'potato': 20,
            'sugar_cane': 25,    
            'pumpkin': 30,
            'melon': 40,

            'oak_wood': 20,    
            'jungle_wood': 30,
            'dark_oak_wood': 40
        }

        
        base_xp = base_xp_map.get(resource_type, 1)
        return base_xp * amount
    
    @classmethod
    async def mine_block(cls, db, user_id: int, block_type: str, event_bonuses: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return await cls.gather_resource(db, user_id, block_type, 'pickaxe', 1.0, event_bonuses)
    
    @classmethod
    async def chop_tree(cls, db, user_id: int, tree_type: str = 'oak_wood', event_bonuses: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return await cls.gather_resource(db, user_id, tree_type, 'axe', 1.5, event_bonuses)
    
    @classmethod
    async def harvest_crop(cls, db, user_id: int, crop_type: str, event_bonuses: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return await cls.gather_resource(db, user_id, crop_type, 'hoe', 0.5, event_bonuses)
    
    @classmethod
    async def fish(cls, db, user_id: int, event_bonuses: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        stats = await StatCalculator.calculate_full_stats(db, user_id)
        
        if event_bonuses:
            for stat, value in event_bonuses.items():
                if stat in stats:
                    stats[stat] += value
        
        skills = await db.get_skills(user_id)
        fishing_skill = next((s for s in skills if s['skill_name'] == 'fishing'), None)
        fishing_level = fishing_skill['level'] if fishing_skill else 0
        
        skill_speed_multiplier = 1.0 + fishing_level * 0.02
        skill_luck_bonus = 1.0 + fishing_level * 0.5
        
        base_time = 20.0
        fishing_time = StatCalculator.calculate_fishing_speed(stats, base_time)
        fishing_time *= skill_speed_multiplier
        
        sea_creature_chance = StatCalculator.calculate_sea_creature_chance(stats)
        sea_creature_chance += skill_luck_bonus
        
        tool_bonuses = {
            'speed': stats.get('fishing_speed', 0),
            'fortune': stats.get('sea_creature_chance', 0)
        }
        
        is_sea_creature = random.random() * 100 < sea_creature_chance
        
        if is_sea_creature:
            catch = await cls._generate_sea_creature(db, stats)
        else:
            catch = await cls._generate_fish_drop(db, stats)
        
        xp_gained = catch.get('xp', 10)
        xp_gained = int(xp_gained * (1.0 + fishing_level * 0.15))
        
        return {
            'success': True,
            'catch': catch,
            'xp': xp_gained,
            'time_taken': fishing_time,
            'is_sea_creature': is_sea_creature,
            'skill': 'fishing',
            'skill_level': fishing_level,
            'skill_speed_multiplier': skill_speed_multiplier,
            'tool_bonuses': tool_bonuses
        }
    
    @classmethod
    async def _generate_fish_drop(cls, db, stats: Dict) -> Dict[str, Any]:
        drop_multiplier = StatCalculator.calculate_drop_multiplier(stats)
        
        rarity_roll = random.random()
        
        if rarity_roll < 0.01 * drop_multiplier:
            rarity = 'legendary'
            item_id = 'clownfish'
            amount = 20
            xp = 500
        elif rarity_roll < 0.05 * drop_multiplier:
            rarity = 'epic'
            item_id = 'raw_fish'
            amount = 15
            xp = 200
        elif rarity_roll < 0.15 * drop_multiplier:
            rarity = 'rare'
            item_id = 'pufferfish'
            amount = 5
            xp = 75
        elif rarity_roll < 0.40:
            rarity = 'uncommon'
            item_id = 'clownfish'
            amount = 3
            xp = 30
        else:
            rarity = 'common'
            item_id = 'raw_fish'
            amount = 1
            xp = 10
        
        return {
            'item_id': item_id,
            'amount': amount,
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
        achievement_bonus = await db.achievements.calculate_achievement_skill_bonus(user_id, skill)
        xp_amount = int(xp_amount * achievement_bonus)
        await db.update_skill(user_id, skill, xp=xp_amount)
    
    @classmethod
    async def get_tool_efficiency(cls, db, user_id: int, tool_type: str) -> float:
        multiplier = await db.get_tool_multiplier(user_id, tool_type)
        return 1.0 + (multiplier / 100)
