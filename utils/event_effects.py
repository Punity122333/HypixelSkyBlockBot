import time
from typing import Optional, Dict, Any

class EventEffects:
    def __init__(self, bot):
        self.bot = bot
    
    async def get_active_events(self):
        current_time = int(time.time())
        active_events = []
        events = await self.bot.game_data.get_all_game_events()
        for event in events:
            cycle_position = current_time % event['occurs_every']
            if cycle_position < event['duration']:
                time_remaining = event['duration'] - cycle_position
                active_events.append({**event, 'time_remaining': time_remaining})
        return active_events
    
    async def get_gathering_multiplier(self) -> float:
        multiplier = 1.0
        active_events = await self.get_active_events()
        for event in active_events:
            if event.get('bonus_type') == 'gathering' or 'gathering' in event.get('bonus_types', []):
                multiplier += event.get('bonus_amount', 0)
        return multiplier
    
    async def get_combat_multiplier(self) -> float:
        multiplier = 1.0
        active_events = await self.get_active_events()
        for event in active_events:
            if event.get('bonus_type') == 'combat' or 'combat' in event.get('bonus_types', []):
                multiplier += event.get('bonus_amount', 0)
        return multiplier
    
    async def get_bazaar_tax_reduction(self) -> float:
        reduction = 0.0
        active_events = await self.get_active_events()
        for event in active_events:
            if event.get('bonus_type') == 'bazaar' or 'bazaar' in event.get('bonus_types', []):
                reduction += event.get('bonus_amount', 0)
        return min(reduction, 0.5)
    
    async def get_xp_multiplier(self, skill_type: Optional[str] = None) -> float:
        multiplier = 1.0
        active_events = await self.get_active_events()
        for event in active_events:
            if event.get('bonus_type') == 'xp' or 'xp' in event.get('bonus_types', []):
                if skill_type and event.get('specific_skill'):
                    if event['specific_skill'] == skill_type:
                        multiplier += event.get('bonus_amount', 0)
                else:
                    multiplier += event.get('bonus_amount', 0)
        return multiplier
    
    async def get_coin_multiplier(self) -> float:
        multiplier = 1.0
        active_events = await self.get_active_events()
        for event in active_events:
            if event.get('bonus_type') == 'coins' or 'coins' in event.get('bonus_types', []):
                multiplier += event.get('bonus_amount', 0)
        return multiplier
    
    async def get_magic_find_bonus(self) -> int:
        bonus = 0
        active_events = await self.get_active_events()
        for event in active_events:
            if event.get('bonus_type') == 'magic_find' or 'magic_find' in event.get('bonus_types', []):
                bonus += int(event.get('bonus_amount', 0) * 100)
        return bonus
    
    async def apply_all_bonuses(self, base_stats: Dict[str, Any], context: str = 'general') -> Dict[str, Any]:
        stats = base_stats.copy()
        if context == 'gathering':
            mult = await self.get_gathering_multiplier()
            stats['gathering_multiplier'] = mult
        elif context == 'combat':
            mult = await self.get_combat_multiplier()
            stats['combat_multiplier'] = mult
            stats['magic_find'] = stats.get('magic_find', 0) + await self.get_magic_find_bonus()
        
        xp_mult = await self.get_xp_multiplier()
        stats['xp_multiplier'] = xp_mult
        
        coin_mult = await self.get_coin_multiplier()
        stats['coin_multiplier'] = coin_mult
        
        return stats
