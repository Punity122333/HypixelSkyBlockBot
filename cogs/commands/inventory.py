import discord
from discord.ext import commands
from discord import app_commands
from components.views.inventory_menu_view import InventoryMenuView

class InventoryCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="inventory", description="View your inventory and storage")
    async def inventory(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        await self.bot.player_manager.get_or_create_player(
            interaction.user.id, interaction.user.name
        )
        
        view = InventoryMenuView(self.bot, interaction.user.id, interaction.user.name)
        embed = await view.get_embed()
        view._update_buttons()
        
        await interaction.followup.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(InventoryCommands(bot))
