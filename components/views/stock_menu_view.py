import discord
import math
from components.buttons.stock_buttons import (
    StockPreviousButton,
    StockNextButton,
    StockPortfolioButton,
    StockRefreshButton,
    StockBuyButton,
    StockSellButton,
    StockInfoButton
)

class StockMenuView(discord.ui.View):
    def __init__(self, bot, user_id):
        super().__init__(timeout=180)
        self.bot = bot
        self.user_id = user_id
        self.current_page = 0
        self.stocks = []
        
        self.add_item(StockPreviousButton(self))
        self.add_item(StockNextButton(self))
        self.add_item(StockPortfolioButton(self))
        self.add_item(StockRefreshButton(self))
        self.add_item(StockBuyButton(self))
        self.add_item(StockSellButton(self))
        self.add_item(StockInfoButton(self))
    
    async def load_stocks(self):
        self.stocks = await self.bot.db.get_all_stocks()
    
    async def get_embed(self):
        embed = discord.Embed(
            title="📈 SkyBlock Stock Exchange",
            description="View and trade stocks",
            color=discord.Color.blue()
        )
        
        per_page = 4
        start = self.current_page * per_page
        end = start + per_page
        page_stocks = self.stocks[start:end]
        
        if not page_stocks:
            embed.description = "No stocks available at the moment."
        else:
            for stock in page_stocks:
                change = ((stock['current_price'] - stock['opening_price']) / stock['opening_price']) * 100
                emoji = "📈" if change > 0 else "📉" if change < 0 else "➡️"
                value = f"**${stock['current_price']:.2f}** {emoji}\nChange: {change:+.2f}%\nVol: {stock['volume']:,}\nHigh: ${stock['daily_high']:.2f} | Low: ${stock['daily_low']:.2f}"
                embed.add_field(name=f"{stock['symbol']} - {stock['company_name']}", value=value, inline=True)
        
        total_pages = math.ceil(len(self.stocks) / per_page) if len(self.stocks) > 0 else 1
        embed.set_footer(text=f"Page {self.current_page + 1}/{total_pages}")
        return embed
