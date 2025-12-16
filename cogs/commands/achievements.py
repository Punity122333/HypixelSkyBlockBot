import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional
from components.views.achievements_view import AchievementsMenuView


class AchievementsCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="achievements", description="View your achievements")
    @app_commands.describe(
        user="The user whose achievements you want to view (defaults to yourself)"
    )
    async def achievements(self, interaction: discord.Interaction, user: Optional[discord.User] = None):
        await interaction.response.defer()
        
        target_user = user or interaction.user
        
        view = AchievementsMenuView(self.bot, interaction.user.id, target_user)
        await view.load_data()
        embed = await view.get_embed()
        
        await interaction.followup.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(AchievementsCommands(bot))
