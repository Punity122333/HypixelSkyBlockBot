from typing import Optional, Dict, Any, List
from database import GameDatabase


class PlayerManager:
    def __init__(self, db: GameDatabase):
        self.db = db
        self._cache: Dict[int, Dict[str, Any]] = {}

    async def get_or_create_player(self, user_id: int, username: str) -> Dict[str, Any]:
        if user_id in self._cache:
            cached = self._cache[user_id]
            if cached:
                return cached
        
        player = await self.db.get_player(user_id)
        if not player:
            await self.db.create_player(user_id, username)
            player = await self.db.get_player(user_id)
        
        if player:
            self._cache[user_id] = dict(player)
            return dict(player)
        
        default_player = {
            'user_id': user_id,
            'username': username,
            'coins': 0,
            'health': 100,
            'max_health': 100,
            'defense': 0,
            'strength': 0,
            'level': 1,
            'xp': 0
        }
        self._cache[user_id] = default_player
        return default_player

    async def update_player(self, user_id: int, **kwargs):
        await self.db.update_player(user_id, **kwargs)
        if user_id in self._cache:
            self._cache[user_id].update(kwargs)

    async def add_coins(self, user_id: int, amount: int) -> int:
        player = await self.db.get_player(user_id)
        if player:
            new_balance = player['coins'] + amount
            current_total_earned = player.get('total_earned', 0)
            new_total_earned = current_total_earned + amount
            await self.update_player(user_id, coins=new_balance, total_earned=new_total_earned)
            return new_balance
        return 0

    async def remove_coins(self, user_id: int, amount: int) -> bool:
        player = await self.db.get_player(user_id)
        if player and player['coins'] >= amount:
            new_balance = player['coins'] - amount
            current_total_spent = player.get('total_spent', 0)
            new_total_spent = current_total_spent + amount
            await self.update_player(user_id, coins=new_balance, total_spent=new_total_spent)
            return True
        return False
    
    async def add_xp(self, user_id: int, amount: int) -> Dict[str, Any]:
        player = await self.db.get_player(user_id)
        if not player:
            return {'leveled_up': False, 'new_level': 1}
        
        current_xp = player.get('xp', 0)
        current_level = player.get('level', 1)
        new_xp = current_xp + amount
        
        xp_for_next = self._calculate_xp_for_level(current_level + 1)
        leveled_up = False
        new_level = current_level
        
        while new_xp >= xp_for_next and new_level < 100:
            new_xp -= xp_for_next
            new_level += 1
            leveled_up = True
            xp_for_next = self._calculate_xp_for_level(new_level + 1)
        
        await self.update_player(user_id, xp=new_xp, level=new_level)
        
        return {
            'leveled_up': leveled_up,
            'new_level': new_level,
            'xp': new_xp,
            'xp_for_next': xp_for_next
        }
    
    def _calculate_xp_for_level(self, level: int) -> int:
        if level <= 15:
            return level * 100
        elif level <= 30:
            return level * 150
        elif level <= 50:
            return level * 250
        else:
            return level * 500
    
    async def give_item(self, user_id: int, item_id: str, amount: int = 1) -> bool:
        try:
            await self.db.add_item_to_inventory(user_id, item_id, amount)
            return True
        except Exception:
            return False
    
    async def take_item(self, user_id: int, item_id: str, amount: int = 1) -> bool:
        item_count = await self.db.get_item_count(user_id, item_id)
        if item_count >= amount:
            await self.db.remove_item_from_inventory(user_id, item_id, amount)
            return True
        return False
    
    async def has_item(self, user_id: int, item_id: str, amount: int = 1) -> bool:
        item_count = await self.db.get_item_count(user_id, item_id)
        return item_count >= amount
    
    async def get_net_worth(self, user_id: int) -> int:
        player = await self.db.get_player(user_id)
        if not player:
            return 0
        
        net_worth = player.get('coins', 0)
        
        inventory = await self.db.get_inventory(user_id)
        for item_row in inventory:
            item_id = item_row['item_id']
            amount = item_row['amount']
            
            if self.db.conn:
                cursor = await self.db.conn.execute('''
                    SELECT npc_sell_price FROM game_items WHERE item_id = ?
                ''', (item_id,))
                item_data = await cursor.fetchone()
                
                if item_data:
                    net_worth += item_data['npc_sell_price'] * amount
        
        return net_worth
    
    async def get_skill_average(self, user_id: int) -> float:
        skills = await self.db.get_skills(user_id)
        if not skills:
            return 0.0
        
        total_levels = sum(skill['level'] for skill in skills)
        return total_levels / len(skills)

    def clear_cache(self, user_id: Optional[int] = None):
        if user_id:
            self._cache.pop(user_id, None)
        else:
            self._cache.clear()
    
    async def get_player_fresh(self, user_id: int) -> Dict[str, Any]:
        """Always fetch the latest player data from DB, bypassing cache."""
        player = await self.db.get_player(user_id)
        if player:
            self._cache[user_id] = dict(player)
            return dict(player)
        return {}
