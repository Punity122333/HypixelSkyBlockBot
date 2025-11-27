from typing import Optional, Dict, List
import random
import time
from .base import DatabaseBase


class TradingDatabase(DatabaseBase):

    async def init_bot_traders(self):
        """Initialize bot traders for bazaar trading."""
        behaviors = ['aggressive', 'conservative', 'balanced', 'opportunistic', 'market_maker']
        bot_names = ['TraderBot_Alpha', 'TraderBot_Beta', 'TraderBot_Gamma', 'TraderBot_Delta', 'TraderBot_Epsilon']
        
        for name, behavior in zip(bot_names, behaviors):
            await self.conn.execute('''
                INSERT OR IGNORE INTO bot_traders (bot_name, coins, trading_behavior)
                VALUES (?, ?, ?)
            ''', (name, 1000000, behavior))
        await self.conn.commit()
    
    async def get_active_bot_traders(self) -> List[Dict]:
        async with self.conn.execute('SELECT * FROM bot_traders WHERE active = 1') as cursor:
            rows = await cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
    
    async def update_bot_trader(self, bot_id: int, coins: int):
        await self.conn.execute('UPDATE bot_traders SET coins = ? WHERE id = ?', (coins, bot_id))
        await self.conn.commit()

    async def init_auction_bots(self):
        bot_configs = [
            ('AuctionSniper_X1', 'sniper', 0.8),
            ('BulkBuyer_Pro', 'bulk_trader', 0.3),
            ('FlipMaster_2000', 'flipper', 0.6),
            ('PatientInvestor', 'long_term', 0.2),
            ('MarketMaker_Alpha', 'market_maker', 0.5),
            ('OpportunistBot', 'opportunist', 0.7),
            ('ValueHunter', 'value_hunter', 0.4),
            ('TrendFollower', 'trend_follower', 0.5)
        ]
        
        for bot_name, strategy, risk in bot_configs:
            await self.conn.execute('''
                INSERT OR IGNORE INTO auction_bot_traders (bot_name, trading_strategy, risk_tolerance, coins)
                VALUES (?, ?, ?, ?)
            ''', (bot_name, strategy, risk, random.randint(300000, 1000000)))
        await self.conn.commit()
    
    async def get_auction_bots(self) -> List[Dict]:
        async with self.conn.execute('SELECT * FROM auction_bot_traders WHERE active = 1') as cursor:
            rows = await cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
    
    async def update_auction_bot(self, bot_id: int, **kwargs):
        set_clause = ', '.join([f'{k} = ?' for k in kwargs.keys()])
        values = list(kwargs.values()) + [bot_id]
        await self.conn.execute(
            f'UPDATE auction_bot_traders SET {set_clause} WHERE id = ?',
            values
        )
        await self.conn.commit()

    async def init_stock_market(self):
        stocks = [
            ('WOOD', 'Lumber Corp', 100.0, 0.15),
            ('CROP', 'AgriTech Industries', 250.0, 0.20),
            ('MINE', 'Crystal Mining Co.', 500.0, 0.25),
            ('DRAG', 'Dragon Holdings', 5000.0, 0.40),
            ('ENCH', 'Enchantment Ltd.', 1500.0, 0.30),
            ('PETS', 'Pet Emporium Inc.', 800.0, 0.22),
            ('DUNG', 'Dungeon Exploration Corp.', 2500.0, 0.35),
            ('SLAY', 'Slayer Industries', 1800.0, 0.28)
        ]
        
        now = int(time.time())
        
        for symbol, name, price, volatility in stocks:
            await self.conn.execute('''
                INSERT OR IGNORE INTO stock_market 
                (stock_symbol, company_name, current_price, opening_price, daily_high, daily_low, volatility, market_cap, last_update)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (symbol, name, price, price, price * 1.05, price * 0.95, volatility, int(price * 1000000), now))
        await self.conn.commit()
    
    async def get_stock(self, symbol: str) -> Optional[Dict]:
        """Get stock data by symbol."""
        async with self.conn.execute('SELECT * FROM stock_market WHERE stock_symbol = ?', (symbol,)) as cursor:
            row = await cursor.fetchone()
            if row:
                columns = [description[0] for description in cursor.description]
                return dict(zip(columns, row))
            return None
    
    async def get_all_stocks(self) -> List[Dict]:
        """Get all stocks."""
        async with self.conn.execute('SELECT * FROM stock_market ORDER BY stock_symbol') as cursor:
            rows = await cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
    
    async def update_stock_price(self, symbol: str, new_price: float, volume: int):
        """Update stock price and volume."""
        now = int(time.time())
        
        stock = await self.get_stock(symbol)
        if not stock:
            return
        
        new_high = max(stock['daily_high'], new_price)
        new_low = min(stock['daily_low'], new_price)
        
        await self.conn.execute('''
            UPDATE stock_market 
            SET current_price = ?, daily_high = ?, daily_low = ?, volume = volume + ?, last_update = ?
            WHERE stock_symbol = ?
        ''', (new_price, new_high, new_low, volume, now, symbol))
        
        await self.conn.execute('''
            INSERT INTO price_history (item_id, price, volume, timestamp, price_type, source)
            VALUES (?, ?, ?, ?, 'stock', 'market')
        ''', (symbol, new_price, volume, now))
        
        await self.conn.commit()
    
    async def buy_stock(self, user_id: int, symbol: str, shares: int, price: float) -> bool:
        """Buy stock shares."""
        total_cost = int(shares * price)
        
        # Check if player has enough coins
        async with self.conn.execute('SELECT coins, total_spent FROM players WHERE user_id = ?', (user_id,)) as cursor:
            player_data = await cursor.fetchone()
            if not player_data or player_data[0] < total_cost:
                return False
        
        # Deduct coins
        await self.conn.execute(
            'UPDATE players SET coins = coins - ?, total_spent = total_spent + ? WHERE user_id = ?',
            (total_cost, total_cost, user_id)
        )
        
        # Update or create player stock position
        async with self.conn.execute('''
            SELECT shares, avg_buy_price FROM player_stocks WHERE user_id = ? AND stock_symbol = ?
        ''', (user_id, symbol)) as cursor:
            result = await cursor.fetchone()
        
        if result:
            current_shares, avg_price = result
            new_shares = current_shares + shares
            new_avg_price = ((current_shares * avg_price) + (shares * price)) / new_shares
            
            await self.conn.execute('''
                UPDATE player_stocks SET shares = ?, avg_buy_price = ? WHERE user_id = ? AND stock_symbol = ?
            ''', (new_shares, new_avg_price, user_id, symbol))
        else:
            await self.conn.execute('''
                INSERT INTO player_stocks (user_id, stock_symbol, shares, avg_buy_price)
                VALUES (?, ?, ?, ?)
            ''', (user_id, symbol, shares, price))
        
        await self.update_stock_price(symbol, price, shares)
        await self.conn.commit()
        return True
    
    async def sell_stock(self, user_id: int, symbol: str, shares: int, price: float) -> bool:
        """Sell stock shares."""
        async with self.conn.execute('''
            SELECT shares FROM player_stocks WHERE user_id = ? AND stock_symbol = ?
        ''', (user_id, symbol)) as cursor:
            result = await cursor.fetchone()
        
        if not result or result[0] < shares:
            return False
        
        total_gain = int(shares * price)
        
        # Add coins
        await self.conn.execute(
            'UPDATE players SET coins = coins + ?, total_earned = total_earned + ? WHERE user_id = ?',
            (total_gain, total_gain, user_id)
        )
        
        # Update player stock position
        new_shares = result[0] - shares
        if new_shares > 0:
            await self.conn.execute('''
                UPDATE player_stocks SET shares = ? WHERE user_id = ? AND stock_symbol = ?
            ''', (new_shares, user_id, symbol))
        else:
            await self.conn.execute('''
                DELETE FROM player_stocks WHERE user_id = ? AND stock_symbol = ?
            ''', (user_id, symbol))
        
        await self.update_stock_price(symbol, price, shares)
        await self.conn.commit()
        return True
    
    async def get_player_stocks(self, user_id: int) -> List[Dict]:
        """Get all stocks owned by a player."""
        async with self.conn.execute('''
            SELECT ps.*, sm.current_price, sm.company_name
            FROM player_stocks ps
            JOIN stock_market sm ON ps.stock_symbol = sm.stock_symbol
            WHERE ps.user_id = ?
        ''', (user_id,)) as cursor:
            rows = await cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
    
    # Merchant Deals
    async def create_merchant_deal(self, npc_name: str, item_id: str, quantity: int, 
                                  price: int, deal_type: str, duration: int):
        """Create a merchant deal."""
        now = int(time.time())
        expires = now + duration
        
        await self.conn.execute('''
            INSERT INTO merchant_deals (npc_name, item_id, quantity, price, deal_type, expires_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (npc_name, item_id, quantity, price, deal_type, expires))
        await self.conn.commit()
    
    async def get_active_merchant_deals(self) -> List[Dict]:
        """Get all active merchant deals."""
        now = int(time.time())
        
        async with self.conn.execute('''
            SELECT * FROM merchant_deals WHERE available = 1 AND expires_at > ?
            ORDER BY expires_at ASC
        ''', (now,)) as cursor:
            rows = await cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
    
    async def get_merchant_deal(self, deal_id: int) -> Optional[Dict]:
        """Get a specific merchant deal."""
        async with self.conn.execute('SELECT * FROM merchant_deals WHERE id = ?', (deal_id,)) as cursor:
            row = await cursor.fetchone()
            if row:
                columns = [description[0] for description in cursor.description]
                return dict(zip(columns, row))
            return None
    
    async def claim_merchant_deal(self, deal_id: int, user_id: int) -> bool:
        """Claim a merchant deal."""
        async with self.conn.execute('''
            SELECT * FROM merchant_deals WHERE id = ? AND available = 1
        ''', (deal_id,)) as cursor:
            result = await cursor.fetchone()
        
        if not result:
            return False
        
        columns = [description[0] for description in cursor.description]    
        async with self.conn.execute('SELECT coins FROM players WHERE user_id = ?', (user_id,)) as cursor:
            player = await cursor.fetchone()
        
        if not player:
            return False
        
        deal = dict(zip(columns, result))
        
        if deal['deal_type'] == 'buy':
            # Player buys from merchant
            if player[0] < deal['price']:
                return False
            await self.conn.execute('UPDATE players SET coins = coins - ? WHERE user_id = ?', (deal['price'], user_id))
            # Add item handled elsewhere
        elif deal['deal_type'] == 'sell':
            # Player sells to merchant - handled elsewhere for item checks
            await self.conn.execute('UPDATE players SET coins = coins + ? WHERE user_id = ?', (deal['price'], user_id))
        
        await self.conn.execute('UPDATE merchant_deals SET available = 0 WHERE id = ?', (deal_id,))
        await self.conn.commit()
        return True
