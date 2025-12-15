from typing import Dict, List, Optional, Any
import time
from .core import DatabaseCore

class AchievementsDB(DatabaseCore):
    """Database layer for achievements system"""
    
    async def get_all_achievements(self) -> List[Dict]:
        """Get all available achievements from the database"""
        rows = await self.fetchall('SELECT * FROM game_achievements ORDER BY category, achievement_id')
        return [dict(row) for row in rows]
    
    async def get_achievements_dict(self) -> Dict:
        """Get achievements as a dictionary keyed by achievement_id"""
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
        """Get a single achievement by ID"""
        row = await self.fetchone(
            'SELECT * FROM game_achievements WHERE achievement_id = ?',
            (achievement_id,)
        )
        return dict(row) if row else None
    
    async def unlock_achievement(self, user_id: int, achievement_id: str) -> bool:
        """Unlock an achievement for a user"""
        if not user_id or not achievement_id:
            return False
        
        # Check if achievement exists
        achievement = await self.get_achievement(achievement_id)
        if not achievement:
            return False
        
        # Check if already unlocked
        existing = await self.fetchone(
            'SELECT id FROM player_achievements WHERE user_id = ? AND achievement_id = ?',
            (user_id, achievement_id)
        )
        
        if existing:
            return False
        
        # Unlock achievement
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
            'SELECT id FROM player_achievements WHERE user_id = ? AND achievement_id = ?',
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
