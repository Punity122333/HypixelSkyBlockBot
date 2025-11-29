import json
from typing import Optional

class AchievementTracker:
    ACHIEVEMENTS = {
        'first_mine': {
            'name': 'First Steps',
            'description': 'Complete your first mining session',
            'icon': '⛏️'
        },
        'first_farm': {
            'name': 'Farmer',
            'description': 'Complete your first farming session',
            'icon': '🌾'
        },
        'first_fish': {
            'name': 'Angler',
            'description': 'Go fishing for the first time',
            'icon': '🎣'
        },
        'first_craft': {
            'name': 'Craftsman',
            'description': 'Craft your first item',
            'icon': '🔨'
        },
        'first_combat': {
            'name': 'Warrior',
            'description': 'Win your first combat',
            'icon': '⚔️'
        },
        'first_auction': {
            'name': 'Auctioneer',
            'description': 'Create your first auction',
            'icon': '🔨'
        },
        'first_trade': {
            'name': 'Merchant',
            'description': 'Complete your first bazaar trade',
            'icon': '💰'
        },
        'millionaire': {
            'name': 'Millionaire',
            'description': 'Accumulate 1,000,000 coins',
            'icon': '💎'
        },
        'skill_master_10': {
            'name': 'Skill Master',
            'description': 'Reach level 10 in any skill',
            'icon': '📚'
        },
        'skill_master_20': {
            'name': 'Skill Grandmaster',
            'description': 'Reach level 20 in any skill',
            'icon': '✨'
        },
        'combat_5': {
            'name': 'Combat Novice',
            'description': 'Reach Combat Level 5',
            'icon': '⚔️'
        },
        'combat_10': {
            'name': 'Combat Expert',
            'description': 'Reach Combat Level 10',
            'icon': '🗡️'
        },
        'mining_10': {
            'name': 'Mining Expert',
            'description': 'Reach Mining Level 10',
            'icon': '⛏️'
        },
        'farming_10': {
            'name': 'Farming Expert',
            'description': 'Reach Farming Level 10',
            'icon': '🌾'
        }
    }
    
    @staticmethod
    async def unlock_achievement(db, user_id: int, achievement_id: str) -> Optional[dict]:
        if achievement_id not in AchievementTracker.ACHIEVEMENTS:
            return None
        
        progression = await db.get_player_progression(user_id)
        if not progression:
            return None
        
        achievements = json.loads(progression.get('achievements', '[]'))
        
        if achievement_id in achievements:
            return None
        
        achievements.append(achievement_id)
        await db.update_progression(user_id, achievements=json.dumps(achievements))
        
        return AchievementTracker.ACHIEVEMENTS[achievement_id]
    
    @staticmethod
    async def check_and_unlock_wealth(db, user_id: int, total_wealth: int):
        if total_wealth >= 1000000:
            return await AchievementTracker.unlock_achievement(db, user_id, 'millionaire')
        return None
    
    @staticmethod
    async def check_and_unlock_skill(db, user_id: int, skill_name: str, level: int):
        achievements = []
        
        if level >= 10:
            result = await AchievementTracker.unlock_achievement(db, user_id, 'skill_master_10')
            if result:
                achievements.append(result)
            
            skill_achievement = f'{skill_name}_10'
            if skill_achievement in AchievementTracker.ACHIEVEMENTS:
                result = await AchievementTracker.unlock_achievement(db, user_id, skill_achievement)
                if result:
                    achievements.append(result)
        
        if level >= 20:
            result = await AchievementTracker.unlock_achievement(db, user_id, 'skill_master_20')
            if result:
                achievements.append(result)
        
        return achievements if achievements else None
