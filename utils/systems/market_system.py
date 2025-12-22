import random
from typing import Dict, List, Optional, TYPE_CHECKING, Any
import time

if TYPE_CHECKING:
    from database import GameDatabase

class MarketSystem:
    def __init__(self, db: 'GameDatabase'):
        self.db = db
        self.price_cache: Dict[str, Dict] = {}
        self.base_prices: Dict[str, float] = {}
        self.supply_demand: Dict[str, Dict] = {}
        self.game_data: Optional[Any] = None
    
    async def initialize(self, game_data: Any) -> None:
        self.game_data = game_data
        await self._initialize_base_prices(game_data)
        await self._initialize_supply_demand(game_data)
    
    async def _initialize_base_prices(self, game_data: Any) -> None:
        try:
            from utils.data.all_items import ALL_ITEMS
            for item_id, item in ALL_ITEMS.items():
                self.base_prices[item_id] = item.default_bazaar_price
        except Exception:
            pass
    
    async def _initialize_supply_demand(self, game_data: Any) -> None:
        try:
            from utils.data.all_items import ALL_ITEMS
            for item_id in ALL_ITEMS.keys():
                self.supply_demand[item_id] = {
                    'supply': random.uniform(0.8, 1.2),
                    'demand': random.uniform(0.8, 1.2),
                    'trend': random.choice(['stable', 'rising', 'falling']),
                    'last_update': time.time()
                }
        except Exception:
            pass
    
    def update_supply_demand(self, item_id: str, transaction_type: str, quantity: int):
        if item_id not in self.supply_demand:
            self.supply_demand[item_id] = {
                'supply': 1.0,
                'demand': 1.0,
                'trend': 'stable',
                'last_update': time.time()
            }
        
        sd = self.supply_demand[item_id]
        
        if transaction_type == 'buy':
            sd['demand'] = min(sd['demand'] + (quantity * 0.001), 2.0)
            sd['supply'] = max(sd['supply'] - (quantity * 0.0005), 0.3)
        elif transaction_type == 'sell':
            sd['supply'] = min(sd['supply'] + (quantity * 0.001), 2.0)
            sd['demand'] = max(sd['demand'] - (quantity * 0.0005), 0.3)
        
        ratio = sd['demand'] / sd['supply']
        if ratio > 1.3:
            sd['trend'] = 'rising'
        elif ratio < 0.7:
            sd['trend'] = 'falling'
        else:
            sd['trend'] = 'stable'
        
        sd['last_update'] = time.time()
    
    def get_base_price(self, item_id: str) -> float:
        return self.base_prices.get(item_id, 100)
    
    async def calculate_market_price(self, product_id: str) -> tuple[float, float]:
        base_price = self.get_base_price(product_id)
        
        sd = self.supply_demand.get(product_id, {'supply': 1.0, 'demand': 1.0, 'trend': 'stable'})
        supply_demand_factor = sd['demand'] / sd['supply']
        
        history = await self.db.get_market_history(product_id, 50)
        
        if history:
            recent_prices = [h['price'] for h in history[:10]]
            avg_price = sum(recent_prices) / len(recent_prices)
            
            trend_factor = 1.0
            if sd['trend'] == 'rising':
                trend_factor = random.uniform(1.05, 1.15)
            elif sd['trend'] == 'falling':
                trend_factor = random.uniform(0.85, 0.95)
            else:
                trend_factor = random.uniform(0.95, 1.05)
            
            buy_price = avg_price * supply_demand_factor * trend_factor
            sell_price = buy_price * 0.93
        else:
            variation = random.uniform(0.9, 1.1)
            buy_price = base_price * variation * supply_demand_factor
            sell_price = buy_price * 0.93
        
        return buy_price, sell_price
    
    async def update_bazaar_prices(self) -> None:
        from utils.systems.market_graphing_system import MarketGraphingSystem
        
        if not self.game_data:
            return
        try:
            from utils.data.all_items import ALL_ITEMS
            for item_id in list(ALL_ITEMS.keys())[:100]:
                buy_price, sell_price = await self.calculate_market_price(item_id)
                
                buy_volume = random.randint(100, 10000)
                sell_volume = random.randint(100, 10000)
                
                await self.db.update_bazaar_product(item_id, buy_price, sell_price, buy_volume, sell_volume)
                
                await MarketGraphingSystem.log_price(self.db, item_id, buy_price, buy_volume, 'bazaar')
        except Exception:
            pass
    
    async def instant_buy(self, user_id: int, product_id: str, amount: int) -> tuple[bool, str]:
        from utils.systems.market_graphing_system import MarketGraphingSystem
        
        product = await self.db.get_bazaar_product(product_id)
        if not product:
            return False, "Product not found"
        
        total_cost = int(product['buy_price'] * amount)
        
        player = await self.db.get_player(user_id)
        if not player or player['coins'] < total_cost:
            return False, f"Not enough coins! Need {total_cost:,}"
        
        await self.db.players.update_player(user_id, coins=player['coins'] - total_cost, total_spent=player.get('total_spent', 0) + total_cost)
        await self.db.add_item_to_inventory(user_id, product_id, amount)
        
        await self.db.execute_bazaar_transaction(-1, user_id, product_id, amount, product['buy_price'])
        
        self.update_supply_demand(product_id, 'buy', amount)
        
        await MarketGraphingSystem.log_price(self.db, product_id, product['buy_price'], amount, 'bazaar')
        
        networth = await MarketGraphingSystem.calculate_networth(self.db, user_id)
        await MarketGraphingSystem.log_networth(self.db, user_id, networth)
        
        return True, f"Bought {amount}x {product_id} for {total_cost:,} coins"
    
    async def instant_sell(self, user_id: int, product_id: str, amount: int) -> tuple[bool, str]:
        from utils.systems.market_graphing_system import MarketGraphingSystem
        
        item_count = await self.db.get_item_count(user_id, product_id)
        if item_count < amount:
            return False, f"You only have {item_count}x {product_id}"
        
        product = await self.db.get_bazaar_product(product_id)
        if not product:
            return False, "Product not found"
        
        total_gain = int(product['sell_price'] * amount)
        
        await self.db.remove_item_from_inventory(user_id, product_id, amount)
        
        player = await self.db.get_player(user_id)
        if player:
            await self.db.players.update_player(user_id, coins=player['coins'] + total_gain, total_earned=player.get('total_earned', 0) + total_gain)
        
        await self.db.execute_bazaar_transaction(user_id, -1, product_id, amount, product['sell_price'])
        
        self.update_supply_demand(product_id, 'sell', amount)
        
        await self.db.log_bazaar_flip(user_id, product_id, product['buy_price'], product['sell_price'], amount)
        
        await MarketGraphingSystem.log_price(self.db, product_id, product['sell_price'], amount, 'bazaar')
        
        networth = await MarketGraphingSystem.calculate_networth(self.db, user_id)
        await MarketGraphingSystem.log_networth(self.db, user_id, networth)
        
        return True, f"Sold {amount}x {product_id} for {total_gain:,} coins"
    
    async def create_buy_order(self, user_id: int, product_id: str, price: float, amount: int) -> tuple[bool, str]:
        total_cost = int(price * amount)
        
        player = await self.db.get_player(user_id)
        if not player or player['coins'] < total_cost:
            return False, f"Not enough coins! Need {total_cost:,}"
        
        await self.db.players.update_player(user_id, coins=player['coins'] - total_cost, total_spent=player.get('total_spent', 0) + total_cost)
        await self.db.create_bazaar_order(user_id, product_id, 'BUY', amount, price)
        
        return True, f"Created buy order for {amount}x {product_id} at {price:.1f} coins each"
    
    async def create_sell_order(self, user_id: int, product_id: str, price: float, amount: int) -> tuple[bool, str]:
        item_count = await self.db.get_item_count(user_id, product_id)
        if item_count < amount:
            return False, f"You only have {item_count}x {product_id}"
        
        await self.db.remove_item_from_inventory(user_id, product_id, amount)
        await self.db.create_bazaar_order(user_id, product_id, 'SELL', amount, price)
        
        return True, f"Created sell order for {amount}x {product_id} at {price:.1f} coins each"

