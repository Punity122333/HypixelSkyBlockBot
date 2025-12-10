from typing import Dict, List, Optional
from .core import DatabaseCore
import time


class MarketDB(DatabaseCore):
    async def create_auction(self, seller_id: int, item_id: str, starting_bid: int, 
                           buy_now_price: Optional[int], duration: int, bin: bool = False, amount: int = 1):
        end_time = int(time.time()) + duration
        cursor = await self.execute(
            '''INSERT INTO auction_house (seller_id, item_id, starting_bid, current_bid, buy_now_price,
                                         end_time, bin, created_at, amount)
               VALUES (?, ?, ?, 0, ?, ?, ?, ?)''',
            (seller_id, item_id, starting_bid, buy_now_price, end_time, 1 if bin else 0, int(time.time()), amount)
        )
        auction_id = cursor.lastrowid
        
        await self.execute(
            'INSERT INTO auction_items (auction_id, item_id, amount) VALUES (?, ?, 1)',
            (auction_id, item_id)
        )
        await self.commit()
        return auction_id

    async def get_active_auctions(self, limit: int = 100) -> List[Dict]:
        rows = await self.fetchall(
            '''SELECT ah.*, ai.item_id, ai.amount
               FROM auction_house ah
               JOIN auction_items ai ON ah.id = ai.auction_id
               WHERE ah.ended = 0
               ORDER BY ah.created_at DESC
               LIMIT ?''',
            (limit,)
        )
        return [dict(row) for row in rows]

    async def get_bazaar_product(self, product_id: str) -> Optional[Dict]:
        row = await self.fetchone(
            'SELECT * FROM bazaar_products WHERE product_id = ?',
            (product_id,)
        )
        return dict(row) if row else None

    async def update_bazaar_product(self, product_id: str, buy_price: float, sell_price: float,
                                   buy_volume: int, sell_volume: int):
        await self.execute(
            '''INSERT INTO bazaar_products (product_id, buy_price, sell_price, buy_volume, sell_volume, last_update)
               VALUES (?, ?, ?, ?, ?, ?)
               ON CONFLICT(product_id)
               DO UPDATE SET buy_price = ?, sell_price = ?, buy_volume = ?, sell_volume = ?, last_update = ?''',
            (product_id, buy_price, sell_price, buy_volume, sell_volume, int(time.time()),
             buy_price, sell_price, buy_volume, sell_volume, int(time.time()))
        )
        await self.commit()

    async def execute_bazaar_transaction(self, buyer_id: int, seller_id: int, product_id: str,
                                        amount: int, price: float):
        await self.execute(
            '''INSERT INTO bazaar_transactions (buyer_id, seller_id, product_id, amount, price, timestamp)
               VALUES (?, ?, ?, ?, ?, ?)''',
            (buyer_id, seller_id, product_id, amount, price, int(time.time()))
        )
        await self.commit()

    async def get_all_stocks(self) -> List[Dict]:
        rows = await self.fetchall('SELECT * FROM stock_market')
        return [dict(row) for row in rows]

    async def get_stock(self, symbol: str) -> Optional[Dict]:
        row = await self.fetchone(
            'SELECT * FROM stock_market WHERE symbol = ?',
            (symbol,)
        )
        return dict(row) if row else None

    async def get_player_stocks(self, user_id: int) -> List[Dict]:
        rows = await self.fetchall(
            '''SELECT ps.*, sm.current_price, sm.company_name, sm.symbol as stock_symbol
               FROM player_stocks ps
               JOIN stock_market sm ON ps.symbol = sm.symbol
               WHERE ps.user_id = ?''',
            (user_id,)
        )
        return [dict(row) for row in rows]

    async def buy_stock(self, user_id: int, symbol: str, shares: int, price: float) -> bool:
        total_cost = shares * price
        
        row = await self.fetchone(
            'SELECT coins FROM player_economy WHERE user_id = ?',
            (user_id,)
        )
        
        if not row or row['coins'] < total_cost:
            return False
        
        await self.execute(
            'UPDATE player_economy SET coins = coins - ? WHERE user_id = ?',
            (total_cost, user_id)
        )
        
        await self.execute(
            '''INSERT INTO player_stocks (user_id, stock_symbol, shares, avg_buy_price)
               VALUES (?, ?, ?, ?)
               ON CONFLICT(user_id, stock_symbol)
               DO UPDATE SET shares = shares + ?, avg_buy_price = ((avg_buy_price * shares) + (? * ?)) / (shares + ?)''',
            (user_id, symbol, shares, price, shares, price, shares, shares)
        )
        await self.commit()
        return True

    async def sell_stock(self, user_id: int, symbol: str, shares: int, price: float) -> bool:
        row = await self.fetchone(
            'SELECT shares FROM player_stocks WHERE user_id = ? AND stock_symbol = ?',
            (user_id, symbol)
        )
        
        if not row or row['shares'] < shares:
            return False
        
        total_gain = shares * price
        
        await self.execute(
            'UPDATE player_economy SET coins = coins + ? WHERE user_id = ?',
            (total_gain, user_id)
        )
        
        if row['shares'] == shares:
            await self.execute(
                'DELETE FROM player_stocks WHERE user_id = ? AND stock_symbol = ?',
                (user_id, symbol)
            )
        else:
            await self.execute(
                'UPDATE player_stocks SET shares = shares - ? WHERE user_id = ? AND stock_symbol = ?',
                (shares, user_id, symbol)
            )
        
        await self.commit()
        return True

    async def get_market_history(self, symbol: str, limit: int = 50) -> List[Dict]:
        rows = await self.fetchall(
            '''SELECT * FROM market_history 
               WHERE product_id = ? 
               ORDER BY timestamp DESC 
               LIMIT ?''',
            (symbol, limit)
        )
        return [dict(row) for row in rows]

    async def add_stock_history(self, symbol: str, price: float, volume: int = 0):
        await self.execute(
            '''INSERT INTO market_history (product_id, price, volume, timestamp)
               VALUES (?, ?, ?, ?)''',
            (symbol, price, volume, int(time.time()))
        )
        await self.commit()

    async def update_stock_price(self, symbol: str, price: float, change_percent: float, volume: int):
        stock = await self.get_stock(symbol)
        if not stock:
            return
        
        daily_high = max(stock['daily_high'], price)
        daily_low = min(stock['daily_low'], price)
        
        await self.execute(
            '''UPDATE stock_market 
               SET current_price = ?, 
                   change_percent = ?,
                   daily_high = ?, 
                   daily_low = ?, 
                   volume = ?,
                   last_update = ?
               WHERE symbol = ?''',
            (price, change_percent, daily_high, daily_low, volume, int(time.time()), symbol)
        )
        await self.commit()
        await self.add_stock_history(symbol, price, volume)

    async def place_bid(self, user_id: int, auction_id: int, bid_amount: int) -> bool:
        auction = await self.fetchone(
            '''SELECT ah.*, ai.item_id, ai.amount
               FROM auction_house ah
               JOIN auction_items ai ON ah.id = ai.auction_id
               WHERE ah.id = ? AND ah.ended = 0''',
            (auction_id,)
        )
        if not auction:
            return False
        min_bid = max(auction['starting_bid'], auction['current_bid'] + 1)
        if bid_amount < min_bid:
            return False
        await self.execute(
            'UPDATE auction_house SET current_bid = ?, highest_bidder_id = ? WHERE id = ?',
            (bid_amount, user_id, auction_id)
        )
        await self.commit()
        return True
