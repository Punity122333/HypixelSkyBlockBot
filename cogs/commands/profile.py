import discord
from discord.ext import commands
from discord import app_commands
import typing
import json
from utils.stat_calculator import StatCalculator
from components.views.profile_menu_view import ProfileMenuView

class ProfileCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="profile", description="View your SkyBlock profile")
    async def profile(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        await self.bot.player_manager.get_or_create_player(
            interaction.user.id, interaction.user.name
        )
        
        view = ProfileMenuView(self.bot, interaction.user.id, interaction.user.name)
        embed = await view.get_embed()
        
        await interaction.followup.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(ProfileCommands(bot))