class AuctionBotTrader:
    def __init__(self, db: 'GameDatabase', market: MarketSystem, bot_data: Dict):
        self.db = db
        self.market = market
        self.bot_id = bot_data['id']
        self.bot_name = bot_data['bot_name']
        self.coins = bot_data['coins']
        self.strategy = bot_data['trading_strategy']
        self.risk_tolerance = bot_data['risk_tolerance']
        self.items_owned = {}
    
    async def execute_strategy(self):
        if self.strategy == 'sniper':
            await self._sniper_strategy()
        elif self.strategy == 'bulk_trader':
            await self._bulk_trader_strategy()
        elif self.strategy == 'flipper':
            await self._flipper_strategy()
        elif self.strategy == 'long_term':
            await self._long_term_strategy()
        elif self.strategy == 'market_maker':
            await self._market_maker_strategy()
        elif self.strategy == 'opportunist':
            await self._opportunist_strategy()
        elif self.strategy == 'value_hunter':
            await self._value_hunter_strategy()
        elif self.strategy == 'trend_follower':
            await self._trend_follower_strategy()
    
    async def _sniper_strategy(self):
        if random.random() > 0.4:
            return
        
        auctions = await self.db.get_active_auctions(50)
        
        for auction in auctions:
            base_value = self.market.get_base_price(auction['item_id'])
            
            if auction['bin'] and auction['buy_now_price'] < base_value * (1 - self.risk_tolerance * 0.3):
                if self.coins >= auction['buy_now_price']:
                    success = await self.db.buy_bin(auction['id'], -self.bot_id, auction['buy_now_price'])
                    if success:
                        self.coins -= auction['buy_now_price']
                        await self.db.update_auction_bot(self.bot_id, coins=self.coins, trades_completed=self.bot_id)
                        break
    
    async def _bulk_trader_strategy(self):
        if random.random() > 0.3:
            return
        
        if not self.market.game_data:
            return
        all_items = await self.market.game_data.get_all_items()
        common_items = [item_id for item_id, item in all_items.items() if item.rarity in ['COMMON', 'UNCOMMON']]
        item_id = random.choice(common_items[:50])
        
        product = await self.db.get_bazaar_product(item_id)
        if not product:
            return
        
        if random.random() > 0.5:
            amount = random.randint(100, 500)
            cost = int(product['buy_price'] * amount * 1.05)
            if self.coins >= cost:
                await self.db.create_bazaar_order(-self.bot_id, item_id, 'BUY', product['buy_price'] * 1.05, amount)
        else:
            amount = random.randint(100, 500)
            await self.db.create_bazaar_order(-self.bot_id, item_id, 'SELL', product['sell_price'] * 0.95, amount)
    
    async def _flipper_strategy(self):
        if random.random() > 0.35:
            return
        
        if not self.market.game_data:
            return
        all_items = await self.market.game_data.get_all_items()
        tradeable_items = list(all_items.keys())[:50]
        item_id = random.choice(tradeable_items)
        
        product = await self.db.get_bazaar_product(item_id)
        if not product:
            return
        
        spread = product['buy_price'] - product['sell_price']
        if spread > product['buy_price'] * 0.1:
            amount = random.randint(10, 50)
            
            if random.random() > 0.5 and self.coins >= product['buy_price'] * amount:
                await self.db.create_bazaar_order(-self.bot_id, item_id, 'BUY', product['sell_price'] * 1.02, amount)
            else:
                await self.db.create_bazaar_order(-self.bot_id, item_id, 'SELL', product['buy_price'] * 0.98, amount)
    
    async def _long_term_strategy(self):
        if random.random() > 0.15:
            return
        
        if not self.market.game_data:
            return
        all_items = await self.market.game_data.get_all_items()
        rare_items = [item_id for item_id, item in all_items.items() if item.rarity in ['EPIC', 'LEGENDARY', 'MYTHIC']]
        
        if rare_items:
            item_id = random.choice(rare_items[:20])
            
            history = await self.db.get_market_history(item_id, 100)
            if len(history) > 20:
                recent_avg = sum(h['price'] for h in history[:10]) / 10
                older_avg = sum(h['price'] for h in history[10:20]) / 10
                
                if recent_avg < older_avg * 0.85:
                    product = await self.db.get_bazaar_product(item_id)
                    if product and self.coins >= product['buy_price'] * 5:
                        amount = random.randint(1, 5)
                        await self.db.create_bazaar_order(-self.bot_id, item_id, 'BUY', product['buy_price'], amount)
    
    async def _market_maker_strategy(self):
        if random.random() > 0.5:
            return
        
        if not self.market.game_data:
            return
        all_items = await self.market.game_data.get_all_items()
        item_id = random.choice(list(all_items.keys())[:50])
        
        product = await self.db.get_bazaar_product(item_id)
        if not product:
            return
        
        spread_percentage = 0.08
        buy_price = product['sell_price'] * (1 + spread_percentage / 2)
        sell_price = product['buy_price'] * (1 - spread_percentage / 2)
        
        amount = random.randint(20, 80)
        
        if self.coins >= buy_price * amount:
            await self.db.create_bazaar_order(-self.bot_id, item_id, 'BUY', buy_price, amount)
        
        await self.db.create_bazaar_order(-self.bot_id, item_id, 'SELL', sell_price, amount)
    
    async def _opportunist_strategy(self):
        if random.random() > 0.3:
            return
        
        if not self.market.game_data:
            return
        all_items = await self.market.game_data.get_all_items()
        items_to_check = random.sample(list(all_items.keys())[:50], min(10, len(list(all_items.keys())[:50])))
        
        for item_id in items_to_check:
            sd = self.market.supply_demand.get(item_id, {})
            
            if sd.get('trend') == 'rising':
                product = await self.db.get_bazaar_product(item_id)
                if product and self.coins >= product['buy_price'] * 20:
                    amount = random.randint(10, 30)
                    await self.db.create_bazaar_order(-self.bot_id, item_id, 'BUY', product['buy_price'] * 1.03, amount)
                    break
            elif sd.get('trend') == 'falling':
                product = await self.db.get_bazaar_product(item_id)
                if product:
                    await self.db.create_bazaar_order(-self.bot_id, item_id, 'SELL', product['sell_price'] * 0.97, random.randint(10, 30))
                    break
    
    async def _value_hunter_strategy(self):
        if random.random() > 0.25:
            return
        
        auctions = await self.db.get_active_auctions(30)
        
        for auction in auctions:
            base_value = self.market.get_base_price(auction['item_id'])
            current_bid = auction['current_bid']
            
            if current_bid < base_value * 0.7:
                if self.coins >= current_bid * 1.1:
                    new_bid = int(current_bid * random.uniform(1.05, 1.15))
                    if self.coins >= new_bid:
                        await self.db.place_bid(auction['id'], -self.bot_id, new_bid)
                        break
    
    async def _trend_follower_strategy(self):
        if random.random() > 0.35:
            return
        
        trending_items = []
        for item_id, sd in self.market.supply_demand.items():
            if sd.get('trend') == 'rising' and sd.get('demand', 1.0) > 1.2:
                trending_items.append(item_id)
        
        if trending_items:
            item_id = random.choice(trending_items)
            product = await self.db.get_bazaar_product(item_id)
            
            if product:
                amount = random.randint(15, 40)
                if self.coins >= product['buy_price'] * amount * 1.1:
                    await self.db.create_bazaar_order(-self.bot_id, item_id, 'BUY', product['buy_price'] * 1.08, amount)

