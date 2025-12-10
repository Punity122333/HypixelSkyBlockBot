import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Button
from typing import TYPE_CHECKING
from components.views.party_menu_view import PartyMenuView

if TYPE_CHECKING:
    from main import SkyblockBot

class PartyCommands(commands.Cog):
    def __init__(self, bot: "SkyblockBot"):
        self.bot = bot
    
    @app_commands.command(name="party", description="Manage your party")
    async def party(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        view = PartyMenuView(self.bot, interaction.user.id, interaction.user.name)
        embed = await view.get_embed()
        
        await interaction.followup.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(PartyCommands(bot))
