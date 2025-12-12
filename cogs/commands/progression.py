import discord
from discord.ext import commands
from discord import app_commands
from components.views.progression_view import ProgressionMenuView

class ProgressionCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="progression", description="View your progression, milestones, and tool upgrades")
    async def progression(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        await self.bot.player_manager.get_or_create_player(
            interaction.user.id, interaction.user.name
        )
        
        view = ProgressionMenuView(self.bot, interaction.user.id)
        embed = await view.get_embed()
        
        await interaction.followup.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(ProgressionCommands(bot))
