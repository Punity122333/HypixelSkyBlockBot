from typing import Dict, List, Optional, Any, TYPE_CHECKING
import time
import io
from .core import DatabaseCore

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import matplotlib.cm as cm
    import matplotlib.dates as mdates
    from datetime import datetime
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    if TYPE_CHECKING:
        import matplotlib.pyplot as plt
        import matplotlib.cm as cm
        from datetime import datetime
        import matplotlib.dates as mdates

class MarketGraphingDB(DatabaseCore):
    
    async def log_price(self, item_id: str, price: float, volume: int = 0, source: str = 'bazaar'):
        await self.execute(
            '''INSERT INTO market_price_history (item_id, price, volume, timestamp, source)
               VALUES (?, ?, ?, ?, ?)''',
            (item_id, price, volume, int(time.time()), source)
        )
        await self.commit()
    
    async def log_networth(self, user_id: int, networth: float):
        await self.execute(
            '''INSERT INTO player_networth_history (user_id, networth, timestamp)
               VALUES (?, ?, ?)''',
            (user_id, networth, int(time.time()))
        )
        await self.commit()
    
    async def get_price_history(self, item_id: str, days: int = 7) -> List[Dict[str, Any]]:
        cutoff_time = int(time.time()) - (days * 86400)
        rows = await self.fetchall(
            '''SELECT price, volume, timestamp FROM market_price_history
               WHERE item_id = ? AND timestamp >= ?
               ORDER BY timestamp ASC''',
            (item_id, cutoff_time)
        )
        return [{'price': row['price'], 'volume': row['volume'], 'timestamp': row['timestamp']} for row in rows]
    
    async def get_networth_history(self, user_id: int, days: int = 30) -> List[Dict[str, Any]]:
        cutoff_time = int(time.time()) - (days * 86400)
        rows = await self.fetchall(
            '''SELECT networth, timestamp FROM player_networth_history
               WHERE user_id = ? AND timestamp >= ?
               ORDER BY timestamp ASC''',
            (user_id, cutoff_time)
        )
        return [{'networth': row['networth'], 'timestamp': row['timestamp']} for row in rows]
    
    async def calculate_best_flips(self, days: int = 7) -> List[Dict[str, Any]]:
        cutoff_time = int(time.time()) - (days * 86400)
        
        rows = await self.fetchall(
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
            profit_margin = ((row['max_price'] - row['min_price']) / row['min_price']) * 100 if row['min_price'] > 0 else 0
            flips.append({
                'item_id': row['item_id'],
                'min_price': row['min_price'],
                'max_price': row['max_price'],
                'avg_volume': row['avg_volume'],
                'profit_margin': profit_margin,
                'potential_profit': row['max_price'] - row['min_price']
            })
        
        return flips
    
    def create_price_graph(self, price_data: List[Dict[str, Any]], item_id: str) -> Optional[io.BytesIO]:
        if not MATPLOTLIB_AVAILABLE:
            return None
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
        
        if not price_data:
            ax1.text(0.5, 0.5, 'No price data available', ha='center', va='center')
            ax2.text(0.5, 0.5, 'No volume data available', ha='center', va='center')
        else:
            timestamps = [datetime.fromtimestamp(d['timestamp']) for d in price_data]
            prices = [d['price'] for d in price_data]
            volumes = [d['volume'] for d in price_data]
            
            ax1.plot(timestamps, prices, marker='o', linestyle='-', linewidth=2, markersize=4)
            ax1.set_title(f'{item_id.replace("_", " ").title()} - Price History', fontsize=14, fontweight='bold')
            ax1.set_xlabel('Date')
            ax1.set_ylabel('Price (coins)')
            ax1.grid(True, alpha=0.3)
            ax1.tick_params(axis='x', rotation=45)
            
            ax2.bar(timestamps, volumes, alpha=0.7, color='green')
            ax2.set_title('Volume', fontsize=12)
            ax2.set_xlabel('Date')
            ax2.set_ylabel('Volume')
            ax2.grid(True, alpha=0.3)
            ax2.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        buf.seek(0)
        plt.close(fig)
        
        return buf
    
    def create_networth_graph(self, networth_data: List[Dict[str, Any]], username: str) -> Optional[io.BytesIO]:
        if not MATPLOTLIB_AVAILABLE:
            return None
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        if not networth_data:
            ax.text(0.5, 0.5, 'No networth data available', ha='center', va='center')
        else:
            timestamps = [datetime.fromtimestamp(d['timestamp']) for d in networth_data]
            networth = [d['networth'] for d in networth_data]
            
            date_nums = mdates.date2num(timestamps)
            ax.plot(date_nums, networth, marker='o', linestyle='-', linewidth=2, markersize=6, color='gold')
            ax.fill_between(date_nums, networth, alpha=0.3, color='gold')
            ax.set_title(f'{username} - Networth History', fontsize=14, fontweight='bold')
            ax.set_xlabel('Date')
            ax.set_ylabel('Networth (coins)')
            ax.grid(True, alpha=0.3)
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
            ax.xaxis.set_major_locator(mdates.AutoDateLocator())
            ax.tick_params(axis='x', rotation=45)
            
            if len(networth) > 1:
                change = networth[-1] - networth[0]
                change_percent = (change / networth[0] * 100) if networth[0] > 0 else 0
                ax.text(0.02, 0.98, f'Total Change: {change:+,.0f} ({change_percent:+.1f}%)',
                       transform=ax.transAxes, verticalalignment='top',
                       bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        plt.tight_layout()
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        buf.seek(0)
        plt.close(fig)
        
        return buf
    
    def create_flip_comparison_graph(self, flips: List[Dict[str, Any]]) -> Optional[io.BytesIO]:
        if not MATPLOTLIB_AVAILABLE:
            return None
        
        fig, ax = plt.subplots(figsize=(14, 8))
        
        if not flips:
            ax.text(0.5, 0.5, 'No flip data available', ha='center', va='center')
        else:
            items = [f['item_id'].replace('_', ' ').title()[:20] for f in flips]
            profits = [f['potential_profit'] for f in flips]
            margins = [f['profit_margin'] for f in flips]
            
            cmap = cm.get_cmap('RdYlGn')
            colors = cmap([m/100 for m in margins])
            
            bars = ax.barh(items, profits, color=colors)
            ax.set_xlabel('Potential Profit (coins)', fontsize=12)
            ax.set_title('Best Bazaar Flips - Profit Comparison', fontsize=14, fontweight='bold')
            ax.grid(True, alpha=0.3, axis='x')
            
            for i, (bar, margin) in enumerate(zip(bars, margins)):
                width = bar.get_width()
                ax.text(width, bar.get_y() + bar.get_height()/2, f' {margin:.1f}%',
                       ha='left', va='center', fontsize=9)
        
        plt.tight_layout()
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        buf.seek(0)
        plt.close(fig)
        
        return buf
    
    async def calculate_networth(self, user_id: int) -> float:
        player = await self.fetchone('SELECT coins, bank FROM player_economy WHERE user_id = ?', (user_id,))
        if not player:
            return 0.0
        
        coins = player['coins'] or 0
        bank = player['bank'] or 0
        
        inventory = await self.fetchall('SELECT item_id, amount FROM inventory_items WHERE user_id = ?', (user_id,))
        
        item_value = 0.0
        for item in inventory:
            price_row = await self.fetchone(
                '''SELECT price FROM market_price_history
                   WHERE item_id = ?
                   ORDER BY timestamp DESC
                   LIMIT 1''',
                (item['item_id'],)
            )
            if price_row:
                item_value += price_row['price'] * item['amount']
        
        return float(coins + bank + item_value)
