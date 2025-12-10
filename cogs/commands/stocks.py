import discord
from discord.ext import commands
from discord import app_commands
import matplotlib
matplotlib.use('Agg')
from components.views.stock_menu_view import StockMenuView

class StockMarketCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="stocks", description="Access the Stock Exchange")
    async def stocks_menu(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        await self.bot.player_manager.get_or_create_player(
            interaction.user.id, interaction.user.name
        )
        
        view = StockMenuView(self.bot, interaction.user.id)
        await view.load_stocks()
        embed = await view.get_embed()
        
        await interaction.followup.send(embed=embed, view=view)


async def setup(bot):
    await bot.add_cog(StockMarketCommands(bot))