class BazaarBotTrader:
    def __init__(self, db: 'GameDatabase', market: MarketSystem, bot_data: Dict):
        self.db = db
        self.market = market
        self.bot_id = bot_data['id']
        self.bot_name = bot_data['bot_name']
        self.coins = bot_data['coins']
        self.behavior = bot_data['trading_behavior']
    
    async def execute_trading_strategy(self):
        if not self.market.game_data:
            return
        all_items = await self.market.game_data.get_all_items()
        tradeable_items = list(all_items.keys())[:50]
        
        if self.behavior == 'aggressive':
            await self._aggressive_strategy(tradeable_items)
        elif self.behavior == 'conservative':
            await self._conservative_strategy(tradeable_items)
        elif self.behavior == 'balanced':
            await self._balanced_strategy(tradeable_items)
        elif self.behavior == 'opportunistic':
            await self._opportunistic_strategy(tradeable_items)
        elif self.behavior == 'market_maker':
            await self._market_maker_strategy(tradeable_items)
    
    async def _aggressive_strategy(self, items: List[str]):
        if random.random() > 0.3:
            return
        
        item = random.choice(items)
        product = await self.db.get_bazaar_product(item)
        if not product:
            return
        
        if random.random() > 0.5:
            price = product['buy_price'] * random.uniform(1.1, 1.3)
            amount = random.randint(10, 50)
            if self.coins >= price * amount:
                await self.db.create_bazaar_order(-self.bot_id, item, 'BUY', price, amount)
        else:
            price = product['sell_price'] * random.uniform(0.8, 0.95)
            amount = random.randint(10, 50)
            await self.db.create_bazaar_order(-self.bot_id, item, 'SELL', price, amount)
    
    async def _conservative_strategy(self, items: List[str]):
        if random.random() > 0.1:
            return
        
        item = random.choice(items)
        product = await self.db.get_bazaar_product(item)
        if not product:
            return
        
        price = product['buy_price'] * random.uniform(0.95, 1.05)
        amount = random.randint(5, 20)
        
        if random.random() > 0.5 and self.coins >= price * amount:
            await self.db.create_bazaar_order(-self.bot_id, item, 'BUY', price, amount)
        else:
            await self.db.create_bazaar_order(-self.bot_id, item, 'SELL', price, amount)
    
    async def _balanced_strategy(self, items: List[str]):
        if random.random() > 0.2:
            return
        
        item = random.choice(items)
        product = await self.db.get_bazaar_product(item)
        if not product:
            return
        
        price = product['buy_price'] * random.uniform(0.98, 1.12)
        amount = random.randint(15, 40)
        
        if random.random() > 0.5 and self.coins >= price * amount:
            await self.db.create_bazaar_order(-self.bot_id, item, 'BUY', price, amount)
        else:
            await self.db.create_bazaar_order(-self.bot_id, item, 'SELL', price, amount)
    
    async def _opportunistic_strategy(self, items: List[str]):
        if random.random() > 0.25:
            return
        
        for item in random.sample(items, 5):
            history = await self.db.get_market_history(item, 20)
            if len(history) < 10:
                continue
            
            recent_avg = sum(h['price'] for h in history[:5]) / 5
            older_avg = sum(h['price'] for h in history[5:10]) / 5
            
            if recent_avg < older_avg * 0.9:
                price = recent_avg * random.uniform(0.95, 1.05)
                amount = random.randint(20, 60)
                if self.coins >= price * amount:
                    await self.db.create_bazaar_order(-self.bot_id, item, 'BUY', amount, price)
                    break
            elif recent_avg > older_avg * 1.1:
                price = recent_avg * random.uniform(1.05, 1.15)
                amount = random.randint(20, 60)
                await self.db.create_bazaar_order(-self.bot_id, item, 'SELL', amount, price)
                break
    
    async def _market_maker_strategy(self, items: List[str]):
        if random.random() > 0.4:
            return
        
        item = random.choice(items)
        product = await self.db.get_bazaar_product(item)
        if not product:
            return
        
        spread = product['buy_price'] * 0.05
        
        buy_price = product['buy_price'] - spread
        sell_price = product['buy_price'] + spread
        
        amount = random.randint(25, 75)
        
        if self.coins >= buy_price * amount:
            await self.db.create_bazaar_order(-self.bot_id, item, 'BUY', buy_price, amount)
        
        await self.db.create_bazaar_order(-self.bot_id, item, 'SELL', sell_price, amount)

