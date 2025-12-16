from typing import Dict, Optional, List, Any
from .core import DatabaseCore
import time


class MuseumDB(DatabaseCore):
    
    async def get_milestone_rewards(self) -> Dict[int, Dict[str, Any]]:
        rows = await self.fetchall('SELECT milestone, coins, title FROM museum_milestone_rewards')
        return {row['milestone']: {'coins': row['coins'], 'title': row['title']} for row in rows}
    
    async def get_rarity_points(self, rarity: str) -> int:
        row = await self.fetchone('SELECT points FROM museum_rarity_points WHERE rarity = ?', (rarity,))
        return row['points'] if row else 1
    
    async def donate_item(self, user_id: int, item_id: str, rarity: str) -> Dict[str, Any]:
        existing = await self.fetchone(
            'SELECT * FROM museum_donations WHERE user_id = ? AND item_id = ?',
            (user_id, item_id)
        )
        
        if existing:
            return {'success': False, 'error': 'Item already in museum'}
        
        points = await self.get_rarity_points(rarity)
        
        await self.execute(
            '''INSERT INTO museum_donations (user_id, item_id, rarity, points, donated_at)
               VALUES (?, ?, ?, ?, ?)''',
            (user_id, item_id, rarity, points, int(time.time()))
        )
        await self.commit()
        
        total_donations = await self.get_total_donations(user_id)
        total_points = await self.get_total_points(user_id)
        
        milestone_reward = None
        milestone_rewards = await self.get_milestone_rewards()
        for milestone, reward in sorted(milestone_rewards.items()):
            if total_donations == milestone:
                milestone_reward = reward
                await self.execute(
                    '''INSERT INTO museum_milestones (user_id, milestone, claimed_at)
                       VALUES (?, ?, ?)''',
                    (user_id, milestone, int(time.time()))
                )
                await self.commit()
                break
        
        return {
            'success': True,
            'points': points,
            'total_donations': total_donations,
            'total_points': total_points,
            'milestone_reward': milestone_reward
        }
    
    async def get_museum_items(self, user_id: int) -> List[Dict]:
        rows = await self.fetchall(
            '''SELECT * FROM museum_donations 
               WHERE user_id = ? 
               ORDER BY points DESC, donated_at DESC''',
            (user_id,)
        )
        return [dict(row) for row in rows]
    
    async def get_total_donations(self, user_id: int) -> int:
        row = await self.fetchone(
            'SELECT COUNT(*) as total FROM museum_donations WHERE user_id = ?',
            (user_id,)
        )
        return row['total'] if row else 0
    
    async def get_total_points(self, user_id: int) -> int:
        row = await self.fetchone(
            'SELECT SUM(points) as total FROM museum_donations WHERE user_id = ?',
            (user_id,)
        )
        return row['total'] if row and row['total'] else 0
    
    async def get_rarity_breakdown(self, user_id: int) -> Dict[str, int]:
        rows = await self.fetchall(
            '''SELECT rarity, COUNT(*) as count 
               FROM museum_donations 
               WHERE user_id = ? 
               GROUP BY rarity''',
            (user_id,)
        )
        
        breakdown = {}
        for row in rows:
            breakdown[row['rarity']] = row['count']
        return breakdown
    
    async def get_museum_leaderboard(self, limit: int = 10) -> List[Dict]:
        rows = await self.fetchall(
            '''SELECT user_id, COUNT(*) as total_items, SUM(points) as total_points
               FROM museum_donations 
               GROUP BY user_id
               ORDER BY total_points DESC, total_items DESC
               LIMIT ?''',
            (limit,)
        )
        return [dict(row) for row in rows]
    
    async def get_claimed_milestones(self, user_id: int) -> List[int]:
        rows = await self.fetchall(
            'SELECT milestone FROM museum_milestones WHERE user_id = ? ORDER BY milestone ASC',
            (user_id,)
        )
        return [row['milestone'] for row in rows]
    
    async def get_next_milestone(self, user_id: int) -> Optional[Dict]:
        total = await self.get_total_donations(user_id)
        claimed = await self.get_claimed_milestones(user_id)
        
        milestone_rewards = await self.get_milestone_rewards()
        for milestone in sorted(milestone_rewards.keys()):
            if milestone not in claimed and total < milestone:
                return {
                    'milestone': milestone,
                    'reward': milestone_rewards[milestone],
                    'progress': total,
                    'required': milestone
                }
        
        return None
    
    async def calculate_museum_drop_bonus(self, user_id: int) -> float:
        total_donations = await self.get_total_donations(user_id)
        total_points = await self.get_total_points(user_id)
        donation_bonus = min(0.05, (total_donations / 10) * 0.001)
        rarity_bonus = min(0.03, (total_points / 100) * 0.0005)
        return 1.0 + donation_bonus + rarity_bonus
