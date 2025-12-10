import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional
from utils.systems.coop_system import CoopSystem
from utils.systems.badge_system import BadgeSystem
from utils.decorators import auto_defer
from components.views.coop_view import CoopView

class CoopCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="coop", description="Manage your co-op with all features")
    @auto_defer
    async def coop(self, interaction: discord.Interaction):
        await self.bot.player_manager.get_or_create_player(interaction.user.id, interaction.user.name)
        
        view = CoopView(self.bot, interaction.user.id)
        await view.load_coop_data()
        view._update_buttons()
        embed = await view.get_embed()
        
        await interaction.followup.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(CoopCommands(bot))