import discord
from discord.ext import commands
from discord import app_commands
from components.views.bazaar_view import BazaarMenuView

class BazaarCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="bazaar", description="Access the Bazaar with all features")
    async def bazaar(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        await self.bot.player_manager.get_or_create_player(
            interaction.user.id, interaction.user.name
        )
        
        view = BazaarMenuView(self.bot, interaction.user.id)
        await view.load_orders() 
        embed = await view.get_embed()
        
        await interaction.followup.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(BazaarCommands(bot))