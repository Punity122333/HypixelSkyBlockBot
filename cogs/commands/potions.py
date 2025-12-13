import discord
from discord import app_commands
from discord.ext import commands
from typing import TYPE_CHECKING
from components.views.potion_menu_view import PotionMenuView

if TYPE_CHECKING:
    from main import SkyblockBot

class PotionCommands(commands.Cog):
    def __init__(self, bot: "SkyblockBot"):
        self.bot = bot
    
    @app_commands.command(name="potions", description="Access the Potion menu with all features")
    async def potions(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        await self.bot.player_manager.get_or_create_player(
            interaction.user.id, interaction.user.name
        )
        
        view = PotionMenuView(self.bot, interaction.user.id)
        await view.load_active_potions()
        embed = await view.get_embed()
        
        await interaction.followup.send(embed=embed, view=view)

async def setup(bot: "SkyblockBot"):
    await bot.add_cog(PotionCommands(bot))
