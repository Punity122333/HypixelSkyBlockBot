from typing import Dict, List, Optional

class BadgeSystem:
    
    BADGES = {}
    
    @staticmethod
    async def initialize_badges(db):
        rows = await db.fetchall('SELECT * FROM game_badges')
        BadgeSystem.BADGES = {row['badge_id']: {'name': row['name'], 'description': row['description'], 'category': row['category']} for row in rows}
    
    @staticmethod
    async def unlock_badge(db, user_id: int, badge_id: str) -> bool:
        return await db.badges.unlock_badge(user_id, badge_id)
    
    @staticmethod
    async def get_player_badges(db, user_id: int) -> List[Dict]:
        return await db.badges.get_player_badges(user_id)
    
    @staticmethod
    async def check_and_unlock_badges(db, user_id: int, context: str, **kwargs):
        return await db.badges.check_and_unlock_badges(user_id, context, **kwargs)
    
    @staticmethod
    async def get_all_badges(db) -> List[Dict]:
        return await db.badges.get_all_badges()

