import discord
import time
from discord.ext import commands
from discord import app_commands
from utils.systems.market_graphing_system import MarketGraphingSystem
from utils.decorators import auto_defer
from components.views.market_graphs_view import MarketGraphsView

class MarketGraphingCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="market_graphs", description="View market analytics and trends with all features")
    @auto_defer
    async def market_graphs(self, interaction: discord.Interaction):
        await self.bot.player_manager.get_or_create_player(interaction.user.id, interaction.user.name)
        
        view = MarketGraphsView(self.bot, interaction.user.id)
        embed = await view.get_embed()
        
        await interaction.followup.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(MarketGraphingCommands(bot))