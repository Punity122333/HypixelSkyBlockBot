import random
import time
import json
from typing import Dict, List, Optional, Any, Tuple


class EconomySystem:
    
    BAZAAR_TAX_RATE = 0.01
    AUCTION_TAX_RATE = 0.02
    
    @classmethod
    async def get_item_value(cls, db, item_id: str) -> int:
        if not db.conn:
            return 0
        
        cursor = await db.conn.execute('''
            SELECT npc_sell_price, default_bazaar_price FROM game_items WHERE item_id = ?
        ''', (item_id,))
        item_data = await cursor.fetchone()
        
        if not item_data:
            return 0
        
        npc_price = item_data['npc_sell_price'] or 0
        bazaar_price = item_data['default_bazaar_price'] or 0
        
        return max(npc_price, bazaar_price)
    
    @classmethod
    async def buy_from_npc(cls, db, user_id: int, item_id: str, amount: int) -> Dict[str, Any]:
        price = await cls.get_item_value(db, item_id)
        
        bestiary_discount = await db.bestiary.calculate_bestiary_merchant_discount(user_id)
        price = int(price * bestiary_discount)
        
        total_cost = price * amount
        
        player = await db.get_player(user_id)
        if not player or player['coins'] < total_cost:
            return {
                'success': False,
                'error': 'Insufficient coins'
            }
        
        await db.update_player(user_id, coins=player['coins'] - total_cost)
        await db.add_item_to_inventory(user_id, item_id, amount)
        
        return {
            'success': True,
            'item_id': item_id,
            'amount': amount,
            'total_cost': total_cost,
            'discount_applied': bestiary_discount
        }
    
    @classmethod
    async def sell_to_npc(cls, db, user_id: int, item_id: str, amount: int) -> Dict[str, Any]:
        item_count = await db.get_item_count(user_id, item_id)
        if item_count < amount:
            return {
                'success': False,
                'error': 'Insufficient items'
            }
        
        price = await cls.get_item_value(db, item_id)
        
        bestiary_bonus = await db.bestiary.calculate_bestiary_merchant_discount(user_id)
        sell_multiplier = 2.0 - bestiary_bonus
        price = int(price * sell_multiplier)
        
        total_value = price * amount
        
        await db.remove_item_from_inventory(user_id, item_id, amount)
        
        player = await db.get_player(user_id)
        if player:
            await db.update_player(user_id, coins=player['coins'] + total_value)
        
        return {
            'success': True,
            'item_id': item_id,
            'amount': amount,
            'total_value': total_value,
            'bonus_applied': sell_multiplier
        }
    
    @classmethod
    async def create_bazaar_order(cls, db, user_id: int, product_id: str, order_type: str, 
                                  amount: int, unit_price: float) -> Dict[str, Any]:
        if order_type not in ['buy', 'sell']:
            return {'success': False, 'error': 'Invalid order type'}
        
        if order_type == 'buy':
            total_cost = int(amount * unit_price)
            player = await db.get_player(user_id)
            
            if not player or player['coins'] < total_cost:
                return {'success': False, 'error': 'Insufficient coins'}
            
            await db.update_player(user_id, coins=player['coins'] - total_cost)
        else:
            item_count = await db.get_item_count(user_id, product_id)
            if item_count < amount:
                return {'success': False, 'error': 'Insufficient items'}
            
            await db.remove_item_from_inventory(user_id, product_id, amount)
        
        await db.create_bazaar_order(user_id, product_id, order_type, amount, unit_price)
        
        return {
            'success': True,
            'order_type': order_type,
            'product_id': product_id,
            'amount': amount,
            'unit_price': unit_price
        }
    
    @classmethod
    async def instant_buy_bazaar(cls, db, user_id: int, product_id: str, amount: int) -> Dict[str, Any]:
        bazaar_product = await db.get_bazaar_product(product_id)
        if not bazaar_product:
            return {'success': False, 'error': 'Product not found'}
        
        sell_price = bazaar_product['sell_price']
        total_cost = int(amount * sell_price * (1 + cls.BAZAAR_TAX_RATE))
        
        player = await db.get_player(user_id)
        if not player or player['coins'] < total_cost:
            return {'success': False, 'error': 'Insufficient coins'}
        
        await db.update_player(user_id, coins=player['coins'] - total_cost)
        await db.add_item_to_inventory(user_id, product_id, amount)
        
        new_sell_price = sell_price * 1.01
        await db.update_bazaar_product(
            product_id, 
            bazaar_product['buy_price'],
            new_sell_price,
            bazaar_product.get('buy_volume', 0),
            bazaar_product.get('sell_volume', 0) + amount
        )
        
        return {
            'success': True,
            'product_id': product_id,
            'amount': amount,
            'unit_price': sell_price,
            'total_cost': total_cost,
            'tax': int(amount * sell_price * cls.BAZAAR_TAX_RATE)
        }
    
    @classmethod
    async def instant_sell_bazaar(cls, db, user_id: int, product_id: str, amount: int) -> Dict[str, Any]:
        item_count = await db.get_item_count(user_id, product_id)
        if item_count < amount:
            return {'success': False, 'error': 'Insufficient items'}
        
        bazaar_product = await db.get_bazaar_product(product_id)
        if not bazaar_product:
            return {'success': False, 'error': 'Product not found'}
        
        buy_price = bazaar_product['buy_price']
        total_value = int(amount * buy_price * (1 - cls.BAZAAR_TAX_RATE))
        
        await db.remove_item_from_inventory(user_id, product_id, amount)
        
        player = await db.get_player(user_id)
        if player:
            await db.update_player(user_id, coins=player['coins'] + total_value)
        
        new_buy_price = buy_price * 0.99
        await db.update_bazaar_product(
            product_id,
            new_buy_price,
            bazaar_product['sell_price'],
            bazaar_product.get('buy_volume', 0) + amount,
            bazaar_product.get('sell_volume', 0)
        )
        
        return {
            'success': True,
            'product_id': product_id,
            'amount': amount,
            'unit_price': buy_price,
            'total_value': total_value,
            'tax': int(amount * buy_price * cls.BAZAAR_TAX_RATE)
        }
    
    @classmethod
    async def create_auction(cls, db, user_id: int, item_id: str, amount: int, 
                            starting_bid: int, duration_hours: int, bin_price: Optional[int] = None) -> Dict[str, Any]:
        item_count = await db.get_item_count(user_id, item_id)
        if item_count < amount:
            return {'success': False, 'error': 'Insufficient items'}
        
        duration_seconds = duration_hours * 3600
        is_bin = bin_price is not None and bin_price > 0
        auction_id = await db.create_auction(
            user_id, item_id, amount, starting_bid, bin_price, duration_seconds, is_bin
        )
        
        return {
            'success': True,
            'auction_id': auction_id,
            'item_id': item_id,
            'amount': amount,
            'starting_bid': starting_bid,
            'duration': duration_hours,
            'bin_price': bin_price
        }
    
    @classmethod
    async def place_bid(cls, db, user_id: int, auction_id: int, bid_amount: int) -> Dict[str, Any]:
        player = await db.get_player(user_id)
        if not player or player['coins'] < bid_amount:
            return {'success': False, 'error': 'Insufficient coins'}
        
        success = await db.place_bid(user_id, auction_id, bid_amount)
        
        if not success:
            return {'success': False, 'error': 'Bid failed'}
        
        await db.update_player(user_id, coins=player['coins'] - bid_amount)
        
        return {
            'success': True,
            'auction_id': auction_id,
            'bid_amount': bid_amount
        }
    
    @classmethod
    async def buy_bin(cls, db, user_id: int, auction_id: int) -> Dict[str, Any]:
        if not db.conn:
            return {'success': False, 'error': 'Database not connected'}
        
        cursor = await db.conn.execute('''
            SELECT ah.*, ai.item_id, ai.amount
            FROM auction_house ah
            JOIN auction_items ai ON ah.id = ai.auction_id
            WHERE ah.id = ? AND ah.bin = 1 AND ah.ended = 0
        ''', (auction_id,))
        auction = await cursor.fetchone()
        
        if not auction:
            return {'success': False, 'error': 'Auction not found'}
        
        bin_price = auction['buy_now_price']
        if not bin_price or bin_price <= 0:
            return {'success': False, 'error': 'Invalid BIN price'}
        
        player = await db.get_player(user_id)
        
        if not player or player['coins'] < bin_price:
            return {'success': False, 'error': 'Insufficient coins'}
        
        success = await db.buy_bin(user_id, auction_id, bin_price)
        
        if not success:
            return {'success': False, 'error': 'Purchase failed'}
        
        return {
            'success': True,
            'auction_id': auction_id,
            'item_id': auction['item_id'],
            'amount': auction['amount'],
            'price': bin_price
        }
    
    @classmethod
    async def update_market_prices(cls, db):
        if not db.conn:
            return
        
        cursor = await db.conn.execute('''
            SELECT product_id, buy_price, sell_price FROM bazaar_products
        ''')
        products = await cursor.fetchall()
        
        for product in products:
            volatility = random.uniform(-0.05, 0.05)
            new_buy_price = product['buy_price'] * (1 + volatility)
            new_sell_price = product['sell_price'] * (1 + volatility)
            
            await db.update_bazaar_product(
                product['product_id'],
                new_buy_price,
                new_sell_price,
                0,
                0
            )
    
    @classmethod
    async def calculate_bazaar_profit(cls, db, product_id: str, amount: int) -> Dict[str, Any]:
        bazaar_product = await db.get_bazaar_product(product_id)
        if not bazaar_product:
            return {'potential_profit': 0, 'margin': 0}
        
        buy_price = bazaar_product['buy_price']
        sell_price = bazaar_product['sell_price']
        
        buy_cost = amount * sell_price * (1 + cls.BAZAAR_TAX_RATE)
        sell_value = amount * buy_price * (1 - cls.BAZAAR_TAX_RATE)
        
        profit = sell_value - buy_cost
        margin = (profit / buy_cost * 100) if buy_cost > 0 else 0
        
        return {
            'potential_profit': profit,
            'margin': margin,
            'buy_cost': buy_cost,
            'sell_value': sell_value
        }
    
    @classmethod
    async def get_best_flips(cls, db, budget: int, limit: int = 10) -> List[Dict[str, Any]]:
        if not db.conn:
            return []
        
        cursor = await db.conn.execute('''
            SELECT product_id, buy_price, sell_price FROM bazaar_products
        ''')
        products = await cursor.fetchall()
        
        flips = []
        
        for product in products:
            buy_price = product['buy_price']
            sell_price = product['sell_price']
            
            if sell_price <= 0 or buy_price <= 0:
                continue
            
            max_amount = int(budget / (sell_price * (1 + cls.BAZAAR_TAX_RATE)))
            
            if max_amount <= 0:
                continue
            
            profit_calc = await cls.calculate_bazaar_profit(db, product['product_id'], max_amount)
            
            if profit_calc['potential_profit'] > 0:
                flips.append({
                    'product_id': product['product_id'],
                    'amount': max_amount,
                    'profit': profit_calc['potential_profit'],
                    'margin': profit_calc['margin'],
                    'investment': profit_calc['buy_cost']
                })
        
        flips.sort(key=lambda x: x['profit'], reverse=True)
        
        return flips[:limit]
