import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional
from utils.decorators import auto_defer
from components.views.party_finder_view import PartyFinderView

class PartyFinderCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="party_finder", description="Browse and manage dungeon parties with all features")
    @auto_defer
    async def party_finder(self, interaction: discord.Interaction):
        await self.bot.player_manager.get_or_create_player(interaction.user.id, interaction.user.name)
        
        view = PartyFinderView(self.bot, interaction.user.id)
        await view.load_parties()
        embed = await view.get_embed()
        
        await interaction.followup.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(PartyFinderCommands(bot))