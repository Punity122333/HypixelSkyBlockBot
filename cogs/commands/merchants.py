import discord
from discord.ext import commands
from discord import app_commands
from components.views.merchant_menu_view import MerchantMenuView

class MerchantCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="merchants", description="View and interact with traveling merchants")
    async def merchants(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        await self.bot.player_manager.get_or_create_player(
            interaction.user.id, interaction.user.name
        )
        
        view = MerchantMenuView(self.bot, interaction.user.id)
        await view.load_deals()
        embed = await view.get_embed()
        
        await interaction.followup.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(MerchantCommands(bot))
