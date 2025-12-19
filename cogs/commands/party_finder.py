import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional
from utils.decorators import auto_defer
from components.views.party_finder_view import PartyFinderView

class PartyFinderCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="party", description="Manage your party and browse dungeon parties")
    @auto_defer
    async def party(self, interaction: discord.Interaction):
        await self.bot.player_manager.get_or_create_player(interaction.user.id, interaction.user.name)
        
        view = PartyFinderView(self.bot, interaction.user.id)
        await view.load_parties()
        
        from utils.systems.party_system import PartySystem
        party = PartySystem.get_party(interaction.user.id)
        if party:
            view.current_view = 'my_party'
            view._update_buttons()
        
        embed = await view.get_embed()
        
        await interaction.followup.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(PartyFinderCommands(bot))