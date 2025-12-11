import discord
from discord import app_commands
from discord.ext import commands
from typing import TYPE_CHECKING
from components.views.talisman_pouch_view import TalismanPouchMenuView

if TYPE_CHECKING:
    from main import SkyblockBot

class TalismanPouchCommands(commands.Cog):
    def __init__(self, bot: "SkyblockBot"):
        self.bot = bot
    
    @app_commands.command(name="talisman_pouch", description="View and manage your talisman pouch")
    async def talisman_pouch(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        await self.bot.player_manager.get_or_create_player(
            interaction.user.id, interaction.user.name
        )
        
        view = TalismanPouchMenuView(self.bot, interaction.user.id)
        await view.load_talismans()
        embed = await view.get_embed()
        
        await interaction.followup.send(embed=embed, view=view)

async def setup(bot: "SkyblockBot"):
    await bot.add_cog(TalismanPouchCommands(bot))