async def simulate_stock_market(db: 'GameDatabase'):
    stocks = await db.get_all_stocks()
    
    for stock in stocks:
        volatility = stock.get('volatility', 0.15)
        current_price = stock['current_price']
        
        change_percent = random.uniform(-volatility, volatility)
        new_price = current_price * (1 + change_percent)
        new_price = max(new_price, current_price * 0.5)
        new_price = min(new_price, current_price * 2.0)
        
        volume = random.randint(100, 5000)
        change_percent = change_percent * 100
        
        symbol = stock.get('stock_symbol') or stock.get('symbol') or 'UNKNOWN'
        await db.update_stock_price(symbol, new_price, change_percent, volume)

async def generate_merchant_deals(db: 'GameDatabase', game_data: Any):
    import time
    current_time = int(time.time())
    
    deals = await db.get_active_merchant_deals()
    deals_list = list(deals) if deals else []
    
    active_deals = []
    for deal in deals_list:
        deal_dict = dict(deal)
        created_at = deal_dict.get('created_at', current_time)
        duration = deal_dict.get('duration', 3600)
        if current_time - created_at < duration and deal_dict.get('stock', 0) > 0:
            active_deals.append(deal_dict)
    
    deals_to_create = max(0, 5 - len(active_deals))
    
    if deals_to_create > 0:
        merchants = ['Adventurer Sam', 'Trader Rick', 'Merchant Luna', 'Dealer Alex']
        all_items = await game_data.get_all_items()
        
        for _ in range(deals_to_create):
            merchant = random.choice(merchants)
            
            if isinstance(all_items, dict):
                tradeable_items = list(all_items.keys())[:100]
                item_id = random.choice(tradeable_items) if tradeable_items else None
                item = all_items.get(item_id) if item_id else None
            elif isinstance(all_items, list) and all_items:
                tradeable_items = all_items[:100]
                item = random.choice(tradeable_items) if tradeable_items else None
                item_id = item.get('item_id') if isinstance(item, dict) else getattr(item, 'id', None)
            else:
                continue
            
            if item and item_id:
                if isinstance(item, dict):
                    base_price = item.get('default_bazaar_price', 100)
                else:
                    base_price = getattr(item, 'default_bazaar_price', 100)
                
                deal_type = random.choice(['buy', 'sell'])
                quantity = random.randint(1, 10)
                
                if deal_type == 'buy':
                    price = int(base_price * random.uniform(0.7, 0.9) * quantity)
                else:
                    price = int(base_price * random.uniform(1.1, 1.3) * quantity)
                
                duration = random.randint(1800, 7200)
                
                await db.create_merchant_deal(str(item_id), price, quantity, duration, merchant, deal_type)

