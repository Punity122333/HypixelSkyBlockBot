import discord
from discord.ext import commands
from discord import app_commands
from typing import TYPE_CHECKING
from components.views.museum_view import MuseumView

if TYPE_CHECKING:
    from main import SkyblockBot


class MuseumCommands(commands.Cog):
    def __init__(self, bot: "SkyblockBot"):
        self.bot = bot

    @app_commands.command(name="museum", description="Access your museum collection showcase")
    async def museum(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        await self.bot.player_manager.get_or_create_player(
            interaction.user.id, interaction.user.name
        )
        
        view = MuseumView(self.bot, interaction.user.id, interaction.user.name)
        await view.load_data()
        embed = await view.get_embed()
        
        await interaction.followup.send(embed=embed, view=view)


async def setup(bot):
    await bot.add_cog(MuseumCommands(bot))
