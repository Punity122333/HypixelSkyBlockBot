import discord
from discord.ext import commands
from discord import app_commands
from typing import TYPE_CHECKING
from components.views.slayer_menu_view import SlayerMenuView

if TYPE_CHECKING:
    from main import SkyblockBot
    from discord import Interaction

class SlayerCommands(commands.Cog):
    def __init__(self, bot: "SkyblockBot"):
        self.bot = bot

    @app_commands.command(name="slayer", description="Access the Slayer system")
    async def slayer_menu(self, interaction: "Interaction"):
        await interaction.response.defer()
        
        await self.bot.player_manager.get_or_create_player(
            interaction.user.id, interaction.user.name
        )
        
        view = SlayerMenuView(self.bot, interaction.user.id, interaction.user.name)
        embed = await view.get_embed()
        
        await interaction.followup.send(embed=embed, view=view)

async def setup(bot: "SkyblockBot"):
    await bot.add_cog(SlayerCommands(bot))