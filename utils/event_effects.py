import time
from typing import Optional, Dict, Any

class EventEffects:
    def __init__(self, bot):
        self.bot = bot
    
    async def get_active_events(self):
        import json
        current_time = int(time.time())
        active_events = []
        events = await self.bot.game_data.get_all_game_events()
        for event in events:
            cycle_position = current_time % event['occurs_every']
            if cycle_position < event['duration']:
                time_remaining = event['duration'] - cycle_position
                event_data = dict(event)
                if 'bonuses' in event_data and isinstance(event_data['bonuses'], str):
                    try:
                        event_data['bonuses'] = json.loads(event_data['bonuses'])
                    except:
                        event_data['bonuses'] = {}
                elif 'bonuses' not in event_data:
                    event_data['bonuses'] = {}
                active_events.append({**event_data, 'time_remaining': time_remaining})
        return active_events
    
    async def get_gathering_multiplier(self) -> float:
        multiplier = 1.0
        active_events = await self.get_active_events()
        for event in active_events:
            bonuses = event.get('bonuses', {})
            bonus_types = bonuses.get('bonus_types', [])
            if event.get('bonus_type') == 'gathering' or 'gathering' in bonus_types:
                multiplier += event.get('bonus_amount', bonuses.get('bonus_amount', 0))
        return multiplier
    
    async def get_combat_multiplier(self) -> float:
        multiplier = 1.0
        active_events = await self.get_active_events()
        for event in active_events:
            bonuses = event.get('bonuses', {})
            bonus_types = bonuses.get('bonus_types', [])
            if event.get('bonus_type') == 'combat' or 'combat' in bonus_types:
                multiplier += event.get('bonus_amount', bonuses.get('bonus_amount', 0))
        return multiplier
    
    async def get_bazaar_tax_reduction(self) -> float:
        reduction = 0.0
        active_events = await self.get_active_events()
        for event in active_events:
            bonuses = event.get('bonuses', {})
            bonus_types = bonuses.get('bonus_types', [])
            if event.get('bonus_type') == 'bazaar' or 'bazaar' in bonus_types:
                reduction += event.get('bonus_amount', bonuses.get('bonus_amount', 0))
        return min(reduction, 0.5)
    
    async def get_xp_multiplier(self, skill_type: Optional[str] = None) -> float:
        multiplier = 1.0
        active_events = await self.get_active_events()
        for event in active_events:
            bonuses = event.get('bonuses', {})
            bonus_types = bonuses.get('bonus_types', [])
            
            if skill_type:
                skill_xp_key = f'{skill_type}_xp'
                if skill_xp_key in bonuses:
                    multiplier += bonuses[skill_xp_key]
            
            if event.get('bonus_type') == 'xp' or 'xp' in bonus_types:
                event_bonus_amount = event.get('bonus_amount', bonuses.get('bonus_amount', 0))
                if skill_type:
                    event_specific_skill = event.get('specific_skill', bonuses.get('specific_skill'))
                    if event_specific_skill == skill_type:
                        multiplier += event_bonus_amount
                else:
                    if not event.get('specific_skill') and not bonuses.get('specific_skill'):
                        multiplier += event_bonus_amount
        
        mayor_bonus = await self._get_mayor_xp_bonus(skill_type)
        multiplier += mayor_bonus
        
        return multiplier
    
    async def get_coin_multiplier(self) -> float:
        multiplier = 1.0
        active_events = await self.get_active_events()
        for event in active_events:
            bonuses = event.get('bonuses', {})
            bonus_types = bonuses.get('bonus_types', [])
            if event.get('bonus_type') == 'coins' or 'coins' in bonus_types:
                multiplier += event.get('bonus_amount', bonuses.get('bonus_amount', 0))
        return multiplier
    
    async def get_magic_find_bonus(self) -> int:
        bonus = 0
        active_events = await self.get_active_events()
        for event in active_events:
            bonuses = event.get('bonuses', {})
            bonus_types = bonuses.get('bonus_types', [])
            if event.get('bonus_type') == 'magic_find' or 'magic_find' in bonus_types:
                event_bonus = event.get('bonus_amount', bonuses.get('bonus_amount', 0))
                bonus += int(event_bonus) if event_bonus < 100 else int(event_bonus * 100)
        return bonus
    
    async def get_fortune_bonus(self, skill_type: Optional[str] = None) -> int:
        bonus = 0
        active_events = await self.get_active_events()
        for event in active_events:
            bonuses = event.get('bonuses', {})
            
            if skill_type:
                fortune_key = f'{skill_type}_fortune'
                if fortune_key in bonuses:
                    bonus += int(bonuses[fortune_key])
        
        return bonus
    
    async def get_sea_creature_bonus(self) -> float:
        bonus = 0.0
        active_events = await self.get_active_events()
        for event in active_events:
            bonuses = event.get('bonuses', {})
            if 'sea_creature_chance' in bonuses:
                bonus += bonuses['sea_creature_chance']
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
    
    async def _get_mayor_xp_bonus(self, skill_type: Optional[str] = None) -> float:
        current_time = int(time.time())
        year = (current_time // 86400) // 365
        
        mayors = await self.bot.game_data.get_all_mayors()
        if not mayors:
            return 0.0
        
        current_mayor_data = mayors[year % len(mayors)]
        bonuses = current_mayor_data.get('bonuses', {})
        
        if 'skill_xp_multiplier' in bonuses:
            return bonuses['skill_xp_multiplier']
        
        if skill_type:
            skill_bonus_key = f'{skill_type}_xp'
            if skill_bonus_key in bonuses:
                return bonuses[skill_bonus_key]
        
        return 0.0
