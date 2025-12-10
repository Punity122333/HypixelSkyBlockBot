import discord
from components.buttons.market_graphs_buttons import (
    MarketGraphsPriceButton,
    MarketGraphsNetworthButton,
    MarketGraphsFlipsButton,
    MarketGraphsRefreshButton
)

class MarketGraphsView(discord.ui.View):
    def __init__(self, bot, user_id):
        super().__init__(timeout=180)
        self.bot = bot
        self.user_id = user_id
        self.current_view = 'main'
        self.selected_item = None
        self.days = 7
        
        self.price_button = MarketGraphsPriceButton(self)
        self.networth_button = MarketGraphsNetworthButton(self)
        self.flips_button = MarketGraphsFlipsButton(self)
        self.refresh_button = MarketGraphsRefreshButton(self)
        
        self._update_buttons()
    
    def _update_buttons(self):
        self.clear_items()
        
        if self.current_view == 'main':
            self.add_item(self.price_button)
            self.add_item(self.networth_button)
            self.add_item(self.flips_button)
        else:
            self.add_item(self.refresh_button)
    
    async def get_embed(self):
        if self.current_view == 'main':
            return await self.get_main_embed()
        elif self.current_view == 'price':
            return await self.get_price_embed()
        elif self.current_view == 'networth':
            return await self.get_networth_embed()
        elif self.current_view == 'flips':
            return await self.get_flips_embed()
        else:
            return await self.get_main_embed()
    
    async def get_main_embed(self):
        embed = discord.Embed(
            title="📊 Market Graphs",
            description="View market analytics and trends",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="📈 Price History",
            value="Track item price trends over time",
            inline=False
        )
        embed.add_field(
            name="💰 Networth Graph",
            value="View your networth progression",
            inline=False
        )
        embed.add_field(
            name="💹 Best Flips",
            value="Discover profitable flip opportunities",
            inline=False
        )
        
        return embed
    
    async def get_price_embed(self):
        embed = discord.Embed(
            title="📈 Price History",
            description="Select an item to view price history",
            color=discord.Color.blue()
        )
        return embed
    
    async def get_networth_embed(self):
        embed = discord.Embed(
            title="💰 Networth Graph",
            description="Your networth progression",
            color=discord.Color.gold()
        )
        return embed
    
    async def get_flips_embed(self):
        embed = discord.Embed(
            title="💹 Best Flips",
            description="Most profitable flip opportunities",
            color=discord.Color.green()
        )
        return embed
