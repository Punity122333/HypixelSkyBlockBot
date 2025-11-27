from typing import Optional, Dict, Any
from .database import GameDatabase

class PlayerManager:
    def __init__(self, db: GameDatabase):
        self.db = db
        self._cache: Dict[int, Dict[str, Any]] = {}

    async def get_or_create_player(self, user_id: int, username: str) -> Dict[str, Any]:
        if user_id in self._cache:
            return self._cache[user_id]
        
        player = await self.db.get_player(user_id)
        if not player:
            await self.db.create_player(user_id, username)
            player = await self.db.get_player(user_id)
        
        if player:
            self._cache[user_id] = player
            return player
        
        return {}

    async def update_player(self, user_id: int, **kwargs):
        await self.db.update_player(user_id, **kwargs)
        if user_id in self._cache:
            self._cache[user_id].update(kwargs)

    async def add_coins(self, user_id: int, amount: int):
        player = await self.db.get_player(user_id)
        if player:
            new_balance = player['coins'] + amount
            await self.update_player(user_id, coins=new_balance)
            return new_balance
        return 0

    async def remove_coins(self, user_id: int, amount: int) -> bool:
        player = await self.db.get_player(user_id)
        if player and player['coins'] >= amount:
            new_balance = player['coins'] - amount
            await self.update_player(user_id, coins=new_balance)
            return True
        return False

    def clear_cache(self, user_id: Optional[int] = None):
        if user_id:
            self._cache.pop(user_id, None)
        else:
            self._cache.clear()
