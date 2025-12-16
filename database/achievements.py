from typing import Dict, List, Optional
import time
from .core import DatabaseCore

class AchievementsDB(DatabaseCore):

    async def get_all_achievements(self) -> List[Dict]:

        rows = await self.fetchall('SELECT * FROM game_achievements ORDER BY category, achievement_id')
        return [dict(row) for row in rows]
    
    async def get_achievements_dict(self) -> Dict:

        rows = await self.fetchall('SELECT * FROM game_achievements')
        return {
            row['achievement_id']: {
                'name': row['name'],
                'description': row['description'],
                'category': row['category'],
                'icon': row['icon'],
                'requirement_type': row['requirement_type'],
                'requirement_value': row['requirement_value']
            } for row in rows
        }
    
    async def get_achievement(self, achievement_id: str) -> Optional[Dict]:

        row = await self.fetchone(
            'SELECT * FROM game_achievements WHERE achievement_id = ?',
            (achievement_id,)
        )
        return dict(row) if row else None
    
    async def unlock_achievement(self, user_id: int, achievement_id: str) -> bool:

        if not user_id or not achievement_id:
            return False
        
        achievement = await self.get_achievement(achievement_id)
        if not achievement:
            return False

        existing = await self.fetchone(
            'SELECT user_id FROM player_achievements WHERE user_id = ? AND achievement_id = ?',
            (user_id, achievement_id)
        )
        
        if existing:
            return False

        await self.execute(
            'INSERT INTO player_achievements (user_id, achievement_id, unlocked_at) VALUES (?, ?, ?)',
            (user_id, achievement_id, int(time.time()))
        )
        await self.commit()
        
        return True
    
    async def get_player_achievements(self, user_id: int) -> List[Dict]:
        """Get all achievements unlocked by a player"""
        rows = await self.fetchall(
            '''SELECT pa.*, ga.name, ga.description, ga.category, ga.icon 
               FROM player_achievements pa
               JOIN game_achievements ga ON pa.achievement_id = ga.achievement_id
               WHERE pa.user_id = ? 
               ORDER BY pa.unlocked_at DESC''',
            (user_id,)
        )
        
        return [dict(row) for row in rows]
    
    async def has_achievement(self, user_id: int, achievement_id: str) -> bool:
        """Check if a user has unlocked a specific achievement"""
        row = await self.fetchone(
            'SELECT user_id FROM player_achievements WHERE user_id = ? AND achievement_id = ?',
            (user_id, achievement_id)
        )
        return row is not None
    
    async def get_achievement_count(self, user_id: int) -> int:
        """Get the number of achievements a user has unlocked"""
        row = await self.fetchone(
            'SELECT COUNT(*) as count FROM player_achievements WHERE user_id = ?',
            (user_id,)
        )
        return row['count'] if row else 0
    
    async def get_achievements_by_category(self, category: str) -> List[Dict]:
        """Get all achievements in a specific category"""
        rows = await self.fetchall(
            'SELECT * FROM game_achievements WHERE category = ? ORDER BY achievement_id',
            (category,)
        )
        return [dict(row) for row in rows]
    
    async def get_achievement_leaderboard(self, limit: int = 10) -> List[Dict]:
        """Get top players by achievement count"""
        rows = await self.fetchall(
            '''SELECT user_id, COUNT(*) as achievement_count
               FROM player_achievements
               GROUP BY user_id
               ORDER BY achievement_count DESC
               LIMIT ?''',
            (limit,)
        )
        return [dict(row) for row in rows]
    
    async def calculate_achievement_luck_bonus(self, user_id: int) -> float:
        achievement_count = await self.get_achievement_count(user_id)
        player_achievements = await self.get_player_achievements(user_id)
        base_bonus = min(0.10, achievement_count * 0.002)
        categories = set()
        for achievement in player_achievements:
            categories.add(achievement['category'])
        diversity_bonus = min(0.05, len(categories) * 0.005)
        rare_bonus = 0.0
        for achievement in player_achievements:
            achievement_data = await self.get_achievement(achievement['achievement_id'])
            if achievement_data:
                req_value = achievement_data.get('requirement_value', 0)
                if req_value >= 1000:
                    rare_bonus += 0.001
        rare_bonus = min(0.08, rare_bonus)
        return 1.0 + base_bonus + diversity_bonus + rare_bonus
    
    async def calculate_achievement_crit_bonus(self, user_id: int) -> float:
        player_achievements = await self.get_player_achievements(user_id)
        combat_achievements = 0
        for achievement in player_achievements:
            if achievement['category'] in ['combat', 'slayer', 'dungeons', 'boss']:
                combat_achievements += 1
        return min(0.06, combat_achievements * 0.003)
    
    async def calculate_achievement_skill_bonus(self, user_id: int, skill_name: str) -> float:
        player_achievements = await self.get_player_achievements(user_id)
        skill_category_map = {
            'mining': 'mining',
            'foraging': 'foraging',
            'fishing': 'fishing',
            'farming': 'farming',
            'combat': 'combat',
            'enchanting': 'enchanting',
            'alchemy': 'alchemy'
        }
        category = skill_category_map.get(skill_name.lower())
        if not category:
            return 1.0
        skill_achievements = 0
        for achievement in player_achievements:
            if achievement['category'] == category:
                skill_achievements += 1
        bonus = min(0.10, skill_achievements * 0.01)
        return 1.0 + bonus
