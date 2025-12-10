import discord
from discord.ext import commands
from discord import app_commands
from components.views.hotm_menu_view import HotmMenuView


class HotMCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="hotm", description="View your Heart of the Mountain progress")
    async def hotm(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        await self.bot.player_manager.get_or_create_player(
            interaction.user.id, interaction.user.name
        )
        
        view = HotmMenuView(self.bot, interaction.user.id)
        await view.refresh_data()
        embed = await view.get_embed()
        
        message = await interaction.followup.send(embed=embed, view=view)
        view.message = message


async def setup(bot):
    await bot.add_cog(HotMCommands(bot))
