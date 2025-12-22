from typing import Dict, List, Optional, Any
from .core import DatabaseCore
import time


class TradingDB(DatabaseCore):
    
    async def create_trade(self, initiator_id: int, receiver_id: int) -> int:
        cursor = await self.execute(
            '''INSERT INTO player_trades (initiator_id, receiver_id, status, created_at)
               VALUES (?, ?, 'pending', ?)''',
            (initiator_id, receiver_id, int(time.time()))
        )
        await self.commit()
        return cursor.lastrowid if cursor.lastrowid else 0
    
    async def get_trade(self, trade_id: int) -> Optional[Dict]:
        row = await self.fetchone(
            'SELECT * FROM player_trades WHERE trade_id = ?',
            (trade_id,)
        )
        return dict(row) if row else None
    
    async def add_trade_item(self, trade_id: int, user_id: int, item_id: str, amount: int, inventory_item_id: Optional[int] = None):
        await self.execute(
            '''INSERT INTO trade_items (trade_id, user_id, item_id, amount, inventory_item_id)
               VALUES (?, ?, ?, ?, ?)''',
            (trade_id, user_id, item_id, amount, inventory_item_id)
        )
        await self.commit()
    
    async def remove_trade_item(self, trade_id: int, user_id: int, item_id: str):
        await self.execute(
            'DELETE FROM trade_items WHERE trade_id = ? AND user_id = ? AND item_id = ?',
            (trade_id, user_id, item_id)
        )
        await self.commit()
    
    async def get_trade_items(self, trade_id: int, user_id: Optional[int] = None) -> List[Dict]:
        if user_id:
            rows = await self.fetchall(
                'SELECT * FROM trade_items WHERE trade_id = ? AND user_id = ?',
                (trade_id, user_id)
            )
        else:
            rows = await self.fetchall(
                'SELECT * FROM trade_items WHERE trade_id = ?',
                (trade_id,)
            )
        return [dict(row) for row in rows]
    
    async def set_trade_coins(self, trade_id: int, user_id: int, amount: int):
        trade = await self.get_trade(trade_id)
        if not trade:
            return False
        
        if user_id == trade['initiator_id']:
            await self.execute(
                'UPDATE player_trades SET initiator_coins = ?, initiator_ready = 0 WHERE trade_id = ?',
                (amount, trade_id)
            )
        elif user_id == trade['receiver_id']:
            await self.execute(
                'UPDATE player_trades SET receiver_coins = ?, receiver_ready = 0 WHERE trade_id = ?',
                (amount, trade_id)
            )
        else:
            return False
        
        await self.commit()
        return True
    
    async def set_ready(self, trade_id: int, user_id: int, ready: bool):
        trade = await self.get_trade(trade_id)
        if not trade:
            return False
        
        ready_val = 1 if ready else 0
        
        if user_id == trade['initiator_id']:
            await self.execute(
                'UPDATE player_trades SET initiator_ready = ? WHERE trade_id = ?',
                (ready_val, trade_id)
            )
        elif user_id == trade['receiver_id']:
            await self.execute(
                'UPDATE player_trades SET receiver_ready = ? WHERE trade_id = ?',
                (ready_val, trade_id)
            )
        else:
            return False
        
        await self.commit()
        return True
    
    async def complete_trade(self, trade_id: int) -> bool:
        trade = await self.get_trade(trade_id)
        if not trade:
            return False
        
        if not (trade['initiator_ready'] and trade['receiver_ready']):
            return False
        
        initiator_id = trade['initiator_id']
        receiver_id = trade['receiver_id']
        initiator_coins = trade['initiator_coins']
        receiver_coins = trade['receiver_coins']
        
        trade_items = await self.get_trade_items(trade_id)
        
        initiator_items = [item for item in trade_items if item['user_id'] == initiator_id]
        receiver_items = [item for item in trade_items if item['user_id'] == receiver_id]
        
        from .inventory import InventoryDB
        inventory_db = InventoryDB(self.db_path)
        inventory_db.conn = self.conn
        
        for item in initiator_items:
            await inventory_db.remove_item(initiator_id, item['item_id'], item['amount'])
            await inventory_db.add_item(receiver_id, item['item_id'], item['amount'])
        
        for item in receiver_items:
            await inventory_db.remove_item(receiver_id, item['item_id'], item['amount'])
            await inventory_db.add_item(initiator_id, item['item_id'], item['amount'])
        
        if initiator_coins > 0:
            await self.execute(
                'UPDATE player_economy SET coins = coins - ? WHERE user_id = ?',
                (initiator_coins, initiator_id)
            )
            await self.execute(
                'UPDATE player_economy SET coins = coins + ? WHERE user_id = ?',
                (initiator_coins, receiver_id)
            )
        
        if receiver_coins > 0:
            await self.execute(
                'UPDATE player_economy SET coins = coins - ? WHERE user_id = ?',
                (receiver_coins, receiver_id)
            )
            await self.execute(
                'UPDATE player_economy SET coins = coins + ? WHERE user_id = ?',
                (receiver_coins, initiator_id)
            )
        
        await self.execute(
            'UPDATE player_economy SET trading_reputation = trading_reputation + 1 WHERE user_id IN (?, ?)',
            (initiator_id, receiver_id)
        )
        
        completed_time = int(time.time())
        await self.execute(
            'UPDATE player_trades SET status = ?, completed_at = ? WHERE trade_id = ?',
            ('completed', completed_time, trade_id)
        )
        
        cursor = await self.execute(
            '''INSERT INTO trade_history (trade_id, initiator_id, receiver_id, initiator_coins, receiver_coins, completed_at)
               VALUES (?, ?, ?, ?, ?, ?)''',
            (trade_id, initiator_id, receiver_id, initiator_coins, receiver_coins, completed_time)
        )
        history_id = cursor.lastrowid if cursor.lastrowid else 0
        
        for item in initiator_items:
            await self.execute(
                '''INSERT INTO trade_history_items (history_id, user_id, item_id, amount)
                   VALUES (?, ?, ?, ?)''',
                (history_id, initiator_id, item['item_id'], item['amount'])
            )
        
        for item in receiver_items:
            await self.execute(
                '''INSERT INTO trade_history_items (history_id, user_id, item_id, amount)
                   VALUES (?, ?, ?, ?)''',
                (history_id, receiver_id, item['item_id'], item['amount'])
            )
        
        await self.commit()
        return True
    
    async def cancel_trade(self, trade_id: int):
        await self.execute(
            'UPDATE player_trades SET status = ? WHERE trade_id = ?',
            ('cancelled', trade_id)
        )
        await self.commit()
    
    async def get_trade_history(self, user_id: int, limit: int = 20) -> List[Dict]:
        rows = await self.fetchall(
            '''SELECT * FROM trade_history 
               WHERE initiator_id = ? OR receiver_id = ?
               ORDER BY completed_at DESC LIMIT ?''',
            (user_id, user_id, limit)
        )
        return [dict(row) for row in rows]
    
    async def get_trade_history_items(self, history_id: int) -> List[Dict]:
        rows = await self.fetchall(
            'SELECT * FROM trade_history_items WHERE history_id = ?',
            (history_id,)
        )
        return [dict(row) for row in rows]
    
    async def get_trading_stats(self, user_id: int) -> Dict[str, Any]:
        total_trades = await self.fetchone(
            '''SELECT COUNT(*) as count FROM trade_history 
               WHERE initiator_id = ? OR receiver_id = ?''',
            (user_id, user_id)
        )
        
        total_coins_traded = await self.fetchone(
            '''SELECT 
                   SUM(CASE WHEN initiator_id = ? THEN initiator_coins ELSE 0 END) +
                   SUM(CASE WHEN receiver_id = ? THEN receiver_coins ELSE 0 END) as total
               FROM trade_history 
               WHERE initiator_id = ? OR receiver_id = ?''',
            (user_id, user_id, user_id, user_id)
        )
        
        player = await self.fetchone(
            'SELECT trading_reputation FROM player_economy WHERE user_id = ?',
            (user_id,)
        )
        
        return {
            'total_trades': total_trades['count'] if total_trades else 0,
            'total_coins_traded': total_coins_traded['total'] if total_coins_traded and total_coins_traded['total'] else 0,
            'trading_reputation': player['trading_reputation'] if player else 0
        }
