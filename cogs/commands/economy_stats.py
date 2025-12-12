import discord
from discord.ext import commands
from discord import app_commands
from components.views.economy_view import EconomyMenuView

class EconomyCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="economy_stats", description="View your economy stats, flips, and auctions")
    async def economy_stats(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        await self.bot.player_manager.get_or_create_player(
            interaction.user.id, interaction.user.name
        )
        
        view = EconomyMenuView(self.bot, interaction.user.id)
        embed = await view.get_embed()
        
        await interaction.followup.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(EconomyCommands(bot))
