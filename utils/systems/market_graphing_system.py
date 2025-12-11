import io
import time
from typing import Dict, List, Optional, Any
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta

class MarketGraphingSystem:
    
    @staticmethod
    async def log_price(db, item_id: str, price: float, volume: int = 0, source: str = 'bazaar'):
        await db.market_graphing.log_price(item_id, price, volume, source)
    
    @staticmethod
    async def log_networth(db, user_id: int, networth: float):
        await db.market_graphing.log_networth(user_id, networth)
    
    @staticmethod
    async def get_price_history(db, item_id: str, days: int = 7) -> List[Dict[str, Any]]:
        return await db.market_graphing.get_price_history(item_id, days)
    
    @staticmethod
    async def get_networth_history(db, user_id: int, days: int = 30) -> List[Dict[str, Any]]:
        return await db.market_graphing.get_networth_history(user_id, days)
    
    @staticmethod
    async def calculate_best_flips(db, days: int = 7) -> List[Dict[str, Any]]:
        cutoff_time = int(time.time()) - (days * 86400)
        
        rows = await db.fetchall(
            '''SELECT item_id, MIN(price) as min_price, MAX(price) as max_price,
                      AVG(volume) as avg_volume
               FROM market_price_history
               WHERE timestamp >= ?
               GROUP BY item_id
               HAVING COUNT(*) >= 2
               ORDER BY (max_price - min_price) DESC
               LIMIT 20''',
            (cutoff_time,)
        )
        
        flips = []
        for row in rows:
            item_id, min_price, max_price, avg_volume = row
            profit = max_price - min_price
            profit_percent = (profit / min_price * 100) if min_price > 0 else 0
            flips.append({
                'item_id': item_id,
                'buy_price': min_price,
                'sell_price': max_price,
                'profit': profit,
                'profit_percent': profit_percent,
                'avg_volume': avg_volume or 0
            })
        
        return flips
    
    @staticmethod
    def create_price_graph(price_data: List[Dict[str, Any]], item_id: str) -> io.BytesIO:
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
        
        if not price_data:
            ax1.text(0.5, 0.5, 'No price data available', ha='center', va='center')
            ax2.text(0.5, 0.5, 'No volume data available', ha='center', va='center')
        else:
            timestamps = [datetime.fromtimestamp(d['timestamp']) for d in price_data]
            prices = [d['price'] for d in price_data]
            volumes = [d['volume'] for d in price_data]
            
            ax1.plot(timestamps, prices, marker='o', linestyle='-', color='#2ecc71', linewidth=2, markersize=4)
            ax1.fill_between(timestamps, prices, alpha=0.3, color='#2ecc71')
            ax1.set_title(f'{item_id.replace("_", " ").title()} - Price History', fontsize=16, fontweight='bold')
            ax1.set_ylabel('Price (coins)', fontsize=12)
            ax1.grid(True, alpha=0.3)
            ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
            
            ax2.bar(timestamps, volumes, color='#3498db', alpha=0.7, width=0.02)
            ax2.set_title('Trading Volume', fontsize=14, fontweight='bold')
            ax2.set_xlabel('Date', fontsize=12)
            ax2.set_ylabel('Volume', fontsize=12)
            ax2.grid(True, alpha=0.3)
            ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
        
        plt.tight_layout()
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        buf.seek(0)
        plt.close(fig)
        
        return buf
    
    @staticmethod
    def create_networth_graph(networth_data: List[Dict[str, Any]], username: str) -> io.BytesIO:
        fig, ax = plt.subplots(figsize=(12, 6))
        
        if not networth_data:
            ax.text(0.5, 0.5, 'No networth data available yet', ha='center', va='center', fontsize=14)
        else:
            import numpy as np
            timestamps = [datetime.fromtimestamp(d['timestamp']) for d in networth_data]
            networth = [d['networth'] for d in networth_data]
            
            timestamps_np = np.array(timestamps)
            networth_np = np.array(networth)
            
            ax.plot(timestamps_np, networth_np, marker='o', linestyle='-', color='#f39c12', linewidth=3, markersize=6)
            ax.fill_between(timestamps_np, networth_np, alpha=0.3, color='#f39c12')
            
            start_value = networth[0]
            end_value = networth[-1]
            change = end_value - start_value
            change_percent = (change / start_value * 100) if start_value > 0 else 0
            
            color = '#2ecc71' if change >= 0 else '#e74c3c'
            sign = '+' if change >= 0 else ''
            ax.set_title(
                f'{username}\'s Networth History\n{sign}{change:,.0f} coins ({sign}{change_percent:.1f}%)',
                fontsize=16, fontweight='bold', color=color
            )
            
            ax.set_ylabel('Networth (coins)', fontsize=12)
            ax.set_xlabel('Date', fontsize=12)
            ax.grid(True, alpha=0.3)
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d %H:%M'))
            
            for label in ax.get_yticklabels():
                label.set_fontsize(10)
            for label in ax.get_xticklabels():
                label.set_rotation(45)
                label.set_fontsize(10)
        
        plt.tight_layout()
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        buf.seek(0)
        plt.close(fig)
        
        return buf
    
    @staticmethod
    def create_flip_comparison_graph(flips: List[Dict[str, Any]]) -> io.BytesIO:
        fig, ax = plt.subplots(figsize=(14, 8))
        
        if not flips:
            ax.text(0.5, 0.5, 'No flip data available', ha='center', va='center', fontsize=14)
        else:
            flips_sorted = sorted(flips[:10], key=lambda x: x['profit'], reverse=True)
            items = [f['item_id'].replace('_', ' ').title()[:20] for f in flips_sorted]
            profits = [f['profit'] for f in flips_sorted]
            
            colors = ['#2ecc71' if p > 0 else '#e74c3c' for p in profits]
            bars = ax.barh(items, profits, color=colors, alpha=0.8)
            
            for i, (bar, flip) in enumerate(zip(bars, flips_sorted)):
                width = bar.get_width()
                ax.text(width, bar.get_y() + bar.get_height()/2,
                       f' +{width:,.0f} ({flip["profit_percent"]:.1f}%)',
                       va='center', fontsize=10, fontweight='bold')
            
            ax.set_title('Top 10 Most Profitable Flips (7 Days)', fontsize=16, fontweight='bold')
            ax.set_xlabel('Profit (coins)', fontsize=12)
            ax.grid(True, alpha=0.3, axis='x')
        
        plt.tight_layout()
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        buf.seek(0)
        plt.close(fig)
        
        return buf
    
    @staticmethod
    async def calculate_networth(db, user_id: int) -> float:
        player = await db.get_player(user_id)
        if not player:
            return 0.0
        
        coins = player.get('coins', 0)
        bank = player.get('bank', 0)
        
        inventory = await db.get_inventory(user_id)
        inventory_value = 0
        for item in inventory:
            item_data = await db.game_data.get_game_item(item['item_id'])
            if item_data:
                base_price = item_data.get('npc_sell_price', 0) or item_data.get('default_bazaar_price', 0) or 0
                inventory_value += base_price * item.get('amount', 1)
        
        return float(coins + bank + inventory_value)
