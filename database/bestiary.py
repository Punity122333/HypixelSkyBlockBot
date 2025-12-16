from typing import Dict, List, Optional, Any, Union
from .core import DatabaseCore


class BestiaryDB(DatabaseCore):

    async def get_player_bestiary(self, user_id: int, mob_id: Optional[str] = None) -> Union[Optional[Dict[str, Any]], List[Dict[str, Any]]]:
        if mob_id:
            row = await self.fetchone(
                'SELECT * FROM player_bestiary WHERE user_id = ? AND mob_id = ?',
                (user_id, mob_id)
            )
            return dict(row) if row else None
        else:
            rows = await self.fetchall(
                'SELECT * FROM player_bestiary WHERE user_id = ? ORDER BY kills DESC',
                (user_id,)
            )
            return [dict(row) for row in rows]
    
    async def add_bestiary_kill(self, user_id: int, mob_id: str) -> Dict[str, Any]:
        import time
        current_time = int(time.time())
        
        existing = await self.fetchone(
            'SELECT * FROM player_bestiary WHERE user_id = ? AND mob_id = ?',
            (user_id, mob_id)
        )
        
        if existing:
            new_kills = existing['kills'] + 1
            await self.execute(
                '''UPDATE player_bestiary 
                   SET kills = ?, last_kill_timestamp = ?
                   WHERE user_id = ? AND mob_id = ?''',
                (new_kills, current_time, user_id, mob_id)
            )
        else:
            await self.execute(
                '''INSERT INTO player_bestiary (user_id, mob_id, kills, deaths, bestiary_level, last_kill_timestamp)
                   VALUES (?, ?, 1, 0, 0, ?)''',
                (user_id, mob_id, current_time)
            )
            new_kills = 1
        
        await self.commit()
        
        level_info = await self.get_bestiary_level_requirements(mob_id)
        new_level = self._calculate_bestiary_level(new_kills, level_info)
        
        old_level = existing['bestiary_level'] if existing else 0
        if new_level > old_level:
            await self.execute(
                'UPDATE player_bestiary SET bestiary_level = ? WHERE user_id = ? AND mob_id = ?',
                (new_level, user_id, mob_id)
            )
            await self.commit()
            
            return {
                'kills': new_kills,
                'old_level': old_level,
                'new_level': new_level,
                'leveled_up': True
            }
        
        return {
            'kills': new_kills,
            'old_level': old_level,
            'new_level': new_level,
            'leveled_up': False
        }
    
    async def add_bestiary_death(self, user_id: int, mob_id: str) -> None:
        existing = await self.fetchone(
            'SELECT * FROM player_bestiary WHERE user_id = ? AND mob_id = ?',
            (user_id, mob_id)
        )
        
        if existing:
            new_deaths = existing['deaths'] + 1
            await self.execute(
                'UPDATE player_bestiary SET deaths = ? WHERE user_id = ? AND mob_id = ?',
                (new_deaths, user_id, mob_id)
            )
        else:
            await self.execute(
                '''INSERT INTO player_bestiary (user_id, mob_id, kills, deaths, bestiary_level)
                   VALUES (?, ?, 0, 1, 0)''',
                (user_id, mob_id)
            )
        
        await self.commit()
    
    async def get_bestiary_level_requirements(self, mob_id: str) -> Optional[Dict[str, Any]]:
        row = await self.fetchone(
            'SELECT * FROM bestiary_levels WHERE mob_id = ?',
            (mob_id,)
        )
        return dict(row) if row else None
    
    async def get_bestiary_rewards(self, mob_id: str, level: int) -> List[Dict[str, Any]]:
        rows = await self.fetchall(
            'SELECT * FROM bestiary_rewards WHERE mob_id = ? AND level = ?',
            (mob_id, level)
        )
        return [dict(row) for row in rows]
    
    async def get_all_bestiary_rewards_for_mob(self, mob_id: str) -> List[Dict[str, Any]]:
        rows = await self.fetchall(
            'SELECT * FROM bestiary_rewards WHERE mob_id = ? ORDER BY level',
            (mob_id,)
        )
        return [dict(row) for row in rows]
    
    async def get_total_bestiary_stats(self, user_id: int) -> Dict[str, float]:
        bestiary_entries = await self.get_player_bestiary(user_id)
        if not bestiary_entries or isinstance(bestiary_entries, dict):
            return {}
        
        total_stats = {}
        
        for entry in bestiary_entries:
            mob_id = entry['mob_id']
            level = entry['bestiary_level']
            
            for current_level in range(1, level + 1):
                rewards = await self.get_bestiary_rewards(mob_id, current_level)
                for reward in rewards:
                    stat_name = reward['reward_type']
                    stat_value = reward['reward_value']
                    total_stats[stat_name] = total_stats.get(stat_name, 0) + stat_value
        
        return total_stats
    
    async def calculate_bestiary_merchant_discount(self, user_id: int) -> float:
        bestiary_entries = await self.get_player_bestiary(user_id)
        if not bestiary_entries or isinstance(bestiary_entries, dict):
            return 1.0
        total_level = 0
        max_level_entries = 0
        total_kills = 0
        for entry in bestiary_entries:
            level = entry['bestiary_level']
            kills = entry['kills']
            total_level += level
            total_kills += kills
            level_info = await self.get_bestiary_level_requirements(entry['mob_id'])
            if level_info:
                max_level = level_info.get('max_level', 9)
                if level >= max_level:
                    max_level_entries += 1
        level_discount = min(0.10, (total_level / 10) * 0.005)
        max_entry_discount = min(0.15, max_level_entries * 0.01)
        kill_discount = min(0.05, (total_kills / 100) * 0.001)
        total_discount = level_discount + max_entry_discount + kill_discount
        return 1.0 - total_discount
    
    def _calculate_bestiary_level(self, kills: int, level_info: Optional[Dict[str, Any]]) -> int:
        if not level_info:
            if kills >= 5000:
                return 9
            elif kills >= 2500:
                return 8
            elif kills >= 1000:
                return 7
            elif kills >= 500:
                return 6
            elif kills >= 250:
                return 5
            elif kills >= 100:
                return 4
            elif kills >= 50:
                return 3
            elif kills >= 25:
                return 2
            elif kills >= 10:
                return 1
            else:
                return 0
        
        max_level = level_info.get('max_level', 9)
        for level in range(max_level, 0, -1):
            required_kills = level_info.get(f'level_{level}_kills', 0)
            if kills >= required_kills:
                return level
        
        return 0
    
    async def get_bestiary_progress(self, user_id: int, mob_id: str) -> Dict[str, Any]:
        entry_result = await self.get_player_bestiary(user_id, mob_id)
        level_info = await self.get_bestiary_level_requirements(mob_id)
        
        if not entry_result or isinstance(entry_result, list):
            return {
                'kills': 0,
                'deaths': 0,
                'level': 0,
                'next_level_kills': level_info.get('level_1_kills', 10) if level_info else 10,
                'progress': 0.0
            }
        
        entry: Dict[str, Any] = entry_result
        current_level = entry['bestiary_level']
        kills = entry['kills']
        deaths = entry['deaths']
        
        if not level_info:
            return {
                'kills': kills,
                'deaths': deaths,
                'level': current_level,
                'next_level_kills': 0,
                'progress': 100.0
            }
        
        max_level = level_info.get('max_level', 9)
        if current_level >= max_level:
            return {
                'kills': kills,
                'deaths': deaths,
                'level': current_level,
                'next_level_kills': 0,
                'progress': 100.0
            }
        
        next_level = current_level + 1
        next_level_kills = level_info.get(f'level_{next_level}_kills', 0)
        current_level_kills = level_info.get(f'level_{current_level}_kills', 0) if current_level > 0 else 0
        
        kills_needed = next_level_kills - current_level_kills
        kills_progress = kills - current_level_kills
        progress = (kills_progress / kills_needed * 100) if kills_needed > 0 else 100.0
        
        return {
            'kills': kills,
            'deaths': deaths,
            'level': current_level,
            'next_level_kills': next_level_kills,
            'progress': min(100.0, max(0.0, progress))
        }
    
    async def get_all_mobs_in_category(self, category: str) -> List[Dict[str, Any]]:
        rows = await self.fetchall(
            'SELECT * FROM bestiary_levels WHERE category = ? ORDER BY mob_name',
            (category,)
        )
        return [dict(row) for row in rows]
