from typing import Optional, Dict, Any, List
import json
import time
from .base import DatabaseBase


class MarketDatabase(DatabaseBase):
    """Database operations for auction house and bazaar."""
    
    # Auction House Methods
    async def create_auction(self, seller_id: int, item_id: str, item_data: Dict[str, Any], 
                           starting_bid: int, duration: int, bin_price: Optional[int] = None):
        """Create a new auction."""
        now = int(time.time())
        end_time = now + duration
        is_bin = 1 if bin_price else 0
        buy_now = bin_price if bin_price else 0
        
        await self.conn.execute('''
            INSERT INTO auction_house (seller_id, item_id, item_data, starting_bid, current_bid, 
                                      buy_now_price, end_time, bin, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (seller_id, item_id, json.dumps(item_data), starting_bid, starting_bid, buy_now, end_time, is_bin, now))
        await self.conn.commit()
        
        async with self.conn.execute('SELECT last_insert_rowid()') as cursor:
            result = await cursor.fetchone()
            return result[0] if result else None
    
    async def place_bid(self, auction_id: int, bidder_id: int, bid_amount: int):
        """Place a bid on an auction."""
        async with self.conn.execute(
            'SELECT current_bid, highest_bidder_id, ended FROM auction_house WHERE id = ?', (auction_id,)
        ) as cursor:
            result = await cursor.fetchone()
            if not result or result[2]:
                return False
            
            current_bid, highest_bidder_id = result[0], result[1]
            if bid_amount <= current_bid:
                return False
        
        # Return coins to previous bidder
        if highest_bidder_id:
            await self.conn.execute(
                'UPDATE players SET coins = coins + ? WHERE user_id = ?',
                (current_bid, highest_bidder_id)
            )
        
        await self.conn.execute('''
            UPDATE auction_house SET current_bid = ?, highest_bidder_id = ? WHERE id = ?
        ''', (bid_amount, bidder_id, auction_id))
        
        await self.conn.execute('''
            INSERT INTO auction_bids (auction_id, bidder_id, bid_amount, timestamp)
            VALUES (?, ?, ?, ?)
        ''', (auction_id, bidder_id, bid_amount, int(time.time())))
        
        await self.conn.commit()
        return True
    
    async def buy_bin(self, auction_id: int, buyer_id: int):
        """Buy an item via BIN (Buy It Now)."""
        async with self.conn.execute(
            'SELECT seller_id, item_id, item_data, buy_now_price, bin, ended FROM auction_house WHERE id = ?', 
            (auction_id,)
        ) as cursor:
            result = await cursor.fetchone()
            if not result or not result[4] or result[5]:
                return False
            
            seller_id, item_id, item_data, buy_now_price = result[0], result[1], result[2], result[3]
        
        # Check buyer has enough coins
        async with self.conn.execute('SELECT coins FROM players WHERE user_id = ?', (buyer_id,)) as cursor:
            buyer_data = await cursor.fetchone()
            if not buyer_data or buyer_data[0] < buy_now_price:
                return False
        
        # Process transaction
        await self.conn.execute(
            'UPDATE players SET coins = coins - ? WHERE user_id = ?',
            (buy_now_price, buyer_id)
        )
        
        await self.conn.execute(
            'UPDATE players SET coins = coins + ? WHERE user_id = ?',
            (buy_now_price, seller_id)
        )
        
        # Add item to buyer's inventory (simplified - would use inventory methods)
        await self.conn.execute(
            'UPDATE auction_house SET ended = 1, highest_bidder_id = ?, current_bid = ? WHERE id = ?',
            (buyer_id, buy_now_price, auction_id)
        )
        await self.conn.commit()
        return True
    
    async def get_active_auctions(self, limit: int = 50) -> List[Dict]:
        """Get all active auctions."""
        now = int(time.time())
        
        async with self.conn.execute('''
            SELECT * FROM auction_house 
            WHERE ended = 0 AND end_time > ?
            ORDER BY created_at DESC LIMIT ?
        ''', (now, limit)) as cursor:
            rows = await cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
    
    async def get_user_auctions(self, user_id: int) -> List[Dict]:
        """Get all auctions for a user."""
        async with self.conn.execute('''
            SELECT * FROM auction_house WHERE seller_id = ? AND ended = 0
            ORDER BY created_at DESC
        ''', (user_id,)) as cursor:
            rows = await cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
    
    async def end_expired_auctions(self):
        """End all expired auctions and process results."""
        now = int(time.time())
        
        async with self.conn.execute('''
            SELECT id, seller_id, highest_bidder_id, current_bid, item_id, item_data
            FROM auction_house WHERE ended = 0 AND end_time <= ?
        ''', (now,)) as cursor:
            expired = await cursor.fetchall()
        
        for auction in expired:
            auction_id, seller_id, highest_bidder_id, current_bid, item_id, item_data = auction
            
            if highest_bidder_id:
                # Winner gets item, seller gets coins (simplified)
                await self.conn.execute(
                    'UPDATE players SET coins = coins + ? WHERE user_id = ?',
                    (current_bid, seller_id)
                )
            # else: item returns to seller
            
            await self.conn.execute('UPDATE auction_house SET ended = 1 WHERE id = ?', (auction_id,))
        
        await self.conn.commit()
    
    # Bazaar Methods
    async def get_bazaar_product(self, product_id: str) -> Optional[Dict]:
        """Get bazaar product information."""
        async with self.conn.execute(
            'SELECT * FROM bazaar_products WHERE product_id = ?', (product_id,)
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                columns = [description[0] for description in cursor.description]
                return dict(zip(columns, row))
            return None
    
    async def get_all_bazaar_products(self) -> List[Dict]:
        """Get all bazaar products."""
        async with self.conn.execute(
            'SELECT * FROM bazaar_products ORDER BY last_update DESC'
        ) as cursor:
            rows = await cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
    
    async def update_bazaar_product(self, product_id: str, buy_price: float, sell_price: float, 
                                  buy_volume: int, sell_volume: int):
        """Update bazaar product prices and volumes."""
        await self.conn.execute('''
            INSERT OR REPLACE INTO bazaar_products 
            (product_id, buy_price, sell_price, buy_volume, sell_volume, last_update)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (product_id, buy_price, sell_price, buy_volume, sell_volume, int(time.time())))
        await self.conn.commit()
    
    async def create_bazaar_order(self, user_id: int, product_id: str, order_type: str, 
                                price: float, amount: int):
        """Create a bazaar buy or sell order."""
        await self.conn.execute('''
            INSERT INTO bazaar_orders (user_id, product_id, order_type, price, amount, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, product_id, order_type, price, amount, int(time.time())))
        await self.conn.commit()
    
    async def get_bazaar_orders(self, product_id: str, order_type: str) -> List[Dict]:
        """Get bazaar orders for a product."""
        async with self.conn.execute('''
            SELECT * FROM bazaar_orders 
            WHERE product_id = ? AND order_type = ? AND active = 1
            ORDER BY price DESC
        ''', (product_id, order_type)) as cursor:
            rows = await cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
    
    async def execute_bazaar_transaction(self, buyer_id: int, seller_id: int, product_id: str, 
                                       amount: int, price: float):
        """Execute a bazaar transaction."""
        total_cost = amount * price
        
        # Note: Coin validation should be done before calling this
        await self.conn.execute(
            'UPDATE players SET coins = coins - ? WHERE user_id = ?',
            (int(total_cost), buyer_id)
        )
        
        if seller_id > 0:  # Not a bot transaction
            await self.conn.execute(
                'UPDATE players SET coins = coins + ? WHERE user_id = ?',
                (int(total_cost), seller_id)
            )
        
        await self.conn.execute('''
            INSERT INTO bazaar_transactions (buyer_id, seller_id, product_id, amount, price, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (buyer_id, seller_id, product_id, amount, price, int(time.time())))
        
        await self.conn.execute('''
            INSERT INTO market_history (product_id, price, volume, timestamp, transaction_type)
            VALUES (?, ?, ?, ?, ?)
        ''', (product_id, price, amount, int(time.time()), 'bazaar'))
        
        await self.conn.commit()
        return True
    
    async def get_user_bazaar_orders(self, user_id: int) -> List[Dict]:
        """Get all active bazaar orders for a user."""
        async with self.conn.execute('''
            SELECT * FROM bazaar_orders WHERE user_id = ? AND active = 1
        ''', (user_id,)) as cursor:
            rows = await cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
    
    async def cancel_bazaar_order(self, order_id: int, user_id: int):
        """Cancel a bazaar order."""
        await self.conn.execute('''
            UPDATE bazaar_orders SET active = 0 WHERE id = ? AND user_id = ?
        ''', (order_id, user_id))
        await self.conn.commit()
    
    async def get_market_history(self, product_id: str, limit: int = 100) -> List[Dict]:
        """Get market price history for a product."""
        async with self.conn.execute('''
            SELECT * FROM market_history 
            WHERE product_id = ?
            ORDER BY timestamp DESC LIMIT ?
        ''', (product_id, limit)) as cursor:
            rows = await cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in rows]

    async def log_auction_snipe(self, user_id: int, auction_id: int, item_id: str, 
                              purchase_price: int, estimated_value: int):
        """Log an auction snipe."""
        profit = estimated_value - purchase_price
        await self.conn.execute('''
            INSERT INTO auction_snipes (user_id, auction_id, item_id, purchase_price, estimated_value, profit_potential, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, auction_id, item_id, purchase_price, estimated_value, profit, int(time.time())))
        await self.conn.commit()
    
    async def log_bazaar_flip(self, user_id: int, item_id: str, buy_price: float, 
                            sell_price: float, quantity: int):
        """Log a bazaar flip."""
        profit = int((sell_price - buy_price) * quantity)
        await self.conn.execute('''
            INSERT INTO bazaar_flips (user_id, item_id, buy_price, sell_price, quantity, profit, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, item_id, buy_price, sell_price, quantity, profit, int(time.time())))
        await self.conn.commit()
    
    async def get_top_flippers(self, limit: int = 10) -> List[Dict]:
        """Get top bazaar flippers by profit."""
        async with self.conn.execute('''
            SELECT user_id, SUM(profit) as total_profit, COUNT(*) as flip_count
            FROM bazaar_flips
            GROUP BY user_id
            ORDER BY total_profit DESC
            LIMIT ?
        ''', (limit,)) as cursor:
            rows = await cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
