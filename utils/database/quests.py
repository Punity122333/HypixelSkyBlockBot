from typing import Optional, Dict, List, Tuple
import time
from .base import DatabaseBase


class QuestsDatabase(DatabaseBase):
    """Database operations for quests and daily rewards."""
    
    async def create_quest(self, user_id: int, quest_id: str, progress: int = 0):
        """Create a new quest for a player."""
        await self.conn.execute('''
            INSERT OR IGNORE INTO player_quests (user_id, quest_id, progress, completed, claimed, started_at)
            VALUES (?, ?, ?, 0, 0, ?)
        ''', (user_id, quest_id, progress, int(time.time())))
        await self.conn.commit()
    
    async def get_user_quests(self, user_id: int) -> List[Dict]:
        """Get all quests for a user."""
        async with self.conn.execute('''
            SELECT * FROM player_quests WHERE user_id = ? ORDER BY completed, started_at DESC
        ''', (user_id,)) as cursor:
            rows = await cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
    
    async def get_quest(self, user_id: int, quest_id: str) -> Optional[Dict]:
        """Get a specific quest for a user."""
        async with self.conn.execute('''
            SELECT * FROM player_quests WHERE user_id = ? AND quest_id = ?
        ''', (user_id, quest_id)) as cursor:
            row = await cursor.fetchone()
            if row:
                columns = [description[0] for description in cursor.description]
                return dict(zip(columns, row))
            return None
    
    async def update_quest_progress(self, user_id: int, quest_id: str, progress: int):
        """Update quest progress."""
        await self.conn.execute('''
            UPDATE player_quests SET progress = ? WHERE user_id = ? AND quest_id = ?
        ''', (progress, user_id, quest_id))
        await self.conn.commit()
    
    async def complete_quest(self, user_id: int, quest_id: str):
        """Mark a quest as completed."""
        await self.conn.execute('''
            UPDATE player_quests SET completed = 1 WHERE user_id = ? AND quest_id = ?
        ''', (user_id, quest_id))
        await self.conn.commit()
    
    async def claim_quest_reward(self, user_id: int, quest_id: str):
        """Mark a quest reward as claimed."""
        await self.conn.execute('''
            UPDATE player_quests SET claimed = 1 WHERE user_id = ? AND quest_id = ?
        ''', (user_id, quest_id))
        await self.conn.commit()
    
    async def claim_daily_reward(self, user_id: int) -> Tuple[int, int]:
        """Claim daily reward and update streak."""
        now = int(time.time())
        one_day = 86400
        
        async with self.conn.execute('''
            SELECT last_claim, streak FROM daily_rewards WHERE user_id = ?
        ''', (user_id,)) as cursor:
            result = await cursor.fetchone()
        
        if result:
            last_claim, streak = result
            time_since = now - last_claim
            
            # Already claimed today
            if time_since < one_day:
                return (0, streak)
            
            # Streak continues
            if time_since < one_day * 2:
                new_streak = streak + 1
            else:
                # Streak broken
                new_streak = 1
            
            reward = 1000 + (new_streak * 500)
            
            await self.conn.execute('''
                UPDATE daily_rewards SET last_claim = ?, streak = ? WHERE user_id = ?
            ''', (now, new_streak, user_id))
        else:
            # First claim
            new_streak = 1
            reward = 1000
            await self.conn.execute('''
                INSERT INTO daily_rewards (user_id, last_claim, streak)
                VALUES (?, ?, ?)
            ''', (user_id, now, new_streak))
        
        await self.conn.commit()
        return (reward, new_streak)