async def run_market_simulation(db: 'GameDatabase', market: MarketSystem):
    from utils.systems.market_graphing_system import MarketGraphingSystem
    
    try:
        await market.update_bazaar_prices()
        
        bazaar_bots = await db.get_active_bot_traders()
        bazaar_traders = [BazaarBotTrader(db, market, dict(bot)) for bot in bazaar_bots]
        
        for trader in bazaar_traders:
            await trader.execute_trading_strategy()
        
        auction_bots = await db.get_auction_bots()
        auction_traders = [AuctionBotTrader(db, market, dict(bot)) for bot in auction_bots]
        
        for trader in auction_traders:
            await trader.execute_strategy()
        
        await db.end_expired_auctions()
        
        await simulate_stock_market(db)
        
        if market.game_data:
            await generate_merchant_deals(db, market.game_data)
        
        all_players = await db.fetchall('SELECT user_id FROM players LIMIT 100')
        for player_row in all_players:
            try:
                user_id = player_row['user_id']
                networth = await MarketGraphingSystem.calculate_networth(db, user_id)
                if networth > 0:
                    await MarketGraphingSystem.log_networth(db, user_id, networth)
            except Exception:
                pass
                
    except Exception as e:
        print(f'Market simulation error details: {e}')
        import traceback
        traceback.print_exc()
