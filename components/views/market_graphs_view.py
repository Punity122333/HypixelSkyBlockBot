import discord
from components.buttons.market_graphs_buttons import (
    MarketGraphsPriceButton,
    MarketGraphsNetworthButton,
    MarketGraphsFlipsButton,
    MarketGraphsRefreshButton
)
from utils.systems.market_graphing_system import MarketGraphingSystem

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
            return await self.get_main_embed(), None
        elif self.current_view == 'price':
            return await self.get_price_embed()
        elif self.current_view == 'networth':
            return await self.get_networth_embed()
        elif self.current_view == 'flips':
            return await self.get_flips_embed()
        else:
            return await self.get_main_embed(), None
    
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
        if self.selected_item:
            price_history = await MarketGraphingSystem.get_price_history(self.bot.db, self.selected_item, self.days)
            
            if not price_history:
                embed = discord.Embed(
                    title="📈 Price History",
                    description=f"No price data available for {self.selected_item}",
                    color=discord.Color.red()
                )
                return embed, None
            
            graph = MarketGraphingSystem.create_price_graph(price_history, self.selected_item)
            
            embed = discord.Embed(
                title=f"📈 {self.selected_item.replace('_', ' ').title()} - Price History",
                description=f"Last {self.days} days",
                color=discord.Color.blue()
            )
            embed.set_image(url="attachment://price_graph.png")
            
            return embed, discord.File(graph, filename="price_graph.png")
        else:
            embed = discord.Embed(
                title="📈 Price History",
                description="No item selected. Use dropdown to select an item.",
                color=discord.Color.blue()
            )
            return embed, None
    
    async def get_networth_embed(self):
        player = await self.bot.db.players.get_player(self.user_id)
        if not player:
            embed = discord.Embed(
                title="💰 Networth Graph",
                description="Player not found",
                color=discord.Color.red()
            )
            return embed, None
        
        networth_history = await MarketGraphingSystem.get_networth_history(self.bot.db, self.user_id, self.days)
        
        if not networth_history:
            embed = discord.Embed(
                title="💰 Networth Graph",
                description="No networth data available yet. Your networth will be tracked over time.",
                color=discord.Color.gold()
            )
            return embed, None
        
        graph = MarketGraphingSystem.create_networth_graph(networth_history, player['username'])
        
        embed = discord.Embed(
            title="💰 Networth Graph",
            description=f"Last {self.days} days",
            color=discord.Color.gold()
        )
        embed.set_image(url="attachment://networth_graph.png")
        
        return embed, discord.File(graph, filename="networth_graph.png")
    
    async def get_flips_embed(self):
        flips = await MarketGraphingSystem.calculate_best_flips(self.bot.db, self.days)
        
        if not flips:
            embed = discord.Embed(
                title="💹 Best Flips",
                description="No flip data available. Price data will be tracked over time.",
                color=discord.Color.green()
            )
            return embed, None
        
        graph = MarketGraphingSystem.create_flip_comparison_graph(flips)
        
        embed = discord.Embed(
            title="💹 Best Flips",
            description=f"Top profit opportunities (Last {self.days} days)",
            color=discord.Color.green()
        )
        embed.set_image(url="attachment://flips_graph.png")
        
        return embed, discord.File(graph, filename="flips_graph.png")
