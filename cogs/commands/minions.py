import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Button
from components.views.minion_menu_view import MinionMenuView

class MinionCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="minions", description="View and manage your minions")
    async def minions(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        await self.bot.player_manager.get_or_create_player(
            interaction.user.id, interaction.user.name
        )
        
        minions = await self.bot.db.get_user_minions(interaction.user.id)
        
        view = MinionMenuView(self.bot, interaction.user.id, minions)
        embed = await view.get_embed()
        
        await interaction.followup.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(MinionCommands(bot))
