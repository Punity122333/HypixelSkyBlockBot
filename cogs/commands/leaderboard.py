import discord
from discord.ext import commands
from discord import app_commands
from components.views.leaderboard_menu_view import LeaderboardMenuView

class LeaderboardCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="leaderboard", description="View server leaderboards")
    async def leaderboard(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        view = LeaderboardMenuView(self.bot, interaction.user.id)
        await view.load_data()
        embed = await view.get_embed()
        
        await interaction.followup.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(LeaderboardCommands(bot))